/**
 * Manejador de eventos para la vista de Hoja de Vida (CV).
 * Control del selector de tema y preparación para pdfmake.
 * Cargado con atributo 'defer' — se ejecuta inmediatamente tras el parseo del DOM.
 */

// Elementos de la interfaz
const toggleBtn = document.getElementById("theme-toggle");
const darkIcon = document.getElementById("theme-icon-dark");
const lightIcon = document.getElementById("theme-icon-light");
const downloadBtn = document.getElementById("download-cv-btn");

/**
 * Actualiza la visibilidad de los iconos de sol/luna según el modo actual.
 */
function updateThemeIcons() {
  const isDark = document.documentElement.classList.contains("dark");
  if (isDark) {
    darkIcon?.classList.remove("hidden");
    lightIcon?.classList.add("hidden");
  } else {
    lightIcon?.classList.remove("hidden");
    darkIcon?.classList.add("hidden");
  }
}

// Sincronizar estado inicial de iconos
updateThemeIcons();

// Evento de alternancia de tema claro/oscuro
toggleBtn?.addEventListener("click", () => {
  document.documentElement.classList.toggle("dark");
  const isDark = document.documentElement.classList.contains("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
  updateThemeIcons();
});

// Evento de descarga del CV
downloadBtn?.addEventListener("click", () => {
  const cvDataElement = document.getElementById("cv-data");
  if (!cvDataElement) {
    console.error("No se encontró el elemento #cv-data en el DOM.");
    return;
  }

  try {
    const cvData = JSON.parse(cvDataElement.textContent);
    console.log("Datos de CV estructurados para pdfmake:", cvData);
    alert(
      `Generador de CV en PDF:\nDatos de ${cvData.profile?.full_name || "usuario"} cargados correctamente.\nListo para compilar con pdfmake.`
    );
  } catch (err) {
    console.error("Error al procesar el payload de cv-data:", err);
  }
});
