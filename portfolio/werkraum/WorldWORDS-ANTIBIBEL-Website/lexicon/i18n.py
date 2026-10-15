SUPPORTED = ("de", "en", "es")

TEXT = {
    "de": {
        "lang_name": "Deutsch",
        "skip": "Direkt zum Inhalt",
        "nav": {
            "home": "Wunderkammer", "explore": "Wörter erkunden", "collections": "Wege",
            "people": "Mitwirkende", "submit": "Wort einreichen", "dashboard": "Mein Bereich",
            "curation": "Daniel-Inbox", "login": "Anmelden", "register": "Konto öffnen", "logout": "Abmelden",
        },
        "hero": {
            "eyebrow": "Eine offene, kuratierte Wortwelt", "title": "Wörter dürfen Welten werden.",
            "body": "Rohformen bleiben roh. Menschen dürfen beitragen, widersprechen und weiterdenken. Daniel entscheidet sichtbar, welche Begriffe in sein offizielles Register einziehen.",
            "explore": "In die Sammlung", "submit": "Ein Wort hineinwerfen", "random": "Überrasch mich",
        },
        "sections": {
            "featured": "Aufgenommene Fundstücke", "new": "Neu im Sammelbecken", "active": "Gespräche in Bewegung",
            "paths": "Wege durch die Wunderkammer", "classes": "Nach Wortarten", "provenance": "Herkunftsspur",
            "discussion": "Diskussion", "relations": "Verwandte Fundstücke", "contribute": "Etwas ergänzen",
            "decision": "Daniels Entscheidung", "raw": "Unveränderte Rohform", "origin": "Herkunft",
            "definitions": "Erklärungen", "not_meant": "Bedeutet ausdrücklich nicht", "variants": "Varianten",
            "embodiments": "Verkörperungen", "timeline": "Zeitspur",
        },
        "actions": {
            "read": "Fundstück öffnen", "filter": "Filtern", "clear": "Leeren", "search": "Suchen",
            "reply": "Antworten", "comment": "Beitrag senden", "follow": "Gespräch folgen", "unfollow": "Nicht mehr folgen",
            "suggest": "Ergänzung vorschlagen", "report": "Melden", "save": "Speichern", "decide": "Entscheidung festhalten",
            "export": "Öffentlichen Stand exportieren", "mark_read": "Als gelesen markieren", "load_more": "Mehr zeigen",
            "copy": "Link kopieren", "edit": "Bearbeiten", "close": "Schließen", "send": "Senden",
        },
        "status": {
            "submitted": "Eingereicht", "under_review": "In Prüfung", "accepted": "Aufgenommen",
            "deferred": "Zurückgestellt", "rejected": "Nicht aufgenommen", "merged": "Als Variante verbunden", "archived": "Archiviert",
        },
        "forms": {
            "required": "Pflichtfeld", "optional": "freiwillig",
            "raw_help": "Genau so, wie das Wort aufgetaucht ist. Diese Rohform wird später nicht still korrigiert.",
            "exact_help": "Der ursprüngliche Satz oder Zusammenhang. Tippfehler dürfen bleiben.",
            "public_help": "Die Einreichung erhält nach dem Absenden eine öffentliche Begriffsseite und kann sofort diskutiert werden.",
            "consent": "Ich darf diesen Inhalt unter CC BY-SA 4.0 veröffentlichen und habe keine privaten Daten fremder Personen eingefügt.",
        },
        "empty": {
            "terms": "Hier liegt noch kein Fundstück. Ein Archiv beginnt bekanntlich mit dem ersten menschlichen Kontrollverlust.",
            "discussion": "Noch kein Beitrag. Die Stille ist hier kein Endzustand.",
            "notifications": "Nichts Neues. Das Internet hat kurz aufgehört, an dir zu ziehen.",
        },
        "footer": {
            "about": "Über die ANTIBIBEL", "governance": "Aufnahme & Governance", "privacy": "Datenschutz",
            "conduct": "Gesprächsregeln", "opensource": "Offener Datenkörper", "contact": "Kontakt",
            "line": "Offen für Beiträge. Kuratiert durch Daniel. Jede Spur bleibt benennbar.",
            "license": "Code: MIT · Inhalte und Daten: CC BY-SA 4.0", "credit": "Daniel und benannte Mitwirkende",
        },
        "auth": {
            "login_title": "Wieder hinein", "register_title": "Ein Konto für eigene Spuren", "username": "Benutzername",
            "password": "Passwort", "email": "E-Mail", "display_name": "Anzeigename",
            "login_body": "Dein Konto verbindet Einreichungen, Diskussionen, Ergänzungen und Benachrichtigungen mit dir.",
            "register_body": "Der Anzeigename wird an öffentlichen Beiträgen gezeigt. Deine E-Mail bleibt privat.",
            "login_art": "Jeder Beitrag behält eine Spur.", "register_art": "Ein Konto, viele zuordenbare Spuren.",
            "change_password": "Passwort ändern", "password_changed": "Passwort geändert.",
        },
        "curation": {
            "title": "Daniel-Inbox", "pending_terms": "Offene Begriffe", "contributions": "Ergänzungsvorschläge",
            "reports": "Meldungen", "decision_history": "Entscheidungsgeschichte", "none": "Nichts wartet. Verdächtig friedlich.",
            "warning": "Eine Aufnahme macht den Begriff offiziell, löscht aber keine frühere Diskussion oder Herkunft.",
        },
        "authorship": {
            "claimed-by-submitter": "Vom Einreicher beansprucht", "direct-daniel-use": "Direkte Verwendung durch Daniel",
            "daniel-coined-ai-systematized": "Daniel geprägt, AI systematisiert", "joint-project-setting": "Gemeinsame Projektsetzung",
            "joint-or-unresolved-project-setting": "Gemeinsam oder ungeklärt", "layered-joint-origin": "Mehrschichtige gemeinsame Herkunft",
            "existing-word-redefined-by-daniel": "Bestehendes Wort von Daniel neu bestimmt",
            "existence-confirmed-authorship-open": "Existenz belegt, Urheberschaft offen", "origin-unresolved": "Herkunft ungeklärt",
            "intent-unclear": "Absicht ungeklärt", "other": "Andere oder beschriebene Herkunft",
        },
        "precision": {"day": "Tag", "month": "Monat", "year": "Jahr", "unknown": "unbekannt"},
        "origin_language": {"de": "Deutsch", "en": "Englisch", "es": "Spanisch", "mixed": "sprachübergreifend", "unknown": "ungeklärt"},
        "ui": {
            "navigation": "Navigation", "cabinet_caption": "ROHFORM · HERKUNFT · BEDEUTUNG · STREIT · ENTSCHEIDUNG",
            "featured_note": "Vier bereits aufgenommene Ausgangswörter. Ihre Diskussion endet durch die Aufnahme nicht.",
            "archive_description": "Kein Strom der neuesten Beiträge, sondern ein Bestand: sortierbar nach Wortart, Herkunft, Sprache und Aufnahmezustand.",
            "all": "Alle", "language": "Sprache", "sorting": "Sortierung", "newest": "Neueste zuerst",
            "most_discussed": "Meistdiskutiert", "by_status": "Nach Status", "findings": "Fundstücke", "for_query": "für",
            "close_filters": "Filter schließen", "submission": "Einreichung", "unknown": "ungeklärt", "first_trace": "Erste Spur",
            "main_threads": "Hauptstränge", "open": "offen", "yes": "ja", "no": "nein", "open_curation": "Im Kuratorium öffnen",
            "source": "Quelle", "named_participation": "Benannte Beteiligung", "word_anatomy": "Wortanatomie",
            "components": "Bestandteile", "no_provenance": "Noch keine Herkunftsereignisse.",
            "no_rationale": "Für diesen Status liegt noch keine öffentliche Begründung vor.",
            "discussion_rule": "Die Diskussion gehört zum Begriff, unabhängig davon, ob er aufgenommen, offen, zurückgestellt oder nicht aufgenommen ist.",
            "curatorium": "Kuratorium", "edited": "bearbeitet", "markdown_help": "Markdown für Listen, Zitate und Links ist erlaubt. Herkunftsbehauptungen brauchen möglichst eine Quelle.",
            "curator_note": "Als Kuratoriumsnotiz markieren", "join_discussion": "Mitreden",
            "join_help": "Ein Konto hält deine Beiträge, Korrekturen und Übersetzungen sauber bei dir.",
            "discussion_closed": "Die Diskussion ist derzeit geschlossen.",
            "contribute_help": "Erklärung, Übersetzung, Herkunftskorrektur, Variante oder Verkörperung werden als benannte Ergänzung eingereicht. Die Rohform wird dabei nicht überschrieben.",
            "submit_steps": ["Rohform bewahren", "Herkunft benennen", "Sofort diskutierbar", "Daniel entscheidet sichtbar"],
            "submit_heading": "Was beim Absenden geschieht",
            "submit_process": ["Das Wort erhält eine eigene öffentliche Seite.", "Deine Eingabe und dein Anzeigename bleiben als Ursprungsspur erhalten.", "Andere dürfen diskutieren und Ergänzungen vorschlagen.", "Eine spätere Aufnahme verändert den Status, nicht die Vorgeschichte."],
            "submit_quote": "Das Formular ist eine Eingangstür, keine automatische Heiligsprechungsmaschine.",
            "people_description": "Menschen werden nicht zu kleinen grauen Nutzernamen zusammengeschrumpft. Ihre Wörter und Beiträge bleiben als eigene Spuren erreichbar.",
            "contributor": "Mitwirkende Person", "words": "Wörter", "contributions": "Beiträge", "no_profiles": "Noch keine öffentlichen Profile.",
            "word_submissions": "Worteinreichungen", "conversation_traces": "Gesprächsspuren",
            "collections_description": "Sammlungen sind Wege durch denselben Bestand. Ein Wort kann in mehreren Wegen liegen, ohne kopiert oder seiner Herkunft beraubt zu werden.",
            "contact_title": "Kontakt", "contact_description": "Fragen, Datenschutzanliegen, Herkunftskorrekturen außerhalb eines Begriffs oder andere Nachrichten landen direkt in Daniels Inbox.",
            "send_message": "Nachricht senden", "public_page": "Öffentliche Seite", "account": "Konto",
        },
    },
    "en": {
        "lang_name": "English",
        "skip": "Skip to content",
        "nav": {
            "home": "Cabinet", "explore": "Explore words", "collections": "Paths", "people": "Contributors",
            "submit": "Submit a word", "dashboard": "My area", "curation": "Daniel inbox", "login": "Log in",
            "register": "Create account", "logout": "Log out",
        },
        "hero": {
            "eyebrow": "An open, curated word world", "title": "Words may become worlds.",
            "body": "Raw forms stay raw. People may contribute, disagree and continue a thought. Daniel visibly decides which terms enter his official registry.",
            "explore": "Enter the collection", "submit": "Throw in a word", "random": "Surprise me",
        },
        "sections": {
            "featured": "Admitted findings", "new": "New in the intake pool", "active": "Conversations in motion",
            "paths": "Paths through the cabinet", "classes": "By word class", "provenance": "Provenance trail",
            "discussion": "Discussion", "relations": "Related findings", "contribute": "Add something",
            "decision": "Daniel's decision", "raw": "Unchanged raw form", "origin": "Origin", "definitions": "Explanations",
            "not_meant": "Explicitly does not mean", "variants": "Variants", "embodiments": "Embodiments", "timeline": "Timeline",
        },
        "actions": {
            "read": "Open finding", "filter": "Filter", "clear": "Clear", "search": "Search", "reply": "Reply",
            "comment": "Post contribution", "follow": "Follow discussion", "unfollow": "Unfollow", "suggest": "Suggest an addition",
            "report": "Report", "save": "Save", "decide": "Record decision", "export": "Export public state",
            "mark_read": "Mark read", "load_more": "Show more", "copy": "Copy link", "edit": "Edit", "close": "Close", "send": "Send",
        },
        "status": {
            "submitted": "Submitted", "under_review": "Under review", "accepted": "Admitted", "deferred": "Deferred",
            "rejected": "Not admitted", "merged": "Connected as variant", "archived": "Archived",
        },
        "forms": {
            "required": "required", "optional": "optional",
            "raw_help": "Exactly as the word appeared. This raw form will not be silently corrected later.",
            "exact_help": "The original sentence or context. Typos may stay.",
            "public_help": "After submission the word receives a public page and can be discussed immediately.",
            "consent": "I may publish this material under CC BY-SA 4.0 and have not included private data belonging to other people.",
        },
        "empty": {
            "terms": "No finding here yet. Every archive starts with one human losing control of a noun.",
            "discussion": "No contribution yet. Silence is not the final state here.",
            "notifications": "Nothing new. The internet briefly stopped pulling at you.",
        },
        "footer": {
            "about": "About the ANTIBIBEL", "governance": "Admission & governance", "privacy": "Privacy",
            "conduct": "Conversation rules", "opensource": "Open data body", "contact": "Contact",
            "line": "Open to contributions. Curated by Daniel. Every trace remains attributable.",
            "license": "Code: MIT · Content and data: CC BY-SA 4.0", "credit": "Daniel and named contributors",
        },
        "auth": {
            "login_title": "Enter again", "register_title": "An account for your own traces", "username": "Username",
            "password": "Password", "email": "Email", "display_name": "Display name",
            "login_body": "Your account connects submissions, discussions, additions and notifications to you.",
            "register_body": "Your display name appears on public contributions. Your email remains private.",
            "login_art": "Every contribution keeps a trace.", "register_art": "One account, many attributable traces.",
            "change_password": "Change password", "password_changed": "Password changed.",
        },
        "curation": {
            "title": "Daniel inbox", "pending_terms": "Open terms", "contributions": "Contribution proposals", "reports": "Reports",
            "decision_history": "Decision history", "none": "Nothing is waiting. Suspiciously peaceful.",
            "warning": "Admission makes a term official, but never erases earlier discussion or provenance.",
        },
        "authorship": {
            "claimed-by-submitter": "Claimed by the submitter", "direct-daniel-use": "Direct use by Daniel",
            "daniel-coined-ai-systematized": "Coined by Daniel, systematised by AI", "joint-project-setting": "Joint project setting",
            "joint-or-unresolved-project-setting": "Joint or unresolved project setting", "layered-joint-origin": "Layered joint origin",
            "existing-word-redefined-by-daniel": "Existing word redefined by Daniel",
            "existence-confirmed-authorship-open": "Existence confirmed, authorship open", "origin-unresolved": "Origin unresolved",
            "intent-unclear": "Intent unclear", "other": "Other or described origin",
        },
        "precision": {"day": "day", "month": "month", "year": "year", "unknown": "unknown"},
        "origin_language": {"de": "German", "en": "English", "es": "Spanish", "mixed": "cross-language", "unknown": "unresolved"},
        "ui": {
            "navigation": "Navigation", "cabinet_caption": "RAW FORM · ORIGIN · MEANING · ARGUMENT · DECISION",
            "featured_note": "Four already admitted founding words. Admission does not end their discussion.",
            "archive_description": "Not a stream of the newest posts, but a collection: sortable by word class, origin, language and admission status.",
            "all": "All", "language": "Language", "sorting": "Sorting", "newest": "Newest first",
            "most_discussed": "Most discussed", "by_status": "By status", "findings": "findings", "for_query": "for",
            "close_filters": "Close filters", "submission": "Submission", "unknown": "unresolved", "first_trace": "First trace",
            "main_threads": "main threads", "open": "open", "yes": "yes", "no": "no", "open_curation": "Open in curation",
            "source": "Source", "named_participation": "Named contributors", "word_anatomy": "Word anatomy",
            "components": "Components", "no_provenance": "No provenance events yet.",
            "no_rationale": "No public rationale has been recorded for this status yet.",
            "discussion_rule": "The discussion belongs to the term whether it is admitted, open, deferred or not admitted.",
            "curatorium": "Curation", "edited": "edited", "markdown_help": "Markdown is allowed for lists, quotations and links. Claims about provenance should include a source whenever possible.",
            "curator_note": "Mark as a curator note", "join_discussion": "Join the discussion",
            "join_help": "An account keeps your contributions, corrections and translations cleanly attributed to you.",
            "discussion_closed": "This discussion is currently closed.",
            "contribute_help": "Explanations, translations, provenance corrections, variants and embodiments are submitted as named additions. They do not overwrite the raw form.",
            "submit_steps": ["Preserve the raw form", "Name the origin", "Discuss immediately", "Daniel decides visibly"],
            "submit_heading": "What happens after submission",
            "submit_process": ["The word receives its own public page.", "Your input and display name remain part of the provenance trail.", "Others may discuss it and suggest additions.", "Later admission changes the status, not the history."],
            "submit_quote": "The form is an entrance, not an automatic canonisation machine.",
            "people_description": "People are not reduced to tiny grey usernames. Their words and contributions remain explorable as their own traces.",
            "contributor": "Contributor", "words": "words", "contributions": "contributions", "no_profiles": "No public profiles yet.",
            "word_submissions": "Word submissions", "conversation_traces": "Conversation traces",
            "collections_description": "Collections are paths through the same body of material. A word may appear in several paths without being duplicated or stripped of its provenance.",
            "contact_title": "Contact", "contact_description": "Questions, privacy requests, provenance corrections outside a term, and other messages go directly to Daniel's inbox.",
            "send_message": "Send message", "public_page": "Public page", "account": "Account",
        },
    },
    "es": {
        "lang_name": "Español",
        "skip": "Ir al contenido",
        "nav": {
            "home": "Gabinete", "explore": "Explorar palabras", "collections": "Caminos", "people": "Participantes",
            "submit": "Enviar palabra", "dashboard": "Mi espacio", "curation": "Bandeja de Daniel", "login": "Entrar",
            "register": "Crear cuenta", "logout": "Salir",
        },
        "hero": {
            "eyebrow": "Un mundo abierto y curado de palabras", "title": "Las palabras pueden volverse mundos.",
            "body": "Las formas brutas permanecen intactas. Las personas pueden aportar, discrepar y continuar una idea. Daniel decide de forma visible qué términos entran en su registro oficial.",
            "explore": "Entrar en la colección", "submit": "Lanzar una palabra", "random": "Sorpréndeme",
        },
        "sections": {
            "featured": "Hallazgos admitidos", "new": "Nuevas propuestas", "active": "Conversaciones en movimiento",
            "paths": "Caminos por el gabinete", "classes": "Por clase de palabra", "provenance": "Rastro de procedencia",
            "discussion": "Discusión", "relations": "Hallazgos relacionados", "contribute": "Añadir algo",
            "decision": "Decisión de Daniel", "raw": "Forma bruta intacta", "origin": "Origen", "definitions": "Explicaciones",
            "not_meant": "No significa expresamente", "variants": "Variantes", "embodiments": "Encarnaciones", "timeline": "Línea temporal",
        },
        "actions": {
            "read": "Abrir hallazgo", "filter": "Filtrar", "clear": "Limpiar", "search": "Buscar", "reply": "Responder",
            "comment": "Publicar aporte", "follow": "Seguir conversación", "unfollow": "Dejar de seguir", "suggest": "Proponer añadido",
            "report": "Denunciar", "save": "Guardar", "decide": "Registrar decisión", "export": "Exportar estado público",
            "mark_read": "Marcar leído", "load_more": "Mostrar más", "copy": "Copiar enlace", "edit": "Editar", "close": "Cerrar", "send": "Enviar",
        },
        "status": {
            "submitted": "Presentada", "under_review": "En revisión", "accepted": "Admitida", "deferred": "Aplazada",
            "rejected": "No admitida", "merged": "Conectada como variante", "archived": "Archivada",
        },
        "forms": {
            "required": "obligatorio", "optional": "opcional",
            "raw_help": "Exactamente como apareció la palabra. Esta forma no se corregirá silenciosamente después.",
            "exact_help": "La frase o el contexto original. Los errores pueden quedarse.",
            "public_help": "Tras el envío, la palabra obtiene una página pública y puede discutirse de inmediato.",
            "consent": "Puedo publicar este contenido bajo CC BY-SA 4.0 y no he incluido datos privados de otras personas.",
        },
        "empty": {
            "terms": "Aún no hay hallazgos. Todo archivo empieza cuando alguien pierde el control de un sustantivo.",
            "discussion": "Aún no hay aportes. El silencio no es el estado final.",
            "notifications": "Nada nuevo. Internet dejó de tirar de ti por un momento.",
        },
        "footer": {
            "about": "Sobre la ANTIBIBEL", "governance": "Admisión y gobernanza", "privacy": "Privacidad",
            "conduct": "Reglas de conversación", "opensource": "Cuerpo de datos abierto", "contact": "Contacto",
            "line": "Abierta a aportes. Curada por Daniel. Cada rastro conserva su autoría.",
            "license": "Código: MIT · Contenido y datos: CC BY-SA 4.0", "credit": "Daniel y participantes nombrados",
        },
        "auth": {
            "login_title": "Volver a entrar", "register_title": "Una cuenta para tus propios rastros", "username": "Usuario",
            "password": "Contraseña", "email": "Correo", "display_name": "Nombre visible",
            "login_body": "Tu cuenta conecta contigo los envíos, debates, añadidos y notificaciones.",
            "register_body": "Tu nombre visible aparece en los aportes públicos. Tu correo permanece privado.",
            "login_art": "Cada aporte conserva un rastro.", "register_art": "Una cuenta, muchos rastros atribuibles.",
            "change_password": "Cambiar contraseña", "password_changed": "Contraseña cambiada.",
        },
        "curation": {
            "title": "Bandeja de Daniel", "pending_terms": "Términos abiertos", "contributions": "Propuestas de aporte",
            "reports": "Denuncias", "decision_history": "Historial de decisiones", "none": "Nada espera. Sospechosamente tranquilo.",
            "warning": "La admisión vuelve oficial un término, pero nunca borra debates ni procedencias anteriores.",
        },
        "authorship": {
            "claimed-by-submitter": "Reivindicada por quien la envió", "direct-daniel-use": "Uso directo de Daniel",
            "daniel-coined-ai-systematized": "Acuñada por Daniel, sistematizada por AI", "joint-project-setting": "Definición conjunta del proyecto",
            "joint-or-unresolved-project-setting": "Conjunta o aún sin resolver", "layered-joint-origin": "Origen conjunto por capas",
            "existing-word-redefined-by-daniel": "Palabra existente redefinida por Daniel",
            "existence-confirmed-authorship-open": "Existencia confirmada, autoría abierta", "origin-unresolved": "Origen sin resolver",
            "intent-unclear": "Intención poco clara", "other": "Otro origen o descrito",
        },
        "precision": {"day": "día", "month": "mes", "year": "año", "unknown": "desconocida"},
        "origin_language": {"de": "alemán", "en": "inglés", "es": "español", "mixed": "entre idiomas", "unknown": "sin resolver"},
        "ui": {
            "navigation": "Navegación", "cabinet_caption": "FORMA BRUTA · ORIGEN · SIGNIFICADO · DEBATE · DECISIÓN",
            "featured_note": "Cuatro palabras fundadoras ya admitidas. La admisión no termina su debate.",
            "archive_description": "No es una corriente de las publicaciones más nuevas, sino una colección: ordenable por clase, origen, idioma y estado de admisión.",
            "all": "Todas", "language": "Idioma", "sorting": "Orden", "newest": "Más nuevas primero",
            "most_discussed": "Más debatidas", "by_status": "Por estado", "findings": "hallazgos", "for_query": "para",
            "close_filters": "Cerrar filtros", "submission": "Envío", "unknown": "sin resolver", "first_trace": "Primer rastro",
            "main_threads": "hilos principales", "open": "abierta", "yes": "sí", "no": "no", "open_curation": "Abrir en curaduría",
            "source": "Fuente", "named_participation": "Participación nombrada", "word_anatomy": "Anatomía de la palabra",
            "components": "Componentes", "no_provenance": "Aún no hay eventos de procedencia.",
            "no_rationale": "Aún no hay una justificación pública para este estado.",
            "discussion_rule": "La discusión pertenece al término tanto si está admitido como si sigue abierto, aplazado o no admitido.",
            "curatorium": "Curaduría", "edited": "editado", "markdown_help": "Se permite Markdown para listas, citas y enlaces. Las afirmaciones sobre procedencia deberían incluir una fuente cuando sea posible.",
            "curator_note": "Marcar como nota de curaduría", "join_discussion": "Participar",
            "join_help": "Una cuenta mantiene tus aportes, correcciones y traducciones claramente atribuidos a ti.",
            "discussion_closed": "Esta discusión está cerrada por ahora.",
            "contribute_help": "Las explicaciones, traducciones, correcciones de procedencia, variantes y encarnaciones se envían como añadidos nombrados. No sobrescriben la forma bruta.",
            "submit_steps": ["Conservar la forma bruta", "Nombrar el origen", "Debatir de inmediato", "Daniel decide de forma visible"],
            "submit_heading": "Qué sucede después del envío",
            "submit_process": ["La palabra obtiene su propia página pública.", "Tu entrada y tu nombre visible permanecen en el rastro de procedencia.", "Otras personas pueden debatirla y proponer añadidos.", "Una admisión posterior cambia el estado, no la historia."],
            "submit_quote": "El formulario es una entrada, no una máquina automática de canonización.",
            "people_description": "Las personas no se reducen a pequeños nombres de usuario grises. Sus palabras y aportes permanecen explorables como rastros propios.",
            "contributor": "Participante", "words": "palabras", "contributions": "aportes", "no_profiles": "Aún no hay perfiles públicos.",
            "word_submissions": "Palabras enviadas", "conversation_traces": "Rastros de conversación",
            "collections_description": "Las colecciones son caminos por el mismo cuerpo de material. Una palabra puede aparecer en varios caminos sin duplicarse ni perder su procedencia.",
            "contact_title": "Contacto", "contact_description": "Las preguntas, solicitudes de privacidad, correcciones de procedencia fuera de un término y otros mensajes llegan directamente a la bandeja de Daniel.",
            "send_message": "Enviar mensaje", "public_page": "Página pública", "account": "Cuenta",
        },
    },
}


# Ergänzende maschinenlesbare Bezeichnungen für dynamische Choices und Ereignisse.
TEXT["de"]["ui"].update({"status_label": "Status", "origin_label": "Ursprung", "discussion_count": "Diskussionen"})
TEXT["en"]["ui"].update({"status_label": "Status", "origin_label": "Origin", "discussion_count": "Discussions"})
TEXT["es"]["ui"].update({"status_label": "Estado", "origin_label": "Origen", "discussion_count": "Debates"})

TEXT["de"]["contribution_kind"] = {
    "definition": "Erklärung", "translation": "Übersetzung", "origin": "Herkunftskorrektur",
    "variant": "Variante", "relation": "Beziehung", "embodiment": "Verkörperung",
    "word_class": "Wortart", "other": "Andere Ergänzung",
}
TEXT["en"]["contribution_kind"] = {
    "definition": "Explanation", "translation": "Translation", "origin": "Provenance correction",
    "variant": "Variant", "relation": "Relation", "embodiment": "Embodiment",
    "word_class": "Word class", "other": "Other addition",
}
TEXT["es"]["contribution_kind"] = {
    "definition": "Explicación", "translation": "Traducción", "origin": "Corrección de procedencia",
    "variant": "Variante", "relation": "Relación", "embodiment": "Encarnación",
    "word_class": "Clase de palabra", "other": "Otro añadido",
}

TEXT["de"]["report_reason"] = {
    "spam": "Spam", "abuse": "Beleidigung oder Angriff", "privacy": "Private Daten",
    "copyright": "Urheberrecht", "provenance": "Falsche Herkunft", "other": "Anderer Grund",
}
TEXT["en"]["report_reason"] = {
    "spam": "Spam", "abuse": "Abuse or attack", "privacy": "Private data",
    "copyright": "Copyright", "provenance": "False provenance", "other": "Other reason",
}
TEXT["es"]["report_reason"] = {
    "spam": "Spam", "abuse": "Insulto o ataque", "privacy": "Datos privados",
    "copyright": "Derechos de autor", "provenance": "Procedencia falsa", "other": "Otro motivo",
}

TEXT["de"]["provenance_type"] = {
    "submission": "Einreichung", "first_use": "Erste Verwendung", "definition": "Erklärung",
    "translation": "Übersetzung", "correction": "Korrektur", "decision": "Aufnahmeentscheidung",
    "status": "Statusänderung", "relation": "Beziehung", "embodiment": "Verkörperung",
    "redaction": "Redaktion oder Schwärzung", "import": "Import",
}
TEXT["en"]["provenance_type"] = {
    "submission": "Submission", "first_use": "First use", "definition": "Explanation",
    "translation": "Translation", "correction": "Correction", "decision": "Admission decision",
    "status": "Status change", "relation": "Relation", "embodiment": "Embodiment",
    "redaction": "Editing or redaction", "import": "Import",
}
TEXT["es"]["provenance_type"] = {
    "submission": "Envío", "first_use": "Primer uso", "definition": "Explicación",
    "translation": "Traducción", "correction": "Corrección", "decision": "Decisión de admisión",
    "status": "Cambio de estado", "relation": "Relación", "embodiment": "Encarnación",
    "redaction": "Edición o supresión", "import": "Importación",
}

TEXT["de"]["relation_type"] = {
    "related": "Verwandt", "variant": "Variante", "component": "Bestandteil",
    "contrast": "Gegenbegriff", "inspired": "Angeregt durch", "embodies": "Verkörpert",
}
TEXT["en"]["relation_type"] = {
    "related": "Related", "variant": "Variant", "component": "Component",
    "contrast": "Contrasting term", "inspired": "Inspired by", "embodies": "Embodies",
}
TEXT["es"]["relation_type"] = {
    "related": "Relacionada", "variant": "Variante", "component": "Componente",
    "contrast": "Término opuesto", "inspired": "Inspirada por", "embodies": "Encarnada en",
}

TEXT["de"]["ui"].update({
    "objects": "OBJEKTE", "pagination": "Seitennavigation", "register_eyebrow": "REGISTER",
    "explore_eyebrow": "ERKUNDEN", "grammar_eyebrow": "GRAMMATIK", "intake_eyebrow": "EINGANG",
    "argument_eyebrow": "STREIT", "official_registry": "OFFIZIELLES REGISTER",
    "discussion_eyebrow": "DISKUTIEREN · WIDERSPRECHEN · WEITERDENKEN",
    "contribute_eyebrow": "ERGÄNZEN OHNE ÜBERSCHREIBEN", "open_intake": "OFFENER EINGANG",
    "curated_paths": "KURATIERTE WEGE", "curated_path": "KURATIERTER WEG",
    "attributed_voices": "BENANNTE STIMMEN", "contributor_eyebrow": "MITWIRKENDE PERSON",
    "contact_eyebrow": "KONTAKT · RECHTE · FRAGEN", "account_eyebrow": "KONTO",
    "join_cabinet": "IN DIE WUNDERKAMMER",
})
TEXT["en"]["ui"].update({
    "objects": "OBJECTS", "pagination": "Page navigation", "register_eyebrow": "REGISTRY",
    "explore_eyebrow": "EXPLORE", "grammar_eyebrow": "GRAMMAR", "intake_eyebrow": "INTAKE",
    "argument_eyebrow": "ARGUMENT", "official_registry": "OFFICIAL REGISTRY",
    "discussion_eyebrow": "DISCUSS · DISAGREE · DEVELOP",
    "contribute_eyebrow": "CONTRIBUTE WITHOUT OVERWRITING", "open_intake": "OPEN INTAKE",
    "curated_paths": "CURATED PATHS", "curated_path": "CURATED PATH",
    "attributed_voices": "ATTRIBUTED VOICES", "contributor_eyebrow": "CONTRIBUTOR",
    "contact_eyebrow": "CONTACT · RIGHTS · QUESTIONS", "account_eyebrow": "ACCOUNT",
    "join_cabinet": "JOIN THE CABINET",
})
TEXT["es"]["ui"].update({
    "objects": "OBJETOS", "pagination": "Navegación de páginas", "register_eyebrow": "REGISTRO",
    "explore_eyebrow": "EXPLORAR", "grammar_eyebrow": "GRAMÁTICA", "intake_eyebrow": "ENTRADA",
    "argument_eyebrow": "DEBATE", "official_registry": "REGISTRO OFICIAL",
    "discussion_eyebrow": "DEBATIR · DISCREPAR · DESARROLLAR",
    "contribute_eyebrow": "AÑADIR SIN SOBRESCRIBIR", "open_intake": "ENTRADA ABIERTA",
    "curated_paths": "CAMINOS CURADOS", "curated_path": "CAMINO CURADO",
    "attributed_voices": "VOCES ATRIBUIDAS", "contributor_eyebrow": "PARTICIPANTE",
    "contact_eyebrow": "CONTACTO · DERECHOS · PREGUNTAS", "account_eyebrow": "CUENTA",
    "join_cabinet": "ENTRAR EN EL GABINETE",
})

TEXT["de"]["account"] = {
    "eyebrow": "DEINE SPUREN", "edit_profile": "Profil bearbeiten", "your_words": "Deine Wörter",
    "followed": "Verfolgte Gespräche", "additions": "Ergänzungen", "public_trace": "Öffentliche Spur",
    "no_bio": "Noch keine Selbstbeschreibung.", "public_profile": "Öffentliches Profil",
    "not_following": "Noch keinem Gespräch gefolgt.", "no_additions": "Noch keine Ergänzungen.",
    "notifications": "Benachrichtigungen", "profile": "Profil", "word_submission": "Worteinreichung",
    "conversation_trace": "Gesprächsspur", "revision_note": "Die frühere Fassung bleibt als Revision erhalten.",
}
TEXT["en"]["account"] = {
    "eyebrow": "YOUR TRACES", "edit_profile": "Edit profile", "your_words": "Your words",
    "followed": "Followed discussions", "additions": "Additions", "public_trace": "Public trace",
    "no_bio": "No self-description yet.", "public_profile": "Public profile",
    "not_following": "Not following any discussion yet.", "no_additions": "No additions yet.",
    "notifications": "Notifications", "profile": "Profile", "word_submission": "Word submission",
    "conversation_trace": "Conversation trace", "revision_note": "The previous version remains preserved as a revision.",
}
TEXT["es"]["account"] = {
    "eyebrow": "TUS RASTROS", "edit_profile": "Editar perfil", "your_words": "Tus palabras",
    "followed": "Debates seguidos", "additions": "Añadidos", "public_trace": "Rastro público",
    "no_bio": "Aún no hay descripción personal.", "public_profile": "Perfil público",
    "not_following": "Aún no sigues ningún debate.", "no_additions": "Aún no hay añadidos.",
    "notifications": "Notificaciones", "profile": "Perfil", "word_submission": "Palabra enviada",
    "conversation_trace": "Rastro de conversación", "revision_note": "La versión anterior permanece conservada como revisión.",
}


TEXT["de"]["ui"].update({
    "in_one_sentence": "Kurz gesagt",
    "thought_further": "Was darin steckt",
    "other_languages": "In anderen Sprachen",
})
TEXT["en"]["ui"].update({
    "in_one_sentence": "In one sentence",
    "thought_further": "What it carries",
    "other_languages": "In other languages",
})
TEXT["es"]["ui"].update({
    "in_one_sentence": "En una frase",
    "thought_further": "Lo que contiene",
    "other_languages": "En otros idiomas",
})


def get_text(lang: str):
    return TEXT.get(lang, TEXT["de"])
