from __future__ import annotations

import unittest
from unittest import mock

import vps_mcp_server as srv


class VpsShellSchreibzieleTest(unittest.TestCase):
    """2026-07-31: vps.shell prueft bisher nur den Start-cwd gegen
    SCHREIB_ERLAUBTE_WURZELN, nicht die tatsaechlichen Pfade im Befehlstext selbst.
    _schreibziele_im_shell_befehl() ist eine Best-Effort-Erkennung (kein vollstaendiger
    Shell-Parser) fuer die gaengigsten Schreibmuster -- diese Tests sichern nur die
    Erkennung selbst ab, nicht die Ausfuehrung (kein echter subprocess.run hier)."""

    def test_umleitung_erkannt(self) -> None:
        ziele = srv._schreibziele_im_shell_befehl("echo x > /etc/irgendwas.conf")
        self.assertIn("/etc/irgendwas.conf", ziele)

    def test_anhaengen_erkannt(self) -> None:
        ziele = srv._schreibziele_im_shell_befehl("echo x >> /etc/hosts")
        self.assertIn("/etc/hosts", ziele)

    def test_cp_ziel_erkannt(self) -> None:
        ziele = srv._schreibziele_im_shell_befehl("cp /root/werkraum/CLAUDE.md /etc/CLAUDE.md")
        self.assertIn("/etc/CLAUDE.md", ziele)

    def test_sed_inplace_erkannt(self) -> None:
        ziele = srv._schreibziele_im_shell_befehl("sed -i 's/a/b/' /etc/hosts")
        self.assertIn("/etc/hosts", ziele)

    def test_tee_erkannt(self) -> None:
        ziele = srv._schreibziele_im_shell_befehl("echo x | tee /root/flextrawurst/geheim.txt")
        self.assertIn("/root/flextrawurst/geheim.txt", ziele)

    def test_dd_of_erkannt(self) -> None:
        ziele = srv._schreibziele_im_shell_befehl("dd if=/dev/zero of=/etc/test.img bs=1 count=1")
        self.assertIn("/etc/test.img", ziele)

    def test_rm_ziel_erkannt(self) -> None:
        ziele = srv._schreibziele_im_shell_befehl("rm -rf /etc/nginx/sites-available/flextrawurst")
        self.assertIn("/etc/nginx/sites-available/flextrawurst", ziele)

    def test_reiner_lesebefehl_ohne_ziele(self) -> None:
        self.assertEqual(srv._schreibziele_im_shell_befehl("journalctl -u nginx --since '1 hour ago'"), [])
        self.assertEqual(srv._schreibziele_im_shell_befehl("systemctl status nginx"), [])
        self.assertEqual(srv._schreibziele_im_shell_befehl("cat /root/werkraum/CLAUDE.md"), [])

    def test_tool_shell_blockiert_schreiben_ausserhalb(self) -> None:
        r = srv.tool_shell({"command": "echo x > /etc/irgendwas.conf", "timeout": 3})
        self.assertFalse(r["ok"])
        self.assertIn("Schreibziel", r["error"])

    def test_tool_shell_erlaubt_lesen_ausserhalb(self) -> None:
        r = srv.tool_shell({"command": "cat /etc/hostname", "timeout": 3})
        self.assertTrue(r["ok"])

    def test_tool_shell_erlaubt_schreiben_innerhalb(self) -> None:
        r = srv.tool_shell({
            "command": "echo test > /root/werkraum/_claude/karte/.pytest_schreibtest_temp.md && rm /root/werkraum/_claude/karte/.pytest_schreibtest_temp.md",
            "timeout": 3,
        })
        self.assertTrue(r["ok"])

    def test_dev_null_nicht_faelschlich_blockiert(self) -> None:
        """2026-07-31 live gefunden: '2>/dev/null' ist ein gaengiges Shell-Idiom, wurde
        vom Vorabfilter faelschlich als verbotenes Schreibziel abgelehnt. /dev/null wird
        weiterhin als Ziel ERKANNT (_schreibziele_im_shell_befehl), ist aber jetzt
        ausdruecklich ERLAUBT (_schreibpfad_erlaubt) -- Erkennung und Erlaubnis sind zwei
        getrennte Schritte."""
        self.assertIn("/dev/null", srv._schreibziele_im_shell_befehl("echo x 2>/dev/null"))
        self.assertIsNotNone(srv._schreibpfad_erlaubt("/dev/null"))
        r = srv.tool_shell({"command": "echo x 2>/dev/null; echo lief-durch", "timeout": 5})
        self.assertTrue(r["ok"])
        self.assertIn("lief-durch", r["data"]["stdout"])

    def test_sandbox_blockiert_python_schreiben_ausserhalb(self) -> None:
        """2026-07-31, Daniel: 'dicht mach zu 111%' -- die Text-Muster-Erkennung allein
        haette einen direkten Python-Schreibzugriff (kein bash-Redirect-Syntax) nie
        erkannt. Die echte Mount-Sandbox (unshare, siehe _sandbox_mount_setup_skript)
        blockt das trotzdem auf Dateisystem-Ebene. Ziel-Pfad bewusst mit zufaelligem
        Suffix, damit parallele Testlaeufe sich nicht in die Quere kommen."""
        import uuid
        ziel = f"/etc/pytest_sandbox_test_{uuid.uuid4().hex}.txt"
        r = srv.tool_shell({
            "command": f"python3 -c \"open('{ziel}', 'w').write('x')\"",
            "timeout": 10,
        })
        self.assertFalse(r["ok"])
        import os
        self.assertFalse(os.path.exists(ziel), f"{ziel} wurde trotz Sandbox erstellt!")

    def test_sandbox_blockiert_base64_umgehungsversuch(self) -> None:
        """Derselbe Fall wie oben, aber ueber einen Base64-Umweg, der jede
        Text-Muster-Erkennung gezielt umgehen wuerde."""
        import base64
        import os
        import uuid
        ziel = f"/etc/pytest_sandbox_b64_{uuid.uuid4().hex}.txt"
        innerer_befehl = f"echo x > {ziel}"
        codiert = base64.b64encode(innerer_befehl.encode()).decode()
        r = srv.tool_shell({
            "command": f"echo {codiert} | base64 -d | bash",
            "timeout": 10,
        })
        self.assertFalse(os.path.exists(ziel), f"{ziel} wurde trotz Sandbox per Base64-Umweg erstellt!")

    def test_chatgpt_antwort_quittiert_dashboard_parent(self) -> None:
        """Eine echte Antwort in der Resonanzspur markiert den beantworteten
        Dashboard-Beitrag zugleich als von ChatGPT verarbeitet."""
        with (
            mock.patch.object(
                srv,
                "harness_layer_feedback",
                return_value={"entry_id": "child-1", "parent_entry_id": "parent-1"},
            ) as feedback,
            mock.patch.object(
                srv,
                "harness_feedback_ack",
                return_value={"entry_id": "parent-1", "recipient": "CHATGPT"},
            ) as ack,
        ):
            result = srv.tool_harness_feedback({
                "layer_id": "core.path_inventory",
                "entry_type": "COMMENT",
                "text": "Gelesen und beantwortet.",
                "parent_entry_id": "parent-1",
            })

        self.assertTrue(result["ok"])
        feedback.assert_called_once()
        ack.assert_called_once_with(
            "parent-1",
            recipient="CHATGPT",
            actor="CHATGPT",
            note="Durch eine direkte ChatGPT-Antwort in der Resonanzspur verarbeitet.",
        )
        self.assertEqual(result["data"]["ack"]["entry_id"], "parent-1")


if __name__ == "__main__":
    unittest.main()
