"""RAG über den Ereignisspeicher (G15): Ereignisse, Läufe und Befunde per Bedeutung wiederfinden.

Einbettung lokal per ONNX, 384 Dimensionen, gespeichert in `einbettung` (pgvector, Kosinus). Die Ereignisse sind deutsch, darum ist das mehrsprachige
Modell paraphrase-multilingual-MiniLM-L12-v2 die erste Wahl; all-MiniLM-L6-v2 (englisch, wie `_claude/tools/semantische_suche.py`) ist nur der Ersatz
(gemessen: es setzt „Kaffeemaschine leer“ gleich nah an „kein frisches Bild“ wie den echten Treffer). Jeder Vektor trägt sein Modell; gesucht wird nur im eigenen. Kein Drittanbieter, kein Netz. Einbetten ist nachholbar: `einbetten_neue` nimmt nur Ereignisse ohne Vektor.
Die Suche gibt Treffer mit Quelle, Lauf, Agent, Zeit und Abstand zurück, damit jeder Treffer auf das Original im Speicher zeigt.
"""

from __future__ import annotations

import os
from pathlib import Path

from .ereignisspeicher import Ereignisspeicher

MIN_TEXT = 8
NICHT_EINBETTEN = ("frame",)  # 23 000 gleichförmige „Bild 1632×800“-Zeilen würden den Vektorraum fluten und jede Frage treffen
MAX_TOKEN = 256
CACHES = (Path.home() / ".cache", Path("/vps_root/.cache"))
# (Name, Modellordner relativ zum Cache, Ordner mit model.onnx, Ordner mit tokenizer.json)
MODELLE = (
    ("paraphrase-multilingual-MiniLM-L12-v2", "huggingface/transformers-js/Xenova/paraphrase-multilingual-MiniLM-L12-v2", "onnx", "."),
    ("all-MiniLM-L6-v2", "chroma/onnx_models/all-MiniLM-L6-v2", "onnx", "onnx"),
)


def finde_modell(ordner: Path | None = None) -> tuple[str, Path, Path]:
    """(Name, model.onnx, tokenizer.json). `BRIDGE_EMBED_DIR` (Ordner mit model.onnx und tokenizer.json) hat Vorrang."""
    vorgabe = ordner or (Path(os.environ["BRIDGE_EMBED_DIR"]) if os.environ.get("BRIDGE_EMBED_DIR") else None)
    if vorgabe:
        if (vorgabe / "model.onnx").is_file() and (vorgabe / "tokenizer.json").is_file():
            return vorgabe.name, vorgabe / "model.onnx", vorgabe / "tokenizer.json"
        raise FileNotFoundError(f"kein Modell in {vorgabe}")
    for name, rel, onnx_dir, tok_dir in MODELLE:
        for cache in CACHES:
            m, t = cache / rel / onnx_dir / "model.onnx", cache / rel / tok_dir / "tokenizer.json"
            if m.is_file() and t.is_file():
                return name, m, t
    raise FileNotFoundError("kein ONNX-Einbettungsmodell gefunden (BRIDGE_EMBED_DIR setzen)")


class Einbetter:
    def __init__(self, ordner: Path | None = None):
        import onnxruntime
        from tokenizers import Tokenizer

        self.name, modell, tokenizer = finde_modell(ordner)
        self._tok = Tokenizer.from_file(str(tokenizer))
        self._tok.enable_truncation(max_length=MAX_TOKEN)
        if not self._tok.padding:
            pad = next((t for t in ("<pad>", "[PAD]") if self._tok.token_to_id(t) is not None), None)
            self._tok.enable_padding(pad_id=self._tok.token_to_id(pad) if pad else 0, pad_token=pad or "[PAD]")
        self._sitzung = onnxruntime.InferenceSession(str(modell), providers=["CPUExecutionProvider"])
        self._eingaben = {i.name for i in self._sitzung.get_inputs()}

    def einbetten(self, texte: list[str]) -> list[list[float]]:
        import numpy as np

        if not texte:
            return []
        kodiert = self._tok.encode_batch(texte)
        ids = np.array([k.ids for k in kodiert], dtype=np.int64)
        maske = np.array([k.attention_mask for k in kodiert], dtype=np.int64)
        eingabe = {"input_ids": ids, "attention_mask": maske}
        if "token_type_ids" in self._eingaben:
            eingabe["token_type_ids"] = np.zeros_like(ids)
        ausgabe = self._sitzung.run(None, eingabe)[0]  # (n, tokens, 384)
        m = maske[:, :, None].astype(np.float32)
        mittel = (ausgabe * m).sum(axis=1) / np.clip(m.sum(axis=1), 1e-9, None)
        mittel = mittel / np.clip(np.linalg.norm(mittel, axis=1, keepdims=True), 1e-9, None)
        return mittel.tolist()


def _vektor_text(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"


def dokument(e: dict) -> str:
    """Der Text, der eingebettet wird: Art, Agent, Knoten, Grund und Text — damit auch „Fehlversuch am Lease“ trifft."""
    teile = [e["art"], e.get("agent") or "", e.get("knoten") or "", e.get("grund") or "", e.get("text") or ""]
    return " · ".join(t for t in teile if t)


def einbetten_neue(speicher: Ereignisspeicher, einbetter: Einbetter, grenze: int = 500, stapel: int = 32) -> int:
    """Bettet Ereignisse ohne Vektor ein (nur solche mit Text ab `MIN_TEXT` Zeichen). Gibt die Anzahl zurück."""
    zeilen = speicher.abfrage(
        "SELECT e.* FROM ereignis e LEFT JOIN einbettung b ON b.ereignis_id = e.id AND b.modell = %s "
        "WHERE b.ereignis_id IS NULL AND length(e.text || e.grund) >= %s AND e.art <> ALL(%s) ORDER BY e.id LIMIT %s",
        (einbetter.name, MIN_TEXT, list(NICHT_EINBETTEN), grenze))
    fertig = 0
    for i in range(0, len(zeilen), stapel):
        teil = zeilen[i:i + stapel]
        for e, v in zip(teil, einbetter.einbetten([dokument(e) for e in teil])):
            speicher.abfrage("INSERT INTO einbettung (ereignis_id, modell, vektor) VALUES (%s,%s,%s::vector) ON CONFLICT DO NOTHING RETURNING 1",
                             (e["id"], einbetter.name, _vektor_text(v)))
            fertig += 1
    return fertig


def suche(speicher: Ereignisspeicher, einbetter: Einbetter, frage: str, n: int = 5, *, lauf: str = "", art: str = "", quelle: str = "") -> list[dict]:
    """Die n Ereignisse, die der Frage der Bedeutung nach am nächsten liegen; Filter sind optional."""
    v = _vektor_text(einbetter.einbetten([frage])[0])
    bedingungen, parameter = ["b.modell = %s"], [einbetter.name]
    for feld, wert in (("lauf", lauf), ("art", art), ("quelle", quelle)):
        if wert:
            bedingungen.append(f"e.{feld} = %s")
            parameter.append(wert)
    return speicher.abfrage(
        "SELECT e.id, e.quelle, e.art, e.agent, e.lauf, e.knoten, e.grund, e.text, e.zeit_ms, (b.vektor <=> %s::vector) AS abstand "
        f"FROM einbettung b JOIN ereignis e ON e.id = b.ereignis_id WHERE {' AND '.join(bedingungen)} ORDER BY b.vektor <=> %s::vector LIMIT %s",
        (v, *parameter, v, n))


def volltext(speicher: Ereignisspeicher, wort: str, n: int = 5) -> list[dict]:
    """Der Wortweg: dieselbe Tabelle über den GIN-Index auf dem Text; ein Treffer genügt mit einem der Wörter, mehr Treffer-Wörter stehen oben."""
    woerter = [w for w in "".join(c if c.isalnum() else " " for c in wort).split() if w]
    if not woerter:
        return []
    return speicher.abfrage(
        "SELECT id, quelle, art, agent, lauf, knoten, grund, text, zeit_ms FROM ereignis "
        "WHERE to_tsvector('simple', text) @@ to_tsquery('simple', %s) "
        "ORDER BY ts_rank(to_tsvector('simple', text), to_tsquery('simple', %s)) DESC, id DESC LIMIT %s", (" | ".join(woerter), " | ".join(woerter), n))


def hybrid(speicher: Ereignisspeicher, einbetter: Einbetter, frage: str, n: int = 5, *, lauf: str = "", art: str = "", quelle: str = "") -> list[dict]:
    """Bedeutung und Wort zusammen (Reciprocal Rank Fusion): was in beiden Listen weit oben steht, steht im Ergebnis oben.
    Der Wortweg fängt seltene Fachwörter (`Strg+S`, `lease_fehlt`), die das Modell verwischt; der Bedeutungsweg fängt Umschreibungen."""
    breit = max(20, n * 4)
    listen = [suche(speicher, einbetter, frage, breit, lauf=lauf, art=art, quelle=quelle), volltext(speicher, frage, breit)]
    punkte: dict[int, float] = {}
    zeilen: dict[int, dict] = {}
    for liste in listen:
        for rang, t in enumerate(liste):
            if (lauf and t["lauf"] != lauf) or (art and t["art"] != art) or (quelle and t["quelle"] != quelle):
                continue
            punkte[t["id"]] = punkte.get(t["id"], 0.0) + 1 / (60 + rang)
            zeilen.setdefault(t["id"], t)
    return [zeilen[i] for i in sorted(punkte, key=punkte.get, reverse=True)[:n]]
