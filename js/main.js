/* ============================================================
   SHRESTH SINGH — PORTFOLIO  ·  SHARED JS
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* --- THEME TOGGLE ---------------------------------------- */
  const saved = localStorage.getItem('theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
  }
  // If no saved preference, default is dark (no data-theme attribute needed)

  const toggleBtn = document.querySelector('.theme-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'light' ? 'dark' : 'light';
      if (next === 'dark') {
        document.documentElement.removeAttribute('data-theme');
      } else {
        document.documentElement.setAttribute('data-theme', 'light');
      }
      localStorage.setItem('theme', next);
    });
  }

  /* --- NAV SCROLL EFFECT ----------------------------------- */
  const nav = document.querySelector('.site-nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* --- MOBILE NAV TOGGLE ----------------------------------- */
  const toggle = document.querySelector('.nav-toggle');
  const links  = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      toggle.classList.toggle('open');
      links.classList.toggle('open');
    });
    links.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        toggle.classList.remove('open');
        links.classList.remove('open');
      });
    });
  }

  /* --- SCROLL REVEAL --------------------------------------- */
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    reveals.forEach(el => io.observe(el));
  }

  /* --- BACK TO TOP ----------------------------------------- */
  const btt = document.getElementById('backToTop');
  if (btt) {
    window.addEventListener('scroll', () => {
      btt.classList.toggle('visible', window.scrollY > 500);
    }, { passive: true });
    btt.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* --- HERO CAROUSEL (index page only) --------------------- */
  const carousel = document.querySelector('.hero-carousel');
  if (carousel) {
    const imgs = carousel.querySelectorAll('img');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    let idx = 0;
    let interval;

    const show = (i) => {
      imgs.forEach(img => img.classList.remove('active'));
      idx = (i + imgs.length) % imgs.length;
      imgs[idx].classList.add('active');
    };

    const startAuto = () => {
      clearInterval(interval);
      interval = setInterval(() => show(idx + 1), 4500);
    };

    show(0);
    startAuto();

    if (prevBtn) prevBtn.addEventListener('click', () => { show(idx - 1); startAuto(); });
    if (nextBtn) nextBtn.addEventListener('click', () => { show(idx + 1); startAuto(); });
  }

  /* --- MINI CAROUSELS (Duke Aero, etc.) -------------------- */
  document.querySelectorAll('[data-carousel]').forEach(wrap => {
    const slides = wrap.querySelectorAll('.mini-slide');
    const prev   = wrap.querySelector('[data-prev]');
    const next   = wrap.querySelector('[data-next]');
    let i = 0;
    let auto;

    const go = (n) => {
      slides.forEach(s => s.classList.remove('active'));
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('active');
    };

    const startAuto = () => {
      clearInterval(auto);
      auto = setInterval(() => go(i + 1), 5000);
    };

    go(0);
    startAuto();

    if (prev) prev.addEventListener('click', () => { go(i - 1); startAuto(); });
    if (next) next.addEventListener('click', () => { go(i + 1); startAuto(); });
  });

  /* --- LIGHTBOX (tap a content image to view full-screen) -- */
  const zoomables = document.querySelectorAll('[data-carousel] img, [style*="grid-template-columns"] img');
  if (zoomables.length) {
    const box = document.createElement('div');
    box.className = 'lightbox';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.innerHTML = '<button class="lightbox-close" aria-label="Close image">&times;</button><img alt="">';
    document.body.appendChild(box);
    const boxImg = box.querySelector('img');

    const open = (src, alt) => {
      boxImg.src = src;
      boxImg.alt = alt || '';
      box.classList.add('open');
      document.body.style.overflow = 'hidden';
    };
    const close = () => {
      box.classList.remove('open');
      document.body.style.overflow = '';
      boxImg.src = '';
    };

    zoomables.forEach(img => {
      img.style.cursor = 'zoom-in';
      img.addEventListener('click', () => {
        // In a carousel the slides are stacked; always open the visible one.
        const wrap = img.closest('[data-carousel]');
        const target = wrap ? (wrap.querySelector('.mini-slide.active') || img) : img;
        open(target.src, target.alt);
      });
    });

    box.addEventListener('click', (e) => {
      if (e.target === box || e.target.classList.contains('lightbox-close')) close();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && box.classList.contains('open')) close();
    });
  }

});
