/* =========================================================
   CAROUSEL LOGIC — Shresth Singh Portfolio
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  const log = window.__siteDebugLog || function () {};

  const carousel = document.getElementById("carousel");
  const images = Array.from(document.querySelectorAll("#carousel .carousel-img"));
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  let currentIndex = 0;
  let autoplayInterval = null;
  const AUTOPLAY_MS = 4000;

  if (!carousel || images.length === 0) {
    log("Carousel not found — skipping");
    return;
  }

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
});