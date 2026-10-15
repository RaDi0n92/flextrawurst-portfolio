#!/usr/bin/env python3
"""Playwright DOM checkout/recovery without taking over a production primary."""

from __future__ import annotations

from typing import Any

from .object_store import TriViewObjectStore
from .web_dom_adapter import capture_page_objects, install_mutation_stream, read_mutations, read_rrweb_events


class WebDomSession:
    def __init__(self, page: Any, store: TriViewObjectStore) -> None:
        self.page = page
        self.store = store
        self.checkout_count = 0
        self.recovery_count = 0
        self.attach()

    def attach(self) -> None:
        install_mutation_stream(self.page)

    def checkout(self, selector: str = "[data-fw-object-id]") -> dict[str, Any]:
        mutations = read_mutations(self.page)
        rrweb_events = read_rrweb_events(self.page)
        objects = capture_page_objects(self.page, self.store, selector)
        self.checkout_count += 1
        return {"checkout": self.checkout_count, "objects": objects, "mutations": mutations, "rrweb_events": rrweb_events, "mirror_schema": "rrweb-compatible.v1", "page_url": self.page.url, "fresh": True}

    def recover(self, page: Any) -> dict[str, Any]:
        self.page = page
        self.recovery_count += 1
        self.attach()
        return {"recovered": True, "recovery_count": self.recovery_count, "page_url": self.page.url}
