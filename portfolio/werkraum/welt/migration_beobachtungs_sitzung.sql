-- On-Demand-Beobachtung (2026-07-31, Daniels Auftrag, Task 8): seit dem kompletten
-- Wegfall von Playwright/Chromium fuer alle 7 Wesen (VOLLSTAENDIG_OHNE_BROWSER) gibt es
-- keinen dauerhaft laufenden Browser mehr, den Menschen live beobachten koennten.
--
-- Ein einziger Button startet/verlaengert eine globale, 60-Sekunden-Beobachtungs-Sitzung
-- fuer ALLE 7 Wesen gleichzeitig (nicht pro Wesen) -- ein separater Dienst
-- (on_demand_beobachtung.py) pollt diese Tabelle und faehrt bei aktiver Sitzung einen
-- gemeinsamen Chromium-Prozess mit 7 eigenen Contexts hoch (einer pro Wesen, navigiert
-- zur echten, aktuellen URL aus entity_thinking_log), rrweb-Aufnahme pro Context, faehrt
-- alles nach Ablauf wieder sauber runter. Bewusst KEINE Event-Tabelle (kein append-only) --
-- das hier ist mutierbarer Live-Zustand (ein Schalter mit Ablaufzeit), kein historisches
-- Ereignis. Singleton-Pattern (CHECK id=1): es gibt nur eine globale Sitzung, kein
-- Pro-Wesen-Zustand.

CREATE TABLE IF NOT EXISTS beobachtungs_sitzung (
    id            INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    aktiv_bis     TIMESTAMPTZ,
    meta          JSONB DEFAULT '{}',
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO beobachtungs_sitzung (id, aktiv_bis)
VALUES (1, NULL)
ON CONFLICT (id) DO NOTHING;
