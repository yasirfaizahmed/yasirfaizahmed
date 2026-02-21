# Portfolio

## Structure

```text
.
├── index.html
├── projects.html
├── articles.html
├── quranic-notes.html
├── detail.html
└── assets
    ├── css
    │   └── main.css
    ├── data
    │   ├── articles.json
    │   ├── projects.json
    │   └── quranic_notes.json
    ├── images
    │   └── articles
    │       └── .gitkeep
    ├── videos
    │   └── .gitkeep
    ├── js
    │   ├── content.js
    │   └── main.js
└── scripts
    └── editor.py
```

## How to use

1. Create a GitHub repository named:
   - `YOUR_USERNAME.github.io` (for user site), or
   - Any name (for project site; then configure Pages accordingly).
2. Push these files to the repository root.
3. In GitHub: **Settings → Pages → Build and deployment → Deploy from a branch**.
4. Select your branch (`main`) and root folder (`/`).

## Customize content

Primary content source is JSON data files:

- `assets/data/projects.json`
- `assets/data/articles.json`
- `assets/data/quranic_notes.json`

Fallback/sample content is also available in `assets/js/content.js` arrays:

- `projects`
- `articles`
- `tafseerCollections`

> Note: pages load from JSON first (with `content.js` as fallback).

## Super simple way to add content (with image)

Use the local editor:

```bash
python3 scripts/editor.py
```

Then open:

```text
http://127.0.0.1:8787/editor
```

From the editor, you can add/edit/delete:

- Articles (`assets/data/articles.json`)
- Projects (`assets/data/projects.json`)
- Qur'anic notes (`assets/data/quranic_notes.json`)

Content automatically appears on:

- `articles.html`
- `projects.html`
- `quranic-notes.html`
- Home page featured sections

If you don't want an image, leave the image fields empty.

## Clickable cards and detail pages

- Project and article cards are now clickable.
- Each card opens `detail.html` for a focused full view.
- For best results, provide these fields in `assets/data/articles.json` entries:
  - `id` (stable slug)
  - `content` (full article body text)

## Hero background video (cinematic)

- Current page source uses: `assets/videos/bg.mp4`
- If you prefer `hero-bg.mp4`, rename/update `index.html` accordingly.
- Keep it short + compressed (`.mp4`, H.264) for fast GitHub Pages loading
- The design already applies layered overlays:
  - top is more opaque for text clarity
  - bottom is darker for cinematic depth
  - color accents are tuned away from cyan to a warmer tone matching dynamic footage

## Local preview

You can run a local static server:

```bash
python3 -m http.server 8080
```

Then open: `http://localhost:8080`
