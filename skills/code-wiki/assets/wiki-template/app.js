(function () {
  const links = Array.from(document.querySelectorAll("nav a"));
  const path = window.location.pathname;
  const here = path.endsWith("/") ? "index.html" : path.split("/").pop();

  if (here) {
    for (const link of links) {
      const target = (link.getAttribute("href") || "").split("#")[0].split("?")[0];
      let targetPath = "";
      try {
        targetPath = new URL(target || "index.html", window.location.href).pathname;
      } catch (_) {
        targetPath = "";
      }
      if (targetPath === window.location.pathname) {
        link.classList.add("active");
      }
    }
  }

  const sidebar = document.querySelector(".sidebar");
  const toggle = document.querySelector(".nav-toggle");
  if (sidebar && toggle) {
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      sidebar.classList.toggle("open", !expanded);
    });
  }

  for (const table of Array.from(document.querySelectorAll("main table"))) {
    if (table.parentElement && table.parentElement.classList.contains("table-wrap")) {
      continue;
    }
    const wrapper = document.createElement("div");
    wrapper.className = "table-wrap";
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  }

  for (const section of Array.from(document.querySelectorAll("main > section"))) {
    if (!section.classList.contains("panel") && !section.classList.contains("doc-section")) {
      section.classList.add("doc-section");
    }
  }

  for (const figure of Array.from(document.querySelectorAll("main figure"))) {
    const image = figure.querySelector("img, svg");
    const src = image ? image.getAttribute("src") || "" : "";
    if (
      !figure.classList.contains("diagram-frame") &&
      !figure.classList.contains("hybrid-diagram") &&
      (src.includes("assets/diagrams/") || src.includes("assets/images/") || figure.querySelector("svg"))
    ) {
      figure.classList.add("diagram-frame");
    }
  }

  const main = document.querySelector("main");
  const header = document.querySelector(".hero, .page-header");
  const headings = Array.from(document.querySelectorAll("main h2"));
  if (main && header && headings.length >= 3) {
    const toc = document.createElement("nav");
    toc.className = "toc";
    toc.setAttribute("aria-label", "Page contents");
    const title = document.createElement("strong");
    title.textContent = "On this page";
    toc.appendChild(title);
    for (const heading of headings) {
      if (!heading.id) {
        heading.id = heading.textContent
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-|-$/g, "");
      }
      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent;
      toc.appendChild(link);
    }
    header.insertAdjacentElement("afterend", toc);
  }
})();
