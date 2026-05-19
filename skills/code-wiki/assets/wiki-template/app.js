(function () {
  const links = Array.from(document.querySelectorAll("nav a"));
  const path = window.location.pathname;
  const here = path.endsWith("/") ? "index.html" : path.split("/").pop();
  if (!here) return;

  for (const link of links) {
    const target = (link.getAttribute("href") || "").split("#")[0].split("?")[0];
    const targetFile = target.split("/").filter(Boolean).pop() || "index.html";
    if (targetFile === here) {
      link.classList.add("active");
    }
  }
})();
