"""Rich, immutable office artifacts for canonical browser-chat exports.

The recorder deliberately captures plain, verifiable chat data.  This module is
the presentation layer on the VPS: it turns that canonical data into DOCX, ODT
and PDF without changing the captured conversation or its evidence.
"""

from __future__ import annotations

import html
import io
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from bs4 import BeautifulSoup, NavigableString, Tag
from markdown_it import MarkdownIt


class OfficeExportError(RuntimeError):
    """A requested office artifact cannot be rendered safely."""


FORMATS = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "odt": "application/vnd.oasis.opendocument.text",
    "pdf": "application/pdf",
}
VARIANTS = {"transcript", "events_markers"}


@dataclass(frozen=True)
class OfficeArtifact:
    content: bytes
    filename: str
    mime_type: str
    format: str
    variant: str


_MARKDOWN = MarkdownIt("commonmark", {"html": False, "breaks": False}).enable("table").enable("strikethrough")
_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9ÄÖÜäöüß._-]+")


def _provider(data: dict[str, Any]) -> str:
    value = str(data.get("provider") or "").strip()
    return "ChatGPT" if re.search(r"chatgpt|openai", value, re.IGNORECASE) else (value or "AI-Strom")


def _role_label(role: str, provider: str) -> str:
    if role == "user":
        return "Daniel"
    if role == "assistant":
        return provider
    return role or "AI-Strom"


def _scope_label(data: dict[str, Any]) -> str:
    if data.get("scope") == "recorded_segment" and data.get("recorded_segment_kind") == "live_session":
        return "Gespeicherte Live-Aufnahme"
    if data.get("scope") == "recorded_segment":
        return "Gestoppter historischer Aufnahmeabschnitt"
    return "Kompletter gespeicherter Chat"


def _proof_label(data: dict[str, Any]) -> str:
    proof = data.get("history_proof") if isinstance(data.get("history_proof"), dict) else {}
    status = proof.get("status")
    if status == "browser_chain_verified":
        return "Browserkette belegt (kein Provider-API-Beleg)"
    if status == "gap_detected":
        return "Lücke erkannt — keine Vollständigkeitsbehauptung"
    if status == "partial_chain":
        return "Teilkette — Vollständigkeit nicht bewiesen"
    return "Keine vollständige Belegkette vorhanden"


def _slug(value: Any, fallback: str = "chat_export") -> str:
    clean = _SAFE_FILENAME.sub("_", str(value or "").strip().lower()).strip("._")
    return clean[:96] or fallback


def _filename(data: dict[str, Any], variant: str, format_name: str) -> str:
    scope = "aufnahme" if data.get("scope") == "recorded_segment" else "gesamtchat"
    suffix = "1zu1" if variant == "transcript" else "1zu1_events_marker"
    return f"{_slug(data.get('title'))}_{scope}_{suffix}.{format_name}"


def _rich_inline_html(nodes: Any) -> str:
    """Render only the recorder's tiny presentation AST; never provider HTML."""
    if not isinstance(nodes, list):
        return ""
    parts: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        kind = str(node.get("type") or "")
        if kind == "text":
            parts.append(html.escape(str(node.get("text") or "")))
            continue
        if kind == "break":
            parts.append("<br/>")
            continue
        inner = _rich_inline_html(node.get("children"))
        if kind == "strong":
            parts.append(f"<strong>{inner}</strong>")
        elif kind == "emphasis":
            parts.append(f"<em>{inner}</em>")
        elif kind == "strikethrough":
            parts.append(f"<s>{inner}</s>")
        elif kind == "inline_code":
            parts.append(f"<code>{inner}</code>")
        elif kind == "link":
            href = str(node.get("href") or "").strip()
            if re.match(r"^(?:https?:|mailto:)", href, re.IGNORECASE):
                parts.append(f'<a href="{html.escape(href, quote=True)}">{inner}</a>')
            else:
                parts.append(inner)
        elif kind == "span":
            parts.append(inner)
    return "".join(parts)


def _rich_blocks_html(blocks: Any) -> str:
    if not isinstance(blocks, list):
        return ""
    parts: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        kind = str(block.get("type") or "")
        if kind == "heading":
            try:
                level = int(block.get("level") or 1)
            except (TypeError, ValueError):
                level = 1
            level = min(6, max(1, level))
            parts.append(f"<h{level}>{_rich_inline_html(block.get('children'))}</h{level}>")
        elif kind == "paragraph":
            parts.append(f"<p>{_rich_inline_html(block.get('children'))}</p>")
        elif kind == "blockquote":
            parts.append(f"<blockquote>{_rich_blocks_html(block.get('blocks'))}</blockquote>")
        elif kind == "code_block":
            language = html.escape(str(block.get("language") or "text"), quote=True)
            code = html.escape(str(block.get("text") or ""))
            parts.append(f'<pre><code class="language-{language}">{code}</code></pre>')
        elif kind == "rule":
            parts.append("<hr/>")
        elif kind == "list":
            tag = "ol" if bool(block.get("ordered")) else "ul"
            items = []
            for item in block.get("items") if isinstance(block.get("items"), list) else []:
                if isinstance(item, dict):
                    items.append(f"<li>{_rich_blocks_html(item.get('blocks'))}</li>")
            if items:
                parts.append(f"<{tag}>{''.join(items)}</{tag}>")
        elif kind == "table":
            header = block.get("header") if isinstance(block.get("header"), list) else []
            rows = block.get("rows") if isinstance(block.get("rows"), list) else []
            head = ""
            if header:
                head = "<thead><tr>" + "".join(f"<th>{_rich_inline_html(cell)}</th>" for cell in header) + "</tr></thead>"
            body_rows = []
            for row in rows:
                if isinstance(row, list):
                    body_rows.append("<tr>" + "".join(f"<td>{_rich_inline_html(cell)}</td>" for cell in row) + "</tr>")
            if head or body_rows:
                parts.append(f"<table>{head}<tbody>{''.join(body_rows)}</tbody></table>")
    return "".join(parts)


def _rich_html(value: Any, rich_content: Any = None) -> str:
    # `rich_content` is only a presentation companion.  The transcript value
    # remains untouched and is the safe fallback for prior recordings or for
    # providers that expose no semantic message root.
    if isinstance(rich_content, dict) and rich_content.get("schema_version") == "1.0":
        rendered = _rich_blocks_html(rich_content.get("blocks"))
        if rendered.strip():
            return rendered
    text = str(value or "").replace("\r\n", "\n")
    # Empty upload-only user messages are meaningful capture events.  They get
    # a readable placeholder instead of disappearing in office renderers.
    if not text.strip():
        return "<p><em>Leerer Textbeitrag / Anhangsaktion</em></p>"
    return _MARKDOWN.render(text)


def _metadata(data: dict[str, Any]) -> list[tuple[str, str]]:
    proof = data.get("history_proof") if isinstance(data.get("history_proof"), dict) else {}
    return [
        ("Provider", _provider(data)),
        ("Modell", str(data.get("model") or "Unbekannt")),
        ("Exportbereich", _scope_label(data)),
        ("Aufnahme-ID", str(data.get("recorded_import_id") or "keine")),
        ("Belegkette", _proof_label(data)),
        (
            "Übergänge mit Überlappung",
            f"{proof.get('overlap_confirmed_transition_count', 0)} / {proof.get('transition_count', 0)}",
        ),
        ("Nicht belegte Übergänge", str(proof.get("unproven_transition_count", 0))),
        (
            "VPS quittiert",
            f"{proof.get('vps_confirmed_count', 0)}; bereits vorhanden {proof.get('vps_already_present_count', 0)}",
        ),
    ]


def _event_rows(data: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = [["Zeit", "Typ", "Rolle", "Details"]]
    for event in data.get("events") or []:
        if not isinstance(event, dict):
            continue
        timestamp = str(event.get("timestamp") or event.get("timestamp_utc") or "–")
        kind = str(event.get("type") or event.get("event_type") or "event")
        role = str(event.get("role") or event.get("tag") or "–")
        details = str(event.get("summary") or event.get("text") or event.get("content") or "–")
        rows.append([timestamp, kind, role, details])
    return rows


def _event_log_lines(data: dict[str, Any], *, width: int = 118) -> list[str]:
    """Render every event without building a quadratic office table structure."""
    lines = ["ZEIT │ TYP │ ROLLE │ DETAILS", "─" * min(width, 118)]
    for row in _event_rows(data)[1:]:
        timestamp, kind, role, details = row
        value = f"[{timestamp}] {kind} │ {role} │ {details}".replace("\r\n", " ").replace("\n", " ")
        lines.extend(textwrap.wrap(value, width=width, subsequent_indent="  ", break_long_words=False, break_on_hyphens=False) or [""])
    return lines


def _chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(values), size):
        yield values[index:index + size]


def _soup_nodes(markdown: Any) -> Iterable[Tag | NavigableString]:
    return BeautifulSoup(_rich_html(markdown), "html.parser").contents


def _turn_nodes(turn: dict[str, Any]) -> Iterable[Tag | NavigableString]:
    return BeautifulSoup(_rich_html(turn.get("text"), turn.get("rich_content")), "html.parser").contents


# ---- DOCX ---------------------------------------------------------------


def _docx_shade(paragraph: Any, fill: str) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    props = paragraph._p.get_or_add_pPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    props.append(shading)


def _docx_inline(paragraph: Any, node: Any, *, bold: bool = False, italic: bool = False, code: bool = False) -> None:
    from docx.shared import RGBColor

    if isinstance(node, (NavigableString, str)):
        value = str(node)
        if not value:
            return
        run = paragraph.add_run(value)
        run.bold = bold
        run.italic = italic
        if code:
            run.font.name = "DejaVu Sans Mono"
            run.font.highlight_color = 7  # gray 25 %; portable across Word versions
        return
    if not isinstance(node, Tag):
        return
    name = node.name.lower()
    if name == "br":
        paragraph.add_run().add_break()
        return
    next_bold = bold or name in {"strong", "b"}
    next_italic = italic or name in {"em", "i"}
    next_code = code or name == "code"
    if name == "a":
        for child in node.children:
            before = len(paragraph.runs)
            _docx_inline(paragraph, child, bold=next_bold, italic=next_italic, code=next_code)
            for run in paragraph.runs[before:]:
                run.font.color.rgb = RGBColor(47, 93, 145)
                run.font.underline = True
        href = str(node.get("href") or "").strip()
        if href:
            paragraph.add_run(f" ({href})").italic = True
        return
    for child in node.children:
        _docx_inline(paragraph, child, bold=next_bold, italic=next_italic, code=next_code)


def _docx_block(doc: Any, node: Any, *, list_style: str | None = None) -> None:
    from docx.enum.style import WD_STYLE_TYPE

    if isinstance(node, NavigableString):
        if str(node).strip():
            p = doc.add_paragraph()
            _docx_inline(p, node)
        return
    if not isinstance(node, Tag):
        return
    name = node.name.lower()
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        p = doc.add_heading(level=min(6, int(name[1])))
        for child in node.children:
            _docx_inline(p, child)
        return
    if name == "p":
        p = doc.add_paragraph(style=list_style) if list_style else doc.add_paragraph()
        for child in node.children:
            _docx_inline(p, child)
        return
    if name == "blockquote":
        p = doc.add_paragraph(style="Quote")
        for child in node.children:
            _docx_inline(p, child, italic=True)
        return
    if name == "pre":
        styles = doc.styles
        if "Recorder Code" not in [style.name for style in styles]:
            code_style = styles.add_style("Recorder Code", WD_STYLE_TYPE.PARAGRAPH)
            code_style.font.name = "DejaVu Sans Mono"
            code_style.font.size = __import__("docx").shared.Pt(8.5)
        p = doc.add_paragraph(style="Recorder Code")
        _docx_inline(p, node.get_text())
        _docx_shade(p, "F7F7F8")
        return
    if name in {"ul", "ol"}:
        style = "List Bullet" if name == "ul" else "List Number"
        for child in node.find_all("li", recursive=False):
            direct = [item for item in child.contents if not (isinstance(item, Tag) and item.name in {"ul", "ol"})]
            p = doc.add_paragraph(style=style)
            for item in direct:
                _docx_inline(p, item)
            for nested in child.find_all(["ul", "ol"], recursive=False):
                _docx_block(doc, nested)
        return
    if name == "table":
        raw_rows = node.find_all("tr")
        if not raw_rows:
            return
        width = max(len(row.find_all(["th", "td"], recursive=False)) for row in raw_rows)
        table = doc.add_table(rows=0, cols=width)
        table.style = "Light Shading Accent 1"
        for row_index, raw_row in enumerate(raw_rows):
            cells = raw_row.find_all(["th", "td"], recursive=False)
            cells_out = table.add_row().cells
            for index, cell in enumerate(cells):
                p = cells_out[index].paragraphs[0]
                for child in cell.children:
                    _docx_inline(p, child, bold=(row_index == 0 or cell.name == "th"))
        return
    if name == "hr":
        p = doc.add_paragraph("─" * 44)
        p.alignment = 1
        return
    for child in node.children:
        _docx_block(doc, child, list_style=list_style)


def _render_docx(data: dict[str, Any], variant: str) -> bytes:
    from docx import Document
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    document = Document()
    section = document.sections[0]
    section.top_margin = section.bottom_margin = Inches(0.65)
    section.left_margin = section.right_margin = Inches(0.72)
    normal = document.styles["Normal"]
    normal.font.name = "DejaVu Sans"
    normal.font.size = Pt(10.5)
    if "Recorder Code" not in [style.name for style in document.styles]:
        code_style = document.styles.add_style("Recorder Code", WD_STYLE_TYPE.PARAGRAPH)
        code_style.font.name = "DejaVu Sans Mono"
        code_style.font.size = Pt(8.5)

    title = document.add_heading(str(data.get("title") or "Unbenannter Chat"), 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = document.add_paragraph(f"{_provider(data)} · {_scope_label(data)}")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].italic = True
    meta = document.add_table(rows=0, cols=2)
    meta.style = "Light Grid Accent 1"
    for key, value in _metadata(data):
        cells = meta.add_row().cells
        cells[0].text = key
        cells[1].text = value
        for run in cells[0].paragraphs[0].runs:
            run.bold = True
    document.add_paragraph()

    provider = _provider(data)
    document.add_heading("1:1 Gesprächsverlauf", level=1)
    for index, turn in enumerate(data.get("turns") or [], start=1):
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role") or "unknown")
        role_p = document.add_paragraph()
        role_run = role_p.add_run(f"{index}. {_role_label(role, provider)}")
        role_run.bold = True
        if role == "user":
            role_run.font.color.rgb = RGBColor(255, 255, 255)
        _docx_shade(role_p, "2F2F2F" if role == "user" else "F7F7F8")
        if turn.get("reasoning"):
            reasoning = document.add_paragraph("Denkprozess")
            reasoning.runs[0].bold = True
            _docx_shade(reasoning, "F7F7F8")
            for node in _soup_nodes(turn["reasoning"]):
                _docx_block(document, node)
        for node in _turn_nodes(turn):
            _docx_block(document, node)
        document.add_paragraph("─" * 44).alignment = WD_ALIGN_PARAGRAPH.CENTER

    if variant == "events_markers":
        document.add_page_break()
        document.add_heading("Events & Marker", level=1)
        document.add_paragraph("Der vollständige Ereignis- und Markerlog ergänzt den 1:1-Verlauf. Er ist absichtlich monospaced statt als riesige Word-Tabelle angelegt, damit lange Chats speicherfest bleiben.")
        for block in _chunks(_event_log_lines(data), 160):
            p = document.add_paragraph(style="Recorder Code")
            p.add_run("\n".join(block))
            _docx_shade(p, "F7F7F8")

    out = io.BytesIO()
    document.save(out)
    return out.getvalue()


# ---- ODT ----------------------------------------------------------------


def _odt_styles(document: Any) -> dict[str, str]:
    from odf import style

    styles: dict[str, tuple[str, dict[str, str], dict[str, str]]] = {
        "Meta": ("paragraph", {"fontsize": "9pt", "color": "#555555"}, {}),
        "User": ("paragraph", {"fontweight": "bold", "color": "#ffffff"}, {"backgroundcolor": "#2f2f2f", "padding": "0.12in"}),
        "Assistant": ("paragraph", {"fontweight": "bold", "color": "#202123"}, {"backgroundcolor": "#f7f7f8", "padding": "0.12in"}),
        "Code": ("paragraph", {"fontfamily": "DejaVu Sans Mono", "fontsize": "8.5pt"}, {"backgroundcolor": "#f7f7f8", "padding": "0.1in"}),
        "Quote": ("paragraph", {"fontstyle": "italic", "color": "#555555"}, {"borderleft": "0.02in solid #a0a0a0", "paddingleft": "0.12in"}),
        "Bold": ("text", {"fontweight": "bold"}, {}),
        "Italic": ("text", {"fontstyle": "italic"}, {}),
        "InlineCode": ("text", {"fontfamily": "DejaVu Sans Mono", "backgroundcolor": "#eeeeee"}, {}),
    }
    names: dict[str, str] = {}
    for name, (family, text_attrs, paragraph_attrs) in styles.items():
        item = style.Style(name=name, family=family)
        if text_attrs:
            item.addElement(style.TextProperties(**text_attrs))
        if paragraph_attrs:
            item.addElement(style.ParagraphProperties(**paragraph_attrs))
        document.styles.addElement(item)
        names[name] = name
    return names


def _odt_inline(parent: Any, node: Any, styles: dict[str, str], *, bold: bool = False, italic: bool = False, code: bool = False) -> None:
    from odf import text

    # Renderer-originated labels, metadata and event-log blocks reach this
    # helper as plain ``str`` values; Markdown-originated content is a
    # ``NavigableString``. Both are visible ODT text and must survive.
    if isinstance(node, (NavigableString, str)):
        value = str(node)
        if not value:
            return
        style_name = styles["InlineCode"] if code else styles["Bold"] if bold else styles["Italic"] if italic else None
        target = text.Span(stylename=style_name) if style_name else parent
        target.addText(value)
        if target is not parent:
            parent.addElement(target)
        return
    if not isinstance(node, Tag):
        return
    name = node.name.lower()
    if name == "br":
        parent.addElement(text.LineBreak())
        return
    next_bold = bold or name in {"strong", "b"}
    next_italic = italic or name in {"em", "i"}
    next_code = code or name == "code"
    for child in node.children:
        _odt_inline(parent, child, styles, bold=next_bold, italic=next_italic, code=next_code)
    if name == "a" and node.get("href"):
        parent.addText(f" ({node.get('href')})")


def _odt_paragraph(document: Any, parent: Any, node: Any, styles: dict[str, str], *, style_name: str | None = None) -> None:
    from odf import text

    p = text.P(stylename=style_name) if style_name else text.P()
    if isinstance(node, Tag):
        for child in node.children:
            _odt_inline(p, child, styles)
    else:
        _odt_inline(p, node, styles)
    parent.addElement(p)


def _odt_block(document: Any, parent: Any, node: Any, styles: dict[str, str]) -> None:
    from odf import table, text

    if isinstance(node, NavigableString):
        if str(node).strip():
            _odt_paragraph(document, parent, node, styles)
        return
    if not isinstance(node, Tag):
        return
    name = node.name.lower()
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        heading = text.H(outlinelevel=int(name[1]))
        for child in node.children:
            _odt_inline(heading, child, styles)
        parent.addElement(heading)
        return
    if name == "p":
        _odt_paragraph(document, parent, node, styles)
        return
    if name == "blockquote":
        _odt_paragraph(document, parent, node, styles, style_name=styles["Quote"])
        return
    if name == "pre":
        _odt_paragraph(document, parent, node.get_text(), styles, style_name=styles["Code"])
        return
    if name in {"ul", "ol"}:
        listing = text.List()
        for child in node.find_all("li", recursive=False):
            item = text.ListItem()
            direct = [x for x in child.contents if not (isinstance(x, Tag) and x.name in {"ul", "ol"})]
            p = text.P()
            for part in direct:
                _odt_inline(p, part, styles)
            item.addElement(p)
            listing.addElement(item)
            for nested in child.find_all(["ul", "ol"], recursive=False):
                _odt_block(document, item, nested, styles)
        parent.addElement(listing)
        return
    if name == "table":
        out_table = table.Table(name="Chat Tabelle")
        for row in node.find_all("tr"):
            out_row = table.TableRow()
            for raw_cell in row.find_all(["th", "td"], recursive=False):
                cell = table.TableCell()
                p = text.P()
                for child in raw_cell.children:
                    _odt_inline(p, child, styles, bold=raw_cell.name == "th")
                cell.addElement(p)
                out_row.addElement(cell)
            out_table.addElement(out_row)
        parent.addElement(out_table)
        return
    if name == "hr":
        _odt_paragraph(document, parent, "─" * 44, styles, style_name=styles["Meta"])
        return
    for child in node.children:
        _odt_block(document, parent, child, styles)


def _render_odt(data: dict[str, Any], variant: str) -> bytes:
    from odf import text
    from odf.opendocument import OpenDocumentText

    document = OpenDocumentText()
    styles = _odt_styles(document)
    title = text.H(outlinelevel=1, text=str(data.get("title") or "Unbenannter Chat"))
    document.text.addElement(title)
    _odt_paragraph(document, document.text, f"{_provider(data)} · {_scope_label(data)}", styles, style_name=styles["Meta"])
    for key, value in _metadata(data):
        _odt_paragraph(document, document.text, f"{key}: {value}", styles, style_name=styles["Meta"])
    document.text.addElement(text.H(outlinelevel=2, text="1:1 Gesprächsverlauf"))
    provider = _provider(data)
    for index, turn in enumerate(data.get("turns") or [], start=1):
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role") or "unknown")
        _odt_paragraph(
            document,
            document.text,
            f"{index}. {_role_label(role, provider)}",
            styles,
            style_name=styles["User"] if role == "user" else styles["Assistant"],
        )
        if turn.get("reasoning"):
            _odt_paragraph(document, document.text, "Denkprozess", styles, style_name=styles["Meta"])
            for node in _soup_nodes(turn["reasoning"]):
                _odt_block(document, document.text, node, styles)
        for node in _turn_nodes(turn):
            _odt_block(document, document.text, node, styles)
        _odt_paragraph(document, document.text, "─" * 44, styles, style_name=styles["Meta"])
    if variant == "events_markers":
        document.text.addElement(text.H(outlinelevel=2, text="Events & Marker"))
        _odt_paragraph(document, document.text, "Der vollständige Ereignis- und Markerlog bleibt monospaced, damit auch sehr lange Chats als echte ODT-Datei stabil speicherbar sind.", styles, style_name=styles["Meta"])
        for block in _chunks(_event_log_lines(data), 160):
            _odt_paragraph(document, document.text, "\n".join(block), styles, style_name=styles["Code"])
    out = io.BytesIO()
    document.write(out)
    return out.getvalue()


# ---- PDF ----------------------------------------------------------------


def _pdf_fonts() -> tuple[str, str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    names = ("RecorderDejaVu", "RecorderDejaVuBold", "RecorderDejaVuMono")
    families = (
        (Path("/usr/share/fonts/truetype/dejavu"), ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSansMono.ttf")),
        (Path("/usr/share/fonts/truetype/liberation"), ("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf", "LiberationMono-Regular.ttf")),
        (Path("/usr/share/fonts/truetype/freefont"), ("FreeSans.ttf", "FreeSansBold.ttf", "FreeMono.ttf")),
    )
    paths = next((tuple(root / filename for filename in filenames) for root, filenames in families if all((root / filename).exists() for filename in filenames)), None)
    if paths is None:
        raise OfficeExportError("Keine vollständige PDF-Schriftfamilie (Sans/Bold/Mono) gefunden")
    for name, path in zip(names, paths):
        if name not in pdfmetrics.getRegisteredFontNames():
            if not path.exists():
                raise OfficeExportError(f"PDF-Schrift fehlt: {path}")
            pdfmetrics.registerFont(TTFont(name, str(path)))
    return names


def _pdf_inline(node: Any) -> str:
    if isinstance(node, NavigableString):
        return html.escape(str(node))
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    inner = "".join(_pdf_inline(child) for child in node.children)
    if name in {"strong", "b"}:
        return f"<b>{inner}</b>"
    if name in {"em", "i"}:
        return f"<i>{inner}</i>"
    if name == "code":
        return f'<font name="RecorderDejaVuMono" backColor="#f7f7f8">{inner}</font>'
    if name == "br":
        return "<br/>"
    if name == "a":
        href = html.escape(str(node.get("href") or ""))
        suffix = f" ({href})" if href else ""
        return f'<font color="#2563eb"><u>{inner}</u></font>{suffix}'
    return inner


def _pdf_block(story: list[Any], node: Any, styles: dict[str, Any]) -> None:
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Preformatted, Table, TableStyle

    if isinstance(node, NavigableString):
        if str(node).strip():
            story.append(Paragraph(html.escape(str(node)), styles["body"]))
        return
    if not isinstance(node, Tag):
        return
    name = node.name.lower()
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        story.append(Paragraph(_pdf_inline(node), styles[f"h{min(4, int(name[1]))}"]))
        return
    if name == "p":
        story.append(Paragraph(_pdf_inline(node), styles["body"]))
        return
    if name == "blockquote":
        quote = Table([[Paragraph(_pdf_inline(node), styles["quote"])]], colWidths=[470])
        quote.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f7f8")),
            ("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor("#a0a0a0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(quote)
        return
    if name == "pre":
        story.append(Preformatted(node.get_text(), styles["code"]))
        return
    if name in {"ul", "ol"}:
        for index, child in enumerate(node.find_all("li", recursive=False), start=1):
            prefix = "•" if name == "ul" else f"{index}."
            direct = [item for item in child.contents if not (isinstance(item, Tag) and item.name in {"ul", "ol"})]
            story.append(Paragraph(f"{prefix} {''.join(_pdf_inline(item) for item in direct)}", styles["list"]))
            for nested in child.find_all(["ul", "ol"], recursive=False):
                _pdf_block(story, nested, styles)
        return
    if name == "table":
        data: list[list[Any]] = []
        for row_index, row in enumerate(node.find_all("tr")):
            values = [Paragraph(_pdf_inline(cell), styles["table_header"] if row_index == 0 or cell.name == "th" else styles["table_cell"])
                      for cell in row.find_all(["th", "td"], recursive=False)]
            if values:
                data.append(values)
        if data:
            width = 490 / max(1, max(len(row) for row in data))
            table = Table(data, colWidths=[width] * max(len(row) for row in data), repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f7f7f8")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d1d1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(table)
        return
    if name == "hr":
        story.append(Paragraph("─" * 70, styles["meta"]))
        return
    for child in node.children:
        _pdf_block(story, child, styles)


def _render_pdf(data: dict[str, Any], variant: str) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    regular, bold, mono = _pdf_fonts()
    out = io.BytesIO()
    document = SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm)
    sheet = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("RecorderTitle", parent=sheet["Title"], fontName=bold, fontSize=19, leading=23, alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle("RecorderSubtitle", parent=sheet["Normal"], fontName=regular, fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10),
        "body": ParagraphStyle("RecorderBody", parent=sheet["BodyText"], fontName=regular, fontSize=9.6, leading=14, spaceAfter=7),
        "meta": ParagraphStyle("RecorderMeta", parent=sheet["Normal"], fontName=regular, fontSize=8.2, leading=10.5, textColor=colors.HexColor("#555555"), spaceAfter=2),
        "quote": ParagraphStyle("RecorderQuote", parent=sheet["BodyText"], fontName=regular, fontSize=9.3, leading=13.5, textColor=colors.HexColor("#444444")),
        "code": ParagraphStyle("RecorderCode", parent=sheet["Code"], fontName=mono, fontSize=7.6, leading=9.4, backColor=colors.HexColor("#f7f7f8"), borderPadding=6, spaceAfter=8),
        "list": ParagraphStyle("RecorderList", parent=sheet["BodyText"], fontName=regular, fontSize=9.5, leading=13, leftIndent=14, firstLineIndent=-10, spaceAfter=3),
        "table_header": ParagraphStyle("RecorderTableHeader", parent=sheet["Normal"], fontName=bold, fontSize=7.6, leading=9),
        "table_cell": ParagraphStyle("RecorderTableCell", parent=sheet["Normal"], fontName=regular, fontSize=7.4, leading=9),
    }
    for level, size in ((1, 15), (2, 13), (3, 11.5), (4, 10.5)):
        styles[f"h{level}"] = ParagraphStyle(
            f"RecorderH{level}", parent=sheet["Heading1"], fontName=bold, fontSize=size, leading=size + 4,
            spaceBefore=10, spaceAfter=6,
        )
    story: list[Any] = [
        Paragraph(html.escape(str(data.get("title") or "Unbenannter Chat")), styles["title"]),
        Paragraph(html.escape(f"{_provider(data)} · {_scope_label(data)}"), styles["subtitle"]),
    ]
    meta_data = [[Paragraph(f"<b>{html.escape(key)}</b>", styles["meta"]), Paragraph(html.escape(value), styles["meta"])] for key, value in _metadata(data)]
    meta_table = Table(meta_data, colWidths=[145, 345])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f7f7f8")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d1d1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [meta_table, Spacer(1, 10), Paragraph("1:1 Gesprächsverlauf", styles["h1"])]
    provider = _provider(data)
    for index, turn in enumerate(data.get("turns") or [], start=1):
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role") or "unknown")
        role_color = "#2f2f2f" if role == "user" else "#f7f7f8"
        role_text_color = "#ffffff" if role == "user" else "#202123"
        role_table = Table([[Paragraph(html.escape(f"{index}. {_role_label(role, provider)}"), ParagraphStyle(
            f"Role{index}", parent=styles["body"], fontName=bold, textColor=colors.HexColor(role_text_color), spaceAfter=0,
        ))]], colWidths=[490])
        role_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(role_color)),
            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(role_table)
        if turn.get("reasoning"):
            story.append(Paragraph("Denkprozess", styles["h3"]))
            for node in _soup_nodes(turn["reasoning"]):
                _pdf_block(story, node, styles)
        for node in _turn_nodes(turn):
            _pdf_block(story, node, styles)
        story.append(Spacer(1, 5))
    if variant == "events_markers":
        story += [PageBreak(), Paragraph("Events & Marker", styles["h1"])]
        story.append(Paragraph("Der vollständige Ereignis- und Markerlog ist monospaced gesetzt. Das bewahrt alle Zeilen und bleibt bei langen Chats stabiler als eine zehntausendzeilige Tabelle.", styles["body"]))
        from reportlab.platypus import Preformatted
        for block in _chunks(_event_log_lines(data, width=100), 80):
            story.append(Preformatted("\n".join(block), styles["code"]))

    def footer(canvas: Any, _doc: Any) -> None:
        canvas.saveState()
        canvas.setFont(regular, 7.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(18 * mm, 10 * mm, "AI UI Recorder · VPS-Artefakt")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Seite {canvas.getPageNumber()}")
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()


def build_office_artifact(data: dict[str, Any], *, variant: str, format_name: str) -> OfficeArtifact:
    """Render a complete, format-preserving office artifact from canonical data."""
    if variant not in VARIANTS:
        raise OfficeExportError("Unbekannte Exportvariante. Erlaubt sind transcript oder events_markers.")
    if format_name not in FORMATS:
        raise OfficeExportError("Unbekanntes Zielformat. Erlaubt sind docx, odt oder pdf.")
    turns = data.get("turns") if isinstance(data, dict) else None
    if not isinstance(turns, list) or not turns:
        raise OfficeExportError("Keine gespeicherten Chatbeiträge für den Office-Export vorhanden.")
    if format_name == "docx":
        content = _render_docx(data, variant)
    elif format_name == "odt":
        content = _render_odt(data, variant)
    else:
        content = _render_pdf(data, variant)
    if not content:
        raise OfficeExportError("Der Office-Renderer hat eine leere Datei erzeugt.")
    return OfficeArtifact(
        content=content,
        filename=_filename(data, variant, format_name),
        mime_type=FORMATS[format_name],
        format=format_name,
        variant=variant,
    )
