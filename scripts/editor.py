#!/usr/bin/env python3
"""Local Medium-like editor for adding/editing/deleting articles, projects, and Quranic notes.

Run:
  python3 scripts/editor.py

Open:
  http://127.0.0.1:8787/editor
"""

from __future__ import annotations

import base64
import json
import mimetypes
import re
import subprocess
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = 8787


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return re.sub(r"-+", "-", text)


def data_file_for_kind(kind: str) -> Path:
    if kind == "article":
        return ROOT / "assets" / "data" / "articles.json"
    if kind == "project":
        return ROOT / "assets" / "data" / "projects.json"
    if kind == "quranic":
        return ROOT / "assets" / "data" / "quranic_notes.json"
    raise ValueError("kind must be article, project, or quranic")


def ensure_json_array(path: Path) -> list:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]\n", encoding="utf-8")
        return []
    data = json.loads(path.read_text(encoding="utf-8") or "[]")
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain JSON array")
    return data


def save_image(kind: str, image_name: str, image_data: str) -> str:
    header, encoded = image_data.split(",", 1)
    mime = header.split(";")[0].replace("data:", "").strip()
    ext = mimetypes.guess_extension(mime) or ".png"
    safe_name = slugify(Path(image_name).stem) or f"{kind}-thumbnail"
    file_name = f"{safe_name}{ext}"

    target_dir = ROOT / "assets" / "images" / "articles"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / file_name).write_bytes(base64.b64decode(encoded))
    return f"assets/images/articles/{file_name}"


def list_entries(kind: str) -> list[dict]:
    entries = ensure_json_array(data_file_for_kind(kind))
    out = []
    for item in entries:
        out.append(
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "body": item.get("content", item.get("details", item.get("summary", ""))),
                "tags": ", ".join(item.get("tags", [])),
                "category": item.get("category", ""),
                "link": item.get("link", "#"),
                "image": item.get("image", ""),
                "imageAlt": item.get("imageAlt", ""),
            }
        )
    return out


def compose_body_from_additions(kind: str, additions: list[dict]) -> str:
    blocks: list[str] = []
    for raw in additions:
        if not isinstance(raw, dict):
            continue
        block_type = str(raw.get("type", "")).strip().lower()
        if block_type == "paragraph":
            text = str(raw.get("text", "")).strip()
            if text:
                blocks.append(text)
            continue
        if block_type == "image":
            image_path = str(raw.get("imagePath", "")).strip()
            image_data = str(raw.get("imageData", "")).strip()
            image_name = str(raw.get("imageName", "inline-image")).strip() or "inline-image"
            image_alt = str(raw.get("imageAlt", "")).strip()
            if image_data:
                image_path = save_image(kind, image_name, image_data)
            if image_path:
                blocks.append(f"![{image_alt}]({image_path})")
    return "\n\n".join(blocks).strip()


def persist_entry(payload: dict) -> dict:
    kind = str(payload.get("kind", "article")).strip().lower()
    if kind not in {"article", "project", "quranic"}:
        raise ValueError("Invalid kind")

    title = str(payload.get("title", "")).strip()
    about = str(payload.get("about", "")).strip()
    body = str(payload.get("body", "")).strip()
    additions = payload.get("additions", [])
    if isinstance(additions, list) and additions:
        body = compose_body_from_additions(kind, additions)

    if not title or not about or not body:
        raise ValueError("title, about, and at least one content block are required")

    original_id = str(payload.get("originalId", "")).strip()
    entry_id = slugify(title)
    tags = [t.strip() for t in str(payload.get("tags", "")).split(",") if t.strip()]
    link = str(payload.get("link", "#")).strip() or "#"
    image_alt = str(payload.get("imageAlt", "")).strip()
    category = str(payload.get("category", "Technical")).strip() or "Technical"
    image_path = str(payload.get("imagePath", "")).strip()

    image_data = str(payload.get("imageData", "")).strip()
    image_name = str(payload.get("imageName", "thumbnail")).strip() or "thumbnail"
    if image_data:
        image_path = save_image(kind, image_name, image_data)

    item = {
        "id": entry_id,
        "title": title,
        "summary": about,
        "tags": tags,
        "link": link,
        "image": image_path,
        "imageAlt": image_alt,
    }
    if kind == "article":
        item["category"] = category
        item["content"] = body
    else:
        item["details"] = body

    file_path = data_file_for_kind(kind)
    entries = ensure_json_array(file_path)
    match_ids = {entry_id}
    if original_id:
        match_ids.add(original_id)
    entries = [e for e in entries if str(e.get("id", "")) not in match_ids]
    entries.insert(0, item)
    file_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {"ok": True, "kind": kind, "id": entry_id, "title": title, "file": str(file_path.relative_to(ROOT))}


def delete_entry(payload: dict) -> dict:
    kind = str(payload.get("kind", "")).strip().lower()
    entry_id = str(payload.get("id", "")).strip()
    if kind not in {"article", "project", "quranic"} or not entry_id:
        raise ValueError("kind and id are required")

    file_path = data_file_for_kind(kind)
    entries = ensure_json_array(file_path)
    before = len(entries)
    entries = [e for e in entries if str(e.get("id", "")) != entry_id]
    if len(entries) == before:
        raise ValueError("Entry not found")
    file_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "kind": kind, "id": entry_id, "file": str(file_path.relative_to(ROOT))}


def deploy_to_main(payload: dict) -> dict:
    commit_message = str(payload.get("message", "")).strip() or "Update portfolio content from local editor"

    def run_git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    check_repo = run_git("rev-parse", "--is-inside-work-tree")
    if check_repo.returncode != 0:
        raise ValueError("Current directory is not a git repository")

    add = run_git("add", "-A")
    if add.returncode != 0:
        raise ValueError(add.stderr.strip() or "git add failed")

    diff = run_git("diff", "--cached", "--quiet")
    if diff.returncode == 0:
        return {
            "ok": True,
            "message": "No staged changes to deploy.",
            "details": "Working tree has no new changes.",
        }

    commit = run_git("commit", "-m", commit_message)
    if commit.returncode != 0:
        raise ValueError(commit.stderr.strip() or commit.stdout.strip() or "git commit failed")

    push = run_git("push", "origin", "main")
    if push.returncode != 0:
        raise ValueError(push.stderr.strip() or push.stdout.strip() or "git push failed")

    return {
        "ok": True,
        "message": "Deployed successfully to origin/main",
        "details": (commit.stdout.strip() + "\n" + push.stdout.strip()).strip(),
    }


def editor_page() -> str:
    return r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" type="image/jpeg" href="/icons/tab_icon.jpg" />
  <link rel="icon" type="image/png" href="/icons/tab_icon.png" />
  <title>Editor</title>
  <style>
    :root { --ink:#242424; --muted:#6b6b6b; --line:#e6e6e6; --bg:#fff; --green:#1a8917; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--ink); font-family: Charter, "Times New Roman", serif; }
    .topbar { position:sticky; top:0; z-index:10; background:#fff; border-bottom:1px solid var(--line); }
    .topbar-inner { max-width:1260px; margin:0 auto; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; gap:12px; }
    .brand { font:700 1.05rem Inter, system-ui, sans-serif; }
    .controls { display:flex; gap:10px; align-items:center; }
    .kind, .action-btn { border:1px solid var(--line); border-radius:999px; padding:8px 12px; font:500 0.9rem Inter, system-ui, sans-serif; background:#fff; }
    .save-btn { border:none; background:var(--green); color:#fff; border-radius:999px; padding:8px 14px; font:600 0.9rem Inter, system-ui, sans-serif; cursor:pointer; }
    .deploy-btn { border:none; background:#242424; color:#fff; border-radius:999px; padding:8px 14px; font:600 0.9rem Inter, system-ui, sans-serif; cursor:pointer; }
    .shell { max-width:1260px; margin:0 auto; padding:20px; display:grid; grid-template-columns:220px minmax(0, 1fr) 320px; gap:22px; }
    .card { border:1px solid var(--line); border-radius:10px; padding:14px; background:#fff; }
    .card h3 { margin:0 0 10px; font:700 0.95rem Inter, system-ui, sans-serif; }
    label { display:block; margin:10px 0 6px; color:var(--muted); font:500 0.8rem Inter, system-ui, sans-serif; }
    input[type="text"], textarea { width:100%; border:1px solid var(--line); border-radius:8px; padding:10px 12px; font:400 0.93rem Inter, system-ui, sans-serif; }
    .title { width:100%; border:none; outline:none; font:700 clamp(2rem, 3vw, 2.8rem)/1.2 Inter, system-ui, sans-serif; margin:8px 0 14px; }
    .about { border:none; border-left:3px solid var(--line); border-radius:0; outline:none; padding:0 0 0 12px; min-height:80px; resize:vertical; color:#4f4f4f; font:500 1.02rem/1.55 Inter, system-ui, sans-serif; }
    .body { margin-top:22px; border:none; outline:none; min-height:420px; resize:vertical; font:400 1.16rem/1.9 Charter, "Times New Roman", serif; }
    .additions-bar { margin-top:20px; display:flex; gap:10px; align-items:center; }
    .additions-select { border:1px solid var(--line); border-radius:999px; padding:8px 12px; font:500 0.86rem Inter, system-ui, sans-serif; background:#fff; }
    .additions-btn { border:1px solid var(--line); background:#fff; border-radius:999px; padding:8px 12px; font:500 0.84rem Inter, system-ui, sans-serif; cursor:pointer; }
    .additions-list { margin-top:14px; display:grid; gap:12px; }
    .addition-block { border:1px solid var(--line); border-radius:10px; padding:12px; background:#fff; }
    .addition-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
    .addition-title { font:600 0.85rem Inter, system-ui, sans-serif; color:#3c3c3c; text-transform:capitalize; }
    .remove-block { border:1px solid #ffd8d8; color:#b71c1c; background:#fff; border-radius:999px; padding:4px 10px; font:500 0.76rem Inter, system-ui, sans-serif; cursor:pointer; }
    .addition-image-preview { margin-top:10px; width:100%; max-height:220px; object-fit:cover; border-radius:8px; display:none; }
    .thumb-wrap { margin-top:16px; border:1px dashed var(--line); border-radius:10px; padding:12px; }
    .thumb-preview { margin-top:10px; width:100%; max-height:180px; object-fit:cover; border-radius:8px; display:none; }
    .status { margin-top:12px; font:500 0.88rem Inter, system-ui, sans-serif; }
    .ok { color:#1a8917; } .err { color:#c62828; }
    .items { display:grid; gap:10px; max-height:72vh; overflow:auto; }
    .item { border:1px solid var(--line); border-radius:8px; padding:10px; }
    .item b { display:block; font:600 0.9rem Inter, system-ui, sans-serif; margin-bottom:4px; }
    .item p { margin:0; color:var(--muted); font:400 0.82rem/1.4 Inter, system-ui, sans-serif; }
    .item-actions { margin-top:8px; display:flex; gap:8px; }
    .mini-btn { border:1px solid var(--line); background:#fff; border-radius:999px; padding:4px 10px; font:500 0.78rem Inter, system-ui, sans-serif; cursor:pointer; }
    .mini-danger { border-color:#ffd8d8; color:#b71c1c; }
    @media (max-width:1100px){ .shell{ grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand">Medium-style Portfolio Editor</div>
      <div class="controls">
        <select id="kind" class="kind" aria-label="content type">
          <option value="article">Article</option>
          <option value="project">Project</option>
          <option value="quranic">Quranic Note</option>
        </select>
        <button id="newBtn" class="action-btn" type="button">New</button>
        <button id="saveBtn" class="save-btn" type="button">Save</button>
        <button id="deployBtn" class="deploy-btn" type="button">Deploy</button>
      </div>
    </div>
  </header>

  <main class="shell">
    <aside class="card">
      <h3>Meta</h3>
      <label for="tags">Tags (comma separated)</label>
      <input id="tags" type="text" placeholder="MLOps, LLM, DevOps" />

      <label for="category">Category (article)</label>
      <input id="category" type="text" placeholder="Technical" />

      <label for="link">External link</label>
      <input id="link" type="text" placeholder="https://..." />

      <label for="imageAlt">Thumbnail alt text</label>
      <input id="imageAlt" type="text" placeholder="Describe thumbnail" />

      <label for="imagePath">Or existing image path</label>
      <input id="imagePath" type="text" placeholder="assets/images/articles/example.jpg" />

      <div id="status" class="status"></div>
    </aside>

    <section>
      <input id="title" class="title" type="text" placeholder="Title" />
      <textarea id="about" class="about" placeholder="About section (overview)..."></textarea>
      <div class="thumb-wrap">
        <label for="thumb">Thumbnail image</label>
        <input id="thumb" type="file" accept="image/*" />
        <img id="thumbPreview" class="thumb-preview" alt="thumbnail preview" />
      </div>
      <div class="additions-bar">
        <select id="additionType" class="additions-select" aria-label="Add content block">
          <option value="paragraph">New paragraph</option>
          <option value="image">Add image</option>
        </select>
        <button id="addBlockBtn" class="additions-btn" type="button">Add</button>
      </div>
      <div id="additions" class="additions-list"></div>
      <textarea id="body" class="body" style="display:none" aria-hidden="true"></textarea>
      <p style="margin-top:8px;color:#6b6b6b;font:400 0.78rem/1.45 Inter,system-ui,sans-serif;">
        Add multiple paragraphs and images in order. Images render in detail view using markdown syntax.
      </p>
    </section>

    <aside class="card">
      <h3>Saved items</h3>
      <div id="items" class="items"></div>
    </aside>
  </main>

  <script>
    const state = { originalId: "", imageData: "", imageName: "", additions: [], nextAdditionId: 1 };
    const byId = (id) => document.getElementById(id);
    const statusNode = byId("status");

    function setStatus(msg, kind = "") {
      statusNode.className = `status ${kind}`.trim();
      statusNode.textContent = msg;
    }

    function createAddition(type, data = {}) {
      const addition = {
        id: state.nextAdditionId++,
        type,
        text: "",
        imagePath: "",
        imageAlt: "",
        imageData: "",
        imageName: "",
      };
      Object.assign(addition, data || {});
      return addition;
    }

    function parseBodyToAdditions(bodyText) {
      const source = String(bodyText || "").trim();
      if (!source) return [];
      const chunks = source.split(/\n\s*\n+/).map((part) => part.trim()).filter(Boolean);
      const out = [];
      chunks.forEach((chunk) => {
        const imageMatch = chunk.match(/^!\[(.*?)\]\((.*?)\)$/s);
        if (imageMatch) {
          out.push(createAddition("image", { imageAlt: imageMatch[1] || "", imagePath: imageMatch[2] || "" }));
        } else {
          out.push(createAddition("paragraph", { text: chunk }));
        }
      });
      return out;
    }

    function renderAdditions() {
      const container = byId("additions");
      container.innerHTML = "";
      state.additions.forEach((block) => {
        const card = document.createElement("div");
        card.className = "addition-block";

        const head = document.createElement("div");
        head.className = "addition-head";
        const title = document.createElement("div");
        title.className = "addition-title";
        title.textContent = block.type === "image" ? "Image" : "Paragraph";
        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "remove-block";
        removeBtn.textContent = "Remove";
        removeBtn.addEventListener("click", () => {
          state.additions = state.additions.filter((x) => x.id !== block.id);
          renderAdditions();
        });
        head.appendChild(title);
        head.appendChild(removeBtn);
        card.appendChild(head);

        if (block.type === "paragraph") {
          const area = document.createElement("textarea");
          area.placeholder = "Write paragraph...";
          area.style.minHeight = "120px";
          area.value = block.text || "";
          area.addEventListener("input", (e) => {
            block.text = e.target.value;
          });
          card.appendChild(area);
        } else {
          const altLabel = document.createElement("label");
          altLabel.textContent = "Image alt text";
          const altInput = document.createElement("input");
          altInput.type = "text";
          altInput.placeholder = "Describe image";
          altInput.value = block.imageAlt || "";
          altInput.addEventListener("input", (e) => {
            block.imageAlt = e.target.value;
          });

          const pathLabel = document.createElement("label");
          pathLabel.textContent = "Or existing image path";
          const pathInput = document.createElement("input");
          pathInput.type = "text";
          pathInput.placeholder = "assets/images/articles/example.jpg";
          pathInput.value = block.imagePath || "";
          pathInput.addEventListener("input", (e) => {
            block.imagePath = e.target.value;
          });

          const fileLabel = document.createElement("label");
          fileLabel.textContent = "Upload image";
          const fileInput = document.createElement("input");
          fileInput.type = "file";
          fileInput.accept = "image/*";
          const preview = document.createElement("img");
          preview.className = "addition-image-preview";
          if (block.imageData) {
            preview.src = block.imageData;
            preview.style.display = "block";
          } else if (block.imagePath) {
            preview.src = block.imagePath;
            preview.style.display = "block";
          }
          fileInput.addEventListener("change", async (e) => {
            const file = e.target.files && e.target.files[0];
            block.imageData = "";
            block.imageName = "";
            if (!file) return;
            block.imageName = file.name;
            const dataUrl = await new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () => resolve(String(reader.result || ""));
              reader.onerror = reject;
              reader.readAsDataURL(file);
            });
            block.imageData = dataUrl;
            preview.src = dataUrl;
            preview.style.display = "block";
          });

          card.appendChild(altLabel);
          card.appendChild(altInput);
          card.appendChild(pathLabel);
          card.appendChild(pathInput);
          card.appendChild(fileLabel);
          card.appendChild(fileInput);
          card.appendChild(preview);
        }

        container.appendChild(card);
      });
    }

    function collectAdditionsPayload() {
      return state.additions
        .map((block) => {
          if (block.type === "paragraph") {
            return { type: "paragraph", text: String(block.text || "").trim() };
          }
          return {
            type: "image",
            imageAlt: String(block.imageAlt || "").trim(),
            imagePath: String(block.imagePath || "").trim(),
            imageData: String(block.imageData || "").trim(),
            imageName: String(block.imageName || "").trim(),
          };
        })
        .filter((block) => {
          if (block.type === "paragraph") return !!block.text;
          return !!(block.imagePath || block.imageData);
        });
    }

    function clearForm() {
      state.originalId = "";
      state.imageData = "";
      state.imageName = "";
      byId("title").value = "";
      byId("about").value = "";
      byId("body").value = "";
      state.additions = [];
      state.nextAdditionId = 1;
      byId("tags").value = "";
      byId("category").value = "";
      byId("link").value = "";
      byId("imageAlt").value = "";
      byId("imagePath").value = "";
      byId("thumb").value = "";
      const preview = byId("thumbPreview");
      preview.src = "";
      preview.style.display = "none";
      renderAdditions();
    }

    function fillForm(item) {
      state.originalId = item.id || "";
      state.imageData = "";
      state.imageName = "";
      byId("title").value = item.title || "";
      byId("about").value = item.summary || "";
      byId("body").value = item.body || "";
      state.additions = parseBodyToAdditions(item.body || "");
      byId("tags").value = item.tags || "";
      byId("category").value = item.category || "";
      byId("link").value = item.link || "";
      byId("imageAlt").value = item.imageAlt || "";
      byId("imagePath").value = item.image || "";
      const preview = byId("thumbPreview");
      if (item.image) {
        preview.src = item.image;
        preview.style.display = "block";
      } else {
        preview.src = "";
        preview.style.display = "none";
      }
      renderAdditions();
      setStatus(`Editing: ${item.title}`);
    }

    async function loadList() {
      const kind = byId("kind").value;
      const response = await fetch(`/api/list?kind=${encodeURIComponent(kind)}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Could not load items");
      const root = byId("items");
      root.innerHTML = "";
      if (!data.items.length) {
        root.innerHTML = "<p style='margin:0;color:#6b6b6b;font:400 .86rem Inter,sans-serif'>No items yet.</p>";
        return;
      }

      data.items.forEach((item) => {
        const card = document.createElement("div");
        card.className = "item";
        card.innerHTML = `
          <b>${item.title || "Untitled"}</b>
          <p>${(item.summary || "").slice(0, 110)}</p>
          <div class="item-actions">
            <button class="mini-btn" type="button" data-action="edit">Edit</button>
            <button class="mini-btn mini-danger" type="button" data-action="delete">Delete</button>
          </div>
        `;
        card.querySelector('[data-action="edit"]').addEventListener("click", () => fillForm(item));
        card.querySelector('[data-action="delete"]').addEventListener("click", async () => {
          if (!confirm(`Delete ${item.title}?`)) return;
          await deleteItem(item.id);
        });
        root.appendChild(card);
      });
    }

    async function deleteItem(id) {
      const payload = { kind: byId("kind").value, id };
      const response = await fetch("/api/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Delete failed");
      setStatus(`Deleted ${id}`, "ok");
      if (state.originalId === id) clearForm();
      await loadList();
    }

    byId("thumb").addEventListener("change", async (e) => {
      const file = e.target.files && e.target.files[0];
      state.imageData = "";
      state.imageName = "";
      if (!file) return;
      state.imageName = file.name;
      const dataUrl = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result || ""));
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
      state.imageData = dataUrl;
      const preview = byId("thumbPreview");
      preview.src = dataUrl;
      preview.style.display = "block";
    });

    byId("newBtn").addEventListener("click", () => {
      clearForm();
      setStatus("New draft");
    });

    byId("kind").addEventListener("change", async () => {
      clearForm();
      await loadList();
    });

    byId("addBlockBtn").addEventListener("click", () => {
      const type = byId("additionType").value;
      if (type === "image") {
        state.additions.push(createAddition("image"));
      } else {
        state.additions.push(createAddition("paragraph"));
      }
      renderAdditions();
    });

    byId("saveBtn").addEventListener("click", async () => {
      try {
        setStatus("Saving...");
        const additions = collectAdditionsPayload();
        if (!additions.length) {
          throw new Error("Please add at least one paragraph or image block.");
        }
        const payload = {
          kind: byId("kind").value,
          originalId: state.originalId,
          title: byId("title").value,
          about: byId("about").value,
          body: byId("body").value,
          additions,
          tags: byId("tags").value,
          category: byId("category").value,
          link: byId("link").value,
          imageAlt: byId("imageAlt").value,
          imagePath: byId("imagePath").value,
          imageData: state.imageData,
          imageName: state.imageName,
        };
        const response = await fetch("/api/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Save failed");
        state.originalId = data.id;
        state.imageData = "";
        state.imageName = "";
        byId("thumb").value = "";
        setStatus(`Saved ${data.kind}: ${data.title}`, "ok");
        await loadList();
      } catch (err) {
        setStatus(err.message || String(err), "err");
      }
    });

    byId("deployBtn").addEventListener("click", async () => {
      try {
        const ok = confirm("Deploy all current local changes to origin/main?");
        if (!ok) return;
        const message = prompt("Commit message", "Update portfolio content from local editor") || "";
        setStatus("Deploying...");
        const response = await fetch("/api/deploy", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Deploy failed");
        setStatus(data.message || "Deployed", "ok");
      } catch (err) {
        setStatus(err.message || String(err), "err");
      }
    });

    renderAdditions();
    loadList().catch((err) => setStatus(err.message || String(err), "err"));
  </script>
</body>
</html>
"""


class EditorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _json(self, status: HTTPStatus, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path)
        if route.path in {"/", "/editor", "/editor/"}:
            html = editor_page().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        if route.path == "/api/list":
            try:
                qs = parse_qs(route.query)
                kind = (qs.get("kind", ["article"])[0] or "article").strip().lower()
                self._json(HTTPStatus.OK, {"ok": True, "items": list_entries(kind)})
            except Exception as exc:  # noqa: BLE001
                self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        return super().do_GET()

    def do_POST(self):
        route = urlparse(self.path).path
        if route not in {"/api/save", "/api/delete", "/api/deploy"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads((self.rfile.read(size) or b"{}").decode("utf-8"))
            if route == "/api/save":
                self._json(HTTPStatus.OK, persist_entry(payload))
            elif route == "/api/deploy":
                self._json(HTTPStatus.OK, deploy_to_main(payload))
            else:
                self._json(HTTPStatus.OK, delete_entry(payload))
        except Exception as exc:  # noqa: BLE001
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), EditorHandler)
    print(f"Editor running on http://{HOST}:{PORT}/editor")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
