// JS - paste into script.js or at the end of <body>
(() => {
        const images = [
        'images/1ne.jpg',
        'images/2wo.jpg',
        'images/3hree.jpg',
        'images/4our.jpg',
        'images/5ive.jpg',
        'images/6ix.jpg'
        ];

        const alts = [
        'Profile image 1',
        'Profile image 2',
        'Profile image 3',
        'Profile image 4',
        'Profile image 5',
        'Profile image 6'
  ]; // optional alt text list (same length as images)

  let index = 0;
  const card = document.getElementById('card');
  const img = document.getElementById('carouselImage');
  const indicator = document.getElementById('indicator');

  const updateIndicator = () => {
    if (!indicator) return;
    indicator.textContent = `${index + 1} / ${images.length}`;
  };

  function showImage(i) {
    // ensure index wraps
    index = (i + images.length) % images.length;
    // preload next image (optional)
    const next = new Image();
    next.src = images[index];

    // flip animation: add class -> change src after half-rotation -> remove class
    card.classList.add('flipped');
    setTimeout(() => {
      img.src = images[index];
      img.alt = alts[index] || `Image ${index + 1}`;
      // remove flip to reveal updated image
      card.classList.remove('flipped');
      updateIndicator();
    }, 350); // half of transition duration (0.7s)
  }

  // Click on card to advance
  card.addEventListener('click', () => showImage(index + 1));

  // Prev / Next buttons
  document.getElementById('prevBtn').addEventListener('click', (e) => {
    e.stopPropagation();
    showImage(index - 1);
  });
  document.getElementById('nextBtn').addEventListener('click', (e) => {
    e.stopPropagation();
    showImage(index + 1);
  });

  // Keyboard support: left, right, space/enter to advance
  document.getElementById('viewport').addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      showImage(index + 1);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      showImage(index - 1);
    }
  });

  // Touch swipe support (minimal)
  let startX = null;
  const threshold = 30;
  const vp = document.getElementById('viewport');
  vp.addEventListener('touchstart', (e) => startX = e.touches[0].clientX, {passive: true});
  vp.addEventListener('touchmove', (e) => {
    if (!startX) return;
    const dx = e.touches[0].clientX - startX;
    if (Math.abs(dx) > threshold) {
      if (dx < 0) showImage(index + 1); else showImage(index - 1);
      startX = null;
    }
  }, {passive: true});

  // Initialize
  img.src = images[0];
  img.alt = alts[0] || 'Image 1';
  updateIndicator();
})();
