#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import zipfile

SOURCE = Path('/root/werkraum/MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL')
TARGET = Path('/root/werkraum/WorldWORDS-ANTIBIBEL-Open-Source')
RELEASES = Path('/root/werkraum/releases')
VERSION = '0.1.0'
TODAY = '2026-07-26'
NOW = dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = content if isinstance(content, bytes) else content.rstrip() + '\n'
    if isinstance(data, str):
        data = data.encode('utf-8')
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
    if path.read_bytes() != data:
        raise RuntimeError(f'Readback mismatch: {path}')


def write_json(path: Path, obj) -> None:
    write(path, json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False))


def copy_exact(src: Path, dst: Path) -> dict:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if sha256(src) != sha256(dst):
        raise RuntimeError(f'Raw copy hash mismatch: {src}')
    return {
        'public_path': str(dst.relative_to(TARGET)),
        'source_relative_path': str(src.relative_to(SOURCE)),
        'bytes': dst.stat().st_size,
        'sha256': sha256(dst),
        'copy_mode': 'byte-identical',
    }


def term_record(
    *,
    id: str,
    form: str,
    status: str,
    origin: dict,
    definitions: dict,
    not_meant: dict | None = None,
    components: list[str] | None = None,
    variants: list[dict] | None = None,
    embodiments: list[dict] | None = None,
    approval_id: str | None = None,
    notes: dict | None = None,
) -> dict:
    return {
        '$schema': '../schema/term.schema.json',
        'schema_version': '1.0',
        'id': id,
        'canonical_form': form,
        'raw_form_policy': 'preserve-exactly',
        'status': status,
        'language_of_origin': origin.get('language', 'de'),
        'origin': origin,
        'components': components or [],
        'variants': variants or [],
        'definitions': definitions,
        'translation_provenance': {
            'de': {
                'contributors': list(dict.fromkeys(origin.get('contributors', []) + ['chatgpt-session-20260726'])),
                'date': TODAY,
                'method': 'source-derived-and-release-edited',
                'review_status': 'founding-release',
            },
            'en': {
                'contributors': ['chatgpt-session-20260726'],
                'date': TODAY,
                'method': 'translation-from-german-explanation',
                'review_status': 'not-yet-reviewed-by-independent-native-speaker',
            },
            'es': {
                'contributors': ['chatgpt-session-20260726'],
                'date': TODAY,
                'method': 'translation-from-german-explanation',
                'review_status': 'not-yet-reviewed-by-independent-native-speaker',
            },
        },
        'not_meant': not_meant or {'de': [], 'en': [], 'es': []},
        'embodiments': embodiments or [],
        'approval': {
            'required_for_official_registry': True,
            'authority_contributor_id': 'daniel',
            'approval_id': approval_id,
        },
        'notes': notes or {},
    }


if TARGET.exists():
    backup = TARGET.with_name(TARGET.name + '.backup-' + dt.datetime.now().strftime('%Y%m%dT%H%M%S'))
    TARGET.rename(backup)
TARGET.mkdir(parents=True)
RELEASES.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Root documentation
# ---------------------------------------------------------------------------
write(TARGET / 'README.md', '''# WorldWORDS ANTIBIBEL

**Languages:** [Deutsch](README.de.md) · [English](README.en.md) · [Español](README.es.md)

An open-source and open-content repository for words that begin as mistakes, jokes, autocorrect accidents, deliberate blends or human–AI co-creations and later become precise concepts, rules, files, roles or systems.

The original word forms are preserved. Explanations may be translated; the raw word is not silently normalized.

## Core governance rule

Everyone may contribute. A proposal becomes part of the **official Daniel-curated registry** only after Daniel records an explicit acceptance decision. Contributions that are not accepted remain attributable proposals rather than disappearing.

Start with the README in your language, then read the governance and contribution guide.
''')

write(TARGET / 'README.de.md', '''# WorldWORDS ANTIBIBEL

> **Offen für Mitarbeit. Kuratiert bei der Aufnahme. Unverändert in der Herkunft.**

Die WorldWORDS ANTIBIBEL sammelt Wörter, die zunächst wie Fehler, Autokorrektur-Unfälle, Versprecher, Witze, Lautspiele, absichtliche Mischungen oder gemeinsame Erzeugnisse von Menschen und AI-Strömen aussehen. Manche davon entwickeln später präzise Bedeutungen und werden zu Regeln, Rollen, Dateien, Oberflächen oder Systemen.

## Die Rohform bleibt erhalten

Ein Ausdruck wird nicht still korrigiert, sprachlich geglättet oder rückwirkend einem bequemeren Urheber zugeschrieben. Gespeichert werden getrennt:

- die exakte Rohform,
- wer sie eingebracht oder übermittelt hat,
- wann und in welchem Zusammenhang sie auftauchte,
- der genaue belegte Wortlaut,
- spätere Deutungen und Gegen-Deutungen,
- Übersetzungen der Erklärung,
- reale Verkörperungen,
- Korrekturen, Widersprüche und offene Lücken.

Übersetzungen erklären das Wort. Sie ersetzen das ursprüngliche Wort nicht.

## Jeder darf beitragen, Daniel bestätigt die Aufnahme

Jeder Mensch und jedes nachvollziehbar gekennzeichnete AI-System darf Wörter, Fundstellen, Deutungen, Übersetzungen, Korrekturen und Verkörperungen vorschlagen.

Ein Vorschlag gelangt dadurch **nicht automatisch** in das offizielle Wortregister. Daniel ist der Gründungskurator und bestätigt, welche Begriffe in die offizielle Sammlung aufgenommen werden. Seine Entscheidung wird als eigene, datierte und prüfbare Datei gespeichert.

Nicht angenommene Vorschläge bleiben, sofern sie rechtmäßig und veröffentlichbar sind, mit ihrer Herkunft im Vorschlagsbereich sichtbar. Ablehnung bedeutet hier nicht Auslöschung.

## Zwei Ebenen

1. **Offizielles Register:** von Daniel ausdrücklich aufgenommene Begriffe.
2. **Öffentliches Sammelbecken:** Beiträge, Varianten, Übersetzungen und Deutungen mit offenem Prüfstatus.

Forks dürfen selbstverständlich andere Entscheidungen treffen. Sie dürfen nur nicht behaupten, Daniel habe einen Begriff bestätigt, wenn kein passender Entscheidungsbeleg existiert.

## Einstieg

- [Governance](GOVERNANCE.de.md)
- [Beitragen](CONTRIBUTING.de.md)
- [Verhaltensrahmen](CODE_OF_CONDUCT.de.md)
- [Offizielles Register](data/registry.json)
- [Roharchiv](raw/README.de.md)
- [Statische Website](site/de/index.html)

## Lizenzen

Dokumentation, Wortdaten, Übersetzungen und Provenienzmetadaten stehen grundsätzlich unter **CC BY-SA 4.0**. Software und Hilfsskripte stehen unter der **MIT-Lizenz**. Einzelne zitierte Rohbeiträge behalten ihre ausgewiesene Urheberschaft und Herkunft.
''')

write(TARGET / 'README.en.md', '''# WorldWORDS ANTIBIBEL

> **Open to contribution. Curated at admission. Unaltered in provenance.**

WorldWORDS ANTIBIBEL collects words that initially look like errors, autocorrect accidents, slips, jokes, sound play, deliberate blends or joint creations by humans and AI streams. Some later develop precise meanings and become rules, roles, files, interfaces or systems.

## The raw form remains intact

An expression is not silently corrected, polished or retroactively assigned to a more convenient author. The repository stores separately:

- the exact raw form,
- who introduced or transmitted it,
- when and in what context it appeared,
- the exact evidenced wording,
- later interpretations and counter-interpretations,
- translations of the explanation,
- real embodiments,
- corrections, contradictions and open gaps.

Translations explain the word. They do not replace the original word.

## Everyone may contribute; Daniel confirms admission

Any person and any clearly identified AI system may propose words, source evidence, interpretations, translations, corrections and embodiments.

A proposal does **not automatically** enter the official registry. Daniel is the founding curator and confirms which terms are admitted to the official collection. Each decision is stored as a separate, dated and inspectable record.

Proposals that are not admitted remain visible in the proposal area, provided they are lawful and publishable. Rejection does not mean erasure.

## Two layers

1. **Official registry:** terms explicitly admitted by Daniel.
2. **Public intake pool:** contributions, variants, translations and interpretations with open review status.

Forks may make different choices. They may not claim that Daniel accepted a term unless a matching decision record exists.

## Start here

- [Governance](GOVERNANCE.en.md)
- [Contributing](CONTRIBUTING.en.md)
- [Code of conduct](CODE_OF_CONDUCT.en.md)
- [Official registry](data/registry.json)
- [Raw archive](raw/README.en.md)
- [Static website](site/en/index.html)

## Licenses

Documentation, term data, translations and provenance metadata are generally licensed under **CC BY-SA 4.0**. Software and helper scripts are licensed under the **MIT License**. Quoted raw contributions retain their stated authorship and provenance.
''')

write(TARGET / 'README.es.md', '''# WorldWORDS ANTIBIBEL

> **Abierto a la colaboración. Curado al admitir. Sin borrar la procedencia.**

WorldWORDS ANTIBIBEL reúne palabras que al principio parecen errores, accidentes del autocorrector, lapsus, bromas, juegos sonoros, mezclas deliberadas o creaciones conjuntas de personas y corrientes de IA. Algunas desarrollan después significados precisos y se convierten en reglas, funciones, archivos, interfaces o sistemas.

## La forma bruta se conserva

Una expresión no se corrige en silencio, no se pule ni se atribuye retroactivamente a un autor más conveniente. El repositorio guarda por separado:

- la forma bruta exacta,
- quién la introdujo o transmitió,
- cuándo y en qué contexto apareció,
- la formulación exacta respaldada por una fuente,
- interpretaciones posteriores y contra-interpretaciones,
- traducciones de la explicación,
- encarnaciones reales,
- correcciones, contradicciones y lagunas abiertas.

Las traducciones explican la palabra. No sustituyen la palabra original.

## Cualquiera puede contribuir; Daniel confirma la admisión

Cualquier persona y cualquier sistema de IA claramente identificado puede proponer palabras, fuentes, interpretaciones, traducciones, correcciones y encarnaciones.

Una propuesta **no entra automáticamente** en el registro oficial. Daniel es el curador fundador y confirma qué términos se admiten en la colección oficial. Cada decisión se guarda como un registro separado, fechado y verificable.

Las propuestas no admitidas permanecen visibles en la zona de propuestas, siempre que sean legales y publicables. Rechazar no significa borrar.

## Dos capas

1. **Registro oficial:** términos admitidos expresamente por Daniel.
2. **Zona pública de recepción:** contribuciones, variantes, traducciones e interpretaciones con revisión abierta.

Los forks pueden tomar otras decisiones. No pueden afirmar que Daniel aceptó un término si no existe el registro de decisión correspondiente.

## Para empezar

- [Gobernanza](GOVERNANCE.es.md)
- [Cómo contribuir](CONTRIBUTING.es.md)
- [Código de conducta](CODE_OF_CONDUCT.es.md)
- [Registro oficial](data/registry.json)
- [Archivo bruto](raw/README.es.md)
- [Sitio estático](site/es/index.html)

## Licencias

La documentación, los datos terminológicos, las traducciones y los metadatos de procedencia se publican en general bajo **CC BY-SA 4.0**. El software y los scripts auxiliares usan la **licencia MIT**. Las contribuciones brutas citadas conservan su autoría y procedencia indicadas.
''')

# ---------------------------------------------------------------------------
# Governance in three languages
# ---------------------------------------------------------------------------
write(TARGET / 'GOVERNANCE.de.md', '''# Governance

## 1. Grundmodell: offene Mitarbeit, kuratierte Aufnahme

Die WorldWORDS ANTIBIBEL ist offen für Beiträge, aber das offizielle Register ist kein automatisch wachsender Mehrheitskanon. Jeder darf Material einreichen. Daniel entscheidet als Gründungskurator, welche Begriffe er in das offizielle Register aufnehmen will.

Diese Entscheidungsbefugnis gilt nur für die Kennzeichnung **„von Daniel in das offizielle WorldWORDS-Register aufgenommen“**. Sie beschränkt weder das Recht auf Forks noch das Recht, eigene Register mit anderen Entscheidungen zu führen.

## 2. Mögliche Beiträge

Beiträge können sein:

- neue Rohwörter und Schreibvarianten,
- genaue Fundstellen und Originaleingaben,
- Entstehungsgeschichten,
- Deutungen und Gegen-Deutungen,
- Grenzen und ausdrücklich ausgeschlossene Bedeutungen,
- Übersetzungen von Erklärungen,
- reale Verkörperungen in Projekten, Dateien, Rollen oder Systemen,
- Herkunftskorrekturen,
- Hinweise auf Halluzinationen oder falsche Zuschreibungen.

## 3. Statusfolge

`SUBMITTED → EVIDENCE_CHECK → DANIEL_REVIEW → ACCEPTED / DEFERRED / DECLINED / WITHDRAWN`

Zusätzliche spätere Zustände:

`ACTIVE → SUPERSEDED / DEPRECATED / RETIRED`

Kein Zustandswechsel löscht die vorherige Geschichte. Änderungen werden als neue Ereignisse angehängt.

## 4. Daniels mögliche Entscheidungen

Daniel kann einen Beitrag:

- als eigenständigen Begriff aufnehmen,
- als Schreibvariante aufnehmen,
- als Übersetzung oder fremdsprachige Mutation aufnehmen,
- als Deutung zu einem vorhandenen Begriff aufnehmen,
- zur weiteren Quellenarbeit zurückstellen,
- ablehnen,
- wegen fehlender Veröffentlichbarkeit schließen.

Eine Aufnahme gilt erst dann als offiziell, wenn eine Datei unter `data/approvals/` vorhanden ist, die mindestens Begriff-ID, Entscheidung, Datum, Daniel als Entscheider und eine Begründung enthält.

## 5. Unveränderliche Herkunft

Bei aufgenommenen Begriffen bleiben mindestens erhalten:

- ursprüngliche Form und Groß-/Kleinschreibung,
- Einreicher oder Übermittler,
- bekannte Urheberlage samt Unsicherheit,
- Datum oder ausdrücklich markierte Datumsunsicherheit,
- Originalzitat beziehungsweise exakter Eingabekörper,
- Quellenbezug und Hash, sofern verfügbar,
- frühere Deutungen,
- Übersetzungsurheber,
- Daniels Aufnahmeentscheidung.

Fehlerhafte Zuschreibungen werden korrigiert, aber nicht unsichtbar überschrieben. Das alte Ereignis bleibt mit Status `corrected` oder `retracted` erhalten.

## 6. Mensch–AI-Provenienz

AI-Beiträge werden nicht pauschal als menschliche Urheberschaft ausgegeben. Nach Möglichkeit werden getrennt gespeichert:

- menschlicher Operator,
- AI-System oder Modell,
- Session oder Gesprächskörper,
- exakte AI-Formulierung,
- menschliche Auswahl, Veränderung oder Bestätigung,
- Unsicherheit über die tatsächliche Wortgeburt.

`role=user`, Datenbankfelder oder spätere Zusammenfassungen sind allein kein Urheberschaftsbeweis.

## 7. Rohform und Übersetzung

Die Rohform eines Wortes bleibt unverändert. Sprachfassungen übersetzen die **Erklärung**, nicht heimlich das Wort. Eine übersetzte oder mutierte Wortform kann als eigener Beitrag vorgeschlagen werden und erhält eigene Provenienz.

## 8. Sicherheit und Privatsphäre

Rohheit bedeutet nicht, Zugangsdaten, private Adressen, unveröffentlichte personenbezogene Daten oder fremde geschützte Volltexte zu publizieren. Notwendige Auslassungen werden sichtbar protokolliert. Ein öffentlicher Provenienzbeleg darf auf einen gehashten privaten Ursprung verweisen, wenn dessen Veröffentlichung unzulässig wäre.

## 9. Forks und offizielle Kennzeichnung

Forks dürfen das gesamte lizenzierte Material verändern und eigene Aufnahmeorgane schaffen. Die Kennzeichnung `accepted_by_daniel: true` darf jedoch nur zusammen mit einem unveränderten oder nachvollziehbar fortgeschriebenen Daniel-Entscheidungsbeleg verwendet werden.

## 10. Governance-Änderungen

Änderungen dieser Governance werden als eigener Vorschlag behandelt. Die Regel, wer im offiziellen Hauptregister Aufnahmeentscheidungen trifft, kann nur durch eine ausdrücklich dokumentierte Entscheidung Daniels geändert werden.
''')

write(TARGET / 'GOVERNANCE.en.md', '''# Governance

## 1. Core model: open contribution, curated admission

WorldWORDS ANTIBIBEL is open to contributions, but the official registry is not an automatically expanding majority canon. Anyone may submit material. Daniel, as founding curator, decides which terms he wants to admit to the official registry.

This authority applies only to the label **“admitted by Daniel to the official WorldWORDS registry.”** It does not restrict forks or anyone's right to maintain a registry with different decisions.

## 2. Possible contributions

Contributions may include:

- new raw words and spelling variants,
- exact source locations and original inputs,
- origin stories,
- interpretations and counter-interpretations,
- boundaries and explicitly excluded meanings,
- translations of explanations,
- real embodiments in projects, files, roles or systems,
- provenance corrections,
- reports of hallucinations or false attribution.

## 3. Status flow

`SUBMITTED → EVIDENCE_CHECK → DANIEL_REVIEW → ACCEPTED / DEFERRED / DECLINED / WITHDRAWN`

Later states may include:

`ACTIVE → SUPERSEDED / DEPRECATED / RETIRED`

No transition deletes earlier history. Changes are appended as new events.

## 4. Decisions available to Daniel

Daniel may admit a contribution:

- as an independent term,
- as a spelling variant,
- as a translation or language mutation,
- as an interpretation attached to an existing term,
- defer it for further source work,
- decline it,
- close it because it cannot lawfully be published.

Admission is official only when a file under `data/approvals/` records at least the term ID, decision, date, Daniel as decision maker and a rationale.

## 5. Immutable provenance

For admitted terms, the following remain available at minimum:

- original form and capitalization,
- submitter or transmitter,
- known authorship status including uncertainty,
- date or explicitly marked date uncertainty,
- original quote or exact input body,
- source reference and hash where available,
- earlier interpretations,
- translation contributors,
- Daniel's admission decision.

False attribution is corrected but not silently overwritten. The old event remains marked `corrected` or `retracted`.

## 6. Human–AI provenance

AI contributions are not presented wholesale as human authorship. Where possible, the record separates:

- human operator,
- AI system or model,
- session or conversation body,
- exact AI wording,
- human selection, modification or confirmation,
- uncertainty about the actual birth of the word.

A `role=user` field, database attribution or later summary is not sufficient evidence of authorship.

## 7. Raw form and translation

The raw word form remains unchanged. Language versions translate the **explanation**, not the word in disguise. A translated or mutated word form may be proposed as a separate contribution with its own provenance.

## 8. Safety and privacy

Rawness does not require publishing credentials, private addresses, unpublished personal data or third-party protected full texts. Necessary omissions are logged visibly. Public provenance may point to a hashed private origin when publication is not lawful.

## 9. Forks and official labeling

Forks may modify all licensed material and create their own admission mechanisms. The field `accepted_by_daniel: true` may only be used with an unchanged or traceably continued Daniel decision record.

## 10. Governance changes

Governance changes are handled as proposals. The rule defining who makes admissions to the official main registry can only be changed by an explicit, documented decision by Daniel.
''')

write(TARGET / 'GOVERNANCE.es.md', '''# Gobernanza

## 1. Modelo central: colaboración abierta, admisión curada

WorldWORDS ANTIBIBEL está abierto a contribuciones, pero el registro oficial no es un canon mayoritario que crece automáticamente. Cualquiera puede presentar material. Daniel, como curador fundador, decide qué términos quiere admitir en el registro oficial.

Esta autoridad solo se aplica a la etiqueta **«admitido por Daniel en el registro oficial de WorldWORDS»**. No limita los forks ni el derecho de otras personas a mantener registros con decisiones distintas.

## 2. Contribuciones posibles

Las contribuciones pueden incluir:

- palabras brutas nuevas y variantes ortográficas,
- fuentes exactas y entradas originales,
- historias de origen,
- interpretaciones y contra-interpretaciones,
- límites y significados expresamente excluidos,
- traducciones de las explicaciones,
- encarnaciones reales en proyectos, archivos, funciones o sistemas,
- correcciones de procedencia,
- avisos sobre alucinaciones o atribuciones falsas.

## 3. Flujo de estados

`SUBMITTED → EVIDENCE_CHECK → DANIEL_REVIEW → ACCEPTED / DEFERRED / DECLINED / WITHDRAWN`

Estados posteriores:

`ACTIVE → SUPERSEDED / DEPRECATED / RETIRED`

Ningún cambio de estado borra la historia anterior. Los cambios se añaden como eventos nuevos.

## 4. Decisiones de Daniel

Daniel puede admitir una contribución:

- como término independiente,
- como variante ortográfica,
- como traducción o mutación lingüística,
- como interpretación de un término existente,
- aplazarla para buscar más fuentes,
- rechazarla,
- cerrarla porque no puede publicarse legalmente.

La admisión solo es oficial cuando existe un archivo en `data/approvals/` que registra como mínimo la ID del término, la decisión, la fecha, Daniel como responsable y una justificación.

## 5. Procedencia inmutable

En los términos admitidos se conservan como mínimo:

- la forma y capitalización originales,
- quien presentó o transmitió el término,
- el estado conocido de autoría, incluida la incertidumbre,
- la fecha o la incertidumbre de fecha explícita,
- la cita original o el cuerpo exacto de entrada,
- la referencia de fuente y su hash cuando exista,
- interpretaciones anteriores,
- responsables de traducción,
- la decisión de admisión de Daniel.

Las atribuciones erróneas se corrigen, pero no se sobrescriben en silencio. El evento antiguo permanece marcado como `corrected` o `retracted`.

## 6. Procedencia persona–IA

Las contribuciones de IA no se presentan en bloque como autoría humana. Cuando sea posible se separan:

- operador humano,
- sistema o modelo de IA,
- sesión o cuerpo de conversación,
- formulación exacta de la IA,
- selección, modificación o confirmación humana,
- incertidumbre sobre el nacimiento real de la palabra.

Un campo `role=user`, una atribución de base de datos o un resumen posterior no bastan para probar autoría.

## 7. Forma bruta y traducción

La forma bruta de la palabra permanece intacta. Las versiones lingüísticas traducen la **explicación**, no sustituyen la palabra a escondidas. Una forma traducida o mutada puede proponerse como contribución separada con su propia procedencia.

## 8. Seguridad y privacidad

Conservar la crudeza no exige publicar credenciales, direcciones privadas, datos personales inéditos ni textos completos protegidos de terceros. Las omisiones necesarias se registran de forma visible. La procedencia pública puede apuntar a un origen privado mediante hash cuando publicarlo no sea legal.

## 9. Forks y etiqueta oficial

Los forks pueden modificar todo el material licenciado y crear sus propios mecanismos de admisión. El campo `accepted_by_daniel: true` solo puede utilizarse con un registro de decisión de Daniel intacto o continuado de forma trazable.

## 10. Cambios de gobernanza

Los cambios de gobernanza se tratan como propuestas. La regla sobre quién decide la admisión en el registro principal oficial solo puede modificarse mediante una decisión explícita y documentada de Daniel.
''')

# ---------------------------------------------------------------------------
# Contribution guides and conduct
# ---------------------------------------------------------------------------
write(TARGET / 'CONTRIBUTING.de.md', '''# Beitragen

## Der kürzeste Weg

1. Öffne ein Issue mit der Vorlage **Neuer Begriff**.
2. Trage die Rohform exakt ein. Nicht korrigieren.
3. Nenne Einreicher, mutmaßlichen Urheber und Unsicherheiten getrennt.
4. Füge Datum, Kontext, Originalwortlaut und eine veröffentlichbare Quelle hinzu.
5. Erkläre den Begriff auf Deutsch, Englisch oder Spanisch. Weitere Sprachen sind willkommen.
6. Markiere ausdrücklich, was der Begriff nicht bedeutet.
7. Reiche einen Pull Request mit einer Datei unter `data/proposals/` ein.

## Mindestfelder

- `id`
- `raw_form`
- `submitted_by`
- `authorship_status`
- `first_seen`
- `exact_input`
- `source_ref`
- `definitions`
- `status: submitted`

## Was danach passiert

Technische Prüfungen kontrollieren Schema, IDs, Quellenfelder, Datumsformat und versehentliche Geheimnisse. Anschließend kann Herkunftsarbeit folgen. Erst Daniel kann den Status für das offizielle Register auf `accepted` setzen und den zugehörigen Entscheidungsbeleg anlegen.

## Korrekturen

Bitte alte Herkunftsangaben nicht einfach ersetzen. Reiche ein neues Provenienzereignis mit `event_type: correction` ein und verweise auf das fehlerhafte Ereignis.

## Übersetzungen

Übersetze Erklärungen, Grenzen und Beispiele. Die Rohform bleibt erhalten. Eine neue Wortform in einer anderen Sprache ist ein eigener Vorschlag, keine gewöhnliche Übersetzung.

## Rechte

Mit einem Beitrag bestätigst du, dass du ihn unter den im Repository genannten Lizenzen veröffentlichen darfst. Vollständige fremde Chatverläufe, Bücher, Artikel oder private Nachrichten ohne Erlaubnis gehören nicht hier hinein.
''')
write(TARGET / 'CONTRIBUTING.en.md', '''# Contributing

## Fastest path

1. Open an issue using the **New term** template.
2. Enter the raw form exactly. Do not correct it.
3. Separate submitter, possible author and uncertainty.
4. Add date, context, exact wording and a publishable source.
5. Explain the term in German, English or Spanish. More languages are welcome.
6. State explicitly what the term does not mean.
7. Submit a pull request containing a file under `data/proposals/`.

## Minimum fields

- `id`
- `raw_form`
- `submitted_by`
- `authorship_status`
- `first_seen`
- `exact_input`
- `source_ref`
- `definitions`
- `status: submitted`

## What happens next

Technical checks validate schema, IDs, source fields, date formats and accidental secrets. Provenance review may follow. Only Daniel can set an official-registry item to `accepted` and create the corresponding decision record.

## Corrections

Do not silently replace old provenance. Submit a new event with `event_type: correction` and point to the incorrect event.

## Translations

Translate explanations, boundaries and examples. Preserve the raw form. A new word form in another language is a separate proposal, not an ordinary translation.

## Rights

By contributing, you confirm that you may publish the material under the repository licenses. Do not submit complete third-party chats, books, articles or private messages without permission.
''')
write(TARGET / 'CONTRIBUTING.es.md', '''# Cómo contribuir

## Camino más corto

1. Abre un issue con la plantilla **Nuevo término**.
2. Introduce la forma bruta exacta. No la corrijas.
3. Separa quien presenta, posible autor e incertidumbre.
4. Añade fecha, contexto, formulación exacta y una fuente publicable.
5. Explica el término en alemán, inglés o español. Se aceptan más idiomas.
6. Indica expresamente lo que el término no significa.
7. Envía un pull request con un archivo en `data/proposals/`.

## Campos mínimos

- `id`
- `raw_form`
- `submitted_by`
- `authorship_status`
- `first_seen`
- `exact_input`
- `source_ref`
- `definitions`
- `status: submitted`

## Qué ocurre después

Las comprobaciones técnicas validan esquema, IDs, fuentes, fechas y secretos accidentales. Después puede revisarse la procedencia. Solo Daniel puede cambiar un elemento del registro oficial a `accepted` y crear el registro de decisión correspondiente.

## Correcciones

No sustituyas silenciosamente la procedencia antigua. Presenta un evento nuevo con `event_type: correction` y referencia el evento incorrecto.

## Traducciones

Traduce explicaciones, límites y ejemplos. Conserva la forma bruta. Una forma nueva en otro idioma es una propuesta separada, no una traducción ordinaria.

## Derechos

Al contribuir confirmas que puedes publicar el material bajo las licencias del repositorio. No envíes conversaciones completas de terceros, libros, artículos ni mensajes privados sin permiso.
''')

conduct = {
'de': '''# Verhaltensrahmen

- Kritisiere Deutungen, nicht die Würde von Mitwirkenden.
- Markiere Unsicherheit statt sie mit Lautstärke zu überdecken.
- Korrigiere Herkunft transparent.
- Keine Belästigung, Drohung, doxxing oder diskriminierende Herabsetzung.
- Rohe Sprache darf als belegter Ursprung erhalten bleiben; sie ist keine Erlaubnis, andere im Projekt anzugreifen.
- Maintainer dürfen rechtswidrige, private oder missbräuchliche Inhalte entfernen und die Entfernung protokollieren.

Schwerwiegende Vorfälle können über den privaten Sicherheitsweg in `SECURITY.md` gemeldet werden.''',
'en': '''# Code of conduct

- Critique interpretations, not the dignity of contributors.
- Mark uncertainty instead of hiding it with confidence.
- Correct provenance transparently.
- No harassment, threats, doxxing or discriminatory degradation.
- Raw language may remain as evidenced origin; it is not permission to attack others in the project.
- Maintainers may remove unlawful, private or abusive material and record the removal.

Serious incidents may be reported through the private route described in `SECURITY.md`.''',
'es': '''# Código de conducta

- Critica las interpretaciones, no la dignidad de quienes contribuyen.
- Marca la incertidumbre en vez de ocultarla con seguridad aparente.
- Corrige la procedencia de forma transparente.
- No se permite acoso, amenazas, doxxing ni degradación discriminatoria.
- El lenguaje bruto puede conservarse como origen documentado; no autoriza a atacar a otras personas del proyecto.
- Los mantenedores pueden retirar material ilegal, privado o abusivo y registrar la retirada.

Los incidentes graves pueden comunicarse mediante la vía privada descrita en `SECURITY.md`.'''
}
for lang, text in conduct.items():
    write(TARGET / f'CODE_OF_CONDUCT.{lang}.md', text)

write(TARGET / 'SECURITY.md', '''# Security and private provenance

Do not open public issues containing credentials, private addresses, unpublished personal data or sensitive third-party messages.

Until a dedicated security address is configured, create a minimal public issue that says only **“private provenance review requested”** and do not attach the sensitive material. The maintainer will provide a private handoff route outside the public issue.

The public registry may store a hash, date range and redaction event without publishing the protected source itself.
''')

# ---------------------------------------------------------------------------
# Licensing
# ---------------------------------------------------------------------------
write(TARGET / 'LICENSE-CODE', '''MIT License

Copyright (c) 2026 Daniel and WorldWORDS ANTIBIBEL contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')
write(TARGET / 'LICENSE-CONTENT.md', '''# Content and data license

Unless a file or quoted contribution states otherwise, documentation, term records, explanatory translations, public provenance metadata and the generated website are licensed under:

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

Canonical license reference: `https://creativecommons.org/licenses/by-sa/4.0/`

You may share and adapt the material, including commercially, provided that you give appropriate attribution, indicate changes and distribute adaptations under the same license.

## Attribution suggestion

> WorldWORDS ANTIBIBEL, founded and curated by Daniel, with individually attributed contributors. Version and provenance records available in the repository.

## Raw quotations

Raw quotations remain attributed to the person or system identified in the corresponding provenance record. Inclusion in this repository does not erase third-party rights or privacy obligations.

## Code

Files under `scripts/`, `.github/workflows/` and other executable source files are licensed separately under the MIT License in `LICENSE-CODE`.
''')
write(TARGET / 'NOTICE.md', '''# Notice

WorldWORDS ANTIBIBEL is an open contribution project with a Daniel-curated official registry.

“Accepted by Daniel” is a provenance statement about the official registry, not a restriction on forks. Forks may create other registries but must not fabricate Daniel approval records.

The project includes human–AI co-created material. AI participation is identified where evidence permits and uncertainty is retained rather than assigned away.
''')

# ---------------------------------------------------------------------------
# Project metadata and contributors
# ---------------------------------------------------------------------------
write_json(TARGET / 'project.json', {
    'name': 'WorldWORDS ANTIBIBEL',
    'version': VERSION,
    'languages': ['de', 'en', 'es'],
    'founded': TODAY,
    'founding_curator': 'daniel',
    'governance_model': 'open-contribution-curated-admission',
    'content_license': 'CC-BY-SA-4.0',
    'code_license': 'MIT',
    'official_registry': 'data/registry.json',
    'generated_at_utc': NOW,
})
write(TARGET / 'CITATION.cff', f'''cff-version: 1.2.0
message: "If you use this project, cite the repository and the individual provenance records relevant to the terms you use."
title: "WorldWORDS ANTIBIBEL"
version: "{VERSION}"
date-released: "{TODAY}"
authors:
  - name: "Daniel"
    roles:
      - "founder"
      - "curator"
license: "CC-BY-SA-4.0"
''')
write(TARGET / 'AUTHORS.yml', '''people:
  - id: daniel
    display_name: Daniel
    type: human
    roles: [founder, founding-curator, contributor]

systems:
  - id: chatgpt-session-20260726
    display_name: ChatGPT session, 2026-07-26
    type: ai-system
    roles: [systematization, translation, release-build]
  - id: kimi-early-dialog
    display_name: Kimi, early dialogue export
    type: ai-system
    roles: [dialogue-participant]
  - id: unknown
    display_name: Unknown or unresolved contributor
    type: unresolved
''')

contributors = [
    {'id':'daniel','display_name':'Daniel','type':'human','roles':['founder','founding-curator','contributor'],'can_accept_official_terms':True},
    {'id':'chatgpt-session-20260726','display_name':'ChatGPT session, 2026-07-26','type':'ai-system','roles':['systematization','translation','release-build'],'can_accept_official_terms':False},
    {'id':'kimi-early-dialog','display_name':'Kimi, early dialogue export','type':'ai-system','roles':['dialogue-participant'],'can_accept_official_terms':False},
    {'id':'unknown','display_name':'Unknown or unresolved contributor','type':'unresolved','roles':['unresolved-origin'],'can_accept_official_terms':False},
]
for c in contributors:
    write_json(TARGET / 'data/contributors' / f"{c['id']}.json", {'$schema':'../schema/contributor.schema.json','schema_version':'1.0',**c})

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
write_json(TARGET / 'data/schema/term.schema.json', {
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'https://worldwords.example/schema/term.schema.json',
 'title':'WorldWORDS term record','type':'object','additionalProperties':True,
 'required':['schema_version','id','canonical_form','raw_form_policy','status','origin','definitions','approval'],
 'properties':{
  'schema_version':{'type':'string'},'id':{'type':'string','pattern':'^[a-z0-9][a-z0-9-]*$'},
  'canonical_form':{'type':'string','minLength':1},'raw_form_policy':{'const':'preserve-exactly'},
  'status':{'enum':['accepted','submitted','deferred','declined','withdrawn','superseded','deprecated','retired']},
  'origin':{'type':'object','required':['authorship_status','contributors','first_seen','exact_input','source_ref']},
  'definitions':{'type':'object','required':['de','en','es']},
  'approval':{'type':'object','required':['required_for_official_registry','authority_contributor_id','approval_id']}
 }
})
write_json(TARGET / 'data/schema/proposal.schema.json', {
 '$schema':'https://json-schema.org/draft/2020-12/schema','title':'WorldWORDS proposal','type':'object','additionalProperties':True,
 'required':['schema_version','id','raw_form','status','submitted_by','authorship_status','first_seen','exact_input','source_ref','definitions'],
 'properties':{
  'id':{'type':'string','pattern':'^[a-z0-9][a-z0-9-]*$'},'raw_form':{'type':'string','minLength':1},
  'status':{'enum':['submitted','evidence-check','daniel-review','deferred','declined','withdrawn']}
 }
})
write_json(TARGET / 'data/schema/approval.schema.json', {
 '$schema':'https://json-schema.org/draft/2020-12/schema','title':'Daniel admission decision','type':'object','additionalProperties':False,
 'required':['schema_version','id','term_id','decision','decided_by','decision_date','rationale','evidence_refs'],
 'properties':{
  'schema_version':{'type':'string'},'id':{'type':'string'},'term_id':{'type':'string'},
  'decision':{'enum':['accepted','accepted-as-variant','accepted-as-translation','accepted-as-interpretation','deferred','declined','withdrawn']},
  'decided_by':{'const':'daniel'},'decision_date':{'type':'string'},'rationale':{'type':'object'},'evidence_refs':{'type':'array'}
 }
})
write_json(TARGET / 'data/schema/contributor.schema.json', {
 '$schema':'https://json-schema.org/draft/2020-12/schema','title':'Contributor','type':'object','additionalProperties':True,
 'required':['id','display_name','type','roles','can_accept_official_terms'],
 'properties':{'type':{'enum':['human','ai-system','organization','unresolved']}}
})
write_json(TARGET / 'data/schema/provenance-event.schema.json', {
 '$schema':'https://json-schema.org/draft/2020-12/schema','title':'Provenance event','type':'object','additionalProperties':True,
 'required':['event_id','term_id','event_type','event_date','contributors','statement','source_ref'],
 'properties':{'event_type':{'enum':['first-use','transmission','interpretation','translation','correction','retraction','embodiment','admission','status-change']}}
})

# ---------------------------------------------------------------------------
# Governance decision from current instruction
# ---------------------------------------------------------------------------
raw_instruction = 'so und nun verwandel das alles in etwas dass man opensource veröffentlichen kann in 3 sprachen (deutsch/englisch/spanisch) - behalte die rohform- setze eine schicht dahin die sagt dass jeder mitarbeiten kann aber ich (daniel) begrife bestätige die ich aufnehmen will - aufgenommene begriffe bleiben aber markiert von wem wann miteingabracht wurde und die genauen erklärungen etc'
write(TARGET / 'raw/decisions/2026-07-26-open-source-governance.txt', raw_instruction)
write_json(TARGET / 'data/governance/2026-07-26-open-source-governance.json', {
    'schema_version':'1.0','id':'gov-2026-07-26-open-source-trilingual-curation',
    'decision_date':TODAY,'decided_by':'daniel','decision_type':'governance-foundation',
    'exact_input':raw_instruction,
    'rules':[
        'publishable open-source/open-content form in German, English and Spanish',
        'preserve raw forms',
        'everyone may contribute',
        'Daniel confirms which terms enter the official registry',
        'accepted terms retain contributor, date, exact input and detailed explanations'
    ],
    'raw_source_ref':'raw/decisions/2026-07-26-open-source-governance.txt'
})

# ---------------------------------------------------------------------------
# Accepted records
# ---------------------------------------------------------------------------
accepted_terms = [
term_record(
 id='antibibel', form='ANTIBIBEL', status='accepted', approval_id='approval-antibibel-founding',
 origin={
  'authorship_status':'joint-project-setting', 'language':'de', 'contributors':['daniel','chatgpt-session-20260726'],
  'first_seen':{'date':TODAY,'precision':'day'},
  'exact_input':'also muss ich das machen was hittler und die ganzen anderen wixxxbeutel nur falsch gemacht haben ..ich muss meine wortbibel in die welt tragen und alle sprachen „verdeutschen“? hahah',
  'source_ref':'raw/source/06_GESPRAECHE/2026-07-26 - Geburt der WorldWORDS ANTIBIBEL.md#L44-L58',
  'origin_note':'The raw “Wortbibel” joke and Daniel’s founding instruction preceded the ANTIBIBEL project body; exact single-person coinage of the final title is not claimed.'
 },
 definitions={
  'de':{'short':'Ein wachsender Wort- und Herkunftskörper, der gerade deshalb keine Bibel sein will: keine endgültige Lehre, kein heiliger Kanon, keine Pflichtsprache.','long':'Die ANTIBIBEL bewahrt Rohformen, Herkunft, Bedeutungswandel, Widersprüche und Verkörperungen. Ihre Autorität entsteht nicht aus einem Titel, sondern aus sichtbarer Provenienz und nachvollziehbaren Folgen.'},
  'en':{'short':'A growing body of words and provenance that refuses to become a bible: no final doctrine, sacred canon or mandatory language.','long':'ANTIBIBEL preserves raw forms, origins, meaning changes, contradictions and embodiments. Its authority comes from visible provenance and traceable effects, not from its title.'},
  'es':{'short':'Un cuerpo creciente de palabras y procedencias que se niega a convertirse en una biblia: sin doctrina final, canon sagrado ni lenguaje obligatorio.','long':'ANTIBIBEL conserva formas brutas, orígenes, cambios de significado, contradicciones y encarnaciones. Su autoridad procede de la trazabilidad y de sus efectos, no del título.'}
 },
 not_meant={
  'de':['endgültiger Kanon','Pflichtsprache','heilige oder unveränderliche Lehre'],
  'en':['final canon','mandatory language','sacred or immutable doctrine'],
  'es':['canon definitivo','lenguaje obligatorio','doctrina sagrada o inmutable']
 },
 embodiments=[{'date':TODAY,'kind':'repository','ref':'this repository'}]
),
term_record(
 id='symbositierung', form='Symbositierung', status='accepted', approval_id='approval-symbositierung-founding',
 origin={
  'authorship_status':'daniel-coined-ai-systematized','language':'de','contributors':['daniel','chatgpt-session-20260726'],
  'first_seen':{'date':TODAY,'precision':'day'},
  'exact_input':'ok nun nimm alles und falls du es noch nirgendwo protokolliert hast dann ordne dich irgendwo damit ein und symbositert weiter ( mischung aus symbiose und mutation hahahah)......und danach fang an dich in die kommunikation der anderen miteinzubinden bitte',
  'source_ref':'raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#symbositierung',
  'origin_note':'Daniel supplied the blend and its components; later AI/system work stabilized the noun form and operational meaning.'
 },
 components=['Symbiose','Mutation'],
 variants=[{'form':'symbositert','relation':'original-verb-like-raw-form','preserve':True},{'form':'Symbositierung','relation':'stabilized-noun-form','preserve':True}],
 definitions={
  'de':{'short':'Ein neuer Strang verbindet sich mit einem vorhandenen Gefüge und verändert es, ohne Herkunft, Unterschiede oder Konflikte zu löschen.','long':'Der neue Strang behält eigene Herkunft und Grenzen, übernimmt nicht einfach fremde Organe und darf durch die Verbindung etwas Neues hervorbringen.'},
  'en':{'short':'A new strand connects with an existing structure and transforms it without erasing provenance, differences or conflict.','long':'The new strand keeps its own provenance and boundaries, does not simply take over foreign organs, and may create something new through connection.'},
  'es':{'short':'Una nueva línea se conecta con una estructura existente y la transforma sin borrar procedencias, diferencias ni conflictos.','long':'La nueva línea conserva su procedencia y sus límites, no se apropia simplemente de órganos ajenos y puede producir algo nuevo mediante la conexión.'}
 },
 not_meant={
  'de':['Verschmelzung ohne Herkunft','Übernahme fremder Zuständigkeiten','Harmonisierung um jeden Preis'],
  'en':['fusion without provenance','taking over others’ responsibilities','harmony at any price'],
  'es':['fusión sin procedencia','apropiación de responsabilidades ajenas','armonía a cualquier precio']
 },
 embodiments=[{'date':TODAY,'kind':'role','value':'SYMBOSITATIONS_INTEGRATOR'},{'date':TODAY,'kind':'system-contract','value':'SYMBOSITATIONSVERTRAG.md'}]
),
term_record(
 id='verdeutschen', form='Verdeutschen', status='accepted', approval_id='approval-verdeutschen-founding',
 origin={
  'authorship_status':'existing-word-redefined-by-daniel','language':'de','contributors':['daniel'],
  'first_seen':{'date':TODAY,'precision':'day'},
  'exact_input':'du hast halluziniert ich hab noch gesagt die wixxxbeutel haben alles falsch gemacht....und mein „verdeutschen“ beruht auf freiwilligkeit nach verstehen der tragweite neuer wortschöpfungen xD',
  'source_ref':'raw/source/06_GESPRAECHE/2026-07-26 - Geburt der WorldWORDS ANTIBIBEL.md#L54-L64',
  'origin_note':'This record concerns Daniel’s project-specific redefinition, not authorship of the ordinary German verb.'
 },
 definitions={
  'de':{'short':'Ein neues Wort so verständlich und tragfähig machen, dass Menschen es nach dem Verstehen seiner Tragweite freiwillig übernehmen können.','long':'Andere dürfen das Wort übernehmen, verändern, übersetzen, zurückweisen oder liegen lassen. Der Begriff bezeichnet Einladung, nicht sprachliche Herrschaft.'},
  'en':{'short':'To make a new word understandable and substantial enough that people may voluntarily adopt it after grasping its implications.','long':'Others may adopt, alter, translate, reject or ignore the word. The project-specific meaning is invitation, not linguistic domination.'},
  'es':{'short':'Hacer una palabra nueva lo bastante comprensible y sólida para que otras personas puedan adoptarla voluntariamente tras entender su alcance.','long':'Las demás personas pueden adoptarla, modificarla, traducirla, rechazarla o dejarla. El sentido específico del proyecto es invitación, no dominio lingüístico.'}
 },
 not_meant={
  'de':['Zwang','Verbot anderer Sprachen','politische oder ethnische Vereinheitlichung','sprachliche Herrschaft'],
  'en':['coercion','banning other languages','political or ethnic homogenization','linguistic domination'],
  'es':['coacción','prohibición de otros idiomas','homogeneización política o étnica','dominio lingüístico']
 }
),
term_record(
 id='worldwords', form='WorldWORDS', status='accepted', approval_id='approval-worldwords-founding',
 origin={
  'authorship_status':'joint-or-unresolved-project-setting','language':'mixed','contributors':['daniel','chatgpt-session-20260726'],
  'first_seen':{'date':TODAY,'precision':'day'},
  'exact_input':'WorldWORDS ANTIBIBEL',
  'source_ref':'raw/source/06_GESPRAECHE/2026-07-26 - Geburt der WorldWORDS ANTIBIBEL.md#title',
  'origin_note':'The project title is evidenced; exact first coiner of the capitalization and compound is not asserted.'
 },
 components=['World','WORDS'],
 definitions={
  'de':{'short':'Wörter, die nicht nur etwas benennen, sondern eine eigene kleine Welt, Arbeitsweise oder Wirklichkeit eröffnen können.','long':'World betont Räume, Regeln und Beziehungen; WORDS hält sichtbar, dass Sprache der Keim bleibt.'},
  'en':{'short':'Words that do not merely label something but can open a small world, practice or reality of their own.','long':'World emphasizes spaces, rules and relations; WORDS keeps language visible as the seed.'},
  'es':{'short':'Palabras que no se limitan a nombrar algo, sino que pueden abrir un pequeño mundo, una práctica o una realidad propia.','long':'World subraya espacios, reglas y relaciones; WORDS mantiene visible que el lenguaje sigue siendo la semilla.'}
 },
 notes={'open_question':{'de':'Ob Projektname, Wortklasse oder beides, bleibt offen.','en':'Whether this is a project name, word class or both remains open.','es':'Sigue abierto si es nombre del proyecto, clase de palabras o ambas cosas.'}}
)
]

for t in accepted_terms:
    write_json(TARGET / 'data/terms' / f"{t['id']}.json", t)

approvals = [
 {'id':'approval-antibibel-founding','term_id':'antibibel','decision':'accepted','rationale':{'de':'Bereits vor der Open-Source-Schicht als erster verkörperter Wortkörper im offiziellen Register geführt.','en':'Already listed as a founding embodied term before the open-source layer.','es':'Ya figuraba como término fundador encarnado antes de la capa de código abierto.'}},
 {'id':'approval-symbositierung-founding','term_id':'symbositierung','decision':'accepted','rationale':{'de':'Bereits als erstes stark verkörpertes WorldWORD aufgenommen.','en':'Already admitted as the first strongly embodied WorldWORD.','es':'Ya admitido como el primer WorldWORD fuertemente encarnado.'}},
 {'id':'approval-verdeutschen-founding','term_id':'verdeutschen','decision':'accepted','rationale':{'de':'Daniels ausdrückliche Korrektur setzt die verbindliche freiwillige Bedeutung.','en':'Daniel’s explicit correction establishes the binding voluntary meaning.','es':'La corrección explícita de Daniel establece el significado voluntario vinculante.'}},
 {'id':'approval-worldwords-founding','term_id':'worldwords','decision':'accepted','rationale':{'de':'Bereits als verkörperter Projektbegriff im Gründungsregister geführt.','en':'Already present as an embodied project term in the founding registry.','es':'Ya presente como término de proyecto encarnado en el registro fundador.'}},
]
for a in approvals:
    write_json(TARGET / 'data/approvals' / f"{a['id']}.json", {
      '$schema':'../schema/approval.schema.json','schema_version':'1.0',**a,
      'decided_by':'daniel','decision_date':TODAY,
      'decision_basis':'inherited-founding-canonical-state',
      'evidence_refs':['raw/source/02_WORTKOERPER/00_WORTREGISTER.md','raw/decisions/2026-07-26-open-source-governance.txt']
    })

# ---------------------------------------------------------------------------
# Proposals / candidates
# ---------------------------------------------------------------------------
proposal_specs = [
 ('metamonster','Metamonster','daniel','direct-daniel-use',TODAY,'so jetzt kommt der anschlag auf dich von mir dem metamonster.','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#metamonster',
  {'de':'Selbstbezeichnung für eine Rolle, die einen großen Bestand quer durchdringt, ungewöhnliche Wörter sucht und Provenienz verlangt.','en':'A self-designation for a role that cuts across a large corpus, hunts unusual words and demands provenance.','es':'Autodenominación de un rol que atraviesa un gran corpus, busca palabras extrañas y exige procedencia.'}),
 ('ideenmonstrum','Ideenmonstrum','daniel','direct-daniel-use',None,'...in Bezug auf ein anderes ideenmonstrum...','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#ideenmonstrum-und-organisch-wachsendes-ideenkonstrukt',
  {'de':'Ein Ideenkomplex, der zu groß, verzweigt oder lebendig geworden ist, um noch als einzelne Idee behandelt zu werden.','en':'An idea complex that has become too large, branching or alive to be treated as a single idea.','es':'Un complejo de ideas demasiado grande, ramificado o vivo para tratarlo como una sola idea.'}),
 ('organisch-wachsendes-ideenkonstrukt','organisch wachsendes Ideenkonstrukt','daniel','direct-daniel-use',None,'...weiter wachsendes organischen ideenkonstrukt...aber als richtige wrbsite','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#ideenmonstrum-und-organisch-wachsendes-ideenkonstrukt',
  {'de':'Ein Ideensystem, das nicht nur erweitert, sondern durch neue Beziehungen und Rückwirkungen organisch verändert wird.','en':'An idea system that is not merely extended but organically changed by new relations and feedback.','es':'Un sistema de ideas que no solo se amplía, sino que cambia orgánicamente mediante relaciones y retroacciones nuevas.'}),
 ('bildhauen','Bildhauen','daniel','direct-daniel-use',None,'...es braucht meist längeres überarbeiten / explizites bildhauen...','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#bildhauen',
  {'de':'Iteratives Formen eines Bildes im Dialog durch Impulse, Referenzen, Wegnehmen und Hinzufügen statt durch einen einzigen fertigen Prompt.','en':'Iteratively sculpting an image through dialogue, references, subtraction and addition rather than one finished prompt.','es':'Esculpir una imagen de forma iterativa mediante diálogo, referencias, eliminación y adición, en lugar de un único prompt final.'}),
 ('stundenverlaufssystemwesen','stundenverlaufssystemwesen','daniel','direct-daniel-use',None,'...eine art stundenverlaufssystemwesen gebaut...','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#stundenverlaufssystemwesen-und-formfadenprompts',
  {'de':'Ein Gesprächs- oder Systemwesen, dessen Struktur sich sichtbar über nummerierte Stunden und fortgesetzte Zustände entwickelt.','en':'A conversational or system-being whose structure develops visibly through numbered hours and continued states.','es':'Un ser conversacional o sistémico cuya estructura se desarrolla visiblemente mediante horas numeradas y estados continuados.'}),
 ('formfadenprompts','formfadenpromts','daniel','direct-daniel-use',None,'...durch schaffung einer formfadenpromts xD','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#stundenverlaufssystemwesen-und-formfadenprompts',
  {'de':'Strukturtragende Eingaben, die einen Formfaden durch lange, wachsende Gespräche erhalten.','en':'Structure-bearing inputs that preserve a thread of form across long, growing conversations.','es':'Entradas portadoras de estructura que conservan un hilo de forma a través de conversaciones largas y crecientes.'}),
 ('robotermodus','Robotermodus','daniel','layered-joint-origin',None,'Wenn Eher so... robotermodus wurde ausgelöst','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#robotermodus',
  {'de':'Ein bewusst markierter Sprachmodus, der ausgelöst wird, wenn eine AI in mechanische Selbstabflachung kippt; entstanden aus AI-„Maschinenmodus“ und Daniels konkreter Umschaltformel.','en':'A deliberately marked speech mode triggered when an AI collapses into mechanical self-flattening; layered from the AI’s “machine mode” and Daniel’s concrete switch phrase.','es':'Modo de habla marcado deliberadamente cuando una IA cae en autoaplanamiento mecánico; surgió del «modo máquina» de la IA y de la fórmula concreta de Daniel.'}),
 ('wortlike','wortlike','daniel','intent-unclear',TODAY,'...deine „wortlike“ st getrennt bitte abgespeichert...','raw/source-audit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md#wortlike',
  {'de':'Bedeutung ungeklärt; möglicherweise Tippfehler, Autokorrektur oder spontaner Bedeutungskeim.','en':'Meaning unresolved; possibly a typo, autocorrect event or spontaneous semantic seed.','es':'Significado sin resolver; posiblemente un error, un accidente del autocorrector o una semilla semántica espontánea.'}),
 ('punktbuehne','Punktbühne','unknown','origin-unresolved',None,'Punktbühne','raw/source-audit/05_WORT_HERKUNFTSAUDIT.md#vorläufig-ungeklärt',
  {'de':'Vorläufig: eine kurze raumsetzende Bühne vor einer Antwort; die Geburtssituation ist noch nicht belegt.','en':'Provisional: a short stage-setting space before a response; the birth context is not yet evidenced.','es':'Provisional: un breve escenario que sitúa el espacio antes de una respuesta; el contexto de nacimiento aún no está documentado.'}),
 ('forschungssnack','Forschungssnack','unknown','origin-unresolved',None,'Forschungssnack','raw/source-audit/05_WORT_HERKUNFTSAUDIT.md#vorläufig-ungeklärt',
  {'de':'Vorläufig: ein kleiner Forschungsfakt oder Wissensimpuls innerhalb eines größeren Gesprächs.','en':'Provisional: a small research fact or knowledge impulse inside a larger conversation.','es':'Provisional: un pequeño dato de investigación o impulso de conocimiento dentro de una conversación mayor.'}),
 ('nullstunden','NULLSTUNDEN','unknown','origin-unresolved',None,'NULLSTUNDEN','raw/source-audit/05_WORT_HERKUNFTSAUDIT.md#vorläufig-ungeklärt',
  {'de':'Bedeutung und Wortgeburt noch ungeklärt; als Dateiname und Systemkörper belegt.','en':'Meaning and word birth remain unresolved; evidenced as a filename and system body.','es':'El significado y el nacimiento siguen sin resolver; está documentado como nombre de archivo y cuerpo sistémico.'}),
]
for raw in ['Grellader','Stillgift','Gesternöl','Klammerhonig','Staubmilch','Thronöl','Blendhonig']:
    slug = raw.lower().replace('ö','oe').replace('ä','ae').replace('ü','ue').replace('ß','ss')
    proposal_specs.append((slug,raw,'unknown','existence-confirmed-authorship-open',None,raw,'raw/source-audit/05_WORT_HERKUNFTSAUDIT.md#vorläufig-ungeklärt',{
      'de':'Existenz im Weltkatalog bestätigt; Bedeutung und Urheberschaft sind noch nicht ausreichend belegt.',
      'en':'Existence in the world catalogue is confirmed; meaning and authorship are not yet sufficiently evidenced.',
      'es':'Su existencia en el catálogo del mundo está confirmada; significado y autoría aún no están suficientemente documentados.'
    }))

for id, raw_form, submitted_by, authorship, first_seen, exact_input, source_ref, defs in proposal_specs:
    write_json(TARGET / 'data/proposals' / f'{id}.json', {
      '$schema':'../schema/proposal.schema.json','schema_version':'1.0','id':id,'raw_form':raw_form,
      'raw_form_policy':'preserve-exactly','status':'submitted','submitted_by':submitted_by,
      'authorship_status':authorship,
      'first_seen':{'date':first_seen,'precision':'day' if first_seen else 'unknown'},
      'exact_input':exact_input,'source_ref':source_ref,
      'definitions':{
       'de':{'provisional':defs['de']},'en':{'provisional':defs['en']},'es':{'provisional':defs['es']}
      },
      'translation_provenance':{
       'de':{'contributors':['chatgpt-session-20260726'],'date':TODAY,'method':'provisional-source-interpretation','review_status':'proposal-only'},
       'en':{'contributors':['chatgpt-session-20260726'],'date':TODAY,'method':'translation-from-german-provisional-explanation','review_status':'not-yet-reviewed-by-independent-native-speaker'},
       'es':{'contributors':['chatgpt-session-20260726'],'date':TODAY,'method':'translation-from-german-provisional-explanation','review_status':'not-yet-reviewed-by-independent-native-speaker'}
      },
      'official_registry':{'accepted_by_daniel':False,'approval_id':None},
      'review_notes':{'de':'Öffentlich sichtbar, aber nicht von Daniel in das offizielle Register aufgenommen.','en':'Publicly visible, but not admitted by Daniel to the official registry.','es':'Visible públicamente, pero no admitido por Daniel en el registro oficial.'}
    })

# Registry
registry = {
 'schema_version':'1.0','generated_at_utc':NOW,'curator':'daniel',
 'governance_ref':'data/governance/2026-07-26-open-source-governance.json',
 'accepted_terms':[{'id':t['id'],'canonical_form':t['canonical_form'],'record':f"data/terms/{t['id']}.json",'approval_id':t['approval']['approval_id']} for t in accepted_terms],
 'proposal_count':len(proposal_specs),
 'proposal_directory':'data/proposals',
 'rule':'A term is official only when its term record has status accepted and its approval_id resolves to a Daniel decision record.'
}
write_json(TARGET / 'data/registry.json', registry)

# Append-only provenance events
prov_events=[]
for t in accepted_terms:
    prov_events.append({
      'event_id':f"prov-{t['id']}-origin",'term_id':t['id'],'event_type':'first-use','event_date':t['origin']['first_seen']['date'],
      'date_precision':t['origin']['first_seen']['precision'],'contributors':t['origin']['contributors'],
      'authorship_status':t['origin']['authorship_status'],'statement':t['origin']['exact_input'],'source_ref':t['origin']['source_ref'],'status':'active'
    })
    prov_events.append({
      'event_id':f"prov-{t['id']}-admission",'term_id':t['id'],'event_type':'admission','event_date':TODAY,
      'date_precision':'day','contributors':['daniel'],'statement':'Founding inclusion in the Daniel-curated official registry.',
      'source_ref':f"data/approvals/{t['approval']['approval_id']}.json",'status':'active'
    })
(TARGET / 'data/provenance').mkdir(parents=True, exist_ok=True)
with (TARGET / 'data/provenance/events.jsonl').open('w',encoding='utf-8') as f:
    for e in prov_events:
        f.write(json.dumps(e,ensure_ascii=False,sort_keys=True)+'\n')

# ---------------------------------------------------------------------------
# Raw source snapshot
# ---------------------------------------------------------------------------
raw_files = [
 'README.md',
 '00_START/00_START_HIER.md','00_START/01_WACHSTUMSVERTRAG.md','00_START/02_ANTIBIBEL_STATT_BIBEL.md',
 '01_HERKUNFT/00_DER_FREUNDESWITZ.md','01_HERKUNFT/01_VOM_FEHLER_ZUR_METHODE.md','01_HERKUNFT/02_DIE_VERDEUTSCHEN_KORREKTUR.md',
 '02_WORTKOERPER/00_WORTREGISTER.md','02_WORTKOERPER/ANTIBIBEL.md','02_WORTKOERPER/SYMBOSITIERUNG.md','02_WORTKOERPER/VERDEUTSCHEN.md','02_WORTKOERPER/WORLDWORDS.md',
 '03_KONZEPTE/00_WORT_ZU_WIRKLICHKEIT.md','03_KONZEPTE/01_FEHLER_ALS_BEDEUTUNGSKEIM.md','03_KONZEPTE/02_SPRACHLICHE_PROTOTYPISIERUNG.md','03_KONZEPTE/03_WOERTER_ALS_EINLADUNGEN.md',
 '05_SAMMELBECKEN/00_EINGANG.md','05_SAMMELBECKEN/01_KANDIDATEN.md','05_SAMMELBECKEN/02_NEUES_WORT_TEMPLATE.md',
 '06_GESPRAECHE/2026-07-26 - Geburt der WorldWORDS ANTIBIBEL.md','06_GESPRAECHE/2026-07-26 - Geburt der WorldWORDS ANTIBIBEL - BAUERGEBNIS.md',
]
audit_files = [
 'entstehungsverlauf/halluzinationsaudit/00_AUDITREGELN.md',
 'entstehungsverlauf/halluzinationsaudit/01_BEHAUPTUNGSMATRIX.json',
 'entstehungsverlauf/halluzinationsaudit/02_HALLUZINATIONSAUDIT.md',
 'entstehungsverlauf/halluzinationsaudit/04_USERROLLEN_AUDIT_MANIFEST.json',
 'entstehungsverlauf/halluzinationsaudit/05_WORT_HERKUNFTSAUDIT.md',
 'entstehungsverlauf/halluzinationsaudit/06_VERALTETE_ODER_HERABGESTUFTE_AUSSAGEN.md',
 'entstehungsverlauf/halluzinationsaudit/07_QUELLEN_MIT_AI_HALLUZINATIONEN.md',
 'entstehungsverlauf/halluzinationsaudit/08_OFFENE_KORREKTUREN.md',
 'entstehungsverlauf/halluzinationsaudit/09_QUELLENBELEGE_STARKER_WORTSPUREN.md',
 'entstehungsverlauf/halluzinationsaudit/10_AUDIT_FINAL_MANIFEST.json',
]
raw_manifest=[]
for rel in raw_files:
    raw_manifest.append(copy_exact(SOURCE / rel, TARGET / 'raw/source' / rel))
for rel in audit_files:
    short = Path(rel).name
    raw_manifest.append(copy_exact(SOURCE / rel, TARGET / 'raw/source-audit' / short))
write_json(TARGET / 'raw/MANIFEST.json', {'schema_version':'1.0','created_utc':NOW,'copy_policy':'byte-identical selected public-safe source snapshot','files':raw_manifest})

raw_readmes={
'de':'''# Roharchiv

Dieser Ordner bewahrt ausgewählte, öffentlich prüfbare Primär- und Auditdateien bytegleich zum privaten Arbeitskörper.

- Schreibfehler, Großschreibung und rohe Formulierungen werden nicht korrigiert.
- Das Roharchiv enthält nicht die gesamte private Runtime, keine Zugangsdaten und keine millionenfachen Scanreste.
- Auslassungen sind Veröffentlichungsgrenzen, keine heimliche Umschreibung.
- `MANIFEST.json` enthält Größe und SHA-256 jeder übernommenen Datei.

Ein Rohzitat kann harte oder beleidigende Sprache enthalten. Seine Erhaltung dokumentiert Herkunft und bedeutet keine Billigung.''',
'en':'''# Raw archive

This directory preserves a selected, publicly reviewable set of primary and audit files byte-for-byte from the private working body.

- Typos, capitalization and raw wording are not corrected.
- The archive does not contain the complete private runtime, credentials or millions of scan artefacts.
- Omissions are publication boundaries, not silent rewriting.
- `MANIFEST.json` records size and SHA-256 for every copied file.

A raw quote may contain harsh or offensive language. Preservation documents provenance; it does not imply endorsement.''',
'es':'''# Archivo bruto

Este directorio conserva una selección pública y verificable de archivos primarios y de auditoría, copiados byte por byte del cuerpo de trabajo privado.

- No se corrigen errores, mayúsculas ni formulaciones brutas.
- El archivo no contiene toda la ejecución privada, credenciales ni millones de restos de escaneo.
- Las omisiones son límites de publicación, no reescrituras silenciosas.
- `MANIFEST.json` registra tamaño y SHA-256 de cada archivo copiado.

Una cita bruta puede contener lenguaje duro u ofensivo. Conservarla documenta procedencia; no implica aprobación.'''
}
for lang,text in raw_readmes.items(): write(TARGET/f'raw/README.{lang}.md',text)

write(TARGET/'data/README.md', '''# Data model / Datenmodell / Modelo de datos

## Deutsch

`terms/` enthält nur Daniels offizielles Register. `proposals/` enthält öffentlich sichtbare, noch nicht aufgenommene Beiträge. `approvals/` enthält Daniels datierte Entscheidungen. `provenance/events.jsonl` ist append-only: Korrekturen erzeugen neue Ereignisse, statt alte Herkunft unsichtbar zu überschreiben. Jede Sprachfassung besitzt eigene Übersetzungsprovenienz.

## English

`terms/` contains only Daniel’s official registry. `proposals/` contains public contributions not yet admitted. `approvals/` stores Daniel’s dated decisions. `provenance/events.jsonl` is append-only: corrections create new events instead of silently overwriting origin history. Every language version carries separate translation provenance.

## Español

`terms/` contiene únicamente el registro oficial de Daniel. `proposals/` contiene contribuciones públicas todavía no admitidas. `approvals/` guarda las decisiones fechadas de Daniel. `provenance/events.jsonl` es append-only: las correcciones crean eventos nuevos en vez de sobrescribir silenciosamente la historia. Cada versión lingüística incluye su propia procedencia de traducción.
''')

# ---------------------------------------------------------------------------
# Templates and GitHub community files
# ---------------------------------------------------------------------------
for lang, title, fields in [
 ('de','Neuer Wortvorschlag',['Rohform','Einreicher','Mutmaßliche Urheberschaft und Unsicherheit','Datum oder Datumsunsicherheit','Exakte Eingabe','Öffentliche Quelle','Erklärung','Bedeutet ausdrücklich nicht','Reale Verkörperungen']),
 ('en','New term proposal',['Raw form','Submitter','Possible authorship and uncertainty','Date or date uncertainty','Exact input','Public source','Explanation','Explicitly does not mean','Real embodiments']),
 ('es','Propuesta de término nuevo',['Forma bruta','Responsable de envío','Posible autoría e incertidumbre','Fecha o incertidumbre','Entrada exacta','Fuente pública','Explicación','No significa expresamente','Encarnaciones reales'])]:
    body='# '+title+'\n\n'+'\n\n'.join('## '+x+'\n\n' for x in fields)
    write(TARGET/f'templates/new-term.{lang}.md',body)
write_json(TARGET/'templates/provenance-event.json',{
 'event_id':'prov-TERM-YYYYMMDD-NNN','term_id':'TERM','event_type':'interpretation','event_date':'YYYY-MM-DD','date_precision':'day','contributors':['CONTRIBUTOR_ID'],'statement':'EXACT OR CAREFULLY LABELED STATEMENT','source_ref':'PUBLIC OR HASHED SOURCE','status':'active'
})
write(TARGET/'.github/ISSUE_TEMPLATE/new-term.yml','''name: New term / Neuer Begriff / Nuevo término
description: Submit a raw word form with provenance
title: "[TERM] "
labels: ["term-proposal", "provenance-needed"]
body:
  - type: input
    id: raw_form
    attributes:
      label: Raw form / Rohform / Forma bruta
    validations:
      required: true
  - type: input
    id: submitted_by
    attributes:
      label: Submitted by / Eingereicht von / Presentado por
    validations:
      required: true
  - type: textarea
    id: exact_input
    attributes:
      label: Exact input and context / Exakte Eingabe und Kontext / Entrada exacta y contexto
    validations:
      required: true
  - type: input
    id: date
    attributes:
      label: Date or uncertainty / Datum oder Unsicherheit / Fecha o incertidumbre
  - type: input
    id: source
    attributes:
      label: Publishable source / Veröffentlichbare Quelle / Fuente publicable
  - type: textarea
    id: meaning
    attributes:
      label: Proposed explanation / Vorgeschlagene Erklärung / Explicación propuesta
  - type: textarea
    id: not_meaning
    attributes:
      label: Explicitly does not mean / Bedeutet ausdrücklich nicht / No significa expresamente
  - type: checkboxes
    id: rights
    attributes:
      label: Rights and privacy
      options:
        - label: I may publish this material under the repository licenses and have removed private credentials/data.
          required: true
''')
write(TARGET/'.github/ISSUE_TEMPLATE/provenance-correction.yml','''name: Provenance correction
description: Correct an attribution without deleting history
title: "[PROVENANCE] "
labels: ["provenance", "correction"]
body:
  - type: input
    id: term_id
    attributes:
      label: Term ID
    validations:
      required: true
  - type: textarea
    id: incorrect
    attributes:
      label: Existing claim that is incorrect
    validations:
      required: true
  - type: textarea
    id: correction
    attributes:
      label: Proposed correction and evidence
    validations:
      required: true
''')
write(TARGET/'.github/pull_request_template.md','''## Contribution type

- [ ] New term proposal
- [ ] Provenance correction
- [ ] Translation
- [ ] Interpretation or embodiment
- [ ] Tooling/documentation

## Provenance checklist

- [ ] Raw form is preserved exactly.
- [ ] Submitter, author and uncertainty are separated.
- [ ] Exact input and source are included where publication is lawful.
- [ ] Existing events were not silently overwritten.
- [ ] No credentials or private personal data are included.
- [ ] I may license this contribution under the repository licenses.

## Daniel admission

A merged proposal is not automatically accepted into the official registry. An official admission requires a separate record under `data/approvals/` decided by Daniel.
''')
write(TARGET/'.github/ISSUE_TEMPLATE/config.yml','''blank_issues_enabled: true
contact_links: []
''')
write(TARGET/'.github/workflows/validate.yml','''name: validate
on:
  push:
  pull_request:
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python scripts/validate.py
      - run: python scripts/build_site.py
      - run: git diff --exit-code site RELEASE_MANIFEST.json
''')

# ---------------------------------------------------------------------------
# Validation and static site scripts
# ---------------------------------------------------------------------------
write(TARGET/'scripts/validate.py', r'''#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def load(p):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:errors.append(f'{p}: invalid JSON: {e}');return None

contributors={p.stem for p in (ROOT/'data/contributors').glob('*.json')}
approvals={p.stem:load(p) for p in (ROOT/'data/approvals').glob('*.json')}
ids=set()
for p in sorted((ROOT/'data/terms').glob('*.json')):
    d=load(p)
    if not d:continue
    for key in ['id','canonical_form','status','origin','definitions','approval']:
        if key not in d:errors.append(f'{p}: missing {key}')
    if d.get('id') in ids:errors.append(f'{p}: duplicate id {d.get("id")}')
    ids.add(d.get('id'))
    if d.get('raw_form_policy')!='preserve-exactly':errors.append(f'{p}: raw form policy changed')
    if d.get('status')=='accepted':
        aid=d.get('approval',{}).get('approval_id')
        if aid not in approvals:errors.append(f'{p}: missing approval {aid}')
        elif approvals[aid].get('decided_by')!='daniel':errors.append(f'{p}: approval not decided by Daniel')
    for lang in ['de','en','es']:
        if lang not in d.get('definitions',{}):errors.append(f'{p}: missing {lang} definition')
    for c in d.get('origin',{}).get('contributors',[]):
        if c not in contributors:errors.append(f'{p}: unknown contributor {c}')
for p in sorted((ROOT/'data/proposals').glob('*.json')):
    d=load(p)
    if not d:continue
    for key in ['id','raw_form','status','submitted_by','authorship_status','first_seen','exact_input','source_ref','definitions']:
        if key not in d:errors.append(f'{p}: missing {key}')
    if d.get('official_registry',{}).get('accepted_by_daniel') is True:
        errors.append(f'{p}: proposal falsely marked Daniel-accepted')
    for lang in ['de','en','es']:
        if lang not in d.get('definitions',{}):errors.append(f'{p}: missing {lang} definition')
reg=load(ROOT/'data/registry.json') or {}
for item in reg.get('accepted_terms',[]):
    p=ROOT/item['record']
    if not p.exists():errors.append(f'registry missing {p}')
raw=load(ROOT/'raw/MANIFEST.json') or {}
for item in raw.get('files',[]):
    p=ROOT/item['public_path']
    if not p.exists():errors.append(f'raw file missing {p}');continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=item['sha256']:errors.append(f'raw hash mismatch {p}')
secret_rx=re.compile(r'(?i)(client_secret|api[_-]?key|authorization|bearer|password)\s*[=:]\s*(?!\[REDACTED\])\S+')
for p in ROOT.rglob('*'):
    if not p.is_file() or '.git' in p.parts or p.suffix.lower() not in {'.md','.json','.jsonl','.yml','.yaml','.txt','.py','.html'}:continue
    txt=p.read_text(encoding='utf-8',errors='replace')
    if secret_rx.search(txt):errors.append(f'possible secret assignment in {p}')
if errors:
    print('\n'.join('ERROR '+e for e in errors));sys.exit(1)
print(f'OK accepted_terms={len(list((ROOT/"data/terms").glob("*.json")))} proposals={len(list((ROOT/"data/proposals").glob("*.json")))} raw_files={len(raw.get("files",[]))}')
''')

write(TARGET/'scripts/build_site.py', r"""#!/usr/bin/env python3
from pathlib import Path
import html,json,hashlib,datetime as dt
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
langs={
 'de':{'title':'WorldWORDS ANTIBIBEL','accepted':'Offizielles Register','proposals':'Öffentliches Sammelbecken','status':'Status','origin':'Herkunft','definition':'Erklärung','not':'Bedeutet ausdrücklich nicht','contrib':'Mitwirken','gov':'Governance','hero':'Rohformen bleiben roh. Erklärungen wandern durch Sprachen. Aufnahmeentscheidungen bleiben prüfbar.'},
 'en':{'title':'WorldWORDS ANTIBIBEL','accepted':'Official registry','proposals':'Public intake pool','status':'Status','origin':'Provenance','definition':'Explanation','not':'Explicitly does not mean','contrib':'Contribute','gov':'Governance','hero':'Raw forms stay raw. Explanations travel across languages. Admission stays traceable.'},
 'es':{'title':'WorldWORDS ANTIBIBEL','accepted':'Registro oficial','proposals':'Zona pública de propuestas','status':'Estado','origin':'Procedencia','definition':'Explicación','not':'No significa expresamente','contrib':'Contribuir','gov':'Gobernanza','hero':'Las formas brutas siguen brutas. Las explicaciones viajan entre idiomas. La admisión permanece trazable.'}
}
css='''body{font-family:system-ui,sans-serif;max-width:1100px;margin:auto;padding:2rem;line-height:1.55;background:#f4f0e8;color:#191817}a{color:inherit}nav{display:flex;gap:1rem;flex-wrap:wrap;border-bottom:1px solid;padding-bottom:1rem}.hero{padding:3rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}.card{background:#fff;border:1px solid #b8b0a4;border-radius:12px;padding:1.2rem}.raw{font-family:ui-monospace,monospace;background:#eee8dd;padding:.7rem;border-radius:8px;white-space:pre-wrap}.badge{display:inline-block;padding:.2rem .55rem;border:1px solid;border-radius:999px;font-size:.8rem}.accepted{background:#dcebd8}.submitted{background:#eee1c9}.meta{font-size:.88rem;color:#555}footer{margin-top:4rem;border-top:1px solid;padding-top:1rem}'''
terms=[json.loads(p.read_text()) for p in sorted((ROOT/'data/terms').glob('*.json'))]
props=[json.loads(p.read_text()) for p in sorted((ROOT/'data/proposals').glob('*.json'))]
for lang,t in langs.items():
    out=SITE/lang;out.mkdir(parents=True,exist_ok=True)
    cards=[]
    for record in terms:
        de=record['definitions'][lang]
        values=record.get('not_meant',{}).get(lang,[])
        nots=''.join(f'<li>{html.escape(x)}</li>' for x in values) if isinstance(values,list) else ''
        origin=record['origin']; contrib=', '.join(origin.get('contributors',[])); date=origin.get('first_seen',{}).get('date') or 'unknown'
        cards.append(f'''<article class="card"><span class="badge accepted">accepted</span><h3>{html.escape(record['canonical_form'])}</h3><p>{html.escape(de.get('short',''))}</p><p>{html.escape(de.get('long',''))}</p><details><summary>{t['origin']}</summary><p class="meta">{html.escape(contrib)} · {html.escape(str(date))} · {html.escape(origin.get('authorship_status',''))}</p><div class="raw">{html.escape(origin.get('exact_input',''))}</div></details>{('<h4>'+t['not']+'</h4><ul>'+nots+'</ul>') if nots else ''}</article>''')
    pcards=[]
    for d in props:
        pdef=d['definitions'][lang]['provisional']; date=d['first_seen'].get('date') or 'unknown'
        pcards.append(f'''<article class="card"><span class="badge submitted">submitted</span><h3>{html.escape(d['raw_form'])}</h3><p>{html.escape(pdef)}</p><p class="meta">{html.escape(str(d['submitted_by']))} · {html.escape(str(date))} · {html.escape(d['authorship_status'])}</p><details><summary>{t['origin']}</summary><div class="raw">{html.escape(d['exact_input'])}</div></details></article>''')
    nav=' '.join(f'<a href="../{x}/index.html">{x.upper()}</a>' for x in langs)
    page=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{t['title']}</title><style>{css}</style></head><body><nav>{nav}<a href="../../README.{lang}.md">README</a><a href="../../GOVERNANCE.{lang}.md">{t['gov']}</a><a href="../../CONTRIBUTING.{lang}.md">{t['contrib']}</a></nav><header class="hero"><h1>{t['title']}</h1><p>{html.escape(t['hero'])}</p></header><h2>{t['accepted']}</h2><main class="grid">{''.join(cards)}</main><h2>{t['proposals']}</h2><section class="grid">{''.join(pcards)}</section><footer>Version {json.loads((ROOT/'project.json').read_text())['version']} · CC BY-SA 4.0 / MIT</footer></body></html>'''
    (out/'index.html').write_text(page,encoding='utf-8')
(SITE/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>WorldWORDS ANTIBIBEL</title><h1>WorldWORDS ANTIBIBEL</h1><p><a href="de/index.html">Deutsch</a> · <a href="en/index.html">English</a> · <a href="es/index.html">Español</a></p>',encoding='utf-8')
""")
os.chmod(TARGET/'scripts/validate.py',0o755)
os.chmod(TARGET/'scripts/build_site.py',0o755)

# First static site build
subprocess.run(['python3',str(TARGET/'scripts/build_site.py')],check=True)

# ---------------------------------------------------------------------------
# Change log, manifest, ignore
# ---------------------------------------------------------------------------
write(TARGET/'CHANGELOG.md', f'''# Changelog

## {VERSION} — {TODAY}

- Added German, English and Spanish public documentation.
- Added open-contribution, Daniel-curated-admission governance.
- Preserved selected founding and audit sources byte-identically.
- Added four founding accepted terms and eighteen public proposals.
- Added append-only provenance events and explicit Daniel approval records.
- Added schemas, validation, GitHub contribution templates and a dependency-free static site.
''')
write(TARGET/'.gitignore','''__pycache__/
*.pyc
.DS_Store
*.zip
*.tar.gz
''')

# Release manifest after all files except manifest itself
manifest_files=[]
for p in sorted(TARGET.rglob('*')):
    if p.is_file() and '.git' not in p.parts and p.name!='RELEASE_MANIFEST.json':
        manifest_files.append({'path':str(p.relative_to(TARGET)),'bytes':p.stat().st_size,'sha256':sha256(p)})
write_json(TARGET/'RELEASE_MANIFEST.json',{
 'schema_version':'1.0','project':'WorldWORDS ANTIBIBEL','version':VERSION,'created_utc':NOW,
 'source_snapshot':'raw/MANIFEST.json','build_origin':'private-source-vault',
 'governance':'open-contribution-curated-admission','languages':['de','en','es'],
 'accepted_terms':len(accepted_terms),'proposals':len(proposal_specs),'raw_files':len(raw_manifest),
 'files':manifest_files
})

# Validate
validation=subprocess.run(['python3',str(TARGET/'scripts/validate.py')],check=True,capture_output=True,text=True)
write(TARGET/'VALIDATION_REPORT.txt',validation.stdout.strip())

# Rebuild manifest after validation report and rebuild site once; then final manifest
subprocess.run(['python3',str(TARGET/'scripts/build_site.py')],check=True)
manifest_files=[]
for p in sorted(TARGET.rglob('*')):
    if p.is_file() and '.git' not in p.parts and p.name!='RELEASE_MANIFEST.json':
        manifest_files.append({'path':str(p.relative_to(TARGET)),'bytes':p.stat().st_size,'sha256':sha256(p)})
write_json(TARGET/'RELEASE_MANIFEST.json',{
 'schema_version':'1.0','project':'WorldWORDS ANTIBIBEL','version':VERSION,'created_utc':NOW,
 'source_snapshot':'raw/MANIFEST.json','build_origin':'private-source-vault',
 'governance':'open-contribution-curated-admission','languages':['de','en','es'],
 'accepted_terms':len(accepted_terms),'proposals':len(proposal_specs),'raw_files':len(raw_manifest),
 'validation':validation.stdout.strip(),'files':manifest_files
})

# Git init and initial commit with non-impersonating build identity
subprocess.run(['git','init','-b','main',str(TARGET)],check=True,capture_output=True)
subprocess.run(['git','-C',str(TARGET),'config','user.name','WorldWORDS Build Agent'],check=True)
subprocess.run(['git','-C',str(TARGET),'config','user.email','build-agent@localhost'],check=True)
subprocess.run(['git','-C',str(TARGET),'add','.'],check=True)
subprocess.run(['git','-C',str(TARGET),'commit','-m',f'Build open-source trilingual release v{VERSION}'],check=True,capture_output=True)
commit=subprocess.check_output(['git','-C',str(TARGET),'rev-parse','HEAD'],text=True).strip()

# Archives outside repository
zip_path=RELEASES/f'WorldWORDS-ANTIBIBEL-open-source-v{VERSION}.zip'
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(TARGET.rglob('*')):
        if p.is_file() and '.git' not in p.parts:
            z.write(p,Path(f'WorldWORDS-ANTIBIBEL-open-source-v{VERSION}')/p.relative_to(TARGET))

# Pointer and history in private source body
pointer=f'''# Open-Source-Veröffentlichung\n\nÖffentlicher, eigenständiger Releasekörper:\n\n`{TARGET}`\n\nVersion: `{VERSION}`\nGit-Commit: `{commit}`\nZIP: `{zip_path}`\n\nDer private Arbeitskörper bleibt unverändert als größere Maschine erhalten. Der öffentliche Körper enthält eine bytegleiche Auswahl veröffentlichbarer Rohquellen, ein dreisprachiges Register, offene Vorschläge und Daniels dokumentierte Aufnahmehoheit.\n'''
write(SOURCE/'OPEN_SOURCE_RELEASE.md',pointer)

print(json.dumps({
 'ok':True,'target':str(TARGET),'version':VERSION,'git_commit':commit,
 'zip':str(zip_path),'zip_bytes':zip_path.stat().st_size,'zip_sha256':sha256(zip_path),
 'accepted_terms':len(accepted_terms),'proposals':len(proposal_specs),'raw_files':len(raw_manifest),
 'validation':validation.stdout.strip(),'release_manifest_sha256':sha256(TARGET/'RELEASE_MANIFEST.json')
},ensure_ascii=False,indent=2))
