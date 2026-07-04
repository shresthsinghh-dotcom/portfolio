/* ============================================================
   PHILOSOPHY BOOK SYSTEM — shared behavior
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* --- READING PROGRESS BAR --- */
  const progressBar = document.querySelector('.reading-progress');
  if (progressBar) {
    const updateProgress = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      progressBar.style.width = pct + '%';
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

  /* --- MOBILE TOC TOGGLE --- */
  const tocToggle = document.querySelector('.toc-toggle');
  const bookToc = document.querySelector('.book-toc');
  if (tocToggle && bookToc) {
    tocToggle.addEventListener('click', () => {
      tocToggle.classList.toggle('open');
      bookToc.classList.toggle('open');
    });
  }

  /* --- TOC SCROLLSPY --- */
  const tocLinks = document.querySelectorAll('.book-toc a');
  const chapters = document.querySelectorAll('.chapter[id]');
  if (tocLinks.length && chapters.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const id = entry.target.getAttribute('id');
        const link = document.querySelector(`.book-toc a[href="#${id}"]`);
        if (!link) return;
        if (entry.isIntersecting) {
          tocLinks.forEach(l => l.classList.remove('active'));
          link.classList.add('active');
        }
      });
    }, { rootMargin: '-15% 0px -75% 0px', threshold: 0 });
    chapters.forEach(ch => io.observe(ch));

    // Close mobile TOC on link click
    tocLinks.forEach(link => {
      link.addEventListener('click', () => {
        if (tocToggle && bookToc) {
          tocToggle.classList.remove('open');
          bookToc.classList.remove('open');
        }
      });
    });
  }

  /* --- APPENDIX JUMP LINKS (smooth scroll + auto-open) --- */
  document.querySelectorAll('.appendix-jump').forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href')?.slice(1);
      if (!targetId) return;
      const target = document.getElementById(targetId);
      if (!target) return;
      e.preventDefault();
      // Open all ancestor <details>
      let el = target;
      while (el) {
        if (el.tagName === 'DETAILS') el.open = true;
        el = el.parentElement;
      }
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

});
