/* =========================================================
   GLOBAL JS FLAG — MUST RUN IMMEDIATELY
   ========================================================= */
document.documentElement.classList.add("js");

/* =========================================================
   DEBUG GUARD
   ========================================================= */
(function () {
  const DEBUG = false;
  function log(...args) {
    if (DEBUG && window.console) console.log("[Site JS]", ...args);
  }
  window.__siteDebugLog = log;
})();

/* =========================================================
   DOM READY
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {

  const log = window.__siteDebugLog || function () {};
  log("DOM loaded, JS active");

  /* =========================================================
     CAROUSEL LOGIC
     ========================================================= */
  const carousel = document.getElementById("carousel");
  const images = Array.from(document.querySelectorAll("#carousel .carousel-img"));
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  let currentIndex = 0;
  let autoplayInterval = null;
  const AUTOPLAY_MS = 4000;

  if (carousel && images.length > 0) {
    log("Carousel initialized");

    carousel.style.position ||= "relative";
    carousel.style.overflow ||= "hidden";

    images.forEach((img, idx) => {
      img.style.position = "absolute";
      img.style.top = "0";
      img.style.left = "0";
      img.style.width = "100%";
      img.style.height = "auto";
      img.style.opacity = idx === currentIndex ? "1" : "0";
      img.style.transform = idx === currentIndex ? "translateX(0)" : "translateX(20px)";
      img.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      img.setAttribute("aria-hidden", idx === currentIndex ? "false" : "true");
      img.style.pointerEvents = "none";
    });

    function showIndex(newIndex) {
      newIndex = ((newIndex % images.length) + images.length) % images.length;
      images.forEach((img, idx) => {
        const active = idx === newIndex;
        img.style.opacity = active ? "1" : "0";
        img.style.transform = active ? "translateX(0)" : "translateX(20px)";
        img.setAttribute("aria-hidden", active ? "false" : "true");
      });
      currentIndex = newIndex;
    }

    function next() { showIndex(currentIndex + 1); }
    function prev() { showIndex(currentIndex - 1); }

    if (nextBtn) nextBtn.addEventListener("click", next);
    if (prevBtn) prevBtn.addEventListener("click", prev);

    function startAutoplay() {
      if (!autoplayInterval && AUTOPLAY_MS) {
        autoplayInterval = setInterval(next, AUTOPLAY_MS);
      }
    }

    function stopAutoplay() {
      if (autoplayInterval) {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
      }
    }

    carousel.addEventListener("mouseenter", stopAutoplay);
    carousel.addEventListener("mouseleave", startAutoplay);
    carousel.addEventListener("focusin", stopAutoplay);
    carousel.addEventListener("focusout", startAutoplay);

    showIndex(currentIndex);
    startAutoplay();
  } else {
    log("Carousel not found — skipping");
  }

  /* =========================================================
     SECTION REVEAL — FIXED ORDER (IMMEDIATE FIRST)
     ========================================================= */
  const revealSections = document.querySelectorAll(".reveal-section");

  // 1. Immediately reveal anything already in view
  revealSections.forEach(section => {
    const rect = section.getBoundingClientRect();
    const inView =
      rect.top < window.innerHeight * 0.85 &&
      rect.bottom > 0;

    if (inView) {
      section.classList.add("is-visible");
    }
  });

  // 2. Then create the observer
  if ("IntersectionObserver" in window && revealSections.length > 0) {
    log("Reveal observer active");

    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );

    revealSections.forEach(section => revealObserver.observe(section));
  } else {
    revealSections.forEach(section => section.classList.add("is-visible"));
  }

  /* =========================================================
     ACTIVE NAV HIGHLIGHT
     ========================================================= */
  const trackedSections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".tm-nav-link");

  if ("IntersectionObserver" in window && trackedSections.length > 0) {
    log("Nav highlight observer active");

    const navObserver = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            navLinks.forEach(link => {
              link.classList.toggle(
                "active-section",
                link.getAttribute("href")?.includes(id)
              );
            });
          }
        });
      },
      { threshold: 0.6 }
    );

    trackedSections.forEach(section => navObserver.observe(section));
  }

});