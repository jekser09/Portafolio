/**
 * Manejador de presentación y eventos para la vista de Hoja de Vida (/CV/).
 * Alternancia entre Vista 2 Columnas y Vista 1 Columna (ATS) y preparación de pdfmake.
 * Cargado con atributo 'defer' — se ejecuta inmediatamente tras el parseo del DOM.
 */

const LAYOUT_STORAGE_KEY = "cv_layout";

const LAYOUT_CONFIGS = {
  "two-col": {
    grid: "grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-start",
    sideCol: "lg:col-span-4 space-y-10",
    mainCol: "lg:col-span-8 space-y-10",
    contactGrid: "grid grid-cols-1 gap-3",
  },
  ats: {
    grid: "flex flex-col gap-10",
    sideCol: "contents",
    mainCol: "contents",
    contactGrid: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3",
  },
};

const BASE_LAYOUT_BTN_CLASS =
  "inline-flex items-center gap-2 px-3.5 py-2 rounded-lg border font-mono text-xs font-semibold transition-all cursor-pointer";
const ACTIVE_LAYOUT_BTN_CLASS = `${BASE_LAYOUT_BTN_CLASS} border-[#22A6BF] bg-[#22A6BF] text-white shadow-xs`;
const INACTIVE_LAYOUT_BTN_CLASS = `${BASE_LAYOUT_BTN_CLASS} border-transparent bg-transparent text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white`;

const DEFAULT_DOWNLOAD_LABEL = "Descargar CV (PDF)";

const layoutGrid = document.getElementById("cv-layout-grid");
const sideCol = document.getElementById("cv-side-col");
const mainCol = document.getElementById("cv-main-col");
const contactGrid = document.getElementById("contact-cards-grid");
const twoColBtn = document.getElementById("layout-two-col-btn");
const atsBtn = document.getElementById("layout-ats-btn");
const downloadBtn = document.getElementById("download-cv-btn");
const downloadLabel = document.getElementById("download-cv-label");

let currentLayout = "two-col";

/**
 * Aplica la disposición visual de la Hoja de Vida y sincroniza los botones externos.
 * @param {string} layout - Identificador de vista: "two-col" o "ats".
 */
function applyCvLayout(layout) {
  const normalizedLayout = layout === "ats" ? "ats" : "two-col";
  currentLayout = normalizedLayout;
  const config = LAYOUT_CONFIGS[normalizedLayout];

  if (layoutGrid) {
    layoutGrid.className = config.grid;
  }
  if (sideCol) {
    sideCol.className = config.sideCol;
  }
  if (mainCol) {
    mainCol.className = config.mainCol;
  }
  if (contactGrid) {
    contactGrid.className = config.contactGrid;
  }

  const isAts = normalizedLayout === "ats";

  if (twoColBtn) {
    twoColBtn.className = isAts ? INACTIVE_LAYOUT_BTN_CLASS : ACTIVE_LAYOUT_BTN_CLASS;
    twoColBtn.setAttribute("aria-pressed", String(!isAts));
  }
  if (atsBtn) {
    atsBtn.className = isAts ? ACTIVE_LAYOUT_BTN_CLASS : INACTIVE_LAYOUT_BTN_CLASS;
    atsBtn.setAttribute("aria-pressed", String(isAts));
  }

  localStorage.setItem(LAYOUT_STORAGE_KEY, normalizedLayout);
}

// Inicializar la disposición guardada o usar 2 columnas por defecto
const savedLayout = localStorage.getItem(LAYOUT_STORAGE_KEY);
applyCvLayout(savedLayout || "two-col");

// Eventos de cambio de vista desde la barra externa
twoColBtn?.addEventListener("click", () => applyCvLayout("two-col"));
atsBtn?.addEventListener("click", () => applyCvLayout("ats"));

const COPY_FEEDBACK_DURATION_MS = 1800;
const copyFeedbackTimers = new WeakMap();

/**
 * Copia el texto asociado a una tarjeta de contacto y muestra retroalimentación visual temporal.
 * @param {HTMLElement} element - Tarjeta interactiva con atributo data-copy-text.
 */
async function handleCopyCardAction(element) {
  const text = element.dataset.copyText;
  if (!text) {
    return;
  }

  if (!navigator.clipboard?.writeText) {
    console.warn("La API del portapapeles no está disponible en este contexto.");
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    console.error("No se pudo copiar el texto al portapapeles:", err);
    return;
  }

  const feedbackEl = element.querySelector("[data-copy-feedback]");
  if (!feedbackEl) {
    return;
  }

  const originalLabel = element.dataset.copyLabel || "Copiado";
  const activeTimer = copyFeedbackTimers.get(feedbackEl);
  if (activeTimer) {
    window.clearTimeout(activeTimer);
  }

  feedbackEl.textContent = "¡COPIADO!";
  feedbackEl.classList.remove("text-slate-500", "dark:text-[#94A3B8]");
  feedbackEl.classList.add("text-[#22A6BF]");

  const timerId = window.setTimeout(() => {
    feedbackEl.textContent = originalLabel;
    feedbackEl.classList.remove("text-[#22A6BF]");
    feedbackEl.classList.add("text-slate-500", "dark:text-[#94A3B8]");
    copyFeedbackTimers.delete(feedbackEl);
  }, COPY_FEEDBACK_DURATION_MS);

  copyFeedbackTimers.set(feedbackEl, timerId);
}

// Eventos de copiado rápido al portapapeles para tarjetas interactivas
document.querySelectorAll("[data-copy-text]").forEach((el) => {
  el.addEventListener("click", () => {
    handleCopyCardAction(el);
  });

  el.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleCopyCardAction(el);
    }
  });
});

// Evento de descarga del CV desde la barra externa
downloadBtn?.addEventListener("click", async () => {
  if (downloadBtn.disabled) {
    return;
  }

  const cvDataElement = document.getElementById("cv-data");
  if (!cvDataElement) {
    console.error("No se encontró el elemento #cv-data en el DOM.");
    alert("No se pudo generar el PDF. Inténtalo nuevamente.");
    return;
  }

  let cvData;
  try {
    cvData = JSON.parse(cvDataElement.textContent);
  } catch (err) {
    console.error("Error al procesar el payload de cv-data:", err);
    alert("No se pudo generar el PDF. Inténtalo nuevamente.");
    return;
  }

  if (typeof window.generateCvPdf !== "function") {
    console.error("La función window.generateCvPdf no está disponible.");
    alert("No se pudo generar el PDF. Inténtalo nuevamente.");
    return;
  }

  downloadBtn.disabled = true;
  downloadBtn.setAttribute("aria-busy", "true");
  if (downloadLabel) {
    downloadLabel.textContent = "Generando PDF...";
  }

  try {
    await window.generateCvPdf(cvData, currentLayout);
  } catch (err) {
    console.error("Error al generar el PDF del CV:", err);
    alert("No se pudo generar el PDF. Inténtalo nuevamente.");
  } finally {
    downloadBtn.disabled = false;
    downloadBtn.setAttribute("aria-busy", "false");
    if (downloadLabel) {
      downloadLabel.textContent = DEFAULT_DOWNLOAD_LABEL;
    }
  }
});
