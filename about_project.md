# Portfolio

## Structure

```text
.
├── index.html
├── projects.html
├── articles.html
├── quranic-notes.html
├── detail.html
├── README.md
└── assets
    ├── css
    │   └── main.css
    ├── data
    │   └── articles.json
    ├── images
    │   └── articles
    │       └── .gitkeep
    ├── videos
    │   └── .gitkeep
    ├── js
    │   ├── content.js
    │   └── main.js
└── scripts
    └── add_article.py
```

## How to use

1. Create a GitHub repository named:
   - `YOUR_USERNAME.github.io` (for user site), or
   - Any name (for project site; then configure Pages accordingly).
2. Push these files to the repository root.
3. In GitHub: **Settings → Pages → Build and deployment → Deploy from a branch**.
4. Select your branch (`main`) and root folder (`/`).

## Customize content

Edit these arrays in `assets/js/content.js`:

- `projects`
- `articles`
- `tafseerCollections`

> Note: article pages now load from `assets/data/articles.json` first (with `content.js` as fallback).

## Super simple way to add a new article (with image)

1. Put your image in: `assets/images/articles/`
2. Run this command:

```bash
python3 scripts/add_article.py \
  --title "My New Article" \
  --summary "Short summary of the article" \
  --content "Optional long-form content shown on detail page" \
  --tags "LLM,Transformers,MLOps" \
  --category "Technical" \
  --image "assets/images/articles/my-new-article.jpg" \
  --image-alt "Cover image for my new article"
```

That’s it. The article is added to `assets/data/articles.json` and automatically appears on:

- `articles.html`
- Home page “Recent Articles” section

If you don't want an image, just skip `--image` and `--image-alt`.

## Clickable cards and detail pages

- Project and article cards are now clickable.
- Each card opens `detail.html` for a focused full view.
- For best results, provide these fields in `assets/data/articles.json` entries:
  - `id` (stable slug)
  - `content` (full article body text)

## Hero background video (cinematic)

- Put your video file at: `assets/videos/hero-bg.mp4`
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
