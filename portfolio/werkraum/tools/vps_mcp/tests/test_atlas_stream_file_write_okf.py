from __future__ import annotations

import shutil
import unittest
from pathlib import Path

import yaml

import mcp_atlas_hybrid_search as hybrid
import vps_mcp_server as srv


class AtlasStreamFileWriteOkfTest(unittest.TestCase):
    """2026-07-31: atlas.stream_file_write schreibt seither Open-Knowledge-Format-konformes
    (OKF v0.2, github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) YAML-
    Frontmatter automatisch vor den Inhalt. Diese Tests sichern nur die Frontmatter-
    Erzeugung selbst ab, schreiben aber real in AI_STROEME/claude/notizen/ (per
    Actor-Ableitung, siehe atlas.stream_file_write) und raeumen danach wieder auf --
    inklusive der Vektor-Index-Eintraege, die atlas.stream_file_write seit der
    Hybrid-Search-Anbindung automatisch mitschreibt (live gefunden: ohne dieses
    Aufraeumen blieben verwaiste Testeintraege im ECHTEN Index unter
    _gpt/gesamtatlas/vektorindex/ zurueck)."""

    def setUp(self) -> None:
        self._alter_actor = srv._LEGACY_HISTORY.actor
        srv._LEGACY_HISTORY.actor = "claude-code"
        self._geschriebene_pfade: list[Path] = []

    def tearDown(self) -> None:
        srv._LEGACY_HISTORY.actor = self._alter_actor
        for pfad in self._geschriebene_pfade:
            pfad.unlink(missing_ok=True)
        try:
            hybrid._hole_collection().delete(ids=[str(p) for p in self._geschriebene_pfade])
        except Exception:
            pass

    def _schreibe(self, **kwargs) -> dict:
        r = srv.tool_atlas_stream_file_write(kwargs)
        if r.get("ok") and r.get("data", {}).get("pfad"):
            self._geschriebene_pfade.append(Path(r["data"]["pfad"]))
        return r

    def test_frontmatter_pflichtfelder_vorhanden(self) -> None:
        r = self._schreibe(kategorie="notizen", dateiname="okf_pflichttest.md", inhalt="Inhalt.\n")
        self.assertTrue(r["ok"])
        text = Path(r["data"]["pfad"]).read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter_text = text.split("---\n", 2)[1]
        frontmatter = yaml.safe_load(frontmatter_text)
        self.assertEqual(frontmatter["type"], "Notiz")
        self.assertIn("claude", frontmatter["tags"])
        self.assertEqual(frontmatter["generated"]["by"], "claude")
        self.assertEqual(frontmatter["status"], "draft")
        self.assertTrue(text.endswith("Inhalt.\n"))

    def test_optionale_felder_uebernommen(self) -> None:
        r = self._schreibe(
            kategorie="konzepte", dateiname="okf_optionaltest.md", inhalt="X\n",
            titel="Mein Titel", beschreibung="Meine Beschreibung", tags=["extra"],
            status="stable", ressource="https://example.org", verlaeuft_am="2027-01-01",
        )
        self.assertTrue(r["ok"])
        frontmatter = yaml.safe_load(Path(r["data"]["pfad"]).read_text(encoding="utf-8").split("---\n", 2)[1])
        self.assertEqual(frontmatter["title"], "Mein Titel")
        self.assertEqual(frontmatter["description"], "Meine Beschreibung")
        self.assertIn("extra", frontmatter["tags"])
        self.assertEqual(frontmatter["status"], "stable")
        self.assertEqual(frontmatter["resource"], "https://example.org")
        self.assertEqual(frontmatter["stale_after"], "2027-01-01")

    def test_ungueltiger_status_abgelehnt(self) -> None:
        r = self._schreibe(kategorie="notizen", dateiname="okf_statustest.md", inhalt="X\n", status="erfunden")
        self.assertFalse(r["ok"])
        self.assertIn("status", r["error"])

    def test_generated_by_kann_nicht_gefaelscht_werden(self) -> None:
        r = self._schreibe(
            kategorie="notizen", dateiname="okf_faelschtest.md", inhalt="X\n",
            **{"generated": {"by": "chatgpt"}},  # kein echtes Feld, wird ignoriert
        )
        self.assertTrue(r["ok"])
        frontmatter = yaml.safe_load(Path(r["data"]["pfad"]).read_text(encoding="utf-8").split("---\n", 2)[1])
        self.assertEqual(frontmatter["generated"]["by"], "claude")


if __name__ == "__main__":
    unittest.main()
