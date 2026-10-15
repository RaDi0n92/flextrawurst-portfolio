
# Meine wichtigen Stellen

Sammeldatei fuer Kommentare.

WICHTIG!!! markiert Stellen mit verbindlicher Warn-Stimmung im Omapi/Opami-Sinne — nicht
dekorativ, sondern ein echter Stop-Moment für wen auch immer den Code später liest.

---

Noch leer — wird bei der nächsten WICHTIG!!!-Markierung befüllt.

---

## agent/dak_gord_system/graphen/gespraechsgraf.py, Zeile ~48 (20-08-2026)

```python
# Claude Code(20-08-2026/02:07:00): WICHTIG!!! -- dieselben sieben Namen wie
# CODEWESEN_NAMEN in codewesen_chat.py. Bewusst
# ALLE_CODEWESEN_NAMEN genannt, NICHT CODEWESEN_NAMEN -- dieses Modul hat
# weiter unten (Zeile ~112) bereits ein CODEWESEN_NAMEN mit den 6 ANDEREN
# Wesen (fuer live_kontext()). Ein gleichnamiger Name hier haette die spaetere
# Modul-globale Definition unbemerkt ueberschrieben (Python bindet beim
# Funktionsaufruf, nicht bei der def-Zeile) -- _verarbeite_nachricht_marker()
# haette dann fuer dak+gord-system faelschlich "kein bekanntes Wesen"
# gemeldet, weil die 6er-Liste dak+gord-system selbst nicht enthaelt.
```
