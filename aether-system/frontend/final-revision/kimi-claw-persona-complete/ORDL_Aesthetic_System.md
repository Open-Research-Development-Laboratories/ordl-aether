# ORDL 零式 (Type-Zero) Aesthetic System
## The Definitive Design Bible

**Classification:** UNCLASSIFIED  
**Version:** 1.0.0  
**Date:** 2026-03-08  
**Status:** OPERATIONAL

---

## 目次 / Table of Contents

1. [Philosophy / 理念](#philosophy)
2. [Color Palette / カラーパレット](#color-palette)
3. [Typography / タイポグラフィ](#typography)
4. [Layout System / レイアウトシステム](#layout-system)
5. [Bilingual System / バイリンガルシステム](#bilingual-system)
6. [Decorative Elements / 装飾要素](#decorative-elements)
7. [Components / コンポーネント](#components)
8. [Animation / アニメーション](#animation)
9. [Icon System / アイコンシステム](#icon-system)
10. [Implementation Notes / 実装メモ](#implementation-notes)

---

## Philosophy / 理念 {#philosophy}

```
01001111 01010010 01000100 01001100
   O        R        D        L
```

**Japanese:** 黒い画面の中の白い影。  
**English:** A white silhouette in a black frame.  
**Hex:** 0x00 0xFF

### Core Principles

| ID | Principle | JP | Description |
|----|-----------|-----|-------------|
| P1 | ABSOLUTE CONTRAST | 絶対対比 | Only #000000 and #FFFFFF exist. No grays. |
| P2 | MILITARY MINIMALISM | 軍事的最小限 | Every element serves a function. No decoration without purpose. |
| P3 | TECHNICAL AUTHORITY | 技術的権威 | Display specs, version numbers, hex codes openly. |
| P4 | BILINGUAL PARITY | バイリンガル対等 | JP/EN are equals. Never one without the other. |
| P5 | ASCII OR NOTHING | ASCIIのみ | No raster images. Vector ASCII art only. |

---

## Color Palette / カラーパレット {#color-palette}

### Strict Monochrome Specification

```
╔══════════════════════════════════════════════════════════════╗
║                    COLOR PALETTE v1.0.0                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║   PRIMARY BACKGROUND    #000000    ████████████████████████  ║
║   PRIMARY FOREGROUND    #FFFFFF    ░░░░░░░░░░░░░░░░░░░░░░░░  ║
║                                                               ║
║   INVERSE BACKGROUND    #FFFFFF    ░░░░░░░░░░░░░░░░░░░░░░░░  ║
║   INVERSE FOREGROUND    #000000    ████████████████████████  ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
```

### Usage Matrix

| Element | Background | Foreground | Notes |
|---------|------------|------------|-------|
| Default View | #000000 | #FFFFFF | Standard mode |
| Inverse View | #FFFFFF | #000000 | High-alert, warnings |
| Code Blocks | #000000 | #FFFFFF | Monospace required |
| Headers | #000000 | #FFFFFF | Bold, all-caps |
| Borders | #FFFFFF | — | 1px solid |
| Disabled | #000000 | #FFFFFF @ 50% | NEVER use gray |
| Selected | #FFFFFF | #000000 | Invert for emphasis |

### Contrast Control System (明度/BRIGHT)

```
BRIGHTNESS CONTROL
明度調整
═══════════════════

[████████████████████] 100% ████ 0xFF
[████████████████░░░░]  75% ███░ 0xBF
[████████░░░░░░░░░░░░]  50% ██░░ 0x80
[████░░░░░░░░░░░░░░░░]  25% █░░░ 0x40
[░░░░░░░░░░░░░░░░░░░░]   0% ░░░░ 0x00

Implementation: CSS filter brightness() only.
Never modify the base palette.
```

---

## Typography / タイポグラフィ {#typography}

### Font Stack Specification

```
┌─────────────────────────────────────────────────────────────┐
│  TYPOGRAPHY STACK v1.0.0                                    │
└─────────────────────────────────────────────────────────────┘
```

#### 1. UI/Headers (Clean Sans-Serif)

**Primary:** `Inter, "Noto Sans JP", -apple-system, BlinkMacSystemFont, sans-serif`

- Weight: 400 (Regular), 700 (Bold)
- Tracking: 0.05em (headers), 0em (body)
- Line-height: 1.2 (headers), 1.6 (body)
- Text-transform: UPPERCASE for EN headers

#### 2. Data/Technical (Monospace)

**Primary:** `"JetBrains Mono", "SF Mono", "Noto Sans Mono JP", monospace`

- Weight: 400 (Regular), 700 (Bold)
- Tracking: 0em (fixed-width)
- Line-height: 1.4
- Tabular nums: ALWAYS

#### 3. ASCII Art (Block Monospace)

**Primary:** `"Courier New", Courier, monospace`

- Weight: 400 only
- Line-height: 1.0 (tight)
- Letter-spacing: 0em

### Type Scale

| Level | Size | Weight | Font | Usage |
|-------|------|--------|------|-------|
| H1 | 48px | 700 | Sans | Page titles |
| H2 | 32px | 700 | Sans | Section headers |
| H3 | 24px | 700 | Sans | Subsections |
| H4 | 18px | 700 | Sans | Card titles |
| Body | 16px | 400 | Sans | Paragraphs |
| Data | 14px | 400 | Mono | Technical specs |
| Code | 13px | 400 | Mono | Code blocks |
| Label | 12px | 700 | Sans | UI labels |
| Meta | 11px | 400 | Mono | Version numbers |

### Bilingual Typography Rules

```
ENGLISH HEADER      日本語ヘッダー
──────────────      ────────────
Inter Bold          Noto Sans JP Bold
UPPERCASE           標準ケース
Tracking: +0.05em    Tracking: +0.02em
```

---

## Layout System / レイアウトシステム {#layout-system}

### Grid Specification

```
╔══════════════════════════════════════════════════════════════════════════╗
║  MIL-SPEC GRID SYSTEM                                                    ║
║  12-COLUMN / 24px BASE UNIT                                              ║
╚══════════════════════════════════════════════════════════════════════════╝

    ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
    │ 01 │ 02 │ 03 │ 04 │ 05 │ 06 │ 07 │ 08 │ 09 │ 10 │ 11 │ 12 │
    └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
    ◄────────────── 1200px max-width ──────────────►
    
    Column: 76px | Gutter: 24px | Margin: 48px
```

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| space-0 | 0px | No gap |
| space-1 | 4px | Tight padding |
| space-2 | 8px | Inline elements |
| space-3 | 16px | Component internal |
| space-4 | 24px | Standard gap |
| space-5 | 32px | Section padding |
| space-6 | 48px | Major sections |
| space-7 | 64px | Page sections |
| space-8 | 96px | Hero spacing |

### Container Specifications

```
CONTAINER WIDTHS
────────────────
Full:     100%      (fluid)
XL:       1400px    (wide screens)
LG:       1200px    (default)
MD:       960px     (tablets)
SM:       720px     (mobile)
XS:       100%      (small mobile)

Padding: 24px (mobile), 48px (desktop)
```

### Border System

- **Default:** 1px solid #FFFFFF
- **Thick:** 2px solid #FFFFFF
- **Double:** double 3px #FFFFFF
- **No rounded corners:** border-radius: 0

---

## Bilingual System / バイリンガルシステム {#bilingual-system}

### Navigation Labels

| Page | Japanese | English | Path |
|------|----------|---------|------|
| Home | ホーム | Home | / |
| About | 概要 | About | /about |
| Research | 研究 | R&D | /research |
| Contact | 連絡 | Contact | /contact |
| Documentation | 文書 | Docs | /docs |

### Label Format Standards

```
PRIMARY FORMAT (Headers, Labels):
════════════════════════════════════
日本語ラベル / ENGLISH LABEL

Example:
カラーパレット / COLOR PALETTE
タイポグラフィ / TYPOGRAPHY

SECONDARY FORMAT (Inline):
════════════════════════════════════
English Label (日本語)

Example:
Home (ホーム)
About (概要)

NEVER USE:
× 日本語 - English
× English / 日本語 (wrong order)
× Mixed within same phrase
```

### Content Layout Patterns

```
PATTERN A: SIDE-BY-SIDE (Headers)
──────────────────────────────────
研究 / RESEARCH

PATTERN B: STACKED (Subtitles)
──────────────────────────────────
黒い画面の中の白い影。
A white silhouette in a black frame.

PATTERN C: PARENTHETICAL (Body)
──────────────────────────────────
The ORDL system (零式システム) operates on...
```

---

## Decorative Elements / 装飾要素 {#decorative-elements}

### Binary Headers

```
█████████████████████████████████████████████████████████████
█ 01001111 01010010 01000100 01001100  █  ORDL TYPE-ZERO   █
█     O        R        D        L     █  零式              █
█████████████████████████████████████████████████████████████
```

### ASCII Art Patterns

#### Divider - Single
```
────────────────────────────────────────────────────────────────
```

#### Divider - Double
```
════════════════════════════════════════════════════════════════
```

#### Divider - Heavy
```
████████████████████████████████████████████████████████████████
```

#### Box Drawing
```
╔══════════════════════════════════════════════════════════════╗
║  CONTENT CONTAINER                                           ║
╠══════════════════════════════════════════════════════════════╣
║  Data field .................................. VALUE         ║
║  Another field ................................ DATA         ║
╚══════════════════════════════════════════════════════════════╝
```

### Hex Code Decorations

```
0x00 0x01 0x02 0x03 0x04 0x05 0x06 0x07 0x08 0x09 0x0A 0x0B 0x0C
─────────────────────────────────────────────────────────────────
FF FF FF 00 00 00 FF FF FF 00 00 00 FF FF FF 00 00 00 FF FF FF
```

### Mathematical Notation

```
∴ CONTRAST = lim(x→0) [1 - (bg ⊗ fg)]

   ∀ elements ∈ System:
   ┌─────────────────────────┐
   │ color(element) ≡ {0, 1} │
   └─────────────────────────┘
   
   where 0 ≡ #000000, 1 ≡ #FFFFFF
```

### Version Badges

```
[ v1.0.0 ]  [ BUILD 2026.03.08 ]  [ REV 0xAF ]
```

### Compliance Markers

```
[ CLASS: UNCLASSIFIED ]
[ SEC: PUBLIC ]
[ STATUS: OPERATIONAL ]
[ CHECKSUM: 0x4A7F ]
```

---

## Components / コンポーネント {#components}

### Buttons / ボタン

```
PRIMARY BUTTON
─────────────────────────
┌─────────────────────┐
│  アクション / ACTION  │
└─────────────────────┘

Specs:
- Border: 1px solid #FFFFFF
- Padding: 12px 24px
- Font: Sans-serif, 14px, weight 700
- Background: #000000 (default), #FFFFFF (hover)
- Text: #FFFFFF (default), #000000 (hover)
- Border-radius: 0
- Transition: 150ms ease

States:
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│    DEFAULT     │  │     HOVER      │  │    ACTIVE      │
│  Black bg      │  │  White bg      │  │  White bg      │
│  White text    │  │  Black text    │  │  Black text    │
│  1px border    │  │  1px border    │  │  2px border    │
└────────────────┘  └────────────────┘  └────────────────┘
```

### Forms / フォーム

```
TEXT INPUT
─────────────────────────
ラベル / LABEL
┌──────────────────────────────┐
│ Placeholder text...          │
└──────────────────────────────┘

Specs:
- Border: 1px solid #FFFFFF
- Padding: 12px 16px
- Font: Monospace, 14px
- Background: #000000
- Focus: 2px border, inverse colors optional

DROPDOWN
─────────────────────────
選択 / SELECT
┌──────────────────────────────┐
│ Option 1              [▼]    │
└──────────────────────────────┘

CHECKBOX
─────────────────────────
[■] 有効 / ENABLED    (checked)
[□] 無効 / DISABLED   (unchecked)
```

### Tables / テーブル

```
DATA TABLE
─────────────────────────────────────────────────────────────────
┌──────────────┬──────────────┬──────────────┬──────────────────┐
│ 項目 / FIELD │ 値 / VALUE   │ 型 / TYPE    │ 状態 / STATUS    │
├──────────────┼──────────────┼──────────────┼──────────────────┤
│ ID           │ 0x4A7F       │ HEX          │ [ ACTIVE ]       │
│ VERSION      │ v1.0.0       │ SEMVER       │ [ CURRENT ]      │
│ BUILD        │ 2026.03.08   │ ISO DATE     │ [ STABLE ]       │
│ CHECKSUM     │ 0xAF29       │ HEX          │ [ VERIFIED ]     │
└──────────────┴──────────────┴──────────────┴──────────────────┘

Specs:
- Border-collapse: collapse
- Border: 1px solid #FFFFFF
- Header: Bold, uppercase
- Cell padding: 12px 16px
- Font: Monospace for data, Sans for headers
- Alternating rows: No (never use gray)
- Hover state: Inverse colors
```

### Cards / カード

```
CONTENT CARD
─────────────────────────
┌─────────────────────────────────────┐
│ カードタイトル / CARD TITLE         │
├─────────────────────────────────────┤
│                                     │
│   Card content goes here.           │
│   Use monospace for technical data. │
│                                     │
│   [ v2.1.0 ] [ ID: 0xFF ]           │
│                                     │
├─────────────────────────────────────┤
│ [ 詳細 / DETAILS ]                  │
└─────────────────────────────────────┘

Specs:
- Border: 1px solid #FFFFFF
- Padding: 24px
- No shadow
- No border-radius
- Header separator: 1px solid #FFFFFF
```

### Navigation / ナビゲーション

```
HEADER NAV
─────────────────────────────────────────────────────────────────
┌────────────────────────────────────────────────────────────────┐
│ 01001111 01010010 01000100 01001100      ホーム/Home  概要/About │
│                                          研究/R&D    連絡/Contact│
└────────────────────────────────────────────────────────────────┘

FOOTER NAV
─────────────────────────────────────────────────────────────────
┌────────────────────────────────────────────────────────────────┐
│ [ ホーム/Home ] [ 概要/About ] [ 研究/R&D ] [ 連絡/Contact ]     │
│                                                                │
│ v1.0.0 │ © 2026 ORDL │ 0x4A7F                                  │
└────────────────────────────────────────────────────────────────┘
```

### Alerts / アラート

```
ALERT BOXES
─────────────────────────

INFO:
┌─────────────────────────────────────┐
│ ℹ 情報 / INFO                       │
│ Message content here...             │
└─────────────────────────────────────┘

WARNING (Inverse):
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░ ⚠ 警告 / WARNING                  ░
░ Message content here...             ░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

ERROR (Inverse + Bold):
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░ ✕ エラー / ERROR                  ░
░ Critical message here...            ░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

---

## Animation / アニメーション {#animation}

### Principles

| ID | Principle | Description |
|----|-----------|-------------|
| A1 | SUBTLE ONLY | Animations must be barely perceptible |
| A2 | FUNCTIONAL | Every animation serves a purpose |
| A3 | INSTANT FEEDBACK | No animation > 300ms for UI feedback |
| A4 | NO EASING CURVES | Linear or step functions only |
| A5 | RESPECT REDUCED MOTION | Disable all animations if preferred |

### Timing Specifications

```
TIMING MATRIX
════════════════════════════════════════════

Interaction     Duration    Easing      Property
────────────────────────────────────────────
Hover           150ms       linear      color, bg, border
Focus           100ms       step-end    outline
Active/Press    50ms        linear      transform (scale)
Page Load       300ms       linear      opacity
Data Update     200ms       step-start  content
Modal Open      200ms       linear      opacity, transform
Modal Close     150ms       linear      opacity
```

### Animation Patterns

```
BLINK CURSOR (Terminal effect)
──────────────────────────────
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
duration: 1000ms
iteration: infinite

SCAN LINE (Subtle)
──────────────────────────────
@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}
duration: 8000ms
iteration: infinite
timing: linear

DATA REFRESH
──────────────────────────────
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
duration: 200ms
iteration: 1

TYPING EFFECT
──────────────────────────────
@keyframes typing {
  from { width: 0; }
  to { width: 100%; }
}
duration: proportional to length
```

### CSS Variables

```css
:root {
  --transition-fast: 50ms linear;
  --transition-base: 150ms linear;
  --transition-slow: 300ms linear;
  --transition-instant: 0ms;
  
  --animation-cursor: blink 1000ms linear infinite;
  --animation-scan: scan 8000ms linear infinite;
}
```

---

## Icon System / アイコンシステム {#icon-system}

### Design Principles

- **NO SVG ICON LIBRARIES** (Feather, Heroicons, etc.)
- **ASCII ONLY** for inline icons
- **GEOMETRIC SHAPES** for larger graphics
- **UNICODE BLOCK ELEMENTS** for indicators

### ASCII Icon Library

```
UI ICONS
══════════════════════════════════════════════════════════════

Navigation:
  ←  →  ↑  ↓           Arrows
  «  »                 Double arrows
  ┃  ━                 Section markers

Actions:
  +  -  ×  ÷           Math operations
  [■] [□] [▣]          Checkboxes
  (•) ( ) (◉)          Radio buttons
  ☰                    Menu (hamburger)
  ✕                    Close
  ✓                    Check
  ⚙                    Settings (gear)
  ℹ                    Info
  ⚠                    Warning
  ✕                    Error

Status:
  ●  ○  ◐              Progress dots
  ████░░░░░            Progress bar
  [ON] [OFF]           Toggle states
  ●───●───●            Step indicator

Data:
  ┌─┐  ┌─┐  ┌─┐        File icons
  │█│  │░│  │▒│
  └─┘  └─┘  └─┘
  ▲                    Sort ascending
  ▼                    Sort descending
  ⧖                    Loading spinner (rotates)
```

### Geometric Patterns

```
HEADER DECORATION
══════════════════════════════════════════════════════════════

Type A: Binary
01001111 01010010 01000100 01001100
   O        R        D        L

Type B: Hex
0x4F 0x52 0x44 0x4C
  O    R    D    L

Type C: Grid
┌──┬──┬──┬──┐
│██│░░│██│░░│
├──┼──┼──┼──┤
│░░│██│░░│██│
└──┴──┴──┴──┘

Type D: Wave
▗▄▖▗▄▖▗▄▖▗▄▖▗▄▖

Type E: Dots
● ● ● ● ●
 ○ ○ ○ ○
```

### Status Indicators

```
OPERATIONAL STATUS
══════════════════

[ ● ACTIVE ]      - Solid circle, green intent via context
[ ○ STANDBY ]     - Empty circle
[ ◐ WARNING ]     - Half circle
[ ✕ ERROR ]       - X mark

SYSTEM STATUS
══════════════════

SYS: 0x4A7F [ OK ]
NET: 0x82A1 [ OK ]
DB:  0x11F4 [ OK ]
```

---

## Implementation Notes / 実装メモ {#implementation-notes}

### CSS Architecture

```css
/* ORDL 零式 - Core Variables */
:root {
  /* COLOR - STRICT MONOCHROME */
  --color-bg: #000000;
  --color-fg: #FFFFFF;
  --color-bg-inverse: #FFFFFF;
  --color-fg-inverse: #000000;
  
  /* TYPOGRAPHY */
  --font-ui: 'Inter', 'Noto Sans JP', sans-serif;
  --font-mono: 'JetBrains Mono', 'Noto Sans Mono JP', monospace;
  --font-ascii: 'Courier New', monospace;
  
  /* SPACING */
  --space-unit: 4px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;
  --space-6: 48px;
  --space-7: 64px;
  --space-8: 96px;
  
  /* BORDERS */
  --border-thin: 1px solid var(--color-fg);
  --border-thick: 2px solid var(--color-fg);
  --border-double: double 3px var(--color-fg);
  --border-radius: 0;
  
  /* TRANSITIONS */
  --transition-fast: 50ms linear;
  --transition-base: 150ms linear;
  --transition-slow: 300ms linear;
}

/* INVERSE UTILITY */
.inverse {
  background-color: var(--color-fg);
  color: var(--color-bg);
}

/* NEVER USE */
/* - gradients */
/* - shadows */
/* - rounded corners */
/* - gray colors */
/* - blur effects */
/* - backdrop-filter */
```

### HTML Template

```html
<!DOCTYPE html>
<html lang="ja,en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ORDL 零式 / Type-Zero</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
  <header>
    <div class="binary-logo">
      01001111 01010010 01000100 01001100
    </div>
    <nav>
      <a href="/">ホーム/Home</a>
      <a href="/about">概要/About</a>
      <a href="/research">研究/R&D</a>
    </nav>
  </header>
  
  <main>
    <!-- Content follows bilingual pattern -->
  </main>
  
  <footer>
    <div class="version">v1.0.0</div>
    <div class="checksum">0x4A7F</div>
  </footer>
</body>
</html>
```

### Checklist / チェックリスト

Before deploying any ORDL interface, verify:

- [ ] Only #000000 and #FFFFFF used
- [ ] All text has JP/EN pair
- [ ] No images, only ASCII art
- [ ] No rounded corners
- [ ] No gradients or shadows
- [ ] Monospace for all data
- [ ] Version number displayed
- [ ] Hex/binary decorations present
- [ ] Reduced motion respected
- [ ] Contrast slider functional

---

## Appendix / 付録

### Binary Reference

| Char | Binary | Hex | Decimal |
|------|--------|-----|---------|
| O | 01001111 | 0x4F | 79 |
| R | 01010010 | 0x52 | 82 |
| D | 01000100 | 0x44 | 68 |
| L | 01001100 | 0x4C | 76 |
| 0 | 00110000 | 0x30 | 48 |
| 1 | 00110001 | 0x31 | 49 |

### ASCII Art Library

```
╔══════════════════════════════════════════════════════════════╗
║  ORDL                                                        ║
║  零式                                                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   ██████╗ ██████╗ ██████╗ ██╗                              ║
║  ██╔═══██╗██╔══██╗██╔══██╗██║                              ║
║  ██║   ██║██████╔╝██║  ██║██║                              ║
║  ██║   ██║██╔══██╗██║  ██║██║                              ║
║  ╚██████╔╝██║  ██║██████╔╝███████╗                         ║
║   ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-08 | Initial release |

---

**Document Control**  
**文書管理**

```
DOC ID: ORDL-DS-001
VERSION: 1.0.0
STATUS: OPERATIONAL
CHECKSUM: 0x8F2A
CLASSIFICATION: UNCLASSIFIED
```

---

*黒い画面の中の白い影。*  
*A white silhouette in a black frame.*
