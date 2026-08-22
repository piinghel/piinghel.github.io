(function () {
  "use strict";

  const toc = document.querySelector("[data-article-toc]");
  const article = document.querySelector(".post-content");
  const list = toc && toc.querySelector("[data-article-toc-list]");

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
