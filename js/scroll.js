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
  log("scroll.js loaded");

  /* =========================================================
     PARALLAX FADE-IN ON LOAD
     ========================================================= */
  window.addEventListener("load", () => {
    document.querySelectorAll(".parallax-window").forEach(el => {
      el.style.opacity = "0";
      el.style.transition = "opacity 1.2s ease";
      requestAnimationFrame(() => (el.style.opacity = "1"));
    });
  });

  /* =========================================================
     NAVBAR BACKGROUND TRANSITION ON SCROLL
     ========================================================= */
  const navOuter = document.querySelector(".tm-nav-container-outer");
  if (navOuter) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 80) {
        navOuter.classList.add("nav-solid");
      } else {
        navOuter.classList.remove("nav-solid");
      }
    });
  }

  /* =========================================================
     SMOOTH BACK-TO-TOP BUTTON
     ========================================================= */
  const backToTop = document.getElementById("backToTop");
  if (backToTop) {
    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* =========================================================
     SECTION REVEAL (WITH OPTIONAL STAGGER)
     ========================================================= */
  const revealSections = document.querySelectorAll(".reveal-section");

  // Optional stagger for premium feel
  revealSections.forEach((section, i) => {
    section.style.transitionDelay = `${i * 60}ms`;
  });

  // Immediate reveal for anything already in view
  revealSections.forEach(section => {
    const rect = section.getBoundingClientRect();
    const inView =
      rect.top < window.innerHeight * 0.85 &&
      rect.bottom > 0;

    if (inView) {
      section.classList.add("is-visible");
    }
  });

  // Observer for progressive reveal
  if ("IntersectionObserver" in window && revealSections.length > 0) {
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

  /* =========================================================
     LAZY-LOADING IMAGES (BOOSTS PERFORMANCE)
     ========================================================= */
  const lazyImages = document.querySelectorAll("img[loading='lazy']");
  if ("IntersectionObserver" in window) {
    const imgObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src || img.src;
          imgObserver.unobserve(img);
        }
      });
    });

    lazyImages.forEach(img => imgObserver.observe(img));
  }
});