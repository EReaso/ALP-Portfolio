let active = document.querySelector(`#navbar_items li a[href="${location.pathname}"]`);
  active.classList.add("active", "fw-bold");

const htmlElement = document.querySelector("html")
function updateTheme() {
  document.querySelector("html").setAttribute("data-bs-theme",
  window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
}
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", updateTheme)
updateTheme()
  
