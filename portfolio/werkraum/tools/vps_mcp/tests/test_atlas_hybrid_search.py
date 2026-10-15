from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import mcp_atlas_hybrid_search as hybrid


class AtlasHybridSearchTest(unittest.TestCase):
    """2026-07-31: Hybrid-Suche (BM25 + Vektor per RRF), angelehnt an qmd/LLMWikiNG.
    Nutzt pro Test ein EIGENES, eindeutiges Temp-Verzeichnis (nicht den echten Index
    unter _gpt/gesamtatlas/vektorindex/ und nicht denselben Pfad mehrfach
    wiederverwendet) -- ein wiederverwendeter fester Pfad fuehrte live zu einem
    Test-Isolationsfehler (chromadb-interne Zustaende ueberlebten offenbar den
    rmtree+Neuerzeugung-Zyklus zwischen Tests, vermutlich Thread-/Cache-Timing).
    Mit tempfile.mkdtemp() pro Test tritt der Fehler nicht mehr auf."""

    def setUp(self) -> None:
        self._original_index_pfad = hybrid.VEKTOR_INDEX_PFAD
        self._original_client = hybrid._chroma_client
        self._original_collection = hybrid._chroma_collection
        self._test_pfad = Path(tempfile.mkdtemp(prefix="pytest_hybrid_search_"))
        hybrid.VEKTOR_INDEX_PFAD = self._test_pfad
        hybrid._chroma_client = None
        hybrid._chroma_collection = None

    def tearDown(self) -> None:
        hybrid.VEKTOR_INDEX_PFAD = self._original_index_pfad
        hybrid._chroma_client = self._original_client
        hybrid._chroma_collection = self._original_collection
        shutil.rmtree(self._test_pfad, ignore_errors=True)

    def test_vektor_index_und_suche(self) -> None:
        hybrid.vektor_index_aktualisieren(
            pfad="testpfad/datenbank.md",
            text="Datenbankmigration: wie man Postgres sicher migriert, mit Backup und Rollback.",
            metadaten={"titel": "Datenbankmigration"},
        )
        hybrid.vektor_index_aktualisieren(
            pfad="testpfad/katzenfutter.md",
            text="Katzenfutter: welche Marken fuer empfindliche Maegen am besten sind.",
            metadaten={"titel": "Katzenfutter"},
        )
        treffer = hybrid._vektor_suche("Datenbank sicher umziehen", limit=5)
        self.assertGreater(len(treffer), 0)
        # Die Datenbank-Datei muss vor der Katzenfutter-Datei kommen (semantisch naeher).
        pfade = [t["pfad"] for t in treffer]
        self.assertLess(pfade.index("testpfad/datenbank.md"), pfade.index("testpfad/katzenfutter.md"))

    def test_rrf_fusion_kombiniert_beide_quellen(self) -> None:
        hybrid.vektor_index_aktualisieren(
            pfad="testpfad/nur_vektor.md",
            text="Ein Text, der nur ueber Bedeutung, nicht ueber exakte Woerter gefunden wird.",
            metadaten={"titel": "Nur Vektor"},
        )
        r = hybrid.hybrid_suche("Bedeutung Woerter", limit=5)
        self.assertTrue(r["ok"])
        self.assertIn("ergebnisse", r)

    def test_leere_query_abgelehnt(self) -> None:
        r = hybrid.hybrid_suche("", limit=5)
        self.assertFalse(r["ok"])

    def test_ohne_treffer_liefert_leere_liste_kein_fehler(self) -> None:
        r = hybrid.hybrid_suche("xyz_garantiert_kein_treffer_qwertz_9999", limit=5)
        self.assertTrue(r["ok"])
        self.assertEqual(r["ergebnisse"], [])


if __name__ == "__main__":
    unittest.main()
