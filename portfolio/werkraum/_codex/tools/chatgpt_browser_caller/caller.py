#!/usr/bin/env python3
"""Bounded ChatGPT browser caller.

The first slice is deliberately explicit:

* discovery is read-only;
* a slot is bound only by an explicit selector;
* sending requires an explicitly bound slot;
* no network endpoint, cookie, or browser extension is used;
* no slot fan-out is performed implicitly.

The live ``send`` path is included for the next proof step, but this module's
own tests do not touch a browser.  A real send should only be run against a
ChatGPT conversation selected by the operator.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen


DEFAULT_CDP_ENDPOINT = "http://127.0.0.1:9222"
DEFAULT_STATE_PATH = Path(__file__).with_name("state") / "slots.json"
CHATGPT_HOSTS = {"chatgpt.com", "www.chatgpt.com"}
CHATGPT_PATH = re.compile(r"^/c/[A-Za-z0-9-]+(?:/)?$")


class CallerError(RuntimeError):
    """A user-actionable caller error."""


@dataclass(frozen=True)
class Target:
    target_id: str
    title: str
    url: str
    conversation_id: str | None
    target_type: str

    @property
    def is_chatgpt_conversation(self) -> bool:
        parsed = urlparse(self.url)
        return (
            parsed.scheme in {"http", "https"}
            and parsed.hostname in CHATGPT_HOSTS
            and bool(CHATGPT_PATH.fullmatch(parsed.path))
        )


@dataclass
class Slot:
    slot_id: str
    target_id: str
    url: str
    title: str
    conversation_id: str | None
    bound_explicitly: bool
    created_at: str
    last_seen_at: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def conversation_id_from_url(url: str) -> str | None:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return parts[1] if len(parts) == 2 and parts[0] == "c" else None


def stable_conversation_id_from_url(url: str) -> str | None:
    conversation_id = conversation_id_from_url(url)
    if not conversation_id or conversation_id.startswith("WEB:"):
        return None
    return conversation_id


def normalise_target(raw: dict[str, Any]) -> Target:
    url = str(raw.get("url") or "")
    return Target(
        target_id=str(raw.get("id") or raw.get("targetId") or ""),
        title=str(raw.get("title") or ""),
        url=url,
        conversation_id=conversation_id_from_url(url),
        target_type=str(raw.get("type") or ""),
    )


def parse_targets(payload: Iterable[dict[str, Any]]) -> list[Target]:
    """Return only real ChatGPT conversation page targets."""

    targets = [normalise_target(item) for item in payload]
    return sorted(
        (
            target
            for target in targets
            if target.target_type == "page" and target.is_chatgpt_conversation
        ),
        key=lambda target: (target.title.casefold(), target.target_id),
    )


def target_to_json(target: Target) -> dict[str, Any]:
    return {
        "target_id": target.target_id,
        "title": target.title,
        "url": target.url,
        "conversation_id": target.conversation_id,
        "target_type": target.target_type,
    }


def _load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CallerError(f"Zustandsdatei ist nicht lesbar: {path}: {exc}") from exc


def _atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class SlotStore:
    def __init__(self, path: Path = DEFAULT_STATE_PATH) -> None:
        self.path = path

    def load(self) -> dict[str, Slot]:
        raw = _load_json(self.path, {"slots": {}})
        if not isinstance(raw, dict) or not isinstance(raw.get("slots", {}), dict):
            raise CallerError(f"Ungültiges Slot-Format: {self.path}")
        slots: dict[str, Slot] = {}
        for slot_id, item in raw.get("slots", {}).items():
            if not isinstance(item, dict):
                raise CallerError(f"Ungültiger Slot {slot_id!r} in {self.path}")
            slot_data = dict(item)
            slot_data.pop("slot_id", None)
            slots[str(slot_id)] = Slot(slot_id=str(slot_id), **slot_data)
        return slots

    def save(self, slots: dict[str, Slot]) -> None:
        _atomic_write_json(
            self.path,
            {"version": 1, "slots": {key: asdict(value) for key, value in slots.items()}},
        )


class ChatGPTBrowserCaller:
    def __init__(
        self,
        cdp_endpoint: str = DEFAULT_CDP_ENDPOINT,
        state_path: Path = DEFAULT_STATE_PATH,
    ) -> None:
        self.cdp_endpoint = cdp_endpoint.rstrip("/")
        self.store = SlotStore(state_path)

    def discover(self) -> list[Target]:
        url = f"{self.cdp_endpoint}/json/list"
        try:
            with urlopen(url, timeout=3) as response:
                payload = json.load(response)
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise CallerError(f"Chromium-CDP ist nicht erreichbar: {url}: {exc}") from exc
        if not isinstance(payload, list):
            raise CallerError("Chromium-CDP lieferte keine Zielliste")
        return parse_targets(payload)

    def bind(self, slot_id: str, selector: str) -> Slot:
        if not slot_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", slot_id):
            raise CallerError("Slot-ID muss mit einem Buchstaben/Ziffer beginnen")

        targets = self.discover()
        matching = [target for target in targets if self._selector_matches(target, selector)]
        if not matching:
            raise CallerError(
                f"Kein ChatGPT-Ziel für {selector!r}. Erst discover ausführen und exakt auswählen."
            )
        if len(matching) > 1:
            ids = ", ".join(target.target_id for target in matching)
            raise CallerError(f"Selector ist nicht eindeutig; Treffer: {ids}")

        target = matching[0]
        now = utc_now()
        slot = Slot(
            slot_id=slot_id,
            target_id=target.target_id,
            url=target.url,
            title=target.title,
            conversation_id=target.conversation_id,
            bound_explicitly=True,
            created_at=now,
            last_seen_at=now,
        )
        slots = self.store.load()
        slots[slot_id] = slot
        self.store.save(slots)
        return slot

    @staticmethod
    def _selector_matches(target: Target, selector: str) -> bool:
        return selector in {target.target_id, target.url, target.title}

    def slots(self) -> list[Slot]:
        return sorted(self.store.load().values(), key=lambda slot: slot.slot_id)

    def inspect_live(self) -> list[dict[str, Any]]:
        """Read visible ChatGPT DOM capabilities without changing the browser."""

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CallerError("Python-Paket playwright ist nicht installiert") from exc

        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(self.cdp_endpoint)
        try:
            inspected: list[dict[str, Any]] = []
            for context in browser.contexts:
                for page in context.pages:
                    target = normalise_target(
                        {
                            "id": self._page_target_id(context, page),
                            "type": "page",
                            "title": page.title(),
                            "url": page.url,
                        }
                    )
                    if not target.is_chatgpt_conversation:
                        continue
                    inspected.append(
                        {
                            **target_to_json(target),
                            "visibility_state": page.evaluate("document.visibilityState"),
                            "has_focus": page.evaluate("document.hasFocus()"),
                            "composer_visible": self._composer(page) is not None,
                            "send_control_visible": self._send_control(page) is not None,
                        }
                    )
            return inspected
        finally:
            # For a CDP connection this disconnects Playwright; it does not
            # close the operator's existing Chromium pages.
            browser.close()
            playwright.stop()

    @staticmethod
    def _page_target_id(context, page) -> str:
        """Read Chromium's target identity for exactly this Playwright page."""

        try:
            session = context.new_cdp_session(page)
            info = session.send("Target.getTargetInfo")
            session.detach()
        except Exception as exc:  # pragma: no cover - depends on live Chromium
            raise CallerError(f"Chromium-Tabidentität nicht lesbar: {exc}") from exc
        target_id = str(info.get("targetInfo", {}).get("targetId") or "")
        if not target_id:
            raise CallerError("Chromium lieferte keine Target-ID für einen ChatGPT-Tab")
        return target_id

    def _bound_slot(self, slot_id: str) -> Slot:
        slot = self.store.load().get(slot_id)
        if slot is None:
            raise CallerError(f"Slot {slot_id!r} ist nicht gebunden")
        if not slot.bound_explicitly:
            raise CallerError(f"Slot {slot_id!r} ist nicht explizit gebunden")
        if urlparse(slot.url).hostname not in CHATGPT_HOSTS:
            raise CallerError(f"Slot {slot_id!r} zeigt nicht auf chatgpt.com")
        return slot

    def _touch_slot(self, slot_id: str, page) -> None:
        slots = self.store.load()
        slot = slots.get(slot_id)
        if slot is None:
            raise CallerError(f"Slot {slot_id!r} verschwand während des Turns")
        if self._page_target_id(page.context, page) != slot.target_id:
            raise CallerError(f"Slot {slot_id!r} wechselte während des Turns den Tab")
        if page.url != slot.url or conversation_id_from_url(page.url) != slot.conversation_id:
            raise CallerError(f"Slot {slot_id!r} wechselte während des Turns die Konversation")
        slot.last_seen_at = utc_now()
        slots[slot_id] = slot
        self.store.save(slots)

    def _connect_page(self, slot: Slot):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CallerError("Python-Paket playwright ist nicht installiert") from exc

        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(self.cdp_endpoint)
        candidates = []
        for context in browser.contexts:
            for page in context.pages:
                if not page.url.startswith("https://chatgpt.com/"):
                    continue
                if self._page_target_id(context, page) != slot.target_id:
                    continue
                if page.url != slot.url:
                    raise CallerError(
                        f"Slot {slot.slot_id!r} hat dieselbe Tab-ID, aber eine andere URL"
                    )
                if conversation_id_from_url(page.url) != slot.conversation_id:
                    raise CallerError(
                        f"Slot {slot.slot_id!r} hat eine andere ChatGPT-Konversation"
                    )
                candidates.append(page)
        if len(candidates) != 1:
            browser.close()
            playwright.stop()
            raise CallerError(
                f"Slot {slot.slot_id!r} ist nicht eindeutig mit derselben Target-ID live auffindbar: "
                f"{len(candidates)} Treffer; kein Ausweich-Tab wird verwendet"
            )
        return playwright, browser, candidates[0]

    @staticmethod
    def _composer(page):
        selectors = [
            "#prompt-textarea",
            "textarea",
            "[contenteditable='true']",
        ]
        for selector in selectors:
            locator = page.locator(selector).first
            if locator.count() and locator.is_visible():
                return locator
        return None

    @staticmethod
    def _send_control(page):
        selectors = [
            "button[data-testid='send-button']",
            "button[aria-label='Send prompt']",
            "button[aria-label='Senden']",
            "form button[type='submit']",
        ]
        for selector in selectors:
            locator = page.locator(selector).first
            if locator.count() and locator.is_visible() and locator.is_enabled():
                return locator
        return None

    def spawn(
        self, slot_id: str, message: str, timeout_seconds: float = 90
    ) -> dict[str, Any]:
        """Open a fresh visible ChatGPT tab, start its first turn, and pin it.

        A conversation has no stable conversation ID until the first message
        is sent.  Therefore opening and first contact are one bounded
        operation.  The resulting slot is pinned to the new tab's Chromium
        target ID and the conversation ID observed afterwards.
        """

        if not slot_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", slot_id):
            raise CallerError("Slot-ID muss mit einem Buchstaben/Ziffer beginnen")
        if not message.strip():
            raise CallerError("Leere ChatGPT-Nachricht abgelehnt")
        if slot_id in self.store.load():
            raise CallerError(f"Slot {slot_id!r} existiert bereits; keinen Slot überschreiben")

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CallerError("Python-Paket playwright ist nicht installiert") from exc

        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(self.cdp_endpoint)
        try:
            if not browser.contexts:
                raise CallerError("Chromium hat keinen nutzbaren Browser-Kontext")
            context = browser.contexts[0]
            page = context.new_page()
            page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=30000)
            if urlparse(page.url).hostname not in CHATGPT_HOSTS:
                raise CallerError(f"Neuer Tab landete nicht auf chatgpt.com: {page.url}")
            target_id = self._page_target_id(context, page)
            composer = self._composer(page)
            if composer is None:
                raise CallerError("Neuer Chat hat kein sichtbares ChatGPT-Eingabefeld")
            composer.fill(message)
            send_control = self._send_control(page)
            if send_control is None:
                raise CallerError("Neuer Chat hat keinen sichtbaren Sende-Button")
            send_control.click()
            submitted = self._wait_for_user_message(page, message, timeout_seconds=10)
            if not submitted:
                raise CallerError("Erste ChatGPT-Nachricht wurde im DOM nicht bestätigt")
            assistant_text = self._wait_for_new_assistant_message(
                page, 0, timeout_seconds=timeout_seconds
            )
            conversation_id = self._wait_for_conversation_id(
                page, timeout_seconds=timeout_seconds
            )
            if assistant_text is None:
                raise CallerError("Keine neue ChatGPT-Antwort im DOM beobachtet")
            if conversation_id is None:
                raise CallerError("Keine Konversations-ID nach dem ersten Turn beobachtet")

            now = utc_now()
            slot = Slot(
                slot_id=slot_id,
                target_id=target_id,
                url=page.url,
                title=page.title(),
                conversation_id=conversation_id,
                bound_explicitly=True,
                created_at=now,
                last_seen_at=now,
            )
            slots = self.store.load()
            slots[slot_id] = slot
            self.store.save(slots)
            return {
                "slot": asdict(slot),
                "proof": {
                    "new_tab_opened": True,
                    "new_chat_loaded": True,
                    "target_identity_pinned": True,
                    "message_submitted": True,
                    "assistant_response_observed": True,
                    "conversation_identity_observed": True,
                },
                "assistant_text": assistant_text,
            }
        finally:
            # Disconnect Playwright while leaving the user's visible tab open.
            browser.close()
            playwright.stop()

    def send(self, slot_id: str, message: str, timeout_seconds: float = 90) -> dict[str, Any]:
        """Send one explicit message and read back one new assistant answer.

        This is intentionally not used by the discovery tests.  The method
        performs visible DOM interaction only and returns proof markers that
        describe what was actually observed.
        """

        if not message.strip():
            raise CallerError("Leere ChatGPT-Nachricht abgelehnt")
        slot = self._bound_slot(slot_id)
        playwright, browser, page = self._connect_page(slot)
        try:
            composer = self._composer(page)
            if composer is None:
                raise CallerError("Kein sichtbares ChatGPT-Eingabefeld gefunden")
            if self._generation_in_progress(page):
                raise CallerError(
                    "Der gebundene ChatGPT-Tab generiert noch; kein neuer Turn wird verschachtelt"
                )
            before = self._assistant_message_count(page)
            composer.fill(message)
            send_control = self._send_control(page)
            if send_control is None:
                raise CallerError("Kein sichtbarer ChatGPT-Sende-Button gefunden")
            send_control.click()
            submitted = self._wait_for_user_message(page, message, timeout_seconds=10)
            after = self._wait_for_new_assistant_message(
                page, before, timeout_seconds=timeout_seconds
            )
            if submitted and after is not None:
                self._touch_slot(slot_id, page)
            return {
                "slot_id": slot_id,
                "target_url": page.url,
                "proof": {
                    "attached": True,
                    "target_selected": True,
                    "composer_found": True,
                    "message_submitted": submitted,
                    "assistant_response_observed": after is not None,
                },
                "assistant_text": after,
            }
        finally:
            browser.close()
            playwright.stop()

    @staticmethod
    def _latest_assistant_after_last_user(page) -> str | None:
        turns = page.locator("[data-message-author-role]")
        last_user_index = -1
        candidate: str | None = None
        for index in range(turns.count()):
            turn = turns.nth(index)
            role = turn.get_attribute("data-message-author-role")
            if role == "user":
                last_user_index = index
                candidate = None
            elif role == "assistant" and index > last_user_index:
                text = turn.inner_text().strip()
                if text and not ChatGPTBrowserCaller._is_intermediate_answer(text):
                    candidate = text
        return candidate

    def collect(self, slot_id: str, timeout_seconds: float = 30) -> dict[str, Any]:
        """Collect a late answer from the same pinned slot without sending."""

        slot = self._bound_slot(slot_id)
        playwright, browser, page = self._connect_page(slot)
        try:
            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                if not self._generation_in_progress(page):
                    answer = self._latest_assistant_after_last_user(page)
                    if answer is not None:
                        self._touch_slot(slot_id, page)
                        return {
                            "slot_id": slot_id,
                            "target_url": page.url,
                            "proof": {
                                "attached": True,
                                "target_selected": True,
                                "send_performed": False,
                                "late_response_collected": True,
                            },
                            "assistant_text": answer,
                        }
                page.wait_for_timeout(500)
            return {
                "slot_id": slot_id,
                "target_url": page.url,
                "proof": {
                    "attached": True,
                    "target_selected": True,
                    "send_performed": False,
                    "late_response_collected": False,
                },
                "assistant_text": None,
            }
        finally:
            browser.close()
            playwright.stop()

    def review(
        self,
        slot_id: str,
        task: str,
        context_files: Iterable[Path] = (),
        timeout_seconds: float = 90,
    ) -> dict[str, Any]:
        """Send a bounded build checkpoint to an already pinned slot."""

        if not task.strip():
            raise CallerError("Leerer Review-Auftrag abgelehnt")
        sections = [
            "Du bist der unabhängige ChatGPT-Reviewer in einem Codex-Arbeitszyklus.",
            "Prüfe ausschließlich den unten gelieferten Checkpoint-Kontext.",
            "Melde konkrete Risiken, Widersprüche und fehlende Tests; ändere nichts.",
            "Arbeitsauftrag:",
            task.strip(),
        ]
        for raw_path in context_files:
            path = Path(raw_path).resolve()
            if not path.is_file():
                raise CallerError(f"Review-Kontext ist keine Datei: {path}")
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                raise CallerError(f"Review-Kontext nicht lesbar: {path}: {exc}") from exc
            if len(content.encode("utf-8")) > 250_000:
                raise CallerError(f"Review-Kontext zu groß: {path}")
            sections.extend([f"\n--- {path} ---", content])
        return self.send(slot_id, "\n".join(sections), timeout_seconds)

    @staticmethod
    def _assistant_message_count(page) -> int:
        return page.locator("[data-message-author-role='assistant']").count()

    @staticmethod
    def _assistant_messages(page) -> list[str]:
        values = []
        locator = page.locator("[data-message-author-role='assistant']")
        for index in range(locator.count()):
            text = locator.nth(index).inner_text().strip()
            if text:
                values.append(text)
        return values

    @staticmethod
    def _generation_in_progress(page) -> bool:
        selectors = [
            "button[data-testid='stop-button']",
            "button[aria-label='Stop generating']",
            "button[aria-label='Generierung stoppen']",
            "button[aria-label='Stopp']",
        ]
        return any(
            page.locator(selector).first.count()
            and page.locator(selector).first.is_visible()
            for selector in selectors
        )

    @staticmethod
    def _is_intermediate_answer(text: str) -> bool:
        normalised = " ".join(text.casefold().split())
        return normalised in {
            "denkt nach ...",
            "denkt nach…",
            "thinking ...",
            "thinking…",
            "generating ...",
            "generating…",
        }

    @staticmethod
    def _wait_for_user_message(page, message: str, timeout_seconds: float) -> bool:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if page.get_by_text(message, exact=True).count():
                return True
            page.wait_for_timeout(200)
        return False

    def _wait_for_new_assistant_message(
        self, page, before: int, timeout_seconds: float
    ) -> str | None:
        deadline = time.monotonic() + timeout_seconds
        last_text: str | None = None
        stable_since: float | None = None
        while time.monotonic() < deadline:
            messages = self._assistant_messages(page)
            if len(messages) > before:
                candidate = messages[-1]
                if (
                    candidate
                    and not self._is_intermediate_answer(candidate)
                    and not self._generation_in_progress(page)
                ):
                    now = time.monotonic()
                    if candidate != last_text:
                        last_text = candidate
                        stable_since = now
                    elif stable_since is not None and now - stable_since >= 1.0:
                        return candidate
            page.wait_for_timeout(500)
        return None

    @staticmethod
    def _wait_for_conversation_id(page, timeout_seconds: float) -> str | None:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            conversation_id = stable_conversation_id_from_url(page.url)
            if conversation_id:
                return conversation_id
            page.wait_for_timeout(500)
        return None


def json_output(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdp", default=DEFAULT_CDP_ENDPOINT, help="Chromium-CDP endpoint")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("discover", help="ChatGPT-Ziele read-only auflisten")
    subparsers.add_parser("inspect", help="Live-DOM read-only prüfen")
    subparsers.add_parser("slots", help="Explizit gebundene Slots auflisten")

    bind = subparsers.add_parser("bind", help="Ein Ziel explizit an einen Slot binden")
    bind.add_argument("slot_id")
    bind.add_argument("selector", help="Exakte target_id, URL oder Titel aus discover")

    send = subparsers.add_parser("send", help="Eine Nachricht in einem Slot senden")
    send.add_argument("slot_id")
    send.add_argument("message")
    send.add_argument("--timeout", type=float, default=90)

    review = subparsers.add_parser(
        "review", help="Einen Build-Checkpoint an einen gebundenen Slot senden"
    )
    review.add_argument("slot_id")
    review.add_argument("task")
    review.add_argument("--context-file", action="append", type=Path, default=[])
    review.add_argument("--timeout", type=float, default=90)

    collect = subparsers.add_parser(
        "collect", help="Späte Antwort aus demselben gebundenen Slot abholen"
    )
    collect.add_argument("slot_id")
    collect.add_argument("--timeout", type=float, default=30)

    spawn = subparsers.add_parser(
        "spawn", help="Neuen ChatGPT-Tab öffnen, ersten Turn senden und als Slot pinnen"
    )
    spawn.add_argument("slot_id")
    spawn.add_argument("message")
    spawn.add_argument("--timeout", type=float, default=90)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    caller = ChatGPTBrowserCaller(cdp_endpoint=args.cdp, state_path=args.state)
    try:
        if args.command == "discover":
            json_output(
                {
                    "scope": "chatgpt-browser-caller-only",
                    "read_only": True,
                    "targets": [target_to_json(target) for target in caller.discover()],
                }
            )
        elif args.command == "inspect":
            json_output(
                {
                    "scope": "chatgpt-browser-caller-only",
                    "read_only": True,
                    "live_pages": caller.inspect_live(),
                }
            )
        elif args.command == "slots":
            json_output({"slots": [asdict(slot) for slot in caller.slots()]})
        elif args.command == "bind":
            json_output({"bound": asdict(caller.bind(args.slot_id, args.selector))})
        elif args.command == "send":
            json_output(caller.send(args.slot_id, args.message, args.timeout))
        elif args.command == "review":
            json_output(
                caller.review(
                    args.slot_id,
                    args.task,
                    context_files=args.context_file,
                    timeout_seconds=args.timeout,
                )
            )
        elif args.command == "collect":
            json_output(caller.collect(args.slot_id, args.timeout))
        elif args.command == "spawn":
            json_output(caller.spawn(args.slot_id, args.message, args.timeout))
        else:
            raise CallerError(f"Unbekannter Befehl: {args.command}")
        return 0
    except CallerError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
