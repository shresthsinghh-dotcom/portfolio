/* ============================================================
   SHRESTH SINGH — PORTFOLIO  ·  SHARED JS
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

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
    // Close on link click
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

});
