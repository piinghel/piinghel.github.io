(function () {
  "use strict";

  const toc = document.querySelector("[data-article-toc]");
  const article = document.querySelector(".post-content");
  const list = toc && toc.querySelector("[data-article-toc-list]");

  if (article) {
    article.querySelectorAll("table.research-table").forEach((table) => {
      if (table.parentElement.classList.contains("research-table-scroll")) return;
      const region = document.createElement("div");
      region.className = "research-table-scroll";
      region.tabIndex = 0;
      region.setAttribute("role", "region");
      const caption = table.caption ||
        (table.previousElementSibling?.classList.contains("table-caption")
          ? table.previousElementSibling : table.nextElementSibling);
      region.setAttribute("aria-label", caption &&
        (caption.tagName === "CAPTION" || caption.classList.contains("table-caption"))
        ? caption.textContent.trim() : "Research table");
      table.before(region);
      region.appendChild(table);
    });
    const scrollRegions = Array.from(article.querySelectorAll(
      ".research-table-scroll, .research-figure, .low-vol-figure"
    ));
    const updateScrollAccess = () => {
      scrollRegions.forEach((region) => {
        const scrollable = region.scrollWidth > region.clientWidth + 1;
        region.tabIndex = scrollable ? 0 : -1;
        if (!region.classList.contains("research-table-scroll")) {
          region.setAttribute("role", "group");
          const image = region.querySelector("img");
          region.setAttribute("aria-label", image ? image.alt : "Research diagram");
        }
      });
    };
    updateScrollAccess();
    window.addEventListener("resize", updateScrollAccess);
    article.querySelectorAll("img").forEach((image) => {
      image.addEventListener("load", updateScrollAccess, { once: true });
    });
  }

  if (!toc || !article || !list) return;

  const headings = Array.from(article.querySelectorAll("h2"));
  if (headings.length < 3) return;

  const links = [];

  headings.forEach((heading, index) => {
    if (!heading.id) heading.id = `section-${index + 1}`;

    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent.trim();
    item.appendChild(link);
    list.appendChild(item);
    links.push(link);
  });

  toc.hidden = false;

  const sideRail = window.matchMedia("(min-width: 1160px)");
  const syncLayout = () => {
    toc.open = sideRail.matches;
  };
  syncLayout();
  sideRail.addEventListener("change", syncLayout);

  let ticking = false;
  const updateCurrentSection = () => {
    const readingLine = window.scrollY + Math.min(window.innerHeight * 0.28, 220);
    let currentIndex = 0;

    headings.forEach((heading, index) => {
      const headingTop = heading.getBoundingClientRect().top + window.scrollY;
      if (headingTop <= readingLine) currentIndex = index;
    });

    links.forEach((link, index) => {
      if (index === currentIndex) {
        link.setAttribute("aria-current", "location");
      } else {
        link.removeAttribute("aria-current");
      }
    });
    ticking = false;
  };

  const requestCurrentSectionUpdate = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(updateCurrentSection);
  };

  updateCurrentSection();
  window.addEventListener("scroll", requestCurrentSectionUpdate, { passive: true });
  window.addEventListener("resize", requestCurrentSectionUpdate);
})();
