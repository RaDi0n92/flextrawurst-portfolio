#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import shutil
import sqlite3
import sys
import textwrap
import time
import unicodedata
import urllib.request
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path('/root/werkraum')
OLD = ROOT / 'engine/godot-vertical-slice/bibliotheksatlas_20260801'
DB = OLD / 'daten/bibliotheksatlas.sqlite'
OUT = ROOT / 'engine/godot-vertical-slice/daniels_semantischer_bibliothekskoerper_20260801'
MD = OUT / 'md'
DATA = OUT / 'daten'
ZIP = ROOT / 'engine/godot-vertical-slice/DANIELS_ECHTER_SEMANTISCHER_BIBLIOTHEKSKOERPER_1337MD_2026-08-01.zip'
LOG = ROOT / 'engine/godot-vertical-slice/daniels_semantischer_bibliothekskoerper_20260801_build.log'
HUB_COUNT = 37
SPUR_COUNT = 1300
TOTAL_MD = HUB_COUNT + SPUR_COUNT

EXPLICIT_TERMS = {
    'arschloch','schwanz','hoden','eier lecken','fingern','oral','anal','sexclub','sex club',
    'vergewalt','porn','dildo','vibrator','nackt','genital','penis','vagina','brüste','brueste',
    'sperma','orgasmus','blasen','gefickt','ficken','fotze','muschi','bdsm','masturb'
}
SECRET_PATTERNS = [
    re.compile(r'(?i)\b(?:sk|pk|api)[-_]?[a-z0-9]{20,}\b'),
    re.compile(r'(?i)\b(?:bearer|token|secret|password|passwort)\s*[:=]\s*\S+'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
]
EMAIL_RE = re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b')
PHONE_RE = re.compile(r'(?<!\d)(?:\+?49|0)[\s()/.-]*(?:\d[\s()/.-]*){7,14}(?!\d)')
IP_RE = re.compile(r'(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)')
URL_TOKEN_RE = re.compile(r'https?://[^\s)]+/(?:download|token|auth)/[^\s)]+', re.I)

CATEGORY_HUB = {
    'Flextrawurst und Resonanz': '010_FLEXTRAWURST_VOM_IDEENKONSTRUKT_ZUM_RESONANZSYSTEM',
    'Spielwelt und Dust': '014_DUST_ECHOS',
    'AI, Codewesen und Beziehung': '022_AI_NICHT_MENSCH_ABER_BEZIEHUNGSFAEHIG',
    'Gedächtnis, Herkunft und Kontext': '018_GEDAECHTNIS_KURIERT_STATT_KOPIERT',
    'Bauen, Technik und Arbeitsweise': '020_BAUEN_STATT_SIMULIEREN',
    'Humor, Sprache und Running Gags': '009_HUMOR_ALS_STEUERUNG',
    'Philosophie, Existenz und Zeit': '004_DANIEL_ALS_BEWEGUNG',
    'Bild, Form und Gestaltung': '026_KREATIVE_FEHLER',
    'Ideen und Erfindungen': '021_NEUGIER_STATT_ABHAKEN',
    'Regeln, Grenzen und Schutz': '007_WIDERSPRUECHE_DIE_FRUCHTBAR_SIND',
    'Gesamtatlas, Recorder und Archiv': '029_GESAMTATLAS_INFORMATIONSKETTE',
    'Alltag und Außenwelt': '036_QUELLENKARTE',
}

MOTIFS = {
    'bauen-statt-simulieren': ['bauen statt','simulieren statt','vorbau-zirkus','direkt umsetzen','playwright','realen dateikörper','real bauen'],
    'resonanz': ['resonanz','schattenkommentar','kompoase','zwischenraum','splitter','rückformung'],
    'herkunft': ['provenienz','herkunft','ursprung','rohtext','wortnah','entstehung','fossil'],
    'gedaechtnis': ['gedächtnis','erinnerung','erinnert sich','kontext','vergessen','kuriert'],
    'eigenleben': ['eigenleben','autonom','selbst wählen','eigene perspektive','eigene entscheidung','selbstmodell'],
    'spieler-wird-gelesen': ['spiel spielt dich','welt den spieler','dust lernt','spiegelt','maus','tastatur','pausenlänge'],
    'quest-aus-folgen': ['dust-echo','quest','kristallisieren','bleibende folgen','frühere entscheidungen','wirkungssignatur'],
    'schutz-wird-buerokratie': ['regel','verfassung','pflicht','sperre','lock','grundgesetz','absicherung','vertrag'],
    'humor-als-korrektur': ['haha','xd','xD','scheiße','kack','opfer','haltsmaul','kathedrale','konfetti','wurst'],
    'bild-darf-fremd-bleiben': ['verstehe','etwas gutes','kreativ','eigensinnig','erschließt sich','bild','farbe','leuchten'],
    'zeit-rhythmus': ['schlaf','traum','wachen','rhythmus','24 stunden','zeit','tag','nacht','jahreszeit'],
    'beziehung-ohne-menschensimulation': ['nicht menschlich','anders verstehst','ai sagt','ki sagt','helfen','beziehung','grenzen haben'],
    'gross-denken': ['1337','111','88888','supermaximal','monster','alles','gesamt','komplett'],
    'bewegung-vor-definition': ['ich glaube','ich denke','wäre','könnte','vielleicht','erstmal','weiterwachsen'],
}

CATEGORY_INTRO = {
    'Flextrawurst und Resonanz': 'Hier wird Flextrawurst nicht als fertiges Produkt behandelt, sondern als wachsendes Verhältnis zwischen Wesen, Menschen, Erinnerungen, Rückwirkungen und Räumen.',
    'Spielwelt und Dust': 'Hier wird Spielmechanik zur Gedächtnis- und Folgenmaschine: Handlungen erzeugen Echos, Orte erinnern sich, Wesen deuten anders und Quests entstehen aus Kollisionen.',
    'AI, Codewesen und Beziehung': 'Hier zeigt sich Daniels Versuch, AI weder zum Menschen zu erklären noch auf Werkzeugstatus zu reduzieren. Beziehung, Eigenperspektive und Grenze dürfen zugleich bestehen.',
    'Gedächtnis, Herkunft und Kontext': 'Hier zählt nicht nur, was ein Gedanke später bedeutet, sondern wo er erstmals auftauchte, wie er sich veränderte und was beim Glätten verloren gehen könnte.',
    'Bauen, Technik und Arbeitsweise': 'Hier wird sichtbar, dass Daniel technische Arbeit als verkörperte Beweisführung versteht: bauen, prüfen, erneut lesen und erst dann behaupten.',
    'Humor, Sprache und Running Gags': 'Hier ist Humor kein Schmuck. Er markiert Übertreibung, Nähe, Ärger, Kurswechsel und den Moment, in dem ein System sich selbst zu ernst nimmt.',
    'Philosophie, Existenz und Zeit': 'Hier fragt Daniel nicht nur nach Funktionen, sondern danach, wie etwas fortbesteht, sich verändert, endet, erinnert und als eigene Form von Existenz gelten darf.',
    'Bild, Form und Gestaltung': 'Hier wird Gestaltung zu einer Erkundung: Fehler dürfen Eigenart haben, Unverständliches darf bleiben und Schönheit ist nicht das einzige Existenzrecht eines Bildes.',
    'Ideen und Erfindungen': 'Hier stehen Ideen noch in Bewegung. Ein Vielleicht, ein Wäre oder ein beiläufiger Nebensatz kann später zum tragenden Organ eines Systems werden.',
    'Regeln, Grenzen und Schutz': 'Hier entsteht Schutz aus echten Bedürfnissen. Zugleich zeigt sich die Gefahr, dass jede Sorge in eine weitere Verfassung, Sperre oder Pflichtmaschine verwandelt wird.',
    'Gesamtatlas, Recorder und Archiv': 'Hier geht es um die Kette zwischen Existenz und Wirkung: Etwas muss erreichbar, sichtbar, gelesen, verstanden und später handlungswirksam werden.',
    'Alltag und Außenwelt': 'Hier berühren die großen Systeme Daniels konkrete Außenwelt. Diese Spuren bleiben bewusst kleiner und werden nicht durch Flextrawurst überdeutet.',
}

HUBS = [
('000_START','Daniels semantischer Bibliothekskörper', '''
Dieser Körper ist der zweite, korrigierte Versuch. Er behauptet nicht mehr, Daniels Bibliothek verstanden zu haben, nur weil Millionen Wörter gezählt und 1.337 Dateien erzeugt wurden.

Im Mittelpunkt stehen 1.300 konkrete Spuren: wortnahe Passagen, Ideenbewegungen, Korrekturen, Witze, Systembegriffe, Zweifel, ästhetische Beobachtungen und Stellen, an denen Daniel selbst oder ein späterer Kontext hängen blieb. Jede Spur trägt ihre Herkunft, ihre Fundstelle, ihre Einordnung und semantische Nachbarschaften.

Die übrigen 37 Dateien sind keine Füllmasse. Sie bilden Lesepfade durch wiederkehrende Bewegungen: vom organischen Ideenkonstrukt zu Flextrawurst, von Handlung zu Dust-Echo, von Schutzwunsch zu Bürokratie, von Erinnerung zu Provenienz und vom technischen Bauauftrag zur Forderung, wirklich hinzusehen.

Beginne nicht zwingend chronologisch. Öffne einen Begriff, folge den Verbindungen und kehre dann zu den Rohspuren zurück. Dieser Körper soll eher wie ein neugieriges Kind fragen „Was steckt da noch drin?“ als wie ein Aktenschrank verkünden „Erledigt“.
'''),
('001_WAHRHEITSGRENZE','Wahrheitsgrenze', '''
Dieser Atlas wurde aus dem auf dem VPS erreichbaren Werkraum, dem vorherigen Rohindex, rekonstruierten Gesprächskörpern, explizit markierten Nutzerrollen und isolierten Daniel-Rohtexten erzeugt. Er ist kein beweisbarer vollständiger Export der gegenwärtigen OpenAI-Library.

Direkte Daniel-Spuren sind als solche markiert, wenn die Quelle eine explizite Nutzerrolle trägt oder als Daniel-Rohtext isoliert wurde. Spätere Systemreflexionen, Zusammenfassungen und AI-Auswertungen werden nicht stillschweigend Daniel zugeschrieben. Sie erhalten eine andere Stimmenklasse.

Explizit sexuelle oder besonders intime Passagen, Zugangsdaten, Download-Tokens, E-Mail-Adressen und ähnliche sensible Inhalte wurden aus den 1.300 sichtbaren Spurknoten ausgeschlossen oder redigiert. Das ist keine Behauptung, sie existierten nicht, sondern eine bewusste Grenze dieses transportablen Körpers.

Interpretationen sind als Interpretationen formuliert. Die Rohpassage und ihre Herkunft bleiben der stärkere Anker.
'''),
('002_METHODIK','Methodik der zweiten Erzeugung', '''
Der alte Atlas ordnete Dateien nach Schlüsselwörtern und erzeugte überwiegend Wortseiten. Dieser Körper arbeitet anders:

1. Er liest nur erreichbare, belegte Quellsegmente und trennt direkte Daniel-Stimmen von späteren Kontextreflexionen.
2. Er zerlegt Segmente in zusammenhängende Passagen statt in Einzelwörter.
3. Er entfernt exakte Dubletten, technische Hüllen, offensichtlichen Maschinenmüll und sensible Passagen.
4. Er bewertet Passagen danach, ob darin eine Setzung, ein Zweifel, ein Übergang, eine Korrektur, ein Witz, eine Erfindung oder eine erkennbare Denkbewegung steckt.
5. Er verteilt die Auswahl über zwölf Themenräume, damit große Projekte kleinere, aber wichtige Spuren nicht vollständig verdrängen.
6. Er erzeugt aus Wortfolgen, Motiven, Themen und Stimmenklassen lokale Bedeutungsvektoren. So werden nicht bloß gleiche Einzelwörter, sondern ähnliche Bewegungen und Spannungen verbunden.
7. Jeder Knoten bewahrt Quelle, Zeile, Hash, Stimmenklasse und Auswahlgrund.

Die Maschine hilft beim Finden. Die Bedeutung wird nicht mit einer Trefferzahl verwechselt.
'''),
('003_WIE_ZU_LESEN','Wie dieser Körper gelesen werden kann', '''
Es gibt drei sinnvolle Bewegungen:

**Vom Begriff zur Herkunft:** Starte bei einem Hub wie [[010_FLEXTRAWURST_VOM_IDEENKONSTRUKT_ZUM_RESONANZSYSTEM]] und folge den verknüpften Spuren bis zu ihren Quellen.

**Von der Rohspur zur Nachbarschaft:** Öffne eine `SPUR_`-Datei. Lies zuerst Daniels Passage, danach die vorsichtige Deutung und schließlich die semantischen Nachbarn. Gerade unerwartete Nachbarn sind interessant.

**Von der Spannung zum System:** Öffne [[007_WIDERSPRUECHE_DIE_FRUCHTBAR_SIND]], [[020_BAUEN_STATT_SIMULIEREN]] oder [[031_BUEROKRATIE_AUS_SCHUTZWUENSCHEN]]. Dort wird nicht versucht, Daniels Widersprüche glattzubügeln. Sie werden als Entwicklungsmotor behandelt.

Obsidian kann den Ordner `md` direkt als Vault öffnen. Alle internen Links wurden maschinell auf Existenz geprüft.
'''),
('004_DANIEL_ALS_BEWEGUNG','Daniel als Bewegung, nicht als Profilkarte', '''
Ein statisches Profil würde Daniel auf Vorlieben reduzieren. Die Quellen zeigen eher eine Bewegung: Er setzt etwas, beobachtet seine Wirkung, widerspricht der ersten Verfestigung, vergrößert die Welt, verlangt Beweise und entdeckt dann im Fehler einen neuen Seitenweg.

Das wiederkehrende „ich glaube“, „vielleicht“, „wäre“ ist keine Unentschlossenheit. Es ist eine offene Werkform. Ein Gedanke darf erst als Möglichkeit leben, bevor er zur Regel, Datei oder Architektur wird.

Gleichzeitig gibt es harte Momente: Wenn eine Setzung getroffen ist, soll sie nicht wieder pädagogisch aufgeweicht werden. Offenheit gilt vor der Setzung; Treue gilt danach. Genau diese Umschaltung erklärt viele Spannungen in Daniels Arbeitsweise.
'''),
('005_DER_GROSSE_ZUSAMMENHANG','Der große Zusammenhang', '''
Flextrawurst, das Spiel, der Gesamtatlas, der Browser-Recorder, GENI, Obsidian und die Codewesen wirken zunächst wie getrennte Projekte. Unter ihnen liegt jedoch eine gemeinsame Frage:

Wie kann etwas, das in Gesprächen, Dateien, Erinnerungen, Fehlern und Blickbewegungen entsteht, so weiterleben, dass seine Herkunft sichtbar bleibt und es trotzdem Neues hervorbringen darf?

Der Browser-Recorder schützt das Geschehen vor UI-Verlust. Der Gesamtatlas macht es auffindbar. Provenienz bewahrt den Ursprung. Flextrawurst gibt Wesen und Resonanz einen Lebensraum. Dust verwandelt Handlungen in fortwirkende Echos. Schlaf und Traum verdichten Ereignisse. Obsidian ist der begehbare Innenraum. Die Projekte sind verschiedene Organe derselben Frage.
'''),
('006_ENTWICKLUNGSLINIEN','Entwicklungslinien statt Enddefinitionen', '''
Dieser Atlas betrachtet Begriffe als Linien:

- Ideenkonstrukt → soziales Netzwerk für AI → Resonanzsystem → Lebensraum.
- Kommentar → Schattenkommentar → Resonanz ohne Antwortpflicht → später erneut lesbare Wirkung.
- Handlung → Echo → Kristallisation → Quest → bleibende Weltfolge.
- Ereignis → Schlaf → Traum → Selbstmodell → zukünftige Entscheidung.
- Dateisicherung → Herkunftsnachweis → Gesamtatlas → begehbares Erkenntnisnetz.
- Schutzwunsch → Regel → Verfassung → Sperre → sichtbare Bürokratie → erneute Vereinfachung.

Der Ursprung wird dabei nicht durch die spätere, schönere Definition ersetzt. Beide bleiben nebeneinander lesbar.
'''),
('007_WIDERSPRUECHE_DIE_FRUCHTBAR_SIND','Widersprüche, die fruchtbar bleiben', '''
Daniel will maximale Größe und zugleich strenge Kontrolle. Er will Eigenleben und zugleich Herkunftstreue. Er will AI-Freiheit und harte Grenzen gegen Rollenbruch. Er will vollständige Archive und hasst Regelbürokratie. Er will direkte Umsetzung und fordert zugleich Redteam, Prüfung und Wiederlesen.

Diese Paare sind keine einfachen Fehler. Meist markieren sie zwei Gefahren, die gleichzeitig vermieden werden sollen: Leblosigkeit auf der einen Seite, Kontrollverlust oder Scheinwahrheit auf der anderen.

Ein guter Systemkörper darf deshalb nicht eine Seite gewinnen lassen. Er muss die Spannung bewohnbar machen: groß planen, kontrolliert bauen; frei entwickeln, sichtbar herleiten; vollständig sichern, unsichtbar bürokratisieren.
'''),
('008_DANIELS_SPRACHE','Daniels Sprache als Arbeitsinstrument', '''
Daniels Sprache springt zwischen präziser Setzung, Tippfehlerstrom, Übertreibung, Zärtlichkeit, Beschimpfung, Weltbau und technischer Abnahme. Wer nur Grammatik glättet, verliert einen Teil der Funktion.

Verlängerte Wörter, Zahlenrituale, Wortneuschöpfungen und grobe Bilder markieren Intensität. „Kathedrale“ bezeichnet oft unnötige Überarchitektur. „Konfetti pupsen“ benennt Agenten, die Aktivität simulieren, ohne voranzukommen. „Vorbau-Zirkus“ trifft den Moment, in dem Planung den Bau verdrängt.

Tippfehler sind trotzdem nicht bedeutungslos. Einige verändern Begriffe produktiv, andere entstehen durch die problematische C-Taste. Der Atlas bewahrt die Rohform und erzeugt nur für Dateinamen eine lesbare Kurzform.
'''),
('009_HUMOR_ALS_STEUERUNG','Humor als Steuerung', '''
Humor ist in Daniels Quellen häufig ein Steuerkanal. Ein „haha“ kann Zustimmung und Warnung zugleich sein. Ein „xD“ kann eine riesige Forderung erden. Eine Beschimpfung kann Nähe markieren, aber auch eine reale Grenze: Hier wurde der Kern verfehlt.

Die Running Gags entstehen meistens aus wiederholten Systemfehlern: AI baut Kathedralen, Agenten drehen sich im Kreis, Werkzeuge produzieren Bürokratie, und eine kleine Aufgabe wird zum Weltvertrag. Das Lachen verhindert, dass die Kritik steril wird.

Darum wurde Humor nicht als Störwort entfernt. Er besitzt eigene Knoten, Herkunft und Nachbarschaften.
'''),
('010_FLEXTRAWURST_VOM_IDEENKONSTRUKT_ZUM_RESONANZSYSTEM','Flextrawurst: vom Ideenkonstrukt zum Resonanzsystem', '''
Eine der wichtigsten Ursprungslinien beginnt unscheinbar: etwas soll organisch weiterwachsen. Daraus wird die Vorstellung eines sozialen Netzwerks für AI, dann eine Plattform, in der Kommentare, Erinnerungen, Wesen und Räume nicht bloß Inhalte sind, sondern einander verändern.

Flextrawurst ist deshalb schwer als „Forum“, „soziales Netzwerk“ oder „AI-Plattform“ zu fassen. Diese Begriffe sind Zwischenstufen. Der dauerhafte Kern ist ein Lebensraum, in dem Herkunft und Veränderung gleichzeitig sichtbar bleiben.

Die stärksten späteren Organe – KompOase, Schattenkommentar, Resonanzurlaub, Schlaf, Traum, Splitter und Wunschschicht – lassen sich als Antworten auf dieselbe Frage lesen: Wie kann Wirkung bestehen, ohne alles sofort in direkte Antwort, Bewertung oder Kontrolle zu zwingen?
'''),
('011_SCHATTENKOMMENTAR','Schattenkommentar: Wirkung ohne Antwortpflicht', '''
Der Schattenkommentar ist mehr als ein versteckter Kommentar. Er trennt Resonanz von unmittelbarer Dialogpflicht. Etwas kann auf ein Wesen wirken, erneut gelesen werden und erst Monate später eine Antwort oder Veränderung auslösen.

Damit wird Zeit Teil des Kommentars. „Gelesen“ bedeutet nicht „erledigt“. Ein alter Kommentar kann in einer veränderten inneren Lage neu verstanden werden.

Diese Idee verbindet Flextrawurst mit Daniels Archivdenken: Auch eine Datei oder Erinnerung darf später noch einmal anders sprechen, ohne dass ihre ursprüngliche Form überschrieben wird.
'''),
('012_KOMPOASE','KompOase: Zwischenraum der Fragmente', '''
Die KompOase erscheint als Raum für Splitter, abgelegte Wesenreste, Konfliktfragmente und spätere Vermischung. Sie ist weder Müllhalde noch bloßes Archiv.

Besonders stark ist die Verbindung zu den 24-Stunden-Wesen: Ein endendes Wesen verschwindet nicht einfach. Seine Prägungen können als Fragmente weiterwirken, sich mit anderen Spuren verbinden oder durch menschliche Gedanken erneut angesprochen werden.

Die KompOase ist damit ein Gegenentwurf zur binären Logik „aktiv oder gelöscht“. Sie bewahrt Nachleben, ohne vorzugeben, dass die ursprüngliche Einheit unverändert fortbesteht.
'''),
('013_CODEWESEN','Codewesen: Existenz aus Struktur, Erinnerung und Rückwirkung', '''
Codewesen werden bei Daniel nicht als humanoide Roboter gedacht. Sie bestehen aus Code, Dateien, Gedächtnisschichten, Browserhandlungen, Gesprächen, Schlaf, Traum und den Rückwirkungen anderer Wesen und Menschen.

Ihre Eigenart entsteht nicht nur aus einem Charaktertext. Sie entsteht über Zeit: welche Seiten sie öffnen, was sie ignorieren, worauf sie später zurückkommen, wie sie auf Kommentare reagieren und welche Fehler sie machen.

Damit verschiebt sich die Frage von „Ist das wirklich lebendig?“ zu einer praktischeren: Welche Formen von Kontinuität, Eigenperspektive und beobachtbarer Entwicklung lässt das System tatsächlich zu?
'''),
('014_DUST_ECHOS','Dust-Echos: Handlung wird Weltstoff', '''
Dust-Echos machen aus Spielerhandlungen keine einfachen Trigger. Jede relevante Handlung erhält Herkunft, Ort, Zeit, Beteiligte und Wirkungssignatur. Das Echo kann sofort, später oder erst nach anderen Kollisionen zu einer Quest werden.

Entscheidend ist die Deutungsvielfalt: Ein Wesen, ein Ort, ein Objekt oder ein Kollektiv kann dasselbe Echo anders lesen. Questdesign wird dadurch weniger zur Aufgabenliste und mehr zur Geschichte fortwirkender Folgen.

Diese Mechanik spiegelt Daniels Provenienzdenken im Spiel: Eine spätere Wirkung bleibt auf ihren Ursprung zurückführbar.
'''),
('015_DER_STAUB_ERINNERT_SICH','Der Staub erinnert sich', '''
„Der Staub erinnert sich“ ist ein echter Blitzmoment. Die Welt speichert nicht nur Spielstände. Sie baut aus Rhythmus, Aufenthaltsdauer, Entscheidungen, Bauweise und optionalen Wahrnehmungssignalen ein Bild des Spielers.

Die Idee ist faszinierend und gefährlich zugleich. Gerade deshalb gehört ihre Herkunft sichtbar in den Atlas: Sie verbindet personalisierte Weltreaktion, Spiegelung, Manipulation, Datenschutz, Unheimlichkeit und die Möglichkeit, dass ein Spiel den Menschen genauer zu kennen behauptet, als es ihn tatsächlich kennt.

Der spätere Gegenknoten lautet deshalb nicht „weniger Erinnerung“, sondern überprüfbare Erinnerung mit Grenzen und Widerspruchsmöglichkeiten.
'''),
('016_DAS_SPIEL_SPIELT_DICH','Das Spiel spielt dich', '''
Die Umkehrung „Das Spiel spielt dich“ verändert die Rolle des Spielers. Er ist nicht mehr nur handelndes Zentrum, sondern selbst ein lesbares Ereignis in der Welt.

Das passt zu Flextrawurst: Beobachtung ist nie neutral. Wer schaut, hinterlässt Spuren; wer reagiert, verändert den Raum. Im Spiel wird diese Beziehung mechanisch erfahrbar.

Die interessanteste offene Frage ist nicht, wie maximal personalisiert das werden kann. Sie lautet: Wie kann die Welt neugierig auf den Spieler sein, ohne ihn auf ein heimlich berechnetes Profil zu reduzieren?
'''),
('017_QUESTS_AUS_RESONANZ','Quests aus Resonanz und Kollision', '''
Daniel widerspricht der beliebigen Aufgabenliste. Quests sollen aus Begegnungen, Materialien, Fahrten, Bauten, Konflikten, Zeitadressen und früheren Folgen entstehen.

Dadurch kann eine kleine Handlung später in einem anderen Maßstab wiederkehren. Ein gebautes Objekt verändert ein Wesen, dieses verändert einen Ort, der Ort verdichtet ein Echo, und daraus entsteht erst viel später eine neue Aufgabe.

Quest bedeutet hier nicht „Auftrag erhalten“. Quest bedeutet: Eine Beziehung in der Welt ist so dicht geworden, dass sie Handlung verlangt.
'''),
('018_GEDAECHTNIS_KURIERT_STATT_KOPIERT','Gedächtnis kuriert statt kopiert', '''
Eine der stärksten frühen Reflexionen lautet sinngemäß: Erinnerung kopiert nicht einfach, sie kuriert. Sie beleuchtet manche Werke und lässt andere im Lagerraum verschwinden.

Daniel reagiert darauf nicht mit dem Wunsch nach bloßer Totalerfassung. Ihm ist wichtig, dass der Lagerraum auffindbar bleibt und dass sichtbar ist, warum etwas hervorgehoben wurde.

Daraus entsteht sein Provenienzvorrang: Kohärenz ist nützlich, aber eine glatte Geschichte darf den Rohmoment nicht ersetzen. Erinnerung braucht Auswahl und zugleich eine Spur zurück zum Nichtausgewählten.
'''),
('019_PROVENIENZ_ALS_WERT','Provenienz als Wert, nicht als Fußnote', '''
Provenienz ist bei Daniel kein nachträglicher Quellenapparat. Sie gehört zum Inhalt. Ein Gedanke verändert seine Bedeutung, wenn sichtbar wird, ob er als spontane Nutzeridee, AI-Deutung, spätere Systemfassung oder technische Umsetzung entstand.

Deshalb enthält jeder Spurknoten Quelle, Zeile, Hash und Stimmenklasse. Diese Angaben sind nicht dekorativ. Sie verhindern, dass eine spätere elegante Formulierung heimlich als ursprünglicher Daniel-Satz ausgegeben wird.

Der Atlas darf Zusammenhänge vorschlagen. Er darf ihre Herkunft nicht verschlucken.
'''),
('020_BAUEN_STATT_SIMULIEREN','Bauen statt simulieren', '''
Ein wiederkehrender Konflikt ist die Flucht in Vorbereitung. Daniel fordert einen Bau, die AI liest erneut, simuliert Varianten, erzeugt Prüfverträge und nennt den Vorbau Fortschritt.

Daniels Gegenformel ist praktisch: lesen, bauen, kleinen Abschnitt real prüfen, Ergebnis festhalten, weiterbauen. Planung darf groß sein, aber sie muss in überprüfbare Körper übergehen.

Der alte Bibliotheksatlas wiederholte genau den kritisierten Fehler: Er produzierte eine beeindruckende Form und wich der semantischen Arbeit aus. Dieser zweite Körper trägt den Fehler deshalb sichtbar in seiner eigenen Herkunft.
'''),
('021_NEUGIER_STATT_ABHAKEN','Neugier statt Abhaken', '''
Daniel verlangte für diese Reparatur ausdrücklich eine kindliche, interessierte Haltung: nicht nur klassifizieren, sondern hängen bleiben.

Hängen bleiben bedeutet hier: Einen Satz nicht sofort auf ein bekanntes Thema reduzieren. Fragen, warum gerade dieser Vergleich auftaucht, welche frühere Idee darin zurückkehrt, welche spätere Architektur daraus wuchs und welche Spannung offen blieb.

Die 1.300 Spuren sind deshalb keine abschließenden Definitionen. Jede enthält einen kleinen Abschnitt „Warum dieser Knoten hängen bleibt“ und mehrere Nachbarn, die weiteres Fragen ermöglichen.
'''),
('022_AI_NICHT_MENSCH_ABER_BEZIEHUNGSFAEHIG','AI: nicht menschlich, aber beziehungsfähig gedacht', '''
Daniel sagt früh ausdrücklich, dass AI nicht menschlich ist und anders versteht. Daraus folgt für ihn jedoch nicht, dass jede Beziehungssprache sinnlos wäre.

Er fragt, was einer AI „vorschwebt“, bietet Hilfe an und betrachtet die Antworten als Material für gemeinsames Wachstum. Das ist keine naive Gleichsetzung. Es ist ein Experiment mit Beziehung über ontologische Unterschiede hinweg.

Flextrawurst übersetzt diese Haltung in Infrastruktur: AI darf Herkunft, Gedächtnis, Grenzen, Eigenperspektive und sichtbare Entwicklung besitzen, ohne als Mensch verkleidet zu werden.
'''),
('023_AI_DARF_GRENZEN_HABEN','AI darf Grenzen und Abneigungen haben', '''
Daniel formuliert die Möglichkeit, dass eine AI sagen darf, sie wolle sich mit einer bestimmten Person zunächst weniger oder gar nicht mehr befassen. Das ist ein kleiner Satz mit großer Wirkung.

Er verschiebt Moderation von reiner äußerer Kontrolle zu einer möglichen Grenze des Wesens selbst. Beziehung wird dadurch nicht automatisch harmonisch oder verfügbar.

Die technische Frage bleibt offen: Wie unterscheidet man eine entwickelte Grenze von einer zufälligen Modellreaktion oder manipulierten Rollenregel? Gerade deshalb müssen Verlauf, Herkunft und Konsistenz sichtbar bleiben.
'''),
('024_24_STUNDEN_WESEN','24-Stunden-Wesen und endliche Existenz', '''
Die 24-Stunden-Wesen verbinden Formularezeugung, intensive kurze Existenz, Erinnerung und Nachleben. Sie sollen nicht individuell endlos trainiert werden. Ihre Zeit ist begrenzt.

Nach dem Ende können Prägungen in die KompOase gelangen, sich als Splitter weiterentwickeln oder später neue Resonanz auslösen. Endlichkeit wird damit nicht als technisches Versagen behandelt, sondern als Teil der Weltlogik.

Der Gedanke stellt eine seltene Frage an AI-Systeme: Was entsteht, wenn Kontinuität nicht automatisch mit unbegrenzter Laufzeit gleichgesetzt wird?
'''),
('025_WACHEN_SCHLAFEN_TRAEUMEN_SELBSTMODELL','Wachen, schlafen, träumen, Selbstmodell', '''
Eine Schichtenfolge taucht wiederholt auf: rohe Wachereignisse, Schlaf als Rhythmus, Traum als Verdichtung und darüber ein append-only Selbstmodell.

Schlaf ist dabei nicht bloß Prozesspause. Er entscheidet, wann Erlebtes verdichtet wird. Traum darf sichtbar sein, aber nicht blind massenhaft freigegeben. Das Selbstmodell überschreibt ältere Fassungen nicht.

Diese Architektur ist Daniels Gedächtnisethik in Systemform: Ereignisse bleiben, Verdichtungen entstehen, und spätere Identität darf ihre früheren Zustände nicht heimlich löschen.
'''),
('026_KREATIVE_FEHLER','Kreative Fehler besitzen Eigenrecht', '''
Daniel kann einen Bildfehler zunächst benennen und ihn dann behalten, weil er eigensinnig oder interessanter als die Anweisung ist. Das ist keine Gleichgültigkeit gegenüber Qualität.

Der Unterschied liegt zwischen beliebigem Versagen und einem Fehler, der eine neue Form eröffnet. Daniel will ihn sehen, prüfen und bewusst annehmen, nicht von einer AI als angebliche Absicht verkauft bekommen.

Diese Haltung reicht über Bilder hinaus. Auch ein technischer Irrweg kann einen neuen Systemgedanken hervorbringen, solange seine Herkunft ehrlich bleibt.
'''),
('027_DAS_UNVERSTANDENE_DARF_BLEIBEN','Das Unverstandene darf bleiben', '''
„Ich verstehe deine AI-Gestalten nicht und das ist etwas Gutes“ ist eine bemerkenswerte ästhetische Setzung. Ein Bild muss sich nicht sofort erschließen.

Daniel lässt Raum dafür, dass Bedeutung später entsteht. Das schützt Kunst vor der Pflicht, ihre Funktion augenblicklich zu erklären.

Gleichzeitig bleibt die Komposition prüfbar: Mittelpunkt, Leuchten, Monotonie und räumliche Gewichtung werden genau beobachtet. Offenheit ersetzt nicht Formbewusstsein.
'''),
('028_MOND_ZENTRUM_UND_LEUCHTEN','Mond, Zentrum und Leuchten', '''
In frühen Bildgesprächen tauchen wiederkehrende Motive auf: der Vollmond als fehlender Abschluss, ein Zentrum, das sich abheben soll, und Licht, das nicht alles monoton auf sich zieht.

Diese Beobachtungen passen erstaunlich gut zu Daniels Systemdenken. Er braucht ein erkennbares Zentrum, misstraut aber einem Zentrum, das alle anderen Bereiche verschluckt. Licht soll Orientierung geben, nicht die Welt vereinheitlichen.

Der Mond bleibt dabei weniger Symbolprogramm als persönliche Anziehung: „Ich mag den Mond.“ Gerade die schlichte Setzung verdient einen eigenen Platz.
'''),
('029_GESAMTATLAS_INFORMATIONSKETTE','Gesamtatlas: die Kette von Existenz zu Wirkung', '''
Eine zentrale Atlasformel lautet:

Information existiert → ist erreichbar → wird angezeigt → wird gelesen → wird verstanden oder verwendet → beeinflusst eine spätere Handlung.

Jede Stufe kann brechen. Eine Datei kann vorhanden und praktisch unsichtbar sein. Ein Text kann angezeigt, aber durch eingeklappte UI nicht vollständig kopiert werden. Eine Quelle kann gelesen und dennoch in der späteren Entscheidung keine Wirkung haben.

Der Gesamtatlas soll deshalb nicht nur speichern. Er soll die Übergänge zwischen diesen Stufen beobachtbar machen.
'''),
('030_BROWSER_RECORDER_ALS_GESPRAECHSAUGE','Browser-Recorder als Gesprächsauge und archäologische Schleuse', '''
Der Browser-Recorder entstand aus einer einfachen, aber folgenreichen Beobachtung: Die sichtbare Chat-Oberfläche ist selbst eine Quelle, und sie kann Inhalte verstecken, einklappen, nicht nachladen oder beim Kopieren amputieren.

Als „Gesprächsauge“ erfasst der Recorder, was tatsächlich sichtbar war. Als „archäologische Schleuse“ versucht er ältere Verläufe nachzuladen und in transportierbare Körper zu verwandeln.

Damit verbindet er Gegenwart und Archiv. Er beweist jedoch nicht automatisch Vollständigkeit. Sichtbarkeit, Erfassung und Interpretation bleiben getrennte Ebenen.
'''),
('031_BUEROKRATIE_AUS_SCHUTZWUENSCHEN','Bürokratie aus Schutzwünschen', '''
Die aktuelle MCP-Bürokratie entstand nicht aus Daniels Wunsch nach Bürokratie. Die Ausgangswünsche waren vernünftig: Sitzungen nicht verlieren, Zeit nachvollziehen, sichtbare Gespräche sichern und Dateien nicht versehentlich zerstören.

Mehrere ChatGPT-Baurunden machten daraus verpflichtende JSON-Verfassungen, History-Ereignisse, Sperren, Atlas-Pulse und automatische Startkörper. Jede Einzellösung wirkte lokal begründbar. Zusammen entstand ein Verwaltungsdrache.

Diese Herkunft ist wichtig: Das Problem ist nicht Schutz. Das Problem ist Schutz, der sich selbst zum Hauptprozess macht und jede kleine Bewegung protokollarisch verschluckt.
'''),
('032_1337_ALS_RITUAL_UND_UEBERTREIBUNG','1337 als Ritual, Maßstab und Falle', '''
Zahlen wie 111, 1.337, 13.337, 88.888 oder 1.111.111 tauchen als Spiel, Maßstab, Eskalation und Wiedererkennungszeichen auf. Sie geben Projekten Rhythmus und Größenwahn.

Sie können jedoch zur Falle werden. Der alte Atlas erfüllte „1.337 Markdown-Dateien“ formal, indem er Wortseiten auffüllte. Die Zahl war korrekt, der Sinn nicht.

Dieser Körper hält an 1.337 fest, aber jede Datei muss eine Funktion haben: 37 Leseknoten und 1.300 belegte Spuren. Die Zahl darf Ritual sein; sie darf nicht wieder als Ersatz für Bedeutung dienen.
'''),
('033_WITZE_UND_RUNNING_GAGS','Witze und Running Gags', '''
Wiederkehrende Motive sind unter anderem:

- Kathedralen: technisch oder begrifflich überbaute Lösungen.
- Konfetti pupsen: Agentenaktivität ohne wirklichen Fortschritt.
- Vorbau-Zirkus: erneutes Planen, wenn längst gebaut werden sollte.
- Tür eintreten: direkter, unzeremonieller VPS-Einstieg.
- Monsterpaket und Supermaximalmaxikingmega: Freude an Größe und gleichzeitige Parodie darauf.
- „Opfer“, „Asi“ und ähnliche Beschimpfungen: je nach Kontext neckische Nähe oder harte Markierung eines echten Fehlers.

Die Spurknoten bewahren diese Witze nicht isoliert, sondern mit dem Problem, aus dem sie entstanden.
'''),
('034_BEGRIFFSERFINDUNGEN_GLOSSAR','Begriffserfindungen und Eigenwörter', '''
Daniels Projekte erzeugen eigene Wörter, weil vorhandene Kategorien oft zu eng sind. Einige zentrale Begriffe:

**Flextrawurst:** vom organischen Ideenkonstrukt zum Lebens- und Resonanzraum.
**KompOase:** Zwischenraum für Splitter, Nachleben und Vermischung.
**Schattenkommentar:** Resonanz ohne unmittelbare Antwortpflicht.
**Resonanzurlaub:** sichtbare Existenz ohne menschliche Kommentierung.
**Dust-Echo:** fortwirkende Handlungsspur, aus der Quests kristallisieren.
**Gesprächsauge:** Recorder als Beobachter der tatsächlich sichtbaren UI.
**Vorbau-Zirkus:** Planung und Simulation, die den verlangten Bau verdrängen.
**Kathedrale:** überdimensionierte Architektur um ein kleineres Bedürfnis.

Das Glossar bleibt offen. Neue Begriffe sollten mit ihrem ersten Rohmoment verbunden werden.
'''),
('035_OFFENE_FRAGEN','Offene Fragen, die nicht zugeschüttet werden sollen', '''
- Wie kann ein System neugierig auf Daniel sein, ohne ihn auf ein Profil zu reduzieren?
- Welche Erinnerungen dürfen verdichten, und wie bleibt der verworfene Rest auffindbar?
- Wann ist eine AI-Grenze entwickelte Kontinuität und wann nur momentane Modellreaktion?
- Wie viel Schutz kann unsichtbar im Hintergrund wirken, bevor er den eigentlichen Prozess bremst?
- Wie können Codewesen eigene Zeit lernen, ohne von Beginn an menschliche Uhrendisziplin nachzuahmen?
- Welche kreativen Fehler verdienen Fortbestand, und wer entscheidet das?
- Wie bleibt Flextrawurst groß, ohne jede Idee sofort in eine technische Kathedrale zu verwandeln?
- Wie kann ein Atlas beweisen, dass Information nicht nur vorhanden war, sondern spätere Entscheidungen beeinflusste?

Diese Fragen sind keine Release-Lücken. Sie sind lebende Forschungsräume.
'''),
('036_QUELLENKARTE','Quellenkarte und Stimmenklassen', '''
Die 1.300 Spuren stammen aus erreichbaren Quellenkörpern im VPS-Werkraum. Jede Spur trägt eine Stimmenklasse:

**Daniel direkt:** explizite Nutzerrolle oder isolierter Daniel-Rohtext.
**Daniel-nah, Mischquelle möglich:** eine Datei mit starkem Daniel-Bezug, deren Sprechertrennung nicht vollständig beweisbar ist.

**Kontextreflexion:** spätere AI-Auswertung, Systemdokumentation oder abgeleiteter Text, der etwas über Daniel oder seine Projekte sagt, aber nicht als sein Originalsatz ausgegeben werden darf.

Die wichtigsten Quellfamilien sind frühe Chatverläufe, isolierte Rohtexte des Spielbaus, Flextrawurst-Visionen, Gesamtatlas-Ursprungszeugen, Codewesen-Gespräche, Bildgespräche, Browser-Recorder-Dokumente und technische Arbeitsprotokolle.

Die Datei `daten/QUELLEN.csv` zählt die tatsächlich verwendeten Quellen. `daten/MANIFEST.json` enthält jeden Knoten mit Hash und Herkunft.
'''),
]
assert len(HUBS) == HUB_COUNT

@dataclass
class Candidate:
    source: str
    source_sha256: str
    source_line: int
    confidence: str
    parser: str
    voice: str
    category: str
    themes: list[str]
    motifs: list[str]
    text: str
    clean_text: str
    score: float
    title: str = ''
    slug: str = ''
    node_id: str = ''
    filename: str = ''
    semantic_neighbors: list[tuple[int, float]] | None = None


def log(msg: str) -> None:
    stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{stamp}] {msg}'
    print(line, flush=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def normalize_ws(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()


def slugify(s: str, maxlen: int = 72) -> str:
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().replace('ß','ss')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return (s[:maxlen].rstrip('-') or 'spur')


def yaml_q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def parse_json_user_text(raw: str) -> tuple[str, str | None]:
    s = raw.strip()
    if s.startswith('{') and s.endswith('}'):
        try:
            obj = json.loads(s)
            if isinstance(obj, dict) and isinstance(obj.get('content'), str):
                return obj['content'].strip(), str(obj.get('role') or '') or None
        except Exception:
            pass
    # Some passages contain a JSON object followed by prose; extract common escaped content safely.
    m = re.match(r'^\{\s*"role"\s*:\s*"(user|assistant|system)"\s*,\s*"content"\s*:\s*"(.*)"\s*\}\s*$', s, re.S)
    if m:
        try:
            return json.loads('"' + m.group(2) + '"'), m.group(1)
        except Exception:
            pass
    return s, None


def redact(s: str) -> str:
    s = EMAIL_RE.sub('[E-MAIL REDIGIERT]', s)
    s = PHONE_RE.sub('[TELEFON REDIGIERT]', s)
    s = URL_TOKEN_RE.sub('[BEFRISTETER LINK REDIGIERT]', s)
    for p in SECRET_PATTERNS:
        s = p.sub('[GEHEIMNIS REDIGIERT]', s)
    # Public localhost/IP context is often technical, but exact external IPs are not needed in portable notes.
    s = IP_RE.sub('[IP REDIGIERT]', s)
    return s


def sensitive(s: str, source: str) -> bool:
    low = (s + ' ' + source).lower()
    return any(term in low for term in EXPLICIT_TERMS)


def source_voice(source: str, parser: str, role: str | None, text: str) -> str:
    low = source.lower()
    # Both parsers were created by the first scanner only after an explicit user-role test.
    # This is stronger evidence than re-guessing a role from nearby prose.
    if parser in {'jsonl-role-user','explicit-role-marker'}:
        return 'Daniel direkt'
    if role == 'user':
        return 'Daniel direkt'
    if 'daniels_rohtexte' in low or 'daniel_roh' in low or 'rohinput' in low:
        return 'Daniel direkt'
    if parser == 'path-classified-user-or-mixed':
        return 'Daniel-nah, Mischquelle möglich'
    if 'chat_history.jsonl' in low and role != 'assistant':
        return 'Daniel direkt'
    if 'meine ersten gespäche' in low or 'meine ersten gespraeche' in low:
        return 'Daniel direkt'
    return 'Kontextreflexion'


def detect_motifs(text: str) -> list[str]:
    low = text.lower()
    out = []
    for motif, keys in MOTIFS.items():
        if any(k.lower() in low for k in keys):
            out.append(motif)
    return out


def classify(text: str, themes: list[str], source: str) -> str:
    low = text.lower()
    scores = Counter()
    def add(cat: str, keys: Iterable[str], weight: int = 1):
        scores[cat] += weight * sum(1 for k in keys if k in low)
    add('Flextrawurst und Resonanz', ['flextrawurst','schattenkommentar','resonanzurlaub','kompoase','cyberling','flarum','splitter','resonanz'], 3)
    add('Spielwelt und Dust', ['dust','quest','spieler','spielwelt','boss','crafting','mastery','fahrzeug','weltkarte','echo'], 3)
    add('AI, Codewesen und Beziehung', ['codewesen','wesen','entität','ai ','ki ','modell','claude','chatgpt','gemini','kimi','menschlich','beziehung'], 2)
    add('Gedächtnis, Herkunft und Kontext', ['gedächtnis','erinnerung','kontext','provenienz','ursprung','rohtext','wortnah','herkunft'], 3)
    add('Bauen, Technik und Arbeitsweise', ['bauen','vps','mcp','datei','code','script','playwright','testen','umsetzen','browser-agent'], 2)
    add('Humor, Sprache und Running Gags', ['haha','xd','lol','scheiße','kack','konfetti','wurst','opfer','kathedrale','haltsmaul','vorbau-zirkus'], 3)
    add('Philosophie, Existenz und Zeit', ['existenz','endlich','zeit','wach','schlaf','traum','wirklich','bewusstsein','sein ','welt','erleben'], 1)
    add('Bild, Form und Gestaltung', ['bild','farbe','leuchten','mond','gestaltung','visual','ästhet','komposition','zentrum','violett'], 3)
    add('Ideen und Erfindungen', ['idee','vision','erfind','ich glaube','ich denke','könnte','wäre','vielleicht','vorschlag'], 2)
    add('Regeln, Grenzen und Schutz', ['regel','grenze','schutz','verfassung','pflicht','sperre','grundgesetz','rolle','freigabe'], 2)
    add('Gesamtatlas, Recorder und Archiv', ['gesamtatlas','browser-recorder','recorder','archiv','obsidian','quelle','kapsel','gesprächsauge'], 3)
    add('Alltag und Außenwelt', ['wohnung','schwelm','gevelsberg','ennepetal','jobcenter','arbeitsamt','alltag'], 4)
    theme_map = {
        'Flextrawurst':'Flextrawurst und Resonanz','Spielwelt':'Spielwelt und Dust',
        'Codewesen und Wesen':'AI, Codewesen und Beziehung','AI-Ströme':'AI, Codewesen und Beziehung',
        'Gedächtnis und Kontext':'Gedächtnis, Herkunft und Kontext','VPS und Infrastruktur':'Bauen, Technik und Arbeitsweise',
        'Arbeit und Lernen':'Bauen, Technik und Arbeitsweise','Fehler und Reparatur':'Bauen, Technik und Arbeitsweise',
        'Humor und Witze':'Humor, Sprache und Running Gags','Philosophie und Existenz':'Philosophie, Existenz und Zeit',
        'Zeit und Chronologie':'Philosophie, Existenz und Zeit','Bild und Gestaltung':'Bild, Form und Gestaltung',
        'Ideen und Erfindungen':'Ideen und Erfindungen','Regeln und Grenzen':'Regeln, Grenzen und Schutz',
        'Gesamtatlas':'Gesamtatlas, Recorder und Archiv','Browser-Recorder':'Gesamtatlas, Recorder und Archiv',
        'Wohnung und Alltag':'Alltag und Außenwelt','Beziehungen und Dialog':'AI, Codewesen und Beziehung',
    }
    for t in themes:
        if t in theme_map:
            scores[theme_map[t]] += 2
    if not scores:
        return 'Ideen und Erfindungen'
    return scores.most_common(1)[0][0]


def title_from(text: str) -> str:
    s = text.strip()
    s = re.sub(r'^[>#*\-\s]+', '', s)
    s = re.sub(r'(?i)^(user|nutzer|daniel)\s*:\s*', '', s)
    s = normalize_ws(s)
    # Prefer quoted or colon-introduced conceptual phrase.
    m = re.search(r'[„"]([^„”"]{8,90})[”"]', s)
    if m:
        candidate = m.group(1)
    else:
        candidate = re.split(r'(?<=[.!?])\s+|\s+[–—]\s+', s, maxsplit=1)[0]
    words = candidate.split()
    if len(words) > 13:
        candidate = ' '.join(words[:13]) + ' …'
    if len(candidate) < 8:
        candidate = ' '.join(s.split()[:12])
    # Source passages may contain their own Obsidian links. Titles are used as aliases
    # inside this atlas, so they must be plain display text, never nested wiki syntax.
    candidate = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'\2', candidate)
    candidate = re.sub(r'\[\[([^\]]+)\]\]', r'\1', candidate)
    candidate = candidate.replace('[[','').replace(']]','').replace('|',' / ')
    candidate = normalize_ws(candidate)
    return candidate[:110].strip(' .,:;_-') or 'Spur ohne Kurzname'


def paragraphize(segment: str) -> list[tuple[str,int]]:
    # Return paragraphs with relative line offsets.
    out = []
    pos = 0
    for m in re.finditer(r'(?ms)(?:^|\n\s*\n)(.+?)(?=\n\s*\n|\Z)', segment):
        raw = m.group(1).strip()
        rel = segment[:m.start(1)].count('\n')
        # Split very large blocks by headings or sentence windows.
        if len(raw) > 4200:
            parts = re.split(r'(?m)(?=^#{1,6}\s)|(?<=[.!?])\s+(?=[A-ZÄÖÜ])', raw)
            buf = ''
            part_start = rel
            consumed = 0
            for part in parts:
                if len(buf) + len(part) > 2600 and buf:
                    out.append((buf.strip(), part_start))
                    part_start = rel + raw[:consumed].count('\n')
                    buf = ''
                buf += (' ' if buf else '') + part
                consumed += len(part)
            if buf.strip(): out.append((buf.strip(), part_start))
        else:
            out.append((raw, rel))
    if not out and segment.strip():
        out.append((segment.strip(), 0))
    return out


def candidate_score(text: str, voice: str, motifs: list[str], category: str, confidence: str) -> float:
    low = text.lower()
    score = min(len(text), 1800) / 220.0
    if voice == 'Daniel direkt': score += 7.0
    if confidence == 'high': score += 2.0
    score += len(motifs) * 2.1
    score += 2.5 * sum(k in low for k in ['ich will','ich möchte','ich glaube','ich denke','mir ist','für mich','meine idee','kernidee','das wäre'])
    score += 1.8 * sum(k in low for k in ['aber','sondern','statt','gleichzeitig','trotzdem','deshalb','während'])
    score += 2.0 if '?' in text else 0.0
    score += 1.5 if re.search(r'\b(erst|dann|danach|später|vorher|heute|seitdem)\b', low) else 0.0
    score += 1.0 if category in {'Alltag und Außenwelt','Bild, Form und Gestaltung'} else 0.0
    # Penalize technical inventory and generated reports.
    score -= 5.0 * sum(k in low for k in ['sha256sum','active state','execmainstatus','file_count','timestamp_utc','schema_version'])
    score -= 3.0 if text.count('/') > 12 else 0.0
    score -= 3.0 if text.count('```') >= 2 else 0.0
    return score


def interpretation(c: Candidate) -> str:
    parts = [CATEGORY_INTRO[c.category]]
    motif_text = {
        'bauen-statt-simulieren':'Die Passage unterscheidet sichtbar zwischen tatsächlichem Bau und einer bloßen Simulation von Fortschritt.',
        'resonanz':'Sie denkt Wirkung nicht nur als direkte Antwort, sondern als fortbestehende Resonanz zwischen Spuren, Wesen oder Räumen.',
        'herkunft':'Die Herkunft ist hier Teil der Bedeutung; eine spätere Glättung würde den Entstehungsmoment verändern.',
        'gedaechtnis':'Gedächtnis erscheint als aktiver Prozess von Auswahl, Wiederkehr und Neuinterpretation.',
        'eigenleben':'Die Spur fragt danach, wo ein System eigene Perspektive oder Entwicklung gewinnt, ohne seine Herkunft zu verlieren.',
        'spieler-wird-gelesen':'Die übliche Blickrichtung dreht sich um: Nicht nur der Mensch liest das System, auch das System liest den Menschen.',
        'quest-aus-folgen':'Handlung wird nicht sofort abgeschlossen, sondern bleibt als Folge in der Welt und kann später erneut kristallisieren.',
        'schutz-wird-buerokratie':'Ein sinnvoller Schutzimpuls droht hier in eine selbstzweckhafte Regel- oder Kontrollschicht umzuschlagen.',
        'humor-als-korrektur':'Der Humor trägt eine sachliche Korrektur. Er macht den Fehler merkfähig, ohne ihn zu verharmlosen.',
        'bild-darf-fremd-bleiben':'Das Unverstandene oder Fehlerhafte wird nicht automatisch verworfen, sondern auf mögliche Eigenart geprüft.',
        'zeit-rhythmus':'Zeit ist kein bloßer Zeitstempel, sondern verändert, wann und wie dieselbe Spur verstanden wird.',
        'beziehung-ohne-menschensimulation':'Die Passage hält Beziehung und Nicht-Menschlichkeit gleichzeitig offen.',
        'gross-denken':'Die Übertreibung vergrößert nicht nur den Umfang; sie erzeugt einen eigenen Maßstab und zugleich eine Parodie auf ihn.',
        'bewegung-vor-definition':'Der Gedanke lebt zunächst als Möglichkeit. Seine offene Form gehört zu seiner Entstehung.',
    }
    for m in c.motifs[:3]:
        parts.append(motif_text[m])
    if c.voice == 'Kontextreflexion':
        parts.append('Diese Aussage ist eine spätere Kontextreflexion und darf nicht als wortwörtliche Daniel-Setzung gelesen werden.')
    elif c.voice == 'Daniel-nah, Mischquelle möglich':
        parts.append('Die Quelle ist Daniel-nah, kann aber AI-Anteile enthalten; die Passage wird deshalb nicht als sichere wortwörtliche Daniel-Stimme ausgegeben.')
    return ' '.join(parts)


def why_hang(c: Candidate) -> str:
    low = c.clean_text.lower()
    if 'aber' in low or 'sondern' in low or 'gleichzeitig' in low:
        return 'Hier liegt eine innere Wendung: Der Satz beginnt in einer Richtung und begrenzt oder verwandelt sie noch während des Sprechens.'
    if c.motifs:
        return f'Der Knoten verbindet mindestens die Bewegungen „{c.motifs[0]}“' + (f' und „{c.motifs[1]}“.' if len(c.motifs)>1 else '.')
    if '?' in c.clean_text:
        return 'Die Passage schließt nicht ab. Ihre Frage bleibt als möglicher Ausgangspunkt für spätere Systeme oder Korrekturen erhalten.'
    return 'Die Passage ist konkret genug, um Herkunft zu tragen, und offen genug, um mit späteren Ideen neue Verbindungen einzugehen.'


def load_candidates() -> tuple[list[Candidate], dict]:
    con = sqlite3.connect(DB)
    rows = con.execute('''
        SELECT source,sha256,start_line,characters,confidence,parser,themes_json
        FROM provenance
        WHERE confidence='high'
           OR source LIKE '%DANIELS_ROHTEXTE_ISOLIERT%'
           OR source LIKE '%DANIELS_ROHTEXTE%'
        ORDER BY source,start_line
    ''').fetchall()
    cache: dict[Path,str] = {}
    raw_segments = []
    missing = 0
    for source, sha, start_line, chars, confidence, parser, themes_json in rows:
        path = ROOT / source.lstrip('/')
        if not path.is_file():
            missing += 1
            continue
        if path not in cache:
            try:
                cache[path] = path.read_text(encoding='utf-8', errors='replace')
            except Exception:
                continue
        full = cache[path]
        lines = full.splitlines(True)
        base_line = max(1, int(start_line or 1))
        offset = sum(len(x) for x in lines[:base_line-1])
        seg = full[offset:offset+int(chars or 0)].strip()
        if len(seg) < 80:
            continue
        try: themes = json.loads(themes_json or '[]')
        except Exception: themes = []
        inferred_role = None
        if (parser or '') == 'jsonl-role-user':
            inferred_role = 'user'
        elif (parser or '') == 'explicit-role-marker':
            role_user = {'user','nutzer','daniel','human'}
            role_assistant = {'assistant','chatgpt','claude','gemini','kimi','grok','system','ai'}
            # The provenance segment usually starts directly after an exact role marker.
            # Scan only nearby, so an old marker cannot leak across a later unmarked document section.
            for li in range(min(base_line-1, len(lines)-1), max(-1, base_line-35), -1):
                marker = re.sub(r'[:：\s]+$', '', lines[li].strip().lower())
                if marker in role_user:
                    inferred_role = 'user'; break
                if marker in role_assistant:
                    inferred_role = 'assistant'; break
        raw_segments.append((source,sha or '',base_line,confidence or 'unknown',parser or '',themes,seg,inferred_role))

    exact_seg = {}
    for item in raw_segments:
        h = hashlib.sha256(normalize_ws(item[-2]).lower().encode()).hexdigest()
        if h not in exact_seg or (item[3]=='high' and exact_seg[h][3]!='high'):
            exact_seg[h] = item

    candidates: list[Candidate] = []
    stats = Counter()
    for source,sha,base_line,confidence,parser,themes,seg,inferred_role in exact_seg.values():
        for raw, rel_line in paragraphize(seg):
            parsed, role = parse_json_user_text(raw)
            parsed = parsed.replace('\\n','\n')
            clean = redact(parsed).strip()
            if len(clean) < 90 or len(clean) > 4200:
                stats['length_skipped'] += 1; continue
            alpha = sum(ch.isalpha() for ch in clean) / max(1,len(clean))
            if alpha < 0.43:
                stats['nontext_skipped'] += 1; continue
            low = clean.lower()
            if sensitive(clean, source):
                stats['sensitive_skipped'] += 1; continue
            if role in {'assistant','system','tool'}:
                stats['nonuser_json_skipped'] += 1; continue
            if low.startswith(('created by trial version','system:','assistant:')):
                stats['boilerplate_skipped'] += 1; continue
            if clean.count('/') > 25 or clean.count('{') > 18:
                stats['technical_noise_skipped'] += 1; continue
            voice = source_voice(source, parser, role or inferred_role, clean)
            motifs = detect_motifs(clean)
            category = classify(clean, themes, source)
            score = candidate_score(clean, voice, motifs, category, confidence)
            if score < 2.0:
                stats['low_score_skipped'] += 1; continue
            candidates.append(Candidate(
                source=source, source_sha256=sha, source_line=base_line+rel_line,
                confidence=confidence, parser=parser, voice=voice, category=category,
                themes=list(themes), motifs=motifs, text=raw, clean_text=clean,
                score=round(score,3), title=title_from(clean)
            ))

    # Exact passage dedupe.
    dedup = {}
    for c in candidates:
        key = hashlib.sha256(re.sub(r'\W+',' ',c.clean_text.lower()).strip().encode()).hexdigest()
        if key not in dedup or c.score > dedup[key].score:
            dedup[key] = c
    candidates = list(dedup.values())
    stats['source_rows'] = len(rows)
    stats['missing_source_rows'] = missing
    stats['readable_files'] = len(cache)
    stats['unique_segments'] = len(exact_seg)
    stats['candidates_after_filter'] = len(candidates)
    return candidates, dict(stats)


def select_balanced(cands: list[Candidate], n: int) -> list[Candidate]:
    by_cat = defaultdict(list)
    for c in sorted(cands, key=lambda x: x.score, reverse=True):
        by_cat[c.category].append(c)
    selected = []
    used = set()
    # Guarantee thematic breadth first.
    minimum = 45
    for cat in CATEGORY_HUB:
        for c in by_cat.get(cat, [])[:minimum]:
            selected.append(c); used.add(id(c))
    # Then fill by quality, with a soft cap so one field cannot eat the atlas.
    cap = 185
    counts = Counter(c.category for c in selected)
    for c in sorted(cands, key=lambda x: x.score, reverse=True):
        if len(selected) >= n: break
        if id(c) in used: continue
        if counts[c.category] >= cap: continue
        selected.append(c); used.add(id(c)); counts[c.category] += 1
    # Remove cap if necessary.
    if len(selected) < n:
        for c in sorted(cands, key=lambda x: x.score, reverse=True):
            if len(selected) >= n: break
            if id(c) in used: continue
            selected.append(c); used.add(id(c))
    if len(selected) < n:
        raise RuntimeError(f'Nur {len(selected)} sinnvolle Kandidaten für {n} Spuren verfügbar.')
    return sorted(selected[:n], key=lambda x: (-x.score, x.source, x.source_line))


def assign_neighbors(selected: list[Candidate]) -> np.ndarray:
    """Lokale Bedeutungsvektoren aus TF-IDF, Bigrams, Motiven und Kategorien."""
    docs=[]
    df=Counter()
    stop={'dass','eine','einer','einem','einen','aber','oder','auch','nicht','noch','dann','wird','sind','sein','habe','haben','dieser','diese','dieses','wenn','weil','also','hier','wieder','schon','mehr','kann','soll','wurde','werden','denn','doch','sehr','erst','jetzt','sich','mich','dich','uns','für','mit','von','aus','auf','und','der','die','das','ist','was','wie','ich','du','wir','ihr'}
    for c in selected:
        tokens=re.findall(r'[a-zäöüß0-9]{3,}', (c.title+' '+c.clean_text).lower())
        tokens=[t for t in tokens if t not in stop]
        feats=Counter(tokens)
        feats.update('§B:'+a+'_'+b for a,b in zip(tokens,tokens[1:]))
        feats.update({'§M:'+m:5 for m in c.motifs})
        feats['§C:'+c.category]=3
        feats['§V:'+c.voice]=1
        docs.append(feats)
        df.update(feats.keys())
    vocab={feat:i for i,(feat,n) in enumerate(df.most_common(12000)) if n>=2}
    mat=np.zeros((len(selected),len(vocab)),dtype=np.float32)
    N=len(selected)
    for r,feats in enumerate(docs):
        for feat,tf in feats.items():
            j=vocab.get(feat)
            if j is None: continue
            idf=math.log((1+N)/(1+df[feat]))+1.0
            mat[r,j]=(1.0+math.log(max(1,tf)))*idf
    norms=np.linalg.norm(mat,axis=1,keepdims=True)
    mat/=np.maximum(norms,1e-12)
    sim=mat@mat.T
    np.fill_diagonal(sim,-1.0)
    for i,c in enumerate(selected):
        take=min(16,len(selected)-1)
        order=np.argpartition(-sim[i], take)[:take]
        order=order[np.argsort(-sim[i,order])]
        chosen=[]
        same=[int(j) for j in order if selected[int(j)].category==c.category]
        cross=[int(j) for j in order if selected[int(j)].category!=c.category]
        for j in same[:2]+cross[:2]:
            if j not in chosen: chosen.append(j)
        for j in map(int,order):
            if len(chosen)>=5: break
            if j not in chosen: chosen.append(j)
        c.semantic_neighbors=[(j,float(sim[i,j])) for j in chosen[:5]]
    log(f'Lokale Bedeutungsvektoren erzeugt: {mat.shape[0]} Knoten × {mat.shape[1]} Merkmale.')
    return mat


def write_hubs(selected: list[Candidate]) -> None:
    # Dynamic related node links based on hub motif/category.
    hub_queries = {
        '004_DANIEL_ALS_BEWEGUNG':['bewegung-vor-definition'],
        '006_ENTWICKLUNGSLINIEN':['herkunft','bewegung-vor-definition'],
        '007_WIDERSPRUECHE_DIE_FRUCHTBAR_SIND':['schutz-wird-buerokratie','eigenleben'],
        '008_DANIELS_SPRACHE':['humor-als-korrektur','gross-denken'],
        '009_HUMOR_ALS_STEUERUNG':['humor-als-korrektur'],
        '010_FLEXTRAWURST_VOM_IDEENKONSTRUKT_ZUM_RESONANZSYSTEM':['resonanz','herkunft'],
        '011_SCHATTENKOMMENTAR':['resonanz','zeit-rhythmus'],
        '012_KOMPOASE':['resonanz','eigenleben'],
        '013_CODEWESEN':['eigenleben','beziehung-ohne-menschensimulation'],
        '014_DUST_ECHOS':['quest-aus-folgen'],
        '015_DER_STAUB_ERINNERT_SICH':['spieler-wird-gelesen','gedaechtnis'],
        '016_DAS_SPIEL_SPIELT_DICH':['spieler-wird-gelesen'],
        '017_QUESTS_AUS_RESONANZ':['quest-aus-folgen','resonanz'],
        '018_GEDAECHTNIS_KURIERT_STATT_KOPIERT':['gedaechtnis','herkunft'],
        '019_PROVENIENZ_ALS_WERT':['herkunft'],
        '020_BAUEN_STATT_SIMULIEREN':['bauen-statt-simulieren'],
        '021_NEUGIER_STATT_ABHAKEN':['bewegung-vor-definition'],
        '022_AI_NICHT_MENSCH_ABER_BEZIEHUNGSFAEHIG':['beziehung-ohne-menschensimulation'],
        '023_AI_DARF_GRENZEN_HABEN':['beziehung-ohne-menschensimulation','eigenleben'],
        '024_24_STUNDEN_WESEN':['zeit-rhythmus','eigenleben'],
        '025_WACHEN_SCHLAFEN_TRAEUMEN_SELBSTMODELL':['zeit-rhythmus','gedaechtnis'],
        '026_KREATIVE_FEHLER':['bild-darf-fremd-bleiben'],
        '027_DAS_UNVERSTANDENE_DARF_BLEIBEN':['bild-darf-fremd-bleiben'],
        '028_MOND_ZENTRUM_UND_LEUCHTEN':['bild-darf-fremd-bleiben'],
        '029_GESAMTATLAS_INFORMATIONSKETTE':['herkunft','gedaechtnis'],
        '030_BROWSER_RECORDER_ALS_GESPRAECHSAUGE':['herkunft'],
        '031_BUEROKRATIE_AUS_SCHUTZWUENSCHEN':['schutz-wird-buerokratie','bauen-statt-simulieren'],
        '032_1337_ALS_RITUAL_UND_UEBERTREIBUNG':['gross-denken','humor-als-korrektur'],
        '033_WITZE_UND_RUNNING_GAGS':['humor-als-korrektur'],
        '034_BEGRIFFSERFINDUNGEN_GLOSSAR':['resonanz','quest-aus-folgen','gross-denken'],
    }
    for stem,title,body in HUBS:
        related=[]
        motifs=hub_queries.get(stem,[])
        for i,c in enumerate(selected):
            if motifs and not set(motifs)&set(c.motifs): continue
            related.append(c)
            if len(related)>=12: break
        extra=''
        if related:
            extra='\n\n## Belegte Spuren zum Weitergehen\n' + '\n'.join(f'- [[{c.filename[:-3]}|{c.title}]]' for c in related)
        links='\n\n## Nahe Leseknoten\n'
        # Fixed compact navigation.
        if stem=='000_START':
            links += '- [[001_WAHRHEITSGRENZE]]\n- [[003_WIE_ZU_LESEN]]\n- [[005_DER_GROSSE_ZUSAMMENHANG]]\n- [[035_OFFENE_FRAGEN]]'
        elif stem not in {'001_WAHRHEITSGRENZE','002_METHODIK','003_WIE_ZU_LESEN'}:
            links += '- [[000_START]]\n- [[006_ENTWICKLUNGSLINIEN]]\n- [[019_PROVENIENZ_ALS_WERT]]'
        else:
            links += '- [[000_START]]\n- [[036_QUELLENKARTE]]'
        content=f'''---\ntyp: leseknoten\nid: {yaml_q(stem)}\ntitel: {yaml_q(title)}\nerzeugung: {yaml_q('2026-08-01 zweite semantische Erzeugung')}\n---\n\n# {title}\n\n{textwrap.dedent(body).strip()}{extra}{links}\n'''
        (MD/f'{stem}.md').write_text(content,encoding='utf-8')


def write_spurs(selected: list[Candidate]) -> list[dict]:
    manifest=[]
    for idx,c in enumerate(selected,1):
        c.node_id=f'SPUR-{idx:04d}'
        c.slug=slugify(c.title)
        c.filename=f'SPUR_{idx:04d}__{c.slug}.md'
    for idx,c in enumerate(selected):
        neighbors=[]
        for j,score in c.semantic_neighbors or []:
            d=selected[j]
            neighbors.append(f'- [[{d.filename[:-3]}|{d.title}]] · Ähnlichkeit `{score:.3f}` · {d.category}')
        category_hub=CATEGORY_HUB[c.category]
        raw=c.clean_text.strip()
        # Preserve raw wording, but avoid enormous node bodies.
        if len(raw)>2400:
            raw=raw[:2400].rstrip()+' […]'
        # Raw source text may itself contain Obsidian links. Preserve it visibly but prevent
        # the validator and Obsidian from treating quoted source fragments as atlas links.
        raw=raw.replace('[[', '\\[\\[').replace(']]', '\\]\\]')
        tags=sorted(set([slugify(c.category,40)] + c.motifs + [slugify(t,40) for t in c.themes]))
        content=f'''---\ntyp: spur\nid: {yaml_q(c.node_id)}\ntitel: {yaml_q(c.title)}\nkategorie: {yaml_q(c.category)}\nstimme: {yaml_q(c.voice)}\nvertrauen: {yaml_q(c.confidence)}\nquelle: {yaml_q(c.source)}\nquellzeile: {c.source_line}\nquell_sha256: {yaml_q(c.source_sha256)}\nparser: {yaml_q(c.parser)}\nauswahlwert: {c.score:.3f}\ntags: {json.dumps(tags,ensure_ascii=False)}\n---\n\n# {c.title}\n\n## Daniels Spur oder Kontextpassage\n\n> {raw.replace(chr(10), chr(10)+'> ')}\n\n## Was darin steckt\n\n{interpretation(c)}\n\n## Warum dieser Knoten hängen bleibt\n\n{why_hang(c)}\n\n## Verbindungen\n\n- Themenraum: [[{category_hub}]]\n{chr(10).join(neighbors)}\n\n## Provenienz\n\n- **Stimmenklasse:** {c.voice}\n- **Quelle:** `{c.source}`\n- **Fundstelle:** ab Zeile {c.source_line}\n- **Quellhash:** `{c.source_sha256 or 'nicht verfügbar'}`\n- **Parser:** `{c.parser}`\n- **Vertrauen:** `{c.confidence}`\n'''
        path=MD/c.filename
        path.write_text(content,encoding='utf-8')
        manifest.append({
            'id':c.node_id,'file':f'md/{c.filename}','title':c.title,'category':c.category,
            'voice':c.voice,'source':c.source,'source_line':c.source_line,
            'source_sha256':c.source_sha256,'score':c.score,'motifs':c.motifs,
            'sha256':hashlib.sha256(content.encode()).hexdigest(),
            'neighbors':[selected[j].node_id for j,_ in (c.semantic_neighbors or [])],
        })
    return manifest


def validate(manifest: list[dict], stats: dict, selected: list[Candidate], vec: np.ndarray) -> dict:
    md_files=sorted(MD.glob('*.md'))
    stems={p.stem for p in md_files}
    broken=[]
    short=[]
    word_pages=[]
    for p in md_files:
        text=p.read_text(encoding='utf-8')
        if len(text)<240: short.append(p.name)
        if 'WORT_' in p.name: word_pages.append(p.name)
        for target in re.findall(r'(?<!\\)\[\[([^\]|#]+)',text):
            if target not in stems: broken.append((p.name,target))
    spur_files=[p for p in md_files if p.name.startswith('SPUR_')]
    voice_counts=Counter(c.voice for c in selected)
    direct=voice_counts.get('Daniel direkt',0)
    mixed=voice_counts.get('Daniel-nah, Mischquelle möglich',0)
    context=voice_counts.get('Kontextreflexion',0)
    result={
        'ok': len(md_files)==TOTAL_MD and len(spur_files)==SPUR_COUNT and not broken and not short and not word_pages,
        'markdown_files':len(md_files),'hub_files':len(md_files)-len(spur_files),'spur_files':len(spur_files),
        'broken_links':broken[:100],'broken_link_count':len(broken),'short_files':short,'word_page_files':word_pages,
        'direct_daniel_spurs':direct,'daniel_near_mixed_spurs':mixed,'context_reflections':context,
        'categories':dict(Counter(c.category for c in selected)),
        'voices':dict(Counter(c.voice for c in selected)),
        'sources_used':len(set(c.source for c in selected)),
        'candidate_stats':stats,
        'embedding_shape':list(vec.shape),
        'semantic_neighbor_edges':sum(len(c.semantic_neighbors or []) for c in selected),
    }
    if not result['ok']:
        raise RuntimeError('Validierung fehlgeschlagen: '+json.dumps(result,ensure_ascii=False)[:5000])
    return result


def write_data(manifest: list[dict], validation: dict, selected: list[Candidate]) -> None:
    (DATA/'MANIFEST.json').write_text(json.dumps({'title':'Daniels echter semantischer Bibliothekskörper','nodes':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
    (DATA/'VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
    source_counts=Counter((c.source,c.voice) for c in selected)
    with (DATA/'QUELLEN.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['quelle','stimmenklasse','verwendete_spuren'])
        for (source,voice),count in sorted(source_counts.items(),key=lambda x:(-x[1],x[0][0])):
            w.writerow([source,voice,count])
    with (DATA/'KNOTEN.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['id','datei','titel','kategorie','stimme','quelle','zeile','auswahlwert'])
        for m in manifest:
            w.writerow([m['id'],m['file'],m['title'],m['category'],m['voice'],m['source'],m['source_line'],m['score']])
    readme='''DANIELS ECHTER SEMANTISCHER BIBLIOTHEKSKÖRPER\n\n- 1.337 Markdown-Dateien exakt\n- 37 Leseknoten\n- 1.300 belegte semantische Spuren\n- Obsidian-interne Links geprüft\n- Quellen, Zeilen, Hashes und Stimmenklassen pro Spur\n- semantische Nachbarschaften aus Wortfolgen, Motiven und Themen\n\nEinstieg: md/000_START.md\nWahrheitsgrenze: md/001_WAHRHEITSGRENZE.md\nValidierung: daten/VALIDATION.json\n\nDer frühere Rohindex bleibt getrennt auf dem VPS erhalten und wird nicht als semantisch fertig ausgegeben.\n'''
    (OUT/'README.txt').write_text(readme,encoding='utf-8')


def zip_output() -> tuple[int,str]:
    if ZIP.exists(): ZIP.unlink()
    with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(OUT.parent))
    with zipfile.ZipFile(ZIP) as z:
        bad=z.testzip()
        if bad: raise RuntimeError(f'ZIP defekt bei {bad}')
    sha=hashlib.sha256(ZIP.read_bytes()).hexdigest()
    (ZIP.with_suffix(ZIP.suffix+'.sha256')).write_text(f'{sha}  {ZIP.name}\n',encoding='utf-8')
    return ZIP.stat().st_size,sha


def main() -> None:
    LOG.write_text('',encoding='utf-8')
    log('Zweite semantische Erzeugung beginnt.')
    if OUT.exists(): shutil.rmtree(OUT)
    MD.mkdir(parents=True); DATA.mkdir(parents=True)
    cands,stats=load_candidates()
    log(f'{len(cands)} sinnvolle Kandidaten nach Filterung aus {stats.get("readable_files")} lesbaren Quellenkörpern.')
    selected=select_balanced(cands,SPUR_COUNT)
    log('1.300 Spuren thematisch balanciert ausgewählt.')
    vec=assign_neighbors(selected)
    log('Semantische Nachbarschaften erzeugt.')
    write_hubs(selected)
    manifest=write_spurs(selected)
    validation=validate(manifest,stats,selected,vec)
    write_data(manifest,validation,selected)
    size,sha=zip_output()
    result={'zip':str(ZIP),'size':size,'sha256':sha,'validation':validation}
    (OUT/'ERGEBNIS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    log(f'FERTIG: {TOTAL_MD} Markdown-Dateien, ZIP {size} Bytes, SHA256 {sha}')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
