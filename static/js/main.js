/**
 * Script global del portafolio.
 * Gestión de tema claro/oscuro y utilidades compartidas.
 * Se ejecuta con atributo 'defer' garantizando DOM completamente parseado.
 */

// Inicialización de tema según preferencia persistida o del sistema operativo
const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
  document.documentElement.classList.add("dark");
} else {
  document.documentElement.classList.remove("dark");
}
