from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
text = APP.read_text(encoding="utf-8")

anchor = '@app.get(f"{BASE}/api/megavault/search")'
n = text.count(anchor)
print("anchor:", n)
if n != 1:
    raise SystemExit("abbruch")

endpoint = '''class FrageAnfrage(BaseModel):
    frage: str


@app.post(f"{BASE}/api/megavault/frage")
def api_megavault_frage(payload: FrageAnfrage):
    """Durchreiche zu Daniels bestehendem /fragen-Dienst (fragen_api.py, Port 8055,
    laeuft als eigener systemd-Dienst 'fragen-api.service'): eine ganz andere
    Suchart als die Volltext-/Entitaets-Hybridsuche oben -- eine in normaler
    Sprache gestellte Frage wird von einem lokalen Modell in eine echte,
    nur-lesende SQL-Abfrage uebersetzt, ausgefuehrt, und Frage+Abfrage+Rohergebnis
    werden gemeinsam gezeigt (kein blindes Vertrauen in eine plausibel klingende
    Antwort). Kein eigener Nachbau -- ruft den bestehenden, separat laufenden
    Dienst direkt auf. Kann bis zu ~4-5 Minuten dauern (bis zu drei Modell-Anlaeufe
    a bis zu 90s), deshalb ein grosszuegiger Timeout."""
    frage = (payload.frage or "").strip()
    if not frage:
        return {"fehler": "keine Frage"}
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8055/api/frage",
            data=json.dumps({"frage": frage}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=280) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"fehler": f"/fragen-Dienst nicht erreichbar: {e}"}
    except Exception as e:
        return {"fehler": f"Unerwarteter Fehler beim Durchreichen an /fragen: {e}"}


@app.get(f"{BASE}/api/megavault/search")'''

text = text.replace(anchor, endpoint, 1)
APP.write_text(text, encoding="utf-8")
print("FRAGE-DURCHREICHE-ENDPOINT EINGEFUEGT")
