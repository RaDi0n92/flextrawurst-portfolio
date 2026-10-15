#!/usr/bin/env python3
"""Extract real DOM perception bodies through an existing Playwright page."""

from __future__ import annotations

from typing import Any

from .object_store import TriViewObjectStore


EXTRACT_SCRIPT = r"""(selector) => {
  const pathFor = node => {
    if (node.dataset && node.dataset.fwObjectId) return `[data-fw-object-id="${node.dataset.fwObjectId}"]`;
    const parts=[];
    while (node && node.nodeType===1 && node !== document.body) {
      let index=1, sibling=node;
      while ((sibling=sibling.previousElementSibling)) index++;
      parts.unshift(`${node.tagName.toLowerCase()}:nth-child(${index})`);
      node=node.parentElement;
    }
    return 'body > '+parts.join(' > ');
  };
  return [...document.querySelectorAll(selector)].map(node => ({
    object_id: node.dataset.fwObjectId || node.id || null,
    object_type: node.dataset.fwObjectType || node.tagName.toLowerCase(),
    dom_path: pathFor(node),
    html_fragment: node.outerHTML,
    css_states: [...node.classList],
    ids: node.id ? [node.id] : [],
    classes: [...node.classList],
    actions: [...node.querySelectorAll('button,a,[role="button"]')].map(x => ({
      type:x.tagName.toLowerCase(), label:(x.innerText||x.getAttribute('aria-label')||'').trim(),
      id:x.id||null, disabled:!!x.disabled
    })),
    order: [...node.parentElement.children].indexOf(node),
    freshness: {status:'now', observed_at:Date.now()/1000},
    changed_since: node.dataset.fwChangedSince || null,
    scene: node.dataset.fwScene || `DOM-Objekt ${node.dataset.fwObjectId || node.id || node.tagName}`,
    motion: node.dataset.fwMotion || 'stabil',
    depth: node.dataset.fwDepth || 'nah',
    interaction: [...node.querySelectorAll('button,a,[role="button"]')].map(x => x.innerText.trim()).filter(Boolean),
    provenance: (node.dataset.fwProvenance || '').split(',').map(x=>x.trim()).filter(Boolean),
    linked_organs: (node.dataset.fwOrgans || '').split(',').map(x=>x.trim()).filter(Boolean)
  })).filter(x => x.object_id);
}"""

INSTALL_MUTATION_SCRIPT = r"""() => {
  if (window.__fwDomMutationLog) return;
  window.__fwDomMutationLog = [];
  window.__fwRrwebLog = [];
  const record = (node, kind, detail) => {
    const object = node && node.closest ? node.closest('[data-fw-object-id]') : null;
    const event = {
      object_id: object ? object.dataset.fwObjectId : null,
      kind, detail, observed_at: Date.now() / 1000
    };
    window.__fwDomMutationLog.push(event);
    window.__fwRrwebLog.push({type: 3, data: {source: 0, mutation: event}, timestamp: Date.now()});
    if (window.__fwDomMutationLog.length > 500) window.__fwDomMutationLog.shift();
    if (window.__fwRrwebLog.length > 500) window.__fwRrwebLog.shift();
  };
  const observer = new MutationObserver(mutations => mutations.forEach(mutation => {
    record(mutation.target, mutation.type, mutation.attributeName || mutation.addedNodes.length || mutation.removedNodes.length);
  }));
  observer.observe(document.documentElement, {subtree:true, childList:true, attributes:true, characterData:true});
  window.__fwDomMutationObserver = observer;
}"""

READ_MUTATIONS_SCRIPT = r"""() => {
  const value = window.__fwDomMutationLog || [];
  window.__fwDomMutationLog = [];
  return value;
}"""

READ_RRWEB_SCRIPT = r"""() => {
  const value = window.__fwRrwebLog || [];
  window.__fwRrwebLog = [];
  return value;
}"""


def extract_page_objects(page: Any, selector: str = "[data-fw-object-id]") -> list[dict[str, Any]]:
    """Run only DOM extraction in the browser; no model or hidden enrichment."""
    return list(page.evaluate(EXTRACT_SCRIPT, selector))


def install_mutation_stream(page: Any) -> None:
    page.evaluate(INSTALL_MUTATION_SCRIPT)


def read_mutations(page: Any) -> list[dict[str, Any]]:
    return list(page.evaluate(READ_MUTATIONS_SCRIPT))


def read_rrweb_events(page: Any) -> list[dict[str, Any]]:
    """Return rrweb-compatible incremental mutation envelopes, model-free."""
    return list(page.evaluate(READ_RRWEB_SCRIPT))


def capture_page_objects(page: Any, store: TriViewObjectStore, selector: str = "[data-fw-object-id]") -> list[dict[str, Any]]:
    objects = []
    for source in extract_page_objects(page, selector):
        object_id = source["object_id"]
        source["deep_link"] = f"#fw-object-{object_id}"
        source["share"] = f"/share/{object_id}"
        try:
            value = store.create(source, dom_kind="real", dom_path=source["dom_path"], html_fragment=source["html_fragment"])
        except ValueError:
            value = store.update(object_id, source, dom_kind="real", dom_path=source["dom_path"], html_fragment=source["html_fragment"])
        objects.append(value)
    return objects
