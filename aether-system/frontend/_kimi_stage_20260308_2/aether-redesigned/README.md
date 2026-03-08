# AETHER v2.0

## Adaptive Earth & Technology Harmonization Engine

> A NASA-inspired swarm intelligence platform with industrial, government-contractor aesthetics.

---

## 🎨 Design Philosophy

**"Monochrome Machinery"** - Brutalist terminal meets mechanical watch movement.

- **Colors**: Deep charcoal (#0a0a0a) backgrounds, warm cream (#f5f2e9) text, amber (#f59e0b) accents only for CTAs
- **Typography**: IBM Plex Mono (technical), Space Grotesk (UI)
- **Aesthetic**: Industrial, not playful. Aircraft cockpit, not candy store.
- **Philosophy**: Structure over simulation. Government contractor, not Silicon Valley flashy.

---

## 🚀 Quick Start

```bash
# Clone and enter directory
cd aether-redesigned

# Open in browser (no build step!)
open index.html

# Or serve locally
python -m http.server 8080
# Then visit http://localhost:8080
```

---

## 🏗️ Architecture

### 5-Zone Spatial Layout

```
┌─────────────────────────────────────────────────────────┐
│  TOP BAR (48px) - Logo, breadcrumbs, search, status    │
├──────────┬──────────────────────────────┬───────────────┤
│          │                              │               │
│ SIDEBAR  │      MAIN CANVAS             │ CONTEXT PANEL │
│ (240px)  │      (Dynamic Views)         │ (320px)       │
│          │                              │               │
│          │  - Topology View             │               │
│          │  - Timeline Debug            │               │
│          │  - Mentality Panel           │               │
│          │  - Ghost Fleets              │               │
│          │                              │               │
├──────────┴──────────────────────────────┴───────────────┤
│  ⌘K - Command Palette (Overlay)                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
aether-redesigned/
├── index.html              # Main entry point
├── README.md               # This file
├── css/
│   ├── design-tokens.css   # Color palette, typography, spacing
│   ├── base.css            # Reset + utility classes
│   ├── components.css      # Buttons, inputs, cards, etc.
│   ├── layout.css          # 5-zone layout system
│   ├── topology.css        # Swarm visualization styles
│   ├── timeline.css        # Temporal debugging styles
│   └── mentality.css       # Physical switches & dials
├── js/
│   ├── command-palette.js  # ⌘K fuzzy search
│   ├── sidebar.js          # Navigation + context panel
│   ├── topology.js         # Force-directed graph
│   ├── timeline.js         # Scrubber + causal chain
│   ├── mentality.js        # Switches, dials, meters
│   └── app.js              # Main application
└── assets/
    └── aether-icon.svg     # Favicon
```

---

## ✨ Key Features

### 1. Swarm Topology View
- Force-directed graph visualization
- Live message flow animation
- Interactive node selection
- Real-time statistics

### 2. Temporal Debugging
- Timeline scrubber with drag-to-seek
- Causal chain visualization
- Branch point markers
- Save scenarios as test cases

### 3. Mentality Panel
- Physical toggle switches
- Rotary dial controls
- Compliance meters
- Aircraft cockpit aesthetic

### 4. Ghost Fleets
- Shadow deployment testing
- Opacity slider for comparison
- Divergence highlighting
- Promote to production

### 5. Command Palette
- ⌘K keyboard shortcut
- Fuzzy search
- Keyboard navigation (↑↓, Enter, Escape)

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` / `Ctrl+K` | Open Command Palette |
| `⌘1` - `⌘6` | Switch views (Topology, Agents, Timeline, Mentality, Ghosts, Logs) |
| `⌘,` | Open Settings |
| `Esc` | Close palette / panels |
| `↑` `↓` | Navigate palette results |
| `Enter` | Select palette item |

---

## 🎨 Design Tokens

### Colors
```css
--charcoal-950: #050505;  /* Background */
--charcoal-900: #0a0a0a;  /* Surfaces */
--charcoal-800: #111111;  /* Cards */
--cream-100: #f5f2e9;     /* Primary text */
--cream-400: #9a958a;     /* Secondary text */
--amber-400: #f59e0b;     /* Accents only */
```

### Typography
```css
--font-mono: 'IBM Plex Mono';    /* Code, data */
--font-ui: 'Space Grotesk';      /* UI elements */
```

### Spacing
- Base unit: 4px
- All spacing multiples of 4

---

## 🛠️ Development

### No Build Step Required

This is vanilla HTML/CSS/JS. No npm, no webpack, no dependencies.

Just open `index.html` in a browser.

### Adding New Views

1. Create HTML section in `index.html`:
```html
<section class="view my-view hidden" id="my-view">
  <!-- Content -->
</section>
```

2. Add sidebar link:
```html
<li class="sidebar-item">
  <a href="#my-view" class="sidebar-link">My View</a>
</li>
```

3. Add to command palette in `js/command-palette.js`

---

## 🚀 Deployment

### Static Hosting

```bash
# Copy to any static host
cp -r aether-redesigned/* /var/www/html/

# Or use GitHub Pages
# Or use Netlify/Vercel drop
```

### Docker

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
```

---

## 📸 Screenshots

### Topology View
Force-directed graph with live message flow, interactive nodes, and real-time statistics.

### Timeline Debug
Scrub through time, view causal chains, save test scenarios.

### Mentality Panel
Physical switches and dials for fleet-wide behavioral constraints.

---

## 🔮 Roadmap

- [ ] WebSocket integration for real-time data
- [ ] Agent state machine visualization
- [ ] Performance metrics dashboard
- [ ] Export topology as SVG/PNG
- [ ] Dark/light theme toggle
- [ ] Mobile responsiveness

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Built with ❤️ and industrial precision.**

*Not futuristic. Industrial.*