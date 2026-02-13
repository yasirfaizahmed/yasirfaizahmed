function createCard(item, kind = "generic") {
  const article = document.createElement("article");
  article.className = "content-card";
  const isDetailKind = kind === "article" || kind === "project";
  const detailId = item.id || slugify(item.title || "item");
  const detailLink = `detail.html?type=${encodeURIComponent(kind)}&id=${encodeURIComponent(detailId)}`;

  if (item.image) {
    const media = document.createElement("div");
    media.className = "card-media";
    const img = document.createElement("img");
    img.src = item.image;
    img.alt = item.imageAlt || `${item.title} cover image`;
    img.loading = "lazy";
    media.appendChild(img);
    if (isDetailKind) {
      const mediaAnchor = document.createElement("a");
      mediaAnchor.href = detailLink;
      mediaAnchor.setAttribute("aria-label", `Open details for ${item.title}`);
      mediaAnchor.appendChild(media);
      article.appendChild(mediaAnchor);
    } else {
      article.appendChild(media);
    }
  }

  const title = document.createElement("h3");
  if (isDetailKind) {
    const titleAnchor = document.createElement("a");
    titleAnchor.className = "title-link";
    titleAnchor.href = detailLink;
    titleAnchor.textContent = item.title;
    title.appendChild(titleAnchor);
  } else {
    title.textContent = item.title;
  }

  const summary = document.createElement("p");
  summary.textContent = item.summary;

  const tags = document.createElement("div");
  tags.className = "tags";

  (item.tags || []).forEach((tag) => {
    const span = document.createElement("span");
    span.className = "tag";
    span.textContent = tag;
    tags.appendChild(span);
  });

  article.appendChild(title);
  article.appendChild(summary);
  article.appendChild(tags);

  if (kind === "article" && item.category) {
    const meta = document.createElement("p");
    meta.className = "muted";
    meta.textContent = `Category: ${item.category}`;
    article.appendChild(meta);
  }

  if (item.link && item.link !== "#") {
    const cta = document.createElement("a");
    cta.className = "text-link";
    cta.href = item.link;
    cta.textContent = "External link →";
    cta.target = "_blank";
    cta.rel = "noopener noreferrer";
    article.appendChild(cta);
  }

  if (isDetailKind) {
    const detailsCta = document.createElement("a");
    detailsCta.className = "text-link";
    detailsCta.href = detailLink;
    detailsCta.textContent = kind === "project" ? "View project details →" : "Read article →";
    article.appendChild(detailsCta);
  }

  return article;
}

function renderItems(containerId, data, kind) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!Array.isArray(data) || data.length === 0) {
    container.innerHTML = "<p class='muted'>No items found.</p>";
    return;
  }

  container.innerHTML = "";
  data.forEach((item) => container.appendChild(createCard(item, kind)));
}

function slugify(text) {
  return String(text || "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
}

function escapeHtml(text) {
  return String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderInlineMarkdown(text) {
  let html = escapeHtml(text);

  html = html.replace(
    /!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)/g,
    '<img src="$2" alt="$1" loading="lazy" referrerpolicy="no-referrer" />'
  );
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  html = html.replace(/_([^_]+)_/g, "<em>$1</em>");
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  return html;
}

function markdownToHtml(markdownText) {
  const text = String(markdownText || "").replace(/\r\n/g, "\n");
  if (!text.trim()) return "";

  const lines = text.split("\n");
  const blocks = [];
  let inUl = false;
  let inOl = false;
  let inCode = false;
  let codeLines = [];
  let paragraphLines = [];

  const flushParagraph = () => {
    if (paragraphLines.length === 0) return;
    const merged = paragraphLines.join(" ").trim();
    if (merged) {
      blocks.push(`<p>${renderInlineMarkdown(merged)}</p>`);
    }
    paragraphLines = [];
  };

  const closeLists = () => {
    if (inUl) {
      blocks.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      blocks.push("</ol>");
      inOl = false;
    }
  };

  const closeOpenBlocks = () => {
    flushParagraph();
    closeLists();
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (inCode) {
      if (/^```/.test(line)) {
        blocks.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
        codeLines = [];
        inCode = false;
      } else {
        codeLines.push(rawLine);
      }
      continue;
    }

    if (/^```/.test(line)) {
      closeOpenBlocks();
      inCode = true;
      codeLines = [];
      continue;
    }

    if (!line) {
      closeOpenBlocks();
      continue;
    }

    if (/^---+$/.test(line)) {
      closeOpenBlocks();
      blocks.push("<hr />");
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);
    if (headingMatch) {
      closeOpenBlocks();
      const level = headingMatch[1].length;
      blocks.push(`<h${level}>${renderInlineMarkdown(headingMatch[2])}</h${level}>`);
      continue;
    }

    const quoteMatch = line.match(/^>\s?(.*)$/);
    if (quoteMatch) {
      closeOpenBlocks();
      blocks.push(`<blockquote><p>${renderInlineMarkdown(quoteMatch[1])}</p></blockquote>`);
      continue;
    }

    const ulMatch = line.match(/^[-*+]\s+(.*)$/);
    if (ulMatch) {
      flushParagraph();
      if (inOl) {
        blocks.push("</ol>");
        inOl = false;
      }
      if (!inUl) {
        blocks.push("<ul>");
        inUl = true;
      }
      blocks.push(`<li>${renderInlineMarkdown(ulMatch[1])}</li>`);
      continue;
    }

    const olMatch = line.match(/^\d+\.\s+(.*)$/);
    if (olMatch) {
      flushParagraph();
      if (inUl) {
        blocks.push("</ul>");
        inUl = false;
      }
      if (!inOl) {
        blocks.push("<ol>");
        inOl = true;
      }
      blocks.push(`<li>${renderInlineMarkdown(olMatch[1])}</li>`);
      continue;
    }

    paragraphLines.push(line);
  }

  if (inCode) {
    blocks.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
  }

  closeOpenBlocks();
  return blocks.join("\n");
}

function setupSearch(inputId, data, containerId, kind = "generic") {
  const input = document.getElementById(inputId);
  if (!input) return;

  const normalize = (text) => (text || "").toLowerCase();

  input.addEventListener("input", (e) => {
    const q = normalize(e.target.value.trim());
    if (!q) {
      renderItems(containerId, data, kind);
      return;
    }

    const filtered = data.filter((item) => {
      const blob = [item.title, item.summary, (item.tags || []).join(" "), item.category]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return blob.includes(q);
    });

    renderItems(containerId, filtered, kind);
  });
}

function setYear() {
  document.querySelectorAll("#year").forEach((node) => {
    node.textContent = new Date().getFullYear();
  });
}

function setupMobileNav() {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("site-nav");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

function bootHomePage(projectsData) {
  if (document.getElementById("featured-projects")) {
    renderItems("featured-projects", projectsData.slice(0, 3), "project");
  }

  return document.getElementById("recent-articles") !== null;
}

function renderRecentArticles(articlesData) {
  if (document.getElementById("recent-articles")) {
    renderItems("recent-articles", articlesData.slice(0, 3), "article");
  }
}

function loadArticlesData() {
  return fetch("assets/data/articles.json")
    .then((response) => {
      if (!response.ok) throw new Error("Could not load articles JSON");
      return response.json();
    })
    .then((data) => (Array.isArray(data) ? data : articles))
    .catch(() => articles);
}

function loadProjectsData() {
  return fetch("assets/data/projects.json")
    .then((response) => {
      if (!response.ok) throw new Error("Could not load projects JSON");
      return response.json();
    })
    .then((data) => (Array.isArray(data) ? data : projects))
    .catch(() => projects);
}

function loadQuranicData() {
  return fetch("assets/data/quranic_notes.json")
    .then((response) => {
      if (!response.ok) throw new Error("Could not load quranic notes JSON");
      return response.json();
    })
    .then((data) => (Array.isArray(data) ? data : tafseerCollections))
    .catch(() => tafseerCollections);
}

function findItemById(items, id) {
  const target = String(id || "");
  return (items || []).find((item) => {
    const itemId = item.id || slugify(item.title || "");
    return itemId === target;
  });
}

function renderDetailView(kind, item) {
  const detailRoot = document.getElementById("detail-view");
  if (!detailRoot) return;

  if (!item) {
    detailRoot.innerHTML = `
      <article class="content-card detail-card">
        <h1>Content not found</h1>
        <p class="lead slim">The requested ${kind} could not be found. Please return to the listing page.</p>
        <p><a class="text-link" href="${kind === "project" ? "projects.html" : "articles.html"}">Go back →</a></p>
      </article>
    `;
    return;
  }

  const text = item.content || item.details || item.summary || "";
  const renderedContent = markdownToHtml(text);

  const tags = (item.tags || [])
    .map((tag) => `<span class="tag">${tag}</span>`)
    .join("");

  detailRoot.innerHTML = `
    <article class="content-card detail-card">
      ${item.image ? `<div class="card-media detail-media"><img src="${item.image}" alt="${item.imageAlt || item.title}" /></div>` : ""}
      <p class="eyebrow">${kind === "project" ? "Project" : "Article"}</p>
      <h1>${item.title}</h1>
      <p class="lead slim">${item.summary || ""}</p>
      <div class="tags">${tags}</div>
      <section class="detail-content">${renderedContent}</section>
      <div class="detail-actions">
        <a class="text-link" href="${kind === "project" ? "projects.html" : "articles.html"}">← Back to ${kind === "project" ? "projects" : "articles"}</a>
        ${item.link && item.link !== "#" ? `<a class="text-link" target="_blank" rel="noopener noreferrer" href="${item.link}">Open external resource →</a>` : ""}
      </div>
    </article>
  `;
}

async function bootDetailPage() {
  const detailRoot = document.getElementById("detail-view");
  if (!detailRoot) return;

  const params = new URLSearchParams(window.location.search);
  const type = params.get("type");
  const id = params.get("id");
  const kind = type === "project" ? "project" : "article";

  if (kind === "project") {
    const projectsData = await loadProjectsData();
    const item = findItemById(projectsData, id);
    renderDetailView("project", item);
    return;
  }

  const articlesData = await loadArticlesData();
  const item = findItemById(articlesData, id);
  renderDetailView("article", item);
}

function bootProjectsPage(projectsData) {
  renderItems("projects-grid", projectsData, "project");
  setupSearch("project-search", projectsData, "projects-grid", "project");
}

function bootArticlesPage(articlesData) {
  renderItems("articles-grid", articlesData, "article");
  setupSearch("article-search", articlesData, "articles-grid", "article");
}

function bootQuranicPage(quranicData) {
  renderItems("tafseer-grid", quranicData, "generic");
}

document.addEventListener("DOMContentLoaded", async () => {
  setYear();
  setupMobileNav();
  const projectsData = await loadProjectsData();
  const quranicData = await loadQuranicData();
  const hasRecentArticleSection = bootHomePage(projectsData);
  bootProjectsPage(projectsData);
  bootQuranicPage(quranicData);
  await bootDetailPage();

  const hasArticlesPage = document.getElementById("articles-grid") !== null;
  if (hasRecentArticleSection || hasArticlesPage) {
    const articlesData = await loadArticlesData();
    renderRecentArticles(articlesData);
    if (hasArticlesPage) {
      bootArticlesPage(articlesData);
    }
  }
});
