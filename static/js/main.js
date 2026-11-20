/**
 * Script global del portafolio.
 * Gestión de tema claro/oscuro (oscuro por defecto) y controles de navegación global.
 * Se ejecuta con atributo 'defer' garantizando DOM completamente parseado.
 */

const themeToggleBtn = document.getElementById("theme-toggle");
const themeDarkIcon = document.getElementById("theme-icon-dark");
const themeLightIcon = document.getElementById("theme-icon-light");

/**
 * Actualiza la visibilidad de los iconos de luna/sol según el modo activo.
 */
function updateThemeIcons() {
  const isDark = document.documentElement.classList.contains("dark");
  if (isDark) {
    themeDarkIcon?.classList.remove("hidden");
    themeLightIcon?.classList.add("hidden");
  } else {
    themeLightIcon?.classList.remove("hidden");
    themeDarkIcon?.classList.add("hidden");
  }
}

// Inicialización de tema: modo oscuro por defecto salvo elección explícita previa a claro
const savedTheme = localStorage.getItem("theme");
if (savedTheme === "light") {
  document.documentElement.classList.remove("dark");
} else {
  document.documentElement.classList.add("dark");
}

updateThemeIcons();

// Evento global de alternancia de tema claro/oscuro
themeToggleBtn?.addEventListener("click", () => {
  document.documentElement.classList.toggle("dark");
  const isDark = document.documentElement.classList.contains("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
  updateThemeIcons();
});
