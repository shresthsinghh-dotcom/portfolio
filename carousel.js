document.addEventListener('DOMContentLoaded', () => {
  const carousel = document.getElementById('carousel');
  const images = Array.from(document.querySelectorAll('#carousel .carousel-img'));
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  let currentIndex = 0;
  let autoplayInterval = null; // set to a number (ms) to enable autoplay, or null to disable
  const AUTOPLAY_MS = 4000;

  if (!carousel || images.length === 0) {
    // Nothing to do if carousel or images are missing
    return;
  }

  // Ensure carousel container is positioned for absolute children
  carousel.style.position = carousel.style.position || 'relative';
  carousel.style.overflow = carousel.style.overflow || 'hidden';

  // Initialize image styles
  images.forEach((img, idx) => {
    img.style.position = 'absolute';
    img.style.top = '0';
    img.style.left = '0';
    img.style.width = '100%';
    img.style.height = 'auto';
    img.style.opacity = idx === currentIndex ? '1' : '0';
    img.style.transform = idx === currentIndex ? 'translateX(0)' : 'translateX(20px)';
    img.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    img.setAttribute('aria-hidden', idx === currentIndex ? 'false' : 'true');
    img.style.pointerEvents = 'none';
  });

  function showIndex(newIndex) {
    if (images.length === 0) return;
    newIndex = ((newIndex % images.length) + images.length) % images.length; // safe wrap
    images.forEach((img, idx) => {
      const isActive = idx === newIndex;
      img.style.opacity = isActive ? '1' : '0';
      img.style.transform = isActive ? 'translateX(0)' : 'translateX(20px)';
      img.setAttribute('aria-hidden', isActive ? 'false' : 'true');
    });
    currentIndex = newIndex;
  }

  function next() {
    showIndex(currentIndex + 1);
  }

  function prev() {
    showIndex(currentIndex - 1);
  }

  // Attach handlers if buttons exist
  if (nextBtn) nextBtn.addEventListener('click', () => { next(); resetAutoplay(); });
  if (prevBtn) prevBtn.addEventListener('click', () => { prev(); resetAutoplay(); });

  // Keyboard support: left / right arrows
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') { next(); resetAutoplay(); }
    if (e.key === 'ArrowLeft') { prev(); resetAutoplay(); }
  });

  // Optional autoplay
  function startAutoplay() {
    if (AUTOPLAY_MS && !autoplayInterval) {
      autoplayInterval = setInterval(next, AUTOPLAY_MS);
    }
  }
  function stopAutoplay() {
    if (autoplayInterval) {
      clearInterval(autoplayInterval);
      autoplayInterval = null;
    }
  }
  function resetAutoplay() {
    stopAutoplay();
    startAutoplay();
  }

  // Pause on hover/focus for accessibility
  carousel.addEventListener('mouseenter', stopAutoplay);
  carousel.addEventListener('mouseleave', startAutoplay);
  carousel.addEventListener('focusin', stopAutoplay);
  carousel.addEventListener('focusout', startAutoplay);

  // Start
  showIndex(currentIndex);
  startAutoplay();
});