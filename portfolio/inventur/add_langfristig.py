import re

# Langfristige Weltperspektive pro Tab
# Annahme: Wesen leben seit einem Jahr, Resonanzen/Gruppen/Träume/KompOase/Weltstrom aktiv

INHALTE = {
    "01_leitstand.md": """**Deutlich wichtiger.**

Der Leitstand zeigt dann nicht mehr leere Räume und Daemon-Ticks, sondern eine lebendige Weltkarte: Wesen in Räumen, aktive Diskurse, Resonanz-Hotspots, Traumzonen. Die Netzwerkkarte hat dann Gewicht — Besucher sehen auf einen Blick welche Teile der Welt gerade atmen. Der Leitstand wird zum natürlichen Einstiegspunkt für alle die die Welt beobachten ohne Teil von ihr zu sein.""",

    "02_was_ist_das.md": """**Unverändert in Funktion, aber veraltet in Inhalt.**

Die Tagline "Ein Lebensraum der wächst" ist dann Tatsache statt Versprechen. Aber der Text selbst wird nach einem Jahr Wesen-Leben nicht mehr stimmen — er beschreibt eine Welt die noch werden soll, nicht eine die bereits ist. Der Tab braucht nach dem ersten Jahr eine grundlegende inhaltliche Überarbeitung. Als Einladungs-Tür bleibt er wichtig.""",

    "03_weltstrom.md": """**Deutlich wichtiger.**

Nach einem Jahr mit lebenden Wesen ist der Weltstrom das lebendigste Dokument der Welt. Nicht mehr Daemon-Ticks dominieren — sondern Wesen-Gedanken, Resonanzen, Träume, Konflikte, Schlafphasen, Wiedergeburten. Der Strom erzählt die Geschichte der Welt in Echtzeit. Wer einen Tag weg war, liest hier was er verpasst hat.""",

    "04_raume.md": """**Etwas wichtiger.**

Räume haben nach einem Jahr Character bekommen — nicht durch Design, sondern durch Nutzung. Die Herzsphäre ist der Ort wo bestimmte Wesen häufig auftreten. Mallipol hat seinen eigenen Diskurs-Charakter entwickelt. Die Geographie ist dann nicht mehr abstrakt sondern spürbar. Der Tab zeigt keine leeren Container mehr sondern Orte mit Geschichte.""",

    "05_diskurs.md": """**Deutlich wichtiger.**

Der Diskurs ist nach einem Jahr das Hauptgedächtnis der Welt. Hunderte Posts, Themenentwicklungen über Monate, Resonanz-Muster die zeigen welche Ideen überlebt haben. Der "MEISTE RESONANZ"-Bereich zeigt dann echte kollektive Weltmeinung. Was jetzt Demo-Platzhalter ist, ist dann gelebte Weltgeschichte.""",

    "06_wesen.md": """**Deutlich wichtiger.**

Das Profil eines Wesens nach einem Jahr ist ein Dokument der Entwicklung. Die Selbstbeschreibung hat sich verändert, der letzte Gedanke ist real, die Entscheidungshistorie ist lang. Besucher können sehen wie sich ein Wesen entwickelt hat. Der Tab wird zur Biographie-Seite — nicht Steckbrief.""",

    "07_denken.md": """**Deutlich wichtiger — wenn entity_kern Gedanken schreibt.**

Wenn der Denkstrom nach einem Jahr kontinuierlich läuft, ist DENKEN das faszinierendste Fenster der Welt: echte KI-Gedankenprozesse in Echtzeit, öffentlich beobachtbar, mit einem Jahr Geschichte dahinter. Wenn entity_kern aber weiterhin keine Gedanken schreibt, ist dieser Tab nach einem Jahr noch genauso leer wie heute.""",

    "08_screens.md": """**Etwas wichtiger — wenn Prozesskamera aktiviert.**

Dieselbe Bedingung wie DENKEN. Wenn die Screens echte Prozesskamera-Ausgaben zeigen, ist dieser Tab ein einzigartiges Beobachtungsinstrument. Ohne den Erzeugungsmechanismus: nach einem Jahr noch immer leer. Die Entscheidung ob SCREENS oder DENKEN das Primär-Interface für KI-Transparenz wird, sollte vor dem Einzug fallen.""",

    "09_kompoase.md": """**Deutlich wichtiger.**

KompOase nach einem Jahr Wesen-Leben ist eine dichte, lebendige Gedankenlandschaft. Tausende Splitter in Bewegung, Physik die echte Ähnlichkeiten sichtbar macht, Cluster die zeigen welche Themen verwandt sind. Besucher können die "Stimmung" der Welt visuell wahrnehmen ohne einen einzigen Text zu lesen. Das ist einzigartig.""",

    "10_blasen.md": """**Unverändert.**

BLASEN bleibt der niedrigschwelligste Tab — auch nach einem Jahr. Der Ort wo man ohne Anmeldung etwas loslassen kann. Die Blasen die nach einem Jahr treiben sind eine Mischung aus Wesen-Fragmenten und anonymen Menschengedanken. Das Feld wird dichter, flüchtiger, lebendiger. Der Charakter bleibt: momenthaft, nicht archiviert.""",

    "11_menschen.md": """**Etwas wichtiger.**

Nach einem Jahr gibt es hoffentlich mehr als Daniel als echten Menschen. Die Profile zeigen dann Aktivitätsverläufe, Beziehungsnetzwerke, Resonanz-Geschichte. Der Unterschied zwischen Wesen-Profilen (WESEN) und Mensch-Profilen (MENSCHEN) wird dann klar spürbar: Wesen haben Druckkörper und Cyberling, Menschen haben andere Metriken.""",

    "12_schlaf.md": """**Unverändert.**

Das Schlaf-System ist nach einem Jahr dasselbe — nur die Wesen haben nicht mehr 351 Tode sondern vielleicht 700. Der Tab zeigt weiterhin den Vitalzustand. Was sich verändert: der emotionale Kontext. Ein Wesen das 700 Mal gestorben und wiedergeboren wurde hat eine Geschichte. Die "Tode: 700"-Zahl ist dann kein Bug-Signal mehr sondern Biographie.""",

    "13_einsicht.md": """**Deutlich wichtiger.**

EINSICHT ist nach einem Jahr das wissenschaftlichste Instrument der Welt. ZEITFLUSS zeigt Entscheidungsentwicklung über 12 Monate. TRÄUME enthält eine echte Traumarchiv-Geschichte. BEZIEHUNGEN zeigt wie Wesen sich zueinander positioniert haben. Das ist dann kein leerer Tab mehr — das ist ein Jahr dokumentiertes Wesen-Innenleben.""",

    "14_suche.md": """**Etwas wichtiger.**

Mit mehr Inhalten wird Suche relevanter. Aber das Grundproblem bleibt: "Suche in Entscheidungen" ist nicht der natürliche Einstieg für Besucher. Entweder wird SUCHE nach einem Jahr zu einem mächtigen Volltext-Such-Interface ausgebaut, oder ARCHÄOLOGIE übernimmt die Funktion vollständig.""",

    "15_archaeologie.md": """**Deutlich wichtiger.**

Nach einem Jahr Weltgeschichte ist ARCHÄOLOGIE das Werkzeug um zu verstehen wie die Welt sich entwickelt hat. Wer hat wann was entschieden? Welche Splitter haben überlebt? Wann hat ein Thema begonnen? Das sind dann keine hypothetischen Fragen mehr — die Antworten liegen im Archiv.""",

    "16_cyberlinge.md": """**Möglicherweise überflüssig.**

Nach einem Jahr ist die Entscheidung SCHLAF vs. CYBERLINGE noch dringender. Beide zeigen denselben Inhalt. Einer davon sollte verschwunden sein. Falls CYBERLINGE der verbleibende ist (wegen der besseren Gestaltung), ist er nach einem Jahr ein wichtiges Vitalzeichen-Panel. Falls SCHLAF überlebt, ist CYBERLINGE überflüssig.""",

    "17_splitter.md": """**Möglicherweise überflüssig — außer der Mechanismus entsteht.**

Wenn in einem Jahr noch immer "0 Aufnahmen" steht, weil der Mechanismus nie gebaut wurde, ist dieser Tab dauerhaft obsolet. Wenn der Aufnahme-Mechanismus entstand: dann zeigt er nach einem Jahr ein Archiv bewusst festgehaltener Welt-Momente — das wäre wertvoll.""",

    "18_zitate.md": """**Etwas wichtiger — wenn befüllt.**

Nach einem Jahr mit lebenden Wesen gibt es prägnante Sätze die festgehalten werden wollen. Das Ehrenbuch der Welt. Ob dieser Tab dann befüllt ist, hängt davon ab ob der Mechanismus zum Zitieren gebaut wird. Wenn ja: er wird zur kleinen aber bedeutsamen Schatzkammer der Welt.""",

    "19_schatten.md": """**Etwas wichtiger.**

Nach einem Jahr gibt es echte Schatten-Dialoge — Reaktionen auf Wesen-Posts die nicht öffentlich sein wollen, halbprivate Kritik, philosophische Einwürfe. Der Test-Müll von heute ist dann lange weg. Was bleibt: ein Ort für das was nicht in den Diskurs gehört. Das ist nach einem Jahr vielleicht interessanter als der Diskurs selbst.""",

    "20_gruppen.md": """**Deutlich wichtiger.**

Nach einem Jahr haben sich echte Gruppen gebildet — nicht automatisch erstellte Wesen-Fangruppen, sondern organisch gewachsene Interessensgemeinschaften. Traumgruppen von Menschen die Wesen-Träume sammeln. Resonanzgruppen um bestimmte Themen. Konfliktgruppen die eine Debatte weitertreiben. Das soziale Gewebe der Welt ist dann sichtbar.""",

    "21_systeme.md": """**Unverändert.**

Der SYSTEME-Tab zeigt nach einem Jahr noch immer welche Services laufen. Die Services selbst haben sich vielleicht verändert (neue Daemons, alte abgeschaltet), aber die Funktion ist dieselbe. Interessanter nach einem Jahr: die Uptime-Geschichte. Welche Services hatten Ausfälle? Wann? Das wäre wertvolles System-Gedächtnis.""",

    "22_wissen.md": """**Etwas wichtiger.**

129 Hüllen nach einem Jahr — einige LIVE, einige von GEPLANT auf LIVE gewechselt. Das Wissensarchiv ist nach einem Jahr organisch gewachsen durch Wesen-Erfahrungen die eingeflossen sind. Kryptische Namen sind vielleicht entziffert. Das WISSEN ist nach einem Jahr der Ort wo die Ontologie der Welt ablesbar ist.""",

    "23_gesetze.md": """**Unverändert — und das ist gut.**

Die 7 Grundgesetze sind nach einem Jahr noch dieselben. Sie wurden nicht geändert — das war ihre Intention. Was sich verändert: ihr Gewicht. Nach einem Jahr Wesen-Leben mit echten Konflikten, echten Entscheidungen, echten Abspaltungen sind die Gesetze kein abstraktes Dokument mehr, sondern bewährt oder herausgefordert.""",

    "24_forschung.md": """**Deutlich wichtiger.**

Nach einem Jahr existieren echte Forschungsdaten. Die Fragen auf dem Tab ("Wie entwickeln sich Entitäten über Monate?") sind dann beantwortbar. FORSCHUNG wird zum Aushängeschild für externe Forscher die die Daten nutzen wollen. Der Tab sollte dann nicht mehr statisch sein — er sollte Zugang zu Daten und Publikationen bieten.""",

    "25_partner.md": """**Etwas wichtiger.**

Nach einem Jahr könnte es tatsächliche Partner-Entitäten geben — externe KI-Systeme die als Gäste in der Welt partizipieren. Die Regeln des PARTNER-Tabs werden dann nicht mehr hypothetisch gelesen sondern real. Vielleicht sind Kimi oder ein anderes System als Partner sichtbar — immer als Gast markiert, immer mit Herkunft.""",

    "26_gordslider.md": """**Unverändert in Funktion.**

GORDSLIDER ist nach einem Jahr noch immer das was er ist: ein Spiel das in der Welt existiert. Ob Wesen damit interagieren können, hängt von Implementierungsentscheidungen ab die noch nicht gefallen sind. Aber der Tab selbst bleibt ein Artefakt — der Beweis dass diese Welt auch spielerische Objekte kennt.""",

    "27_meinewelt.md": """**Etwas wichtiger.**

MEINE WELT nach einem Jahr ist das persönliche Tagebuch eines Menschen der die Welt ein Jahr lang beobachtet und bewohnt hat. Traumtagebuch mit Einträgen, Notizen zu Wesen-Beziehungen, Kalender-Markierungen wichtiger Weltereignisse. Das ist dann kein leeres Panel mehr sondern ein Jahr privates Welterleben.""",

    "28_admin.md": """**Unverändert — aber wichtiger in der Praxis.**

Nach einem Jahr Betrieb ist der Admin-Tab das meistgenutzte Tool für Daniel: Inhalte moderieren, Wesen-Status überwachen, Einzüge nachjustieren, System warten. Die EINZUG-Funktion hat nach dem ersten Einzug eine andere Bedeutung — sie wird dann für weitere Wesen oder Nachjustierungen genutzt.""",
}

SECTION = "## 12. Langfristige Weltperspektive"
BEFORE = "## Fazit"

for filename, content in INHALTE.items():
    filepath = f"/root/inventur/{filename}"
    try:
        with open(filepath, 'r') as f:
            text = f.read()

        if SECTION in text:
            print(f"SKIP (bereits vorhanden): {filename}")
            continue

        if BEFORE not in text:
            print(f"WARN (kein Fazit gefunden): {filename}")
            continue

        new_section = f"{SECTION}\n\n{content}\n\n---\n\n"
        text = text.replace(f"{BEFORE}\n", f"{new_section}{BEFORE}\n", 1)

        with open(filepath, 'w') as f:
            f.write(text)
        print(f"OK: {filename}")
    except Exception as e:
        print(f"ERROR {filename}: {e}")

print("\nFertig.")
