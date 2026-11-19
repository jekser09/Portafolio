/**
 * Script global del portafolio.
 * Gestión de tema claro/oscuro y utilidades compartidas.
 */
document.addEventListener("DOMContentLoaded", () => {
  // Inicialización de tema según preferencia guardada o del sistema
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
});
