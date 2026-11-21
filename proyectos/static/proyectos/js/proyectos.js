/**
 * Controlador interactivo para el catálogo de proyectos (/prodep/).
 * Maneja filtrado reactivo (categoría funcional, stack y búsqueda textual),
 * animaciones de scroll vertical + carga diferida de iframes vía IntersectionObserver,
 * y visor seguro de documentación técnica (Markdown + PDF).
 * Cargado con atributo 'defer' — se ejecuta directamente tras el parseo del DOM.
 */

const ACTIVE_CATEGORY_BTN_CLASS =
  "px-3.5 py-1.5 rounded-lg border border-[#22A6BF] bg-[#22A6BF] text-white font-mono text-xs font-semibold transition-all cursor-pointer shadow-xs";
const INACTIVE_CATEGORY_BTN_CLASS =
  "px-3.5 py-1.5 rounded-lg border border-slate-200 dark:border-[#1E2D3D] bg-slate-50 dark:bg-[#0B1118] text-slate-600 dark:text-[#94A3B8] hover:border-[#22A6BF] hover:text-[#22A6BF] font-mono text-xs font-medium transition-all cursor-pointer";

const ACTIVE_SKILL_BTN_CLASS =
  "px-2.5 py-1 rounded-md border border-[#22A6BF] bg-[#22A6BF] text-white font-mono text-[11px] font-semibold transition-all cursor-pointer shadow-xs";
const INACTIVE_SKILL_BTN_CLASS =
  "px-2.5 py-1 rounded-md border border-slate-200 dark:border-[#1E2D3D] bg-slate-50 dark:bg-[#0B1118] text-slate-600 dark:text-[#94A3B8] hover:border-[#22A6BF] hover:text-[#22A6BF] font-mono text-[11px] font-medium transition-all cursor-pointer";

const catalogScriptEl = document.getElementById("projects-catalog-data");
const searchInput = document.getElementById("project-search-input");
const clearFiltersBtn = document.getElementById("clear-filters-btn");
const emptyResetFiltersBtn = document.getElementById("empty-reset-filters-btn");
const projectsCounter = document.getElementById("projects-counter");
const emptyStateEl = document.getElementById("projects-empty-state");

const categoryButtons = Array.from(document.querySelectorAll("[data-category-filter]"));
const skillButtons = Array.from(document.querySelectorAll("[data-skill-filter]"));
const projectCards = Array.from(document.querySelectorAll("[data-project-card]"));
const openDocsButtons = Array.from(document.querySelectorAll("[data-open-docs]"));

const docsModal = document.getElementById("project-docs-modal");
const closeDocsModalBtn = document.getElementById("close-docs-modal-btn");
const secondaryCloseDocsBtns = Array.from(document.querySelectorAll("[data-close-docs-modal]"));
const docsModalCategory = document.getElementById("docs-modal-category");
const docsModalType = document.getElementById("docs-modal-type");
const docsModalTitle = document.getElementById("docs-modal-title");
const docsModalContent = document.getElementById("docs-modal-content");
const docsModalPdfLink = document.getElementById("docs-modal-pdf-link");
const docsModalLiveLink = document.getElementById("docs-modal-live-link");

const projectsBySlug = new Map();
if (catalogScriptEl?.textContent) {
  try {
    const catalogData = JSON.parse(catalogScriptEl.textContent);
    for (const item of catalogData.projects || []) {
      if (item?.slug) {
        projectsBySlug.set(item.slug, item);
      }
    }
  } catch (error) {
    console.error("No se pudo parsear el catálogo JSON de proyectos:", error);
  }
}

const filterState = {
  category: "all",
  skill: "",
  query: "",
};

/**
 * Sincroniza el contador, botones activos y visibilidad de las tarjetas.
 */
function applyProjectFilters() {
  const normalizedCategory = filterState.category.toLowerCase();
  const normalizedSkill = filterState.skill.trim().toLowerCase();
  const normalizedQuery = filterState.query.trim().toLowerCase();

  let visibleCount = 0;
  for (const card of projectCards) {
    const cardCategory = (card.dataset.categorySlug || "").toLowerCase();
    const cardSkills = (card.dataset.skills || "").split("|").filter(Boolean);
    const cardSearchText = (card.dataset.searchText || "").toLowerCase();

    const matchesCategory =
      normalizedCategory === "all" || cardCategory === normalizedCategory;
    const matchesSkill = !normalizedSkill || cardSkills.includes(normalizedSkill);
    const matchesQuery = !normalizedQuery || cardSearchText.includes(normalizedQuery);

    const isVisible = matchesCategory && matchesSkill && matchesQuery;
    card.classList.toggle("hidden", !isVisible);
    if (isVisible) {
      visibleCount += 1;
    }
  }

  const hasActiveFilter =
    normalizedCategory !== "all" || Boolean(normalizedSkill) || Boolean(normalizedQuery);

  if (clearFiltersBtn) {
    clearFiltersBtn.classList.toggle("hidden", !hasActiveFilter);
  }

  if (projectsCounter) {
    const totalCount = projectCards.length;
    if (hasActiveFilter) {
      projectsCounter.textContent = `${visibleCount} de ${totalCount} proyectos`;
    } else {
      const label = totalCount === 1 ? "proyecto" : "proyectos";
      projectsCounter.textContent = `${totalCount} ${label}`;
    }
  }

  if (emptyStateEl && projectCards.length > 0) {
    emptyStateEl.classList.toggle("hidden", visibleCount > 0);
  }

  for (const btn of categoryButtons) {
    const isSelected = (btn.dataset.categoryFilter || "").toLowerCase() === normalizedCategory;
    btn.className = isSelected ? ACTIVE_CATEGORY_BTN_CLASS : INACTIVE_CATEGORY_BTN_CLASS;
    btn.setAttribute("aria-pressed", String(isSelected));
  }

  for (const btn of skillButtons) {
    const isSelected =
      Boolean(normalizedSkill) &&
      (btn.dataset.skillFilter || "").trim().toLowerCase() === normalizedSkill;
    btn.className = isSelected ? ACTIVE_SKILL_BTN_CLASS : INACTIVE_SKILL_BTN_CLASS;
    btn.setAttribute("aria-pressed", String(isSelected));
  }
}

/**
 * Restablece todos los filtros activos del catálogo.
 */
function resetProjectFilters() {
  filterState.category = "all";
  filterState.skill = "";
  filterState.query = "";
  if (searchInput) {
    searchInput.value = "";
  }
  applyProjectFilters();
}

for (const btn of categoryButtons) {
  btn.addEventListener("click", () => {
    filterState.category = btn.dataset.categoryFilter || "all";
    applyProjectFilters();
  });
}

for (const btn of skillButtons) {
  btn.addEventListener("click", () => {
    const selectedSkill = (btn.dataset.skillFilter || "").trim();
    const isSameSkill =
      filterState.skill.toLowerCase() === selectedSkill.toLowerCase();
    filterState.skill = isSameSkill ? "" : selectedSkill;
    applyProjectFilters();
  });
}

searchInput?.addEventListener("input", () => {
  filterState.query = searchInput.value || "";
  applyProjectFilters();
});

clearFiltersBtn?.addEventListener("click", resetProjectFilters);
emptyResetFiltersBtn?.addEventListener("click", resetProjectFilters);

// Inicializar contadores al cargar
applyProjectFilters();

/**
 * Revela una tarjeta suavemente quitando las clases iniciales de desplazamiento.
 * @param {HTMLElement} cardElement
 */
function revealCard(cardElement) {
  cardElement.classList.remove("opacity-0", "translate-y-4");
  cardElement.classList.add("opacity-100", "translate-y-0");
}

/**
 * Hidrata un iframe diferido cuando entra en el área visible del navegador.
 * @param {HTMLIFrameElement} iframeElement
 */
function hydrateLazyIframe(iframeElement) {
  if (iframeElement.dataset.loaded === "true") {
    return;
  }
  const targetUrl = iframeElement.dataset.src;
  if (!targetUrl) {
    return;
  }

  iframeElement.dataset.loaded = "true";
  const loaderEl = iframeElement.parentElement?.querySelector("[data-iframe-loader]");

  iframeElement.addEventListener(
    "load",
    () => {
      iframeElement.classList.remove("opacity-0");
      iframeElement.classList.add("opacity-100");
      loaderEl?.classList.add("hidden");
    },
    { once: true }
  );

  iframeElement.src = targetUrl;
}

const lazyIframes = Array.from(document.querySelectorAll("[data-preview-iframe]"));

if ("IntersectionObserver" in window) {
  const scrollRevealObserver = new IntersectionObserver(
    (entries, observer) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) {
          continue;
        }
        revealCard(entry.target);
        observer.unobserve(entry.target);
      }
    },
    { threshold: 0.08, rootMargin: "0px 0px -30px 0px" }
  );

  for (const card of projectCards) {
    scrollRevealObserver.observe(card);
  }

  const iframeObserver = new IntersectionObserver(
    (entries, observer) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) {
          continue;
        }
        hydrateLazyIframe(entry.target);
        observer.unobserve(entry.target);
      }
    },
    { rootMargin: "120px 0px" }
  );

  for (const iframeEl of lazyIframes) {
    iframeObserver.observe(iframeEl);
  }
} else {
  for (const card of projectCards) {
    revealCard(card);
  }
  for (const iframeEl of lazyIframes) {
    hydrateLazyIframe(iframeEl);
  }
}

/**
 * Escapa caracteres HTML especiales para prevenir inyección XSS al renderizar Markdown.
 * @param {string} rawText
 * @returns {string}
 */
function escapeHtml(rawText) {
  return String(rawText)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

/**
 * Formatea estilos Markdown en línea sobre texto previamente escapado.
 * @param {string} escapedText
 * @returns {string}
 */
function formatInlineMarkdown(escapedText) {
  return escapedText
    .replace(
      /`([^`]+)`/g,
      '<code class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-[#0B1118] border border-slate-200 dark:border-[#1E2D3D] font-mono text-xs text-[#22A6BF]">$1</code>'
    )
    .replace(
      /\*\*([^*]+)\*\*/g,
      '<strong class="font-semibold text-slate-900 dark:text-[#F1F5F9]">$1</strong>'
    )
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (_match, label, url) => {
      return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-[#22A6BF] underline hover:text-[#1B8599]">${label}</a>`;
    });
}

/**
 * Convierte documentación Markdown en HTML seguro para el visor del modal.
 * @param {string} markdownText
 * @returns {string}
 */
function renderSafeMarkdown(markdownText) {
  if (!markdownText || !markdownText.trim()) {
    return '<p class="text-slate-500 dark:text-[#94A3B8]">Este proyecto incluye documentación técnica en PDF descargable.</p>';
  }

  const codeBlocks = [];
  const normalized = escapeHtml(markdownText).replace(
    /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g,
    (_match, lang, code) => {
      const idx = codeBlocks.length;
      const langBadge = lang
        ? `<div class="px-3 py-1 border-b border-slate-200 dark:border-[#1E2D3D] bg-slate-100 dark:bg-[#131C26] font-mono text-[10px] uppercase tracking-widest text-slate-500 dark:text-[#94A3B8]">${lang}</div>`
        : "";
      codeBlocks.push(
        `<div class="rounded-xl border border-slate-200 dark:border-[#1E2D3D] bg-slate-50 dark:bg-[#0B1118] overflow-hidden">${langBadge}<pre class="p-4 overflow-x-auto font-mono text-xs leading-relaxed text-slate-800 dark:text-slate-200"><code>${code.trimEnd()}</code></pre></div>`
      );
      return `\n@@CODE_BLOCK_${idx}@@\n`;
    }
  );

  const lines = normalized.split(/\r?\n/);
  const htmlParts = [];
  let inList = false;

  const closeListIfOpen = () => {
    if (inList) {
      htmlParts.push("</ul>");
      inList = false;
    }
  };

  for (const rawLine of lines) {
    const trimmed = rawLine.trim();

    if (!trimmed) {
      closeListIfOpen();
      continue;
    }

    const codeMatch = trimmed.match(/^@@CODE_BLOCK_(\d+)@@$/);
    if (codeMatch) {
      closeListIfOpen();
      htmlParts.push(codeBlocks[Number(codeMatch[1])] || "");
      continue;
    }

    if (trimmed.startsWith("### ")) {
      closeListIfOpen();
      htmlParts.push(
        `<h4 class="font-heading text-base font-bold text-slate-900 dark:text-[#F1F5F9] pt-2">${formatInlineMarkdown(trimmed.slice(4))}</h4>`
      );
      continue;
    }

    if (trimmed.startsWith("## ")) {
      closeListIfOpen();
      htmlParts.push(
        `<h3 class="font-heading text-lg font-bold text-slate-900 dark:text-[#F1F5F9] border-b border-slate-200 dark:border-[#1E2D3D] pb-1.5 pt-2">${formatInlineMarkdown(trimmed.slice(3))}</h3>`
      );
      continue;
    }

    if (trimmed.startsWith("# ")) {
      closeListIfOpen();
      htmlParts.push(
        `<h2 class="font-heading text-xl font-bold text-slate-900 dark:text-[#F1F5F9] border-b border-slate-200 dark:border-[#1E2D3D] pb-2">${formatInlineMarkdown(trimmed.slice(2))}</h2>`
      );
      continue;
    }

    if (/^[-*]\s+/.test(trimmed)) {
      if (!inList) {
        htmlParts.push('<ul class="list-disc pl-5 space-y-1.5">');
        inList = true;
      }
      htmlParts.push(`<li>${formatInlineMarkdown(trimmed.replace(/^[-*]\s+/, ""))}</li>`);
      continue;
    }

    closeListIfOpen();
    htmlParts.push(`<p>${formatInlineMarkdown(trimmed)}</p>`);
  }

  closeListIfOpen();
  return htmlParts.join("\n");
}

/**
 * Abre el modal con la documentación Markdown y/o enlace PDF del proyecto.
 * @param {string} slug
 */
function openDocsModal(slug) {
  const project = projectsBySlug.get(slug);
  if (!project || !docsModal) {
    return;
  }

  if (docsModalCategory) {
    docsModalCategory.textContent = project.category?.name || "";
  }
  if (docsModalType) {
    docsModalType.textContent = project.project_type || "";
  }
  if (docsModalTitle) {
    docsModalTitle.textContent = project.title || "";
  }
  if (docsModalContent) {
    docsModalContent.innerHTML = renderSafeMarkdown(project.detailed_description || "");
  }

  if (docsModalPdfLink) {
    if (project.documentation_pdf_url) {
      docsModalPdfLink.href = project.documentation_pdf_url;
      docsModalPdfLink.classList.remove("hidden");
    } else {
      docsModalPdfLink.href = "#";
      docsModalPdfLink.classList.add("hidden");
    }
  }

  if (docsModalLiveLink) {
    if (project.live_url) {
      docsModalLiveLink.href = project.live_url;
      docsModalLiveLink.textContent = project.cta_label || "Abrir Enlace";
      docsModalLiveLink.classList.remove("hidden");
    } else {
      docsModalLiveLink.href = "#";
      docsModalLiveLink.classList.add("hidden");
    }
  }

  docsModal.classList.remove("hidden");
  docsModal.classList.add("flex");
  document.body.classList.add("overflow-hidden");
  closeDocsModalBtn?.focus();
}

/**
 * Cierra el modal de documentación técnica.
 */
function closeDocsModal() {
  if (!docsModal || docsModal.classList.contains("hidden")) {
    return;
  }
  docsModal.classList.add("hidden");
  docsModal.classList.remove("flex");
  document.body.classList.remove("overflow-hidden");
}

for (const btn of openDocsButtons) {
  btn.addEventListener("click", () => {
    const slug = btn.dataset.openDocs;
    if (slug) {
      openDocsModal(slug);
    }
  });
}

closeDocsModalBtn?.addEventListener("click", closeDocsModal);
for (const btn of secondaryCloseDocsBtns) {
  btn.addEventListener("click", closeDocsModal);
}

docsModal?.addEventListener("click", (event) => {
  if (event.target === docsModal) {
    closeDocsModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeDocsModal();
  }
});
