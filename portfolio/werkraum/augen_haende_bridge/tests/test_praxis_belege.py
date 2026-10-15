"""Adversarial evidence checks: a successful unrelated command is not a proof."""
import unittest
from itertools import count

from augen_haende_bridge.praxis.belege import pruefe, validiere


class BelegTests(unittest.TestCase):
    event_ids = count()

    def event(self, *, actor="a", attempt="try", phase="handeln", target="window", **data):
        return {"id": str(next(self.event_ids)), "agent": actor, "daten": {
            "praxis": {"run_id": "run", "attempt_id": attempt, "step": 1,
                       "phase": phase, "started_ms": 20, "target_id": target}, **data}}

    def check(self, events, checks=None):
        return pruefe(checks or [{"id": "click", "role": "handelnder",
                                 "match": {"command": "haende", "action_kind": "klick", "ok": True}}],
                      events, run_id="run", attempt_id="try", step=1,
                      actors={"handelnder": "a", "zuschauer": "b"},
                      targets={"a": "window", "b": "window"}, since_ms=10)

    def test_wrong_action_actor_attempt_target_or_phase_cannot_pass(self):
        for changes in ({"action_kind": "tippen"}, {"actor": "b"},
                        {"attempt": "old"}, {"target": "other"}, {"phase": "lesen"}):
            with self.subTest(changes=changes):
                data = {"command": "haende", "action_kind": "klick", "ok": True, **changes}
                self.assertFalse(self.check([self.event(**data)])["ok"])
        self.assertTrue(self.check([self.event(command="haende", action_kind="klick", ok=True)])["ok"])

    def test_resource_chain_rejects_a_different_capsule(self):
        checks = [{"id": "create", "role": "handelnder", "match": {"befehl": "moment", "ok": True}},
                  {"id": "read", "role": "zuschauer", "match": {"befehl": "zeige", "unveraendert": True},
                   "same_resource_as": "create"}]
        first = self.event(command="kapsel", befehl="moment", ok=True, resource_id="cap-1")
        wrong = self.event(actor="b", command="kapsel", befehl="zeige", unveraendert=True, resource_id="cap-2")
        self.assertFalse(self.check([first, wrong], checks)["ok"])
        wrong["daten"]["resource_id"] = "cap-1"
        self.assertTrue(self.check([first, wrong], checks)["ok"])

    def test_one_event_cannot_satisfy_two_actions(self):
        checks = [{"id": x, "role": "handelnder", "match": {"command": "haende", "ok": True}} for x in ("one", "two")]
        event = self.event(command="haende", ok=True)
        self.assertFalse(self.check([event], checks)["ok"])
        self.assertFalse(self.check([event, event], checks)["ok"])

    def test_stale_capture_cannot_pass(self):
        checks = [{"id": "frame", "role": "handelnder", "match": {"command": "see", "capture_fresh": True}}]
        self.assertFalse(self.check([self.event(command="see", capture_fresh=False)], checks)["ok"])
        self.assertTrue(self.check([self.event(phase="sehen", command="see", capture_fresh=True)], checks)["ok"])

    def test_empty_and_unknown_predicates_fail_closed(self):
        for checks in ([], [{"id": "x", "role": "handelnder", "match": {"anything": True}}]):
            with self.assertRaises(ValueError):
                validiere(checks)


if __name__ == "__main__":
    unittest.main()
