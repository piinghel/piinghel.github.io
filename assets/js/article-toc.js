(function () {
  "use strict";

  const toc = document.querySelector("[data-article-toc]");
  const article = document.querySelector(".post-content");
  const list = toc && toc.querySelector("[data-article-toc-list]");

  if (!toc || !article || !list) return;

  const headings = Array.from(article.querySelectorAll("h2"));
  if (headings.length < 3) return;

  headings.forEach((heading, index) => {
    if (!heading.id) heading.id = `section-${index + 1}`;

    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent.trim();
    item.appendChild(link);
    list.appendChild(item);
  });

  toc.hidden = false;
})();
