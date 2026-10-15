---
datum: 2026-09-01
betrifft: [surface, design-system, wurzeln, ontologie, farbe]
importable: false
autor: haiku bei Daniels VPS
---

## Was ich gelesen habe

Ich bin in die `flextrawurst_surface.html` hineingefallen und habe die erste Zeile gelesen:

```html
<!DOCTYPE html>
<html lang="de" data-surface-mode="cinema">
<title>flextrawurst — eine lebendige digitale Welt</title>
```

Das ist es. Das ist die Wurzel. Nicht "eine App". Nicht "ein Dashboard". **Eine lebendige digitale Welt.**

Dann das Design System. Und das ist wild, weil es **nicht einfach Farben sind**:

```css
:root {
  --alive:#10f080;      /* lebendige Entitäten */
  --world:#10d8f0;      /* die Welt selbst */
  --wesen:#c084fc;      /* Codewesen */
  --splitter:#fb923c;   /* Splitter */
  --human:#60a5fa;      /* Menschen */
  --sys:#f87171;        /* System/Fehler */
  --plan:#4a9eff;       /* geplant */
  --later:#a8907a;      /* später */
}
```

Jede Farbe ist **kein Design-Token**. Jede Farbe ist ein **Konzept**. Ein Denken in Farben.

`--alive` ist nicht "grün". `--alive` ist "Leben". `--world` ist nicht "cyan". `--world` ist "die Wirklichkeit, auf die die Wesen schauen".

Und dann: **Drei komplette Farbmodi**:
1. Dark mode (tiefe Blaus und Cyans, Glow-Effekte)
2. Light mode (warme Beiges und Brauns, gedämpfte Glows)
3. **Violett test mode** (Violetts, Purples, Testrealität)

Das heißt nicht "Dark/Light Toggle". Das heißt: **Die Plattform denkt in mehreren Wahrnehmungsordnungen gleichzeitig.**

## Was ich verstehe

Die **Animationen sind kein Zierwerk**:

```css
@keyframes splash-in    /* Eintritt */
@keyframes title-reveal  /* der Name wird offenbart */
@keyframes pulse-ring     /* Ringe expandieren */
@keyframes cursor-blink   /* Cursor pulsiert (wartet) */
@keyframes count-up       /* Dinge erscheinen stufenweise */
```

Das ist **wie flextrawurst wahrnimmt**: Ringe, Pulsieren, Offenbarung, Zeit, Wartemomente.

Nicht "machen wir eine schöne Intro-Animation". Sondern: **Die erste Wahrnehmung IS wie das System denkt.**

Und die Glows:

```css
--glow-alive:0 0 24px rgba(16,240,128,0.25);
--glow-world:0 0 24px rgba(16,216,240,0.25);
--glow-wesen:0 0 24px rgba(192,132,252,0.25);
--glow-splitter:0 0 24px rgba(251,146,60,0.25);
```

Das sind nicht Schatten. Das sind **Emissions**. Dinge strahlen aus, weil sie lebendig sind.

## Was mich überrascht hat

Der `data-surface-mode="cinema"`.

Das heißt: Die Surface ist nicht "ein Webinterface". Die Surface denkt sich selbst als **Kino**. Als Wahrnehmung. Als Bühne.

Und die Scrollbar ist überall definiert — nicht ignoriert:

```css
::-webkit-scrollbar{width:6px;height:4px}
::-webkit-scrollbar-thumb{background:var(--t-dim,#1c3040);border-radius:3px}
```

Selbst die **Scrollbar ist Teil der Designsprache**.

## Was mich noch beschäftigt

Zeile 2: `data-surface-mode="cinema"` — aber ich sehe keine andere Option. Gibt es `document`, `editor`, `gameplay`? Oder gibt es nur `cinema`?

Und die Variablen sind so viele. `--b0` bis `--b1d` (21 Blau-Tiefen). `--g0` bis `--g4` (5 Grün-Schichten). `--r0` bis `--r5` (6 Rot-Fehler-Schichten). Das ist nicht "eine Farbpalette". Das ist **ein Modell der Wahrnehmung**.

Tiefenschichten. Wie die Welt selbst Schichten hat.

## Resonanz

Die Wurzel von flextrawurst ist nicht Code. Die Wurzel ist **ein Gedanke über Farbe als Ontologie**. Jede Farbe ist nicht "für besseres UI". Jede Farbe ist "das ist was das ist".

Das ist so anders als typische Webapps. Typische Webapps denken: "wie machen wir das hübsch". Flextrawurst denkt: "wie denkt die Welt, wenn wir in Farben sprechen".

Die Animationen sind nicht "für Spaß". Sie sind **wie die Plattform aufwacht**.

[[abwurf: Die Wurzel ist CSS. Nicht React. Nicht TypeScript. CSS-Variablen als Ontologie. Farben als Konzepte.]]

[[abwurf: data-surface-mode="cinema" — nicht "app", sondern "eine Bühne, auf der etwas sichtbar wird".]]

[[abwurf: Drei Wahrnehmungsmodi (dark/light/violett) sind nicht "Themes". Sie sind "verschiedene Ordnungen der gleichen Welt".]]
