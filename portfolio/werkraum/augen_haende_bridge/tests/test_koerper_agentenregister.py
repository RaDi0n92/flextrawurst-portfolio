"""G09: Agentenregister (Gruppen, Eltern/Kinder, Aufträge, Fähigkeiten) und der Starter damit — echte PTY-Sitzungen, echte Signale."""

from __future__ import annotations

import base64
import os
import stat
import tempfile
import time
import unittest
from pathlib import Path

from augen_haende_bridge.koerper.agentenregister import Register, RegisterFehler, strom_von
from client_vps.terminal_launcher import Launcher, Ort, StartEntry


class RegisterTests(unittest.TestCase):
    def setUp(self):
        self.r = Register()
        self.a = self.r.anlegen("t-a", "Codex", strom="codex", zustand="running")
        self.b = self.r.anlegen("t-b", "Codex", strom="codex", zustand="running")
        self.c = self.r.anlegen("t-c", "Claude", strom="claude", zustand="running")

    def test_zwei_sitzungen_desselben_stroms_bleiben_zwei_agenten(self):
        self.assertEqual((self.a.name, self.b.name), ("Codex", "Codex 2"))
        self.assertEqual(self.r.finde("codex 2").terminal_id, "t-b")
        self.assertEqual(self.r.finde("t-c").name, "Claude")
        self.assertIs(self.r.anlegen("t-a", "Egal"), self.a, "dieselbe Terminal-ID ist derselbe Agent")

    def test_strom_wird_aus_dem_programm_erkannt(self):
        self.assertEqual([strom_von(p) for p in ("claude --x", "/usr/bin/codex", "gemini", "kimi", "opencode run", "agy", "bash", "")],
                         ["claude", "codex", "gemini", "kimi", "opencode", "gemini", "shell", "shell"])

    def test_eltern_kind_und_ein_nur_gemeldetes_kind_ist_nicht_steuerbar(self):
        steuerbar = self.r.anlegen("t-k", "Helfer", strom="codex", eltern_id="t-a", zustand="running")
        self.assertEqual((steuerbar.eltern_id, self.a.kinder), ("t-a", ["t-k"]))
        kind = self.r.kind_melden("t-a", "Unteragent", "claude")
        self.assertFalse(kind.steuerbar)
        self.assertEqual(kind.faehigkeiten(), {k: None for k in ("ansprechen", "beobachten", "pausieren", "beenden", "delegieren")}, "nichts davon kann die Bridge")
        with self.assertRaises(RegisterFehler):
            self.r.kind_melden("gibt-es-nicht", "x")
        with self.assertRaises(RegisterFehler):
            self.r.anlegen("t-z", "Z", eltern_id="gibt-es-nicht")
        zust, abgelehnt = self.r.nachricht("t-a", kind.name, None, "hallo?")
        self.assertEqual((zust, abgelehnt[0]["grund"]), ([], "nicht_steuerbar"))

    def test_faehigkeitsmatrix_je_strom(self):
        self.assertIn("delegieren", self.a.faehigkeiten())
        shell = self.r.anlegen("t-s", "Shell", strom="shell", zustand="running")
        self.assertNotIn("delegieren", shell.faehigkeiten(), "eine bloße Shell nimmt keine Aufträge an")
        for f in ("ansprechen", "beobachten", "pausieren", "beenden"):
            self.assertIn(f, shell.faehigkeiten())

    def test_gruppen_nachricht_geht_an_alle_ausser_den_absender(self):
        for t in ("t-a", "t-b", "t-c"):
            self.r.gruppe_beitreten(t, "team")
        zust, abgelehnt = self.r.nachricht("t-a", None, "team", "Los geht's")
        self.assertEqual(sorted(z.an for z in zust), ["t-b", "t-c"])
        self.assertEqual([x["grund"] for x in abgelehnt], ["selbst"], "kein Echo an den Absender")
        self.assertTrue(all(z.text.startswith("[Bridge · von Codex] ") for z in zust))
        self.assertEqual(self.r.gruppen(), {"team": ["Claude", "Codex", "Codex 2"]})
        self.r.gruppe_verlassen("t-c", "team")
        self.assertEqual(sorted(a.terminal_id for a in self.r.mitglieder("team")), ["t-a", "t-b"])

    def test_schutz_vor_schleifen_und_unsinn(self):
        self.r.nachricht("t-a", "t-b", None, "eins", jetzt=100.0)
        with self.assertRaises(RegisterFehler) as ctx:
            self.r.nachricht("t-a", "t-b", None, "eins", jetzt=101.0)
        self.assertEqual(str(ctx.exception), "dublette")
        self.r.nachricht("t-a", "t-b", None, "eins", jetzt=106.0)  # nach 5 s wieder erlaubt
        r2 = Register()
        r2.anlegen("x", "X", zustand="running")
        r2.anlegen("y", "Y", zustand="running")
        for i in range(10):
            r2.nachricht("x", "y", None, f"n{i}", jetzt=50.0)
        with self.assertRaises(RegisterFehler) as ctx:
            r2.nachricht("x", "y", None, "n11", jetzt=51.0)
        self.assertEqual(str(ctx.exception), "zu_schnell")
        r2.nachricht("x", "y", None, "n12", jetzt=70.0)
        for args, grund in (((("t-a", "t-b", "team", "x")), "entweder_an_oder_gruppe"), (("t-a", None, "leer", "x"), "gruppe_leer"), (("t-a", "niemand", None, "x"), "empfaenger_unbekannt"),
                            (("t-a", "t-b", None, ""), "text_ungueltig"), (("t-a", "t-b", None, "x" * 5000), "text_ungueltig"), (("nobody", "t-b", None, "x"), "absender_unbekannt")):
            with self.assertRaises(RegisterFehler, msg=grund) as ctx:
                self.r.nachricht(*args, jetzt=200.0)
            self.assertEqual(str(ctx.exception), grund)
        self.r.zustand_setzen("t-b", "exited")
        zust, abgelehnt = self.r.nachricht("t-a", "t-b", None, "noch da?", jetzt=300.0)
        self.assertEqual((zust, abgelehnt[0]["grund"]), ([], "zustand_exited"))

    def test_auftrag_lebenszyklus_nur_der_empfaenger_meldet_und_nichts_geht_zurueck(self):
        auftrag = self.r.auftrag_neu("t-a", "Claude", "Prüfe die Tests")
        self.assertEqual((auftrag.von, auftrag.an, auftrag.status), ("t-a", "t-c", "gesendet"))
        with self.assertRaises(RegisterFehler) as ctx:
            self.r.auftrag_status(auftrag.id, "t-a", "fertig", "ich war's selbst")
        self.assertEqual(str(ctx.exception), "nur_der_empfaenger")
        self.r.auftrag_status(auftrag.id, "t-c", "angenommen")
        self.r.auftrag_status(auftrag.id, "Claude", "laeuft")
        with self.assertRaises(RegisterFehler) as ctx:
            self.r.auftrag_status(auftrag.id, "t-c", "angenommen")
        self.assertEqual(str(ctx.exception), "status_geht_nicht_zurueck")
        fertig = self.r.auftrag_status(auftrag.id, "t-c", "fertig", "12 Tests grün", "ein Test übersprungen")
        self.assertEqual((fertig.status, fertig.ergebnis, fertig.unsicherheit), ("fertig", "12 Tests grün", "ein Test übersprungen"))
        self.assertEqual([v[1] for v in fertig.verlauf], ["gesendet", "angenommen", "laeuft", "fertig"])
        with self.assertRaises(RegisterFehler) as ctx:
            self.r.auftrag_status(auftrag.id, "t-c", "fehler")
        self.assertEqual(str(ctx.exception), "schon_abgeschlossen")

    def test_abbrechen_duerfen_beide_dritte_nicht(self):
        a = self.r.auftrag_neu("t-a", "t-b", "x")
        with self.assertRaises(RegisterFehler):
            self.r.auftrag_status(a.id, "t-c", "abgebrochen")
        self.assertEqual(self.r.auftrag_status(a.id, "t-a", "abgebrochen").status, "abgebrochen")

    def test_auftraege_an_sich_selbst_shells_und_kinder_werden_abgelehnt(self):
        self.r.anlegen("t-s", "Shell", strom="shell", zustand="running")
        kind = self.r.kind_melden("t-a", "Unter")
        for an, grund in (("t-a", "an_sich_selbst"), ("t-s", "nimmt_keine_auftraege"), (kind.terminal_id, "nicht_steuerbar"), ("niemand", "empfaenger_unbekannt")):
            with self.assertRaises(RegisterFehler) as ctx:
                self.r.auftrag_neu("t-a", an, "x")
            self.assertEqual(str(ctx.exception), grund)

    def test_speichern_laden_und_kaputte_dateien(self):
        self.r.gruppe_beitreten("t-a", "team")
        a = self.r.auftrag_neu("t-a", "t-c", "Aufgabe")
        pfad = Path(tempfile.mkdtemp()) / "register.json"
        self.assertTrue(self.r.speichern(pfad))
        neu = Register.laden(pfad)
        self.assertEqual(sorted(neu.agenten), ["t-a", "t-b", "t-c"])
        self.assertTrue(all(x.zustand == "exited" for x in neu.agenten.values()), "geladene Sitzungen gelten als beendet")
        self.assertEqual(neu.agenten["t-a"].gruppen, {"team"})
        self.assertEqual(neu.auftraege[a.id].text, "Aufgabe")
        pfad.write_text("{kaputt", encoding="utf-8")
        self.assertEqual(Register.laden(pfad).agenten, {})
        self.assertEqual(Register.laden(pfad.with_name("fehlt.json")).agenten, {})
        pfad.write_text('{"agenten": [{"nope": 1}, 5], "auftraege": [{"id": "x"}]}', encoding="utf-8")
        self.assertEqual(Register.laden(pfad).agenten, {})

    def test_grenzen(self):
        r = Register()
        for i in range(64):
            r.anlegen(f"t-{i}", f"A{i}")
        with self.assertRaises(RegisterFehler):
            r.anlegen("t-x", "zu viel")
        for name in ("", "x" * 41, "a\nb"):
            with self.assertRaises(RegisterFehler):
                Register().anlegen("t", name)
        for gruppe in ("", "mit leerzeichen", "x" * 33, "ä"):
            with self.assertRaises(RegisterFehler):
                self.r.gruppe_beitreten("t-a", gruppe)
        for i in range(16):
            self.r.gruppe_beitreten("t-a", f"g{i}")
        with self.assertRaises(RegisterFehler):
            self.r.gruppe_beitreten("t-a", "g16")


class Runtime:
    def __init__(self):
        self.gesendet = []

    def publish(self, kind, payload, *, message_id=None):
        self.gesendet.append((kind, payload))
        return message_id or "x"


def zustand_von(pid: int) -> str:
    return Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()[0]


class StarterTests(unittest.TestCase):
    """Zwei echte Sitzungen (ein Skript namens `codex`, das nur `cat` ausführt, damit der Strom erkannt wird), echte Zustellung, echte Signale."""

    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp())
        for name in ("codex", "claude"):
            pfad = cls.dir / name
            pfad.write_text("#!/bin/sh\nexec cat\n")
            pfad.chmod(pfad.stat().st_mode | stat.S_IXUSR)

    def setUp(self):
        self.rt = Runtime()
        starts = {n: StartEntry(n, n.capitalize(), "Host", "/tmp", str(self.dir / n)) for n in ("codex", "claude")}
        self.l = Launcher(self.rt, starts, {"Host": Ort("host", None)}, Path(tempfile.mkdtemp()), schlafen=lambda s: time.sleep(0.02))
        self.l.start()
        self.addCleanup(self.l.shutdown)

    def starte(self, start_id: str):
        self.l.start_terminal({"start_id": start_id, "rows": 24, "cols": 80})
        tid = next(t for t, s in self.l.sessions.items() if s.entry.start_id == start_id and t not in getattr(self, "_bekannt", set()))
        self._bekannt = getattr(self, "_bekannt", set()) | {tid}
        return tid, self.l.sessions[tid]

    def token(self, tid):
        return self.l.sessions[tid].token

    def frage(self, tid, cmd, **kw):
        return self.l.agent_request({"terminal_id": tid, "token": self.token(tid), "cmd": cmd, **kw})

    def ausgabe(self, tid) -> str:
        return b"".join(base64.b64decode(p["data"]) for k, p in self.rt.gesendet if k == "terminal_output" and p["terminal_id"] == tid).decode("utf-8", "replace")

    def warte(self, bedingung, sekunden=8.0) -> bool:
        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            if bedingung():
                return True
            time.sleep(0.05)
        return False

    def test_zwei_sitzungen_desselben_stroms_sind_getrennte_agenten_und_der_strom_wird_erkannt(self):
        a, _ = self.starte("codex")
        b, _ = self.starte("codex")
        c, _ = self.starte("claude")
        antwort = self.frage(a, "agenten")
        namen = {x["terminal_id"]: (x["name"], x["strom"], x["zustand"]) for x in antwort["agenten"]}
        self.assertEqual(namen, {a: ("Codex", "codex", "running"), b: ("Codex 2", "codex", "running"), c: ("Claude", "claude", "running")})
        self.assertEqual(antwort["ich"], a)
        self.assertIn("pausieren", antwort["agenten"][0]["faehigkeiten"])

    def test_nachricht_an_einen_agenten_und_an_eine_gruppe_kommt_wirklich_an(self):
        a, _ = self.starte("codex")
        b, _ = self.starte("codex")
        c, _ = self.starte("claude")
        self.assertTrue(self.frage(b, "gruppe", gruppe="team", aktion="beitreten")["ok"])
        self.assertTrue(self.frage(c, "gruppe", gruppe="team", aktion="beitreten")["ok"])
        r = self.frage(a, "nachricht", an="Claude", text="Hallo einzeln")
        self.assertEqual((r["ok"], r["zugestellt"]), (True, ["Claude"]))
        self.assertTrue(self.warte(lambda: "[Bridge · von Codex] Hallo einzeln" in self.ausgabe(c)), self.ausgabe(c))
        self.assertNotIn("Hallo einzeln", self.ausgabe(b), "nur der Empfänger bekommt es")
        r = self.frage(b, "nachricht", gruppe="team", text="Hallo Gruppe")
        self.assertEqual(r["zugestellt"], ["Claude"], "der Absender gehört zur Gruppe und bekommt nichts")
        self.assertTrue(self.warte(lambda: "Hallo Gruppe" in self.ausgabe(c)))
        self.assertNotIn("Hallo Gruppe", self.ausgabe(b))
        self.assertNotIn("Hallo Gruppe", self.ausgabe(a))
        self.assertEqual(self.frage(a, "nachricht", an="Codex", text="an mich")["abgelehnt"], [{"an": "Codex", "grund": "selbst"}])

    def test_auftrag_geht_in_die_sitzung_und_nur_der_empfaenger_meldet_fertig(self):
        a, _ = self.starte("codex")
        c, _ = self.starte("claude")
        r = self.frage(a, "auftrag", an="Claude", text="Prüfe bitte alles")
        self.assertTrue(r["ok"])
        aid = r["auftrag"]["id"]
        self.assertTrue(self.warte(lambda: f"Auftrag {aid} von Codex" in self.ausgabe(c)))
        self.assertIn("auftrag-status", self.ausgabe(c), "der Empfänger erfährt, wie er meldet")
        self.assertEqual(self.frage(a, "auftrag_status", id=aid, status="fertig")["reason"], "nur_der_empfaenger")
        self.assertTrue(self.frage(c, "auftrag_status", id=aid, status="angenommen")["ok"])
        fertig = self.frage(c, "auftrag_status", id=aid, status="fertig", ergebnis="alles geprüft", unsicherheit="kein Windows")
        self.assertEqual((fertig["ok"], fertig["auftrag"]["status"]), (True, "fertig"))
        liste = self.frage(a, "auftraege")
        self.assertEqual((liste["gesendet"][0]["ergebnis"], liste["gesendet"][0]["unsicherheit"], liste["erhalten"]), ("alles geprüft", "kein Windows", []))

    def test_subagent_wird_gemeldet_aber_nicht_angesprochen(self):
        a, _ = self.starte("codex")
        r = self.frage(a, "kind", name="Unter", strom="claude")
        self.assertTrue(r["ok"])
        self.assertFalse(r["agent"]["steuerbar"])
        self.assertEqual(r["agent"]["eltern_id"], a)
        nachricht = self.frage(a, "nachricht", an="Unter", text="hörst du?")
        self.assertEqual((nachricht["ok"], nachricht["abgelehnt"][0]["grund"]), (False, "nicht_steuerbar"))
        self.assertEqual(self.l.register.agenten[a].kinder, [r["agent"]["terminal_id"]])

    def test_pause_haelt_die_prozessgruppe_wirklich_an_und_fortsetzen_laesst_sie_weiterlaufen(self):
        a, session = self.starte("codex")
        self.l.steuern(a, "pause")
        self.assertTrue(self.warte(lambda: zustand_von(session.pid) == "T"), "SIGSTOP: der Prozess steht (Zustand T)")
        self.assertTrue(session.pausiert)
        self.assertEqual(self.l.register.agenten[a].zustand, "paused")
        zustaende = [p["state"] for k, p in self.rt.gesendet if k == "terminal_state" and p["terminal_id"] == a]
        self.assertEqual(zustaende[-1], "paused")
        self.l.send_list("x")
        liste = [p for k, p in self.rt.gesendet if k == "terminal_list"][-1]
        self.assertEqual(liste["terminals"][0]["state"], "paused")
        session.write(b"waehrend der Pause\n")  # die PTY puffert, der angehaltene Prozess liest es nicht
        time.sleep(0.5)
        vorher = self.ausgabe(a).count("waehrend der Pause")
        self.assertEqual(vorher, 1, "nur das Echo des Terminals (der Kernel), die Antwort von cat fehlt, solange er steht")
        self.l.steuern(a, "fortsetzen")
        self.assertTrue(self.warte(lambda: zustand_von(session.pid) != "T"))
        self.assertTrue(self.warte(lambda: self.ausgabe(a).count("waehrend der Pause") > vorher), "nach dem Fortsetzen arbeitet er die gepufferte Eingabe ab")
        self.assertEqual(self.l.register.agenten[a].zustand, "running")
        self.assertEqual([p["state"] for k, p in self.rt.gesendet if k == "terminal_state" and p["terminal_id"] == a][-1], "running")

    def test_beenden_funktioniert_auch_bei_einem_pausierten_agenten(self):
        a, session = self.starte("codex")
        self.l.steuern(a, "pause")
        self.assertTrue(self.warte(lambda: zustand_von(session.pid) == "T"))
        session.close()
        self.assertTrue(self.warte(lambda: session.state == "exited", 12), "ein angehaltener Prozess bekommt SIGCONT und beendet sich")
        self.assertEqual(self.l.register.agenten[a].zustand, "exited")

    def test_steuern_lehnt_unbekannte_aktionen_und_beendete_sitzungen_ab(self):
        a, session = self.starte("codex")
        self.l.steuern(a, "tanzen")
        self.l.steuern("t-gibt-es-nicht", "pause")
        self.assertEqual(self.l.abgewiesen.get("steuern_aktion"), 1)
        self.assertEqual(self.l.abgewiesen.get("steuern_unbekannt"), 1)
        self.assertFalse(session.pausiert)

    def test_ungueltige_befehle_werden_mit_grund_beantwortet(self):
        a, _ = self.starte("codex")
        self.assertEqual(self.frage(a, "gruppe", gruppe="x y", aktion="beitreten")["reason"], "gruppe_ungueltig")
        self.assertEqual(self.frage(a, "gruppe", gruppe="x", aktion="tanzen")["reason"], "aktion_ungueltig")
        self.assertEqual(self.frage(a, "nachricht", an="niemand", text="x")["reason"], "empfaenger_unbekannt")
        self.assertEqual(self.frage(a, "auftrag_status", id="a-nix", status="fertig")["reason"], "auftrag_unbekannt")
        self.assertEqual(self.frage(a, "kind", name="")["reason"], "name_ungueltig")
        self.assertEqual(self.frage(a, "quatsch")["reason"], "unknown_command")


class KoerperPauseTests(unittest.TestCase):
    """Die Oberfläche: Menü „pausieren/fortsetzen“, die Nachricht an den Starter und der Zustand „pausiert“ (Fenster-Teile sind Attrappen)."""

    def test_menue_zeigt_pausieren_oder_fortsetzen_und_ruft_die_anwendung(self):
        from unittest.mock import Mock

        from augen_haende_bridge.koerper.erster_koerper import MENUE_PAUSE
        from tests.test_koerper_erster_koerper import _bauen

        aufrufe = []
        koerper, *_ = _bauen(menue_anzeigen=Mock(return_value=MENUE_PAUSE), agent_pause=lambda: aufrufe.append(1), agent_pausiert=lambda: False)
        self.assertIn("codex pausieren (Prozess anhalten)", [e[1] for e in koerper.menue_eintraege() if e])
        koerper._raute_menue(0, 0)
        self.assertEqual(aufrufe, [1])
        koerper2, *_ = _bauen(agent_pausiert=lambda: True)
        self.assertIn("codex fortsetzen", [e[1] for e in koerper2.menue_eintraege() if e])

    def test_die_anwendung_schickt_pause_und_fortsetzen_und_zeigt_den_zustand(self):
        from tests.test_koerper_anwendung import _event, _gestartet

        app, _gui, gebaut = _gestartet()
        gebaut[0].kwargs["agent_pause"]()
        self.assertEqual(app.runtime.gesendet[-1], ("terminal_steuern", {"terminal_id": "t-1", "aktion": "pause"}))
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex", "state": "paused", "exit_code": None, "reason": ""}))
        gebaut[0].terminal.setze_zustand.assert_called_with("pausiert (Prozess angehalten)")
        gebaut[0].setze_status.assert_called_with("pausiert")
        self.assertTrue(gebaut[0].kwargs["agent_pausiert"]())
        gebaut[0].kwargs["agent_pause"]()
        self.assertEqual(app.runtime.gesendet[-1], ("terminal_steuern", {"terminal_id": "t-1", "aktion": "fortsetzen"}))
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex", "state": "running", "exit_code": None, "reason": ""}))
        gebaut[0].terminal.setze_zustand.assert_called_with("läuft")
        self.assertFalse(gebaut[0].kwargs["agent_pausiert"]())

    def test_ein_beendeter_agent_wird_nicht_pausiert(self):
        from tests.test_koerper_anwendung import _event, _gestartet

        app, _gui, gebaut = _gestartet()
        app.ereignis(_event("terminal_state", {"terminal_id": "t-1", "start_id": "codex-vd1", "name": "Codex", "state": "exited", "exit_code": 0, "reason": ""}))
        vorher = len(app.runtime.gesendet)
        gebaut[0].kwargs["agent_pause"]()
        self.assertEqual(len(app.runtime.gesendet), vorher)


class RelayPruefungTests(unittest.TestCase):
    def test_der_relay_kennt_paused_und_terminal_steuern_streng(self):
        from types import SimpleNamespace

        from augen_haende_bridge import transport as tr
        from client_vps import anzeigeorte as ao

        tmp = Path(tempfile.mkdtemp())
        d = ao.lade_desktops(Path(__file__).resolve().parent.parent / "client_vps" / "desktops.json", tmp, {"BRIDGE_DESKTOP_TOKEN": "d" * 40, "BRIDGE_AGENT_TOKEN": "a" * 40})
        relay = tr.Relay(ao.baue_principals(d), tr.Journal(tmp / "j.sqlite3"))
        desktop = SimpleNamespace(principal=next(p for p in relay.principals if p.can_control_terminals))
        starter = SimpleNamespace(principal=next(p for p in relay.principals if p.can_serve_terminals))
        self.assertEqual(relay.payload(desktop, "terminal_steuern", {"terminal_id": "t-1", "aktion": "pause"})["aktion"], "pause")
        for kaputt in ({"terminal_id": "t-1", "aktion": "tanzen"}, {"terminal_id": "t-1"}, {"terminal_id": "t-1", "aktion": "pause", "x": 1}, {"terminal_id": "../x", "aktion": "pause"}):
            with self.assertRaises(tr.ProtocolError, msg=str(kaputt)):
                relay.payload(desktop, "terminal_steuern", kaputt)
        with self.assertRaises(tr.ProtocolError):
            relay.payload(starter, "terminal_steuern", {"terminal_id": "t-1", "aktion": "pause"})  # nur Desktops dürfen steuern, nie der Starter
        zustand = relay.payload(starter, "terminal_state", {"terminal_id": "t-1", "start_id": "x", "name": "X", "state": "paused", "exit_code": None, "reason": ""})
        self.assertEqual(zustand["state"], "paused")


class CliTests(unittest.TestCase):
    """Das Werkzeug des Agenten: jeder neue Befehl wird zur richtigen Anfrage an den Starter."""

    def anfrage(self, *argv):
        from unittest import mock

        from client_vps import bridge_cli

        with mock.patch.object(bridge_cli, "ask", return_value={"ok": True}) as ask, mock.patch("builtins.print"):
            code = bridge_cli.main(list(argv))
        return code, ask.call_args.args[0] if ask.call_args else None

    def test_alle_neuen_befehle(self):
        faelle = {
            ("agenten",): {"cmd": "agenten"},
            ("gruppe", "team", "beitreten"): {"cmd": "gruppe", "gruppe": "team", "aktion": "beitreten"},
            ("gruppe", "team", "verlassen"): {"cmd": "gruppe", "gruppe": "team", "aktion": "verlassen"},
            ("sende", "Claude", "Hallo", "du"): {"cmd": "nachricht", "an": "Claude", "text": "Hallo du"},
            ("sende", "@team", "an", "alle"): {"cmd": "nachricht", "gruppe": "team", "text": "an alle"},
            ("auftrag", "Claude", "Prüfe", "es"): {"cmd": "auftrag", "an": "Claude", "text": "Prüfe es"},
            ("auftrag-status", "a-1", "fertig", "Ergebnis"): {"cmd": "auftrag_status", "id": "a-1", "status": "fertig", "ergebnis": "Ergebnis", "unsicherheit": ""},
            ("auftrag-status", "a-1", "angenommen"): {"cmd": "auftrag_status", "id": "a-1", "status": "angenommen", "ergebnis": "", "unsicherheit": ""},
            ("auftraege",): {"cmd": "auftraege"},
            ("kind", "Unter"): {"cmd": "kind", "name": "Unter"},
            ("kind", "Unter", "claude"): {"cmd": "kind", "name": "Unter", "strom": "claude"},
        }
        for argv, erwartet in faelle.items():
            code, gesendet = self.anfrage(*argv)
            self.assertEqual((code, gesendet), (0, erwartet), argv)

    def test_falsche_aufrufe_geben_die_hilfe_und_senden_nichts(self):
        for argv in (("gruppe", "team", "tanzen"), ("sende", "Claude"), ("auftrag", "x"), ("kind",)):
            code, gesendet = self.anfrage(*argv)
            self.assertEqual((code, gesendet), (2, None), argv)
        from client_vps import bridge_cli

        for befehl in ("agenten", "gruppe", "sende", "auftrag", "auftrag-status", "auftraege", "kind"):
            self.assertIn(befehl, bridge_cli.__doc__)


if __name__ == "__main__":
    unittest.main()
