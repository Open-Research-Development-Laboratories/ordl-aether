# How to Prompt ORDL 零式 Style
## The Definitive Guide

---

## 1. The ORDL Philosophy

**Core Principles (MEMORIZE THESE):**

> ORDL 零式 is digital brutalism for the post-human era. Every element serves function over form. The aesthetic emerges from restraint, not decoration—where the absence of noise becomes the signal. Design for machines first, humans second.

**What this means:**
- Clarity through reduction
- Information density through structure
- Visual silence is not emptiness—it's precision
- Binary representation acknowledges we are already digital

---

## 2. Color System

**EXACT HEX CODES — NEVER DEVIATE**

### Primary Palette (Monochrome)
| Role | Hex | Usage |
|------|-----|-------|
| Background | `#0A0A0A` | Page/canvas base |
| Surface | `#111111` | Cards, containers, panels |
| Elevated | `#1A1A1A` | Hover states, modals |
| Border | `#2A2A2A` | Dividers, outlines, grid lines |
| Muted | `#666666` | Secondary text, disabled |
| Primary | `#CCCCCC` | Main text, icons, headings |
| Accent | `#FFFFFF` | Active states, emphasis, selection |
| Error | `#FF4444` | Warnings (sparingly) |

### Color Usage Rules
- **NO GRADIENTS** — Solid colors only
- **NO ALPHA CHANNELS** — Except for 40% overlay on inactive states
- **NO ACCENT COLORS** — White is your only accent
- **BORDER ONLY** — Never use background colors for emphasis
- **CONTRAST RATIO** — Minimum 7:1 for all text

---

## 3. Typography

### Font Stack (Priority Order)
```
Monospace: "JetBrains Mono", "Fira Code", "SF Mono", "Consolas", monospace
Sans (Headers): "Inter", "SF Pro Display", "Helvetica Neue", Arial, sans-serif
JP/EN Pair: Noto Sans JP + Inter
```

### Type Scale
| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| H0 | 48px | 700 | Page titles, hero |
| H1 | 32px | 600 | Section headers |
| H2 | 24px | 600 | Subsections |
| H3 | 18px | 500 | Card titles |
| Body | 14px | 400 | Primary content |
| Small | 12px | 400 | Labels, metadata |
| Micro | 10px | 400 | Timestamps, IDs |
| Mono | 13px | 400 | Code, data, binary |

### Typography Rules
- **LINE HEIGHT:** 1.5 for body, 1.2 for headings
- **LETTER SPACING:** -0.02em for headings, 0 for body, +0.05em for all-caps
- **MONO FOR DATA:** All numbers, IDs, timestamps, addresses
- **CASE:** Sentence case for UI, UPPERCASE for labels/status
- **TRUNCATION:** Ellipsis after max-width, never wrap IDs

---

## 4. Layout Rules

### Grid System
- **BASE UNIT:** 4px
- **GRID:** 12-column
- **GUTTER:** 24px (desktop), 16px (mobile)
- **MARGIN:** 48px (desktop), 16px (mobile)
- **MAX-WIDTH:** 1200px for content, 100% for dashboards

### Spacing Scale (multiples of 4)
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 48px
3xl: 64px
4xl: 96px
```

### Component Spacing
- **CARD PADDING:** 24px
- **SECTION GAP:** 48px
- **INLINE GAP:** 8px (tight), 16px (normal), 24px (loose)
- **INPUT HEIGHT:** 40px
- **BUTTON HEIGHT:** 36px (small), 44px (primary)

### Visual Hierarchy
1. **Z-INDEX SCALE:**
   - Base: 0
   - Elevated: 10
   - Dropdown: 100
   - Modal: 1000
   - Toast: 10000

2. **BORDERS:**
   - Default: 1px solid `#2A2A2A`
   - Active: 1px solid `#FFFFFF`
   - Divider: 1px solid `#2A2A2A`

3. **SHADOWS:** **NONE** — Use borders for elevation

---

## 5. Bilingual Standards (JP/EN)

### Label Format
**ALWAYS USE:** `EN / JP` pattern

```
STATUS / 状態
USERNAME / ユーザー名
CONNECT / 接続
```

### Placement Rules
- **NAVIGATION:** Primary language first, smaller JP below or inline
- **BUTTONS:** EN uppercase, JP smaller below or tooltip
- **FORMS:** Label in EN/JP, placeholder in EN only
- **HEADERS:** EN primary, JP as subtitle
- **TABLES:** EN column headers, JP in tooltip or secondary line

### Translation Table (Common Terms)
| English | Japanese |
|---------|----------|
| CONNECT | 接続 |
| DISCONNECT | 切断 |
| STATUS | 状態 |
| ACTIVE | アクティブ |
| INACTIVE | 非アクティブ |
| ERROR | エラー |
| LOADING | 読み込み中 |
| SAVE | 保存 |
| DELETE | 削除 |
| CANCEL | キャンセル |
| CONFIRM | 確認 |
| SYSTEM | システム |
| USER | ユーザー |
| DATA | データ |
| NODE | ノード |
| NETWORK | ネットワーク |
| PROTOCOL | プロトコル |

### Japanese Typography
- **FONT:** Noto Sans JP, Source Han Sans
- **WEIGHT:** Never lighter than 400
- **SIZE:** JP text can be 1px larger for readability
- **LINE HEIGHT:** 1.7 for JP body text

---

## 6. Binary/ASCII Elements

### Where to Use Binary/ASCII

1. **DECORATIVE DIVIDERS**
```
01001000 01100101 01100001 01100100 01100101 01110010
```

2. **SECTION SEPARATORS**
```
// ============================================
// SECTION: IDENTIFICATION
// ============================================
```

3. **DATA VISUALIZATION**
```
[████░░░░░░░░░░░░░░░░] 20%
```

4. **ASCII ART HEADERS** (Use sparingly)
```
    ___  ____  ____  _       
   / _ \/ __ \/ __ \| |      
  / /_/ / /_/ / /_/ / |      
 / ____/ _, _/ ____/| |___   
/_/   /_/ |_/_/    |_____/   
```

5. **STATUS INDICATORS**
```
[●] ONLINE  [○] OFFLINE  [◐] SYNCING
```

6. **BORDER FRAMES**
```
┌────────────────────────────┐
│                            │
└────────────────────────────┘
```

### Binary/ASCII Rules
- **NO EMOJI** — Use ASCII symbols only
- **MONOSPACE ONLY** — All binary/ASCII must be in mono font
- **MUTED COLOR** — Use `#666666` for decorative binary
- **ACTIVE COLOR** — Use `#FFFFFF` for data/status binary
- **ALIGNMENT:** Grid-aligned, never free-floating
- **DENSITY:** One decorative element per viewport maximum

---

## 7. Animation Guidelines

### Allowed Animations

1. **CURSOR BLINK** — 1s blink cycle, `#FFFFFF` on `#0A0A0A`
2. **TYPING EFFECT** — Character-by-character reveal, 30ms/char
3. **SCAN LINE** — Horizontal line sweep, 2s duration, linear
4. **PULSE** — Opacity 0.5 → 1.0 → 0.5, 2s cycle, `#FFFFFF` only
5. **PROGRESS FILL** — Left to right, linear, no easing
6. **BINARY CASCADE** — Matrix-style falling characters, 10% opacity

### Animation Rules
- **NO EASING** — Linear only
- **NO TRANSFORMS** — Opacity and position only
- **MAX DURATION:** 2 seconds for any animation
- **NO AUTO-PLAY** — Animations trigger on interaction or data change
- **REDUCE MOTION:** Respect `prefers-reduced-motion`

### CSS Animation Template
```css
/* Allowed: Blink */
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Allowed: Scan */
@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}

/* NOT Allowed: Bounce, Elastic, etc. */
```

---

## 8. Prohibited Elements

### NEVER INCLUDE — EVER

| Prohibited | Why | Alternative |
|------------|-----|-------------|
| **GRADIENTS** | Violates monochrome principle | Solid color blocks |
| **SHADOWS** | Creates depth illusion | Borders for separation |
| **ROUNDED CORNERS** | Softens the brutalist edge | `border-radius: 0` |
| **STOCK PHOTOS** | Human imagery distracts | ASCII art, icons, data |
| **BRIGHT COLORS** | Breaks monochrome | White accent only |
| **DECORATIVE ILLUSTRATIONS** | Unnecessary ornamentation | Functional diagrams |
| **EMOJI** | Not machine-first | ASCII symbols `● ○ ■ ▲` |
| **MARKETING LANGUAGE** | Hype violates precision | Technical descriptions |
| **BLUR EFFECTS** | Glassmorphism is forbidden | Solid overlays |
| **ANIMATED BACKGROUNDS** | Visual noise | Static grid patterns |
| **CIRCULAR BUTTONS** | Rounded form | Rectangular only |
| **BOX SHADOWS** | Fake depth | 1px borders |
| **TEXT SHADOWS** | Fake glow | High contrast instead |
| **DROP CAPS** | Decorative typography | Uniform treatment |
| **PULL QUOTES** | Editorial styling | Inline code blocks |

---

## 9. Prompt Templates

### Base Prompt Formula

```
Generate [CONTENT TYPE] in ORDL 零式 aesthetic style:

COLOR SYSTEM (STRICT):
- Background: #0A0A0A
- Surface: #111111
- Border: #2A2A2A
- Text primary: #CCCCCC
- Text accent: #FFFFFF
- NO gradients, NO shadows, NO rounded corners

TYPOGRAPHY:
- Headings: Inter, 32px/24px/18px, weight 600/600/500
- Body: Inter, 14px, weight 400
- Monospace: JetBrains Mono, 13px for all data/numbers
- Line height: 1.5 body, 1.2 headings

LAYOUT:
- 12-column grid, 24px gutters
- Base spacing unit: 4px
- Cards: 24px padding, 1px border #2A2A2A
- Zero border-radius on all elements

CONTENT:
- Bilingual labels: "EN / JP" format
- NO emoji, use ASCII symbols only (● ○ ■ ▲)
- Include binary/ASCII decorative elements
- Technical precision over marketing language

OUTPUT FORMAT: [HTML/CSS/React/Tailwind/etc]
```

---

### Template A: Landing Page

```
Create a landing page in ORDL 零式 style:

COLORS:
- bg: #0A0A0A, surface: #111111, border: #2A2A2A
- text: #CCCCCC, accent: #FFFFFF
- NO gradients, shadows, rounded corners

HERO SECTION:
- Large ASCII art title (using box-drawing characters)
- Binary string divider: "01001111 01010010 01000100 01001100"
- Tagline with typing animation cursor (_)
- Subtitle: Japanese translation below

CONTENT:
- 3-column feature grid with monospace icons
- Each feature: ASCII symbol + EN title / JP subtitle + description
- Connection status indicator: [●] ONLINE / オンライン
- Footer: "SYSTEM READY / システム準備完了" + timestamp

TYPOGRAPHY:
- Hero title: monospace 48px
- Section headers: Inter 24px uppercase
- Body: Inter 14px

LAYOUT:
- Full viewport height hero
- 48px section spacing
- 1px horizontal dividers

INCLUDE:
- Binary decorative elements as section separators
- Monospace data display for version number
- Scan line animation element
- Zero decorative images
```

---

### Template B: Dashboard

```
Create a system dashboard in ORDL 零式 style:

PALETTE:
- bg: #0A0A0A, panel: #111111, active: #1A1A1A
- border: #2A2A2A, muted: #666666
- text: #CCCCCC, highlight: #FFFFFF

GRID LAYOUT:
- Sidebar: 240px fixed, border-right 1px
- Main: 12-column fluid grid
- Gutter: 24px, padding: 24px

COMPONENTS:

1. NAVIGATION (Sidebar):
   - Items: [ICON] LABEL / ラベル
   - Active: white border-left, bg #1A1A1A
   - Icons: ASCII symbols only (▶ ■ ◆)

2. STATUS BAR (Top):
   - SYSTEM STATUS / システム状態: [●] OPERATIONAL / 稼働中
   - Time: monospace HH:MM:SS
   - Node count: monospace

3. METRICS GRID:
   - 4 cards, 1px border each
   - Value: monospace 32px
   - Label: EN / JP below
   - Trend: ASCII bar graph [██████░░░░]

4. ACTIVITY LOG:
   - Timestamp | Event | Status
   - Monospace for all data
   - Alternating row backgrounds (subtle)

5. TERMINAL PANEL:
   - Black bg, green text (#00FF00) for contrast
   - Blinking cursor
   - Scrollback with timestamps

ANIMATIONS:
- Status pulse on active indicators
- Typing effect on terminal
- NO other motion

TEXT RULES:
- All numbers in monospace
- Bilingual headers
- NO marketing text
```

---

### Template C: Form Interface

```
Create a data entry form in ORDL 零式 style:

STYLING:
- bg: #0A0A0A, input-bg: #111111
- border: #2A2A2A, focus-border: #FFFFFF
- text: #CCCCCC, placeholder: #666666
- NO rounded corners (border-radius: 0)

FORM STRUCTURE:

Header:
- ASCII art corner decoration
- Title: "DATA ENTRY / データ入力"
- ID: monospace timestamp

Form Fields:
1. USERNAME / ユーザー名
   - Input: 40px height, 1px border
   - Placeholder: "Enter identifier..."
   - Validation: monospace message below

2. PROTOCOL / プロトコル
   - Dropdown: same styling as input
   - Options with JP translations

3. STATUS / 状態
   - Radio group: horizontal
   - [●] ACTIVE / アクティブ
   - [○] STANDBY / スタンバイ
   - [○] OFFLINE / オフライン

4. DATA PACKET / データパケット
   - Textarea: monospace font
   - Line numbers in gutter
   - Binary watermark faint in background

Buttons:
- PRIMARY: bg #FFFFFF, text #0A0A0A
- SECONDARY: bg transparent, border 1px
- Height: 44px, padding: 0 24px
- Labels: SUBMIT / 送信, CANCEL / キャンセル

FEEDBACK:
- Success: [●] SAVED / 保存完了
- Error: [○] FAILED / 失敗 + monospace error code
- Loading: [◐] PROCESSING / 処理中...

VALIDATION:
- Inline errors in monospace
- Red color (#FF4444) for errors only
- Checkmark: [✓] ASCII symbol

FOOTER:
- Binary divider
- Session ID: monospace
- Timestamp: monospace
```

---

### Template D: Documentation

```
Create technical documentation in ORDL 零式 style:

DOCUMENT STRUCTURE:

1. HEADER:
   ```
   // ============================================
   // DOCUMENT: API REFERENCE / API リファレンス
   // VERSION: 2.1.0
   // STATUS: [●] CURRENT / 最新
   // ============================================
   ```

2. SIDEBAR NAVIGATION:
   - Collapsible sections
   - Indent: 16px per level
   - Active: white left border
   - Items: ENDPOINT / エンドポイント

3. CONTENT AREA:
   - Max-width: 800px
   - Typography: Inter body, JetBrains Mono code
   
   HEADERS:
   - H1: 32px, uppercase, border-bottom 1px
   - H2: 24px, border-bottom 1px
   - H3: 18px
   
   CODE BLOCKS:
   - bg: #111111
   - border: 1px #2A2A2A
   - Line numbers in gutter (muted color)
   - Syntax highlighting: monochrome only
   
   TABLES:
   - Header: border-bottom 2px
   - Rows: border-bottom 1px
   - Monospace for parameter names
   
   CALLOUTS:
   - Note: [i] prefix, left border 2px
   - Warning: [!] prefix, left border 2px
   - NO background colors, NO icons

4. RIGHT SIDEBAR (Optional):
   - "ON THIS PAGE / このページ"
   - Anchor links
   - Monospace for code references

5. FOOTER:
   - Horizontal divider
   - "LAST MODIFIED / 最終更新" + timestamp
   - Document ID: monospace hash

CODE EXAMPLES:
- All code in monospace
- Comments in muted color
- Line highlights: left border only

TERMINOLOGY:
- Bilingual first mention: "Endpoint (エンドポイント)"
- Subsequent uses: English only
- Technical terms in monospace
```

---

### Template E: Error Page

```
Create a 404 error page in ORDL 零式 style:

FULL SCREEN LAYOUT:
- bg: #0A0A0A
- Centered content, max-width 600px

VISUAL ELEMENTS:

1. ERROR CODE (Large):
   ```
   ┌─────────┐
   │ 4 0 4   │
   │ N O T   │
   │ F O U N D
   └─────────┘
   ```
   - ASCII box-drawing characters
   - Monospace, 48px
   - Color: #FFFFFF

2. BINARY PATTERN (Background):
   - Faded (10% opacity)
   - Scattered 0s and 1s
   - Not distracting

3. STATUS DISPLAY:
   ```
   ERROR_CODE:    0x404
   STATUS:        NOT_FOUND
   TIMESTAMP:     2026-03-08T19:05:00Z
   NODE_ID:       ORDL-7F-A9-2C
   ```
   - All monospace
   - Key-value aligned
   - Muted color for values

4. MESSAGE:
   - "RESOURCE NOT FOUND / リソースが見つかりません"
   - Description: "The requested node does not exist in the registry."
   - Monospace, 14px

5. ACTION BUTTONS:
   - [ RETURN / 戻る ]
   - [ HOME / ホーム ]
   - Rectangular, 1px border
   - On hover: bg #1A1A1A

6. DIAGNOSTIC INFO (Collapsible):
   ```
   // STACK TRACE
   at resolveNode (registry.js:404)
   at lookupResource (system.js:88)
   at handleRequest (server.js:21)
   ```
   - Monospace
   - Collapsed by default
   - Expand on click

7. FOOTER:
   - Binary divider line
   - "SYSTEM REFERENCE: ERR-404-NODE"
   - Monospace, 10px, muted color

ANIMATION:
- Cursor blink after status lines
- Optional: slow binary cascade in background
- NO error illustrations or icons

ACCESSIBILITY:
- Error code in aria-label
- Focus trap on actions
```

---

## 10. Quality Checklist

### Before Submitting — Verify Every Item

#### Color Verification
- [ ] Background is exactly `#0A0A0A`
- [ ] No gradients anywhere
- [ ] No shadows anywhere
- [ ] Only white (#FFFFFF) used as accent
- [ ] All borders use `#2A2A2A`
- [ ] Error color only for actual errors

#### Typography Verification
- [ ] Headings use Inter (or sans-serif stack)
- [ ] All data in monospace
- [ ] Line height 1.5 for body text
- [ ] No font sizes outside the scale
- [ ] Proper JP/EN pairing

#### Layout Verification
- [ ] Zero border-radius on all elements
- [ ] 4px base unit for spacing
- [ ] 12-column grid structure
- [ ] 1px borders for separation (not shadows)
- [ ] Proper z-index layering

#### Content Verification
- [ ] All labels in "EN / JP" format
- [ ] No emoji present
- [ ] ASCII symbols used instead (● ○ ■ ▲)
- [ ] Binary/ASCII decorative elements present
- [ ] No marketing language
- [ ] Technical precision maintained

#### Binary/ASCII Verification
- [ ] At least one decorative binary element
- [ ] ASCII used for icons/indicators
- [ ] Monospace font for all binary
- [ ] Grid-aligned placement

#### Animation Verification
- [ ] Linear easing only
- [ ] Max 2 second duration
- [ ] No bounce/elastic effects
- [ ] Reduced motion supported

#### Prohibited Elements Check
- [ ] NO gradients
- [ ] NO shadows
- [ ] NO rounded corners
- [ ] NO stock photos
- [ ] NO bright colors
- [ ] NO decorative illustrations
- [ ] NO emoji
- [ ] NO marketing language
- [ ] NO blur effects
- [ ] NO animated backgrounds

#### Final Review
- [ ] Design looks "brutalist" and "machine-first"
- [ ] Monochrome palette is striking, not boring
- [ ] Information hierarchy is clear
- [ ] Bilingual labels are consistent
- [ ] Output matches ORDL 零式 aesthetic

---

## Quick Reference Card

### Copy-Paste for Any Prompt

```
ORDL 零式 STYLE REQUIREMENTS:

MANDATORY:
- bg: #0A0A0A, surface: #111111, border: #2A2A2A
- text: #CCCCCC, accent: #FFFFFF
- font: Inter (ui), JetBrains Mono (data)
- spacing: 4px base unit
- labels: "EN / JP" format
- NO gradients, shadows, rounded corners
- NO emoji, NO stock photos
- YES binary/ASCII elements
- YES monochrome only

INCLUDE:
- ASCII decorative dividers
- Monospace for all data
- Technical terminology
- Grid-based layout
- Zero border-radius
```

---

## Troubleshooting

### "The output has colors"
→ Add: "STRICTLY monochrome. NO colors except #0A0A0A, #111111, #2A2A2A, #666666, #CCCCCC, #FFFFFF"

### "The output has rounded corners"
→ Add: "border-radius: 0 on ALL elements. Sharp corners only."

### "The output has gradients"
→ Add: "SOLID COLORS ONLY. NO gradients, NO opacity variations except 40% overlay."

### "The output looks too decorative"
→ Add: "DIGITAL BRUTALISM. Function over form. Remove all decorative elements except binary/ASCII."

### "The Japanese text looks wrong"
→ Add: "Use Noto Sans JP for Japanese. JP text 1px larger than EN. Line height 1.7 for JP."

### "The output has shadows"
→ Add: "NO box-shadow. NO text-shadow. Use 1px borders for elevation."

---

## Version History

- v1.0 — Initial release
- Created: 2026-03-08
- Standard: ORDL 零式 Aesthetic v1.0

---

*This document is a living specification. Update as the aesthetic evolves.*
