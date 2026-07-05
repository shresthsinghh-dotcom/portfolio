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

  /* ============ BOOK PAGES ONLY ============ */
  const bookBody = document.querySelector('.book-body');
  if (bookBody) {

    /* --- LIGHTBOX (click any figure or portrait) --- */
    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Image viewer');
    lb.innerHTML = '<button class="lb-close" aria-label="Close image">\u2715</button><img alt=""><p class="lb-cap"></p>';
    document.body.appendChild(lb);
    const lbImg = lb.querySelector('img');
    const lbCap = lb.querySelector('.lb-cap');
    const lbClose = lb.querySelector('.lb-close');
    let lastFocus = null;

    const openLightbox = (img) => {
      lastFocus = document.activeElement;
      lbImg.src = img.src;
      lbImg.alt = img.alt || '';
      const fig = img.closest('figure');
      const cap = fig ? fig.querySelector('figcaption') : null;
      lbCap.textContent = cap ? cap.textContent : (img.alt || '');
      lb.classList.add('open');
      lbClose.focus();
    };
    const closeLightbox = () => {
      lb.classList.remove('open');
      if (lastFocus) lastFocus.focus();
    };
    document.querySelectorAll('figure.pfig img, .chapter-portrait').forEach(img => {
      img.addEventListener('click', () => openLightbox(img));
    });
    lbClose.addEventListener('click', closeLightbox);
    lb.addEventListener('click', (e) => { if (e.target === lb) closeLightbox(); });

    /* --- MINI TOC (sticky contents + scrollspy + reading %) --- */
    const chapters = [...document.querySelectorAll('.chapter[id]')];
    let pctEl = null;
    if (chapters.length > 1) {
      const nav = document.createElement('nav');
      nav.className = 'mini-toc';
      nav.setAttribute('aria-label', 'Chapters');
      nav.innerHTML = '<span class="mt-label">Contents</span>' +
        chapters.map(ch => {
          const t = ch.querySelector('h2');
          return '<a href="#' + ch.id + '">' + (t ? t.textContent : ch.id) + '</a>';
        }).join('') +
        '<p class="mt-progress"><b>0%</b> read</p>';
      document.body.appendChild(nav);
      pctEl = nav.querySelector('.mt-progress b');

      const links = nav.querySelectorAll('a');
      const spy = new IntersectionObserver((entries) => {
        entries.forEach(en => {
          if (en.isIntersecting) {
            links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === '#' + en.target.id));
            localStorage.setItem('resume:' + location.pathname, en.target.id);
          }
        });
      }, { rootMargin: '-30% 0px -60% 0px' });
      chapters.forEach(ch => spy.observe(ch));
    }

    /* --- READING PERCENTAGE (feeds the mini-toc) --- */
    if (pctEl) {
      const updatePct = () => {
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const pct = docHeight > 0 ? Math.min(100, Math.round((window.scrollY / docHeight) * 100)) : 0;
        pctEl.textContent = pct + '%';
      };
      window.addEventListener('scroll', updatePct, { passive: true });
      updatePct();
    }

    /* --- RESUME READING (chip on the cover) --- */
    const savedId = localStorage.getItem('resume:' + location.pathname);
    const actions = document.querySelector('.cover-actions');
    if (savedId && actions && window.scrollY < 100) {
      const target = document.getElementById(savedId);
      const title = target ? target.querySelector('h2') : null;
      if (target && title && savedId !== chapters[0]?.id) {
        const chip = document.createElement('a');
        chip.className = 'resume-chip';
        chip.href = '#' + savedId;
        chip.textContent = '\u21A9 Resume: ' + title.textContent;
        actions.appendChild(chip);
      }
    }

    /* --- FOCUS MODE --- */
    const fb = document.createElement('button');
    fb.className = 'focus-btn';
    fb.setAttribute('aria-pressed', 'false');
    fb.setAttribute('aria-label', 'Toggle focus mode');
    fb.title = 'Focus mode';
    fb.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg>';
    document.body.appendChild(fb);
    fb.addEventListener('click', () => {
      const on = document.body.classList.toggle('focus-mode');
      fb.setAttribute('aria-pressed', String(on));
    });

    /* --- ESC: close lightbox, then exit focus mode --- */
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      if (lb.classList.contains('open')) { closeLightbox(); return; }
      if (document.body.classList.contains('focus-mode')) {
        document.body.classList.remove('focus-mode');
        fb.setAttribute('aria-pressed', 'false');
      }
    });
  }

});


/* ============================================================
   BOOK EXTRAS — running header, timeline, TOC state, foot links
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  const bookBody = document.querySelector('.book-body');
  if (!bookBody) return;
  const chapters = [...document.querySelectorAll('.chapter[id]')];
  const toc = document.getElementById('toc');

  /* --- Collapsible TOC: open on desktop, closed on mobile --- */
  if (toc && toc.tagName === 'DETAILS') {
    toc.open = window.innerWidth > 760;
  }

  /* --- Chapter foot nav: inject a centered Contents link --- */
  if (toc) {
    document.querySelectorAll('.chapter-foot-nav').forEach(nav => {
      const link = document.createElement('a');
      link.className = 'foot-toc';
      link.href = '#toc';
      link.textContent = 'Contents';
      const next = nav.querySelector('.next');
      next ? nav.insertBefore(link, next) : nav.appendChild(link);
    });
  }

  /* --- Running header: "BOOK I · Chapter" once past the cover --- */
  const coverNum = document.querySelector('.cover-num');
  const cover = document.querySelector('.book-cover');
  if (coverNum && chapters.length) {
    const rh = document.createElement('div');
    rh.className = 'running-header';
    rh.setAttribute('aria-hidden', 'true');
    rh.innerHTML = '<b>' + coverNum.textContent.trim() + '</b><span class="rh-sep">\u00B7</span><span class="rh-ch"></span>';
    document.body.appendChild(rh);
    const rhCh = rh.querySelector('.rh-ch');

    const miniLinks = () => document.querySelectorAll('.mini-toc a');
    const spy2 = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          const t = en.target.querySelector('h2');
          if (t) rhCh.textContent = t.textContent;
          miniLinks().forEach(l => {
            if (l.getAttribute('href') === '#' + en.target.id) l.setAttribute('aria-current', 'true');
            else l.removeAttribute('aria-current');
          });
        }
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    chapters.forEach(ch => spy2.observe(ch));

    const rhToggle = () => {
      const threshold = cover ? cover.offsetTop + cover.offsetHeight : 500;
      rh.classList.toggle('visible', window.scrollY > threshold && !!rhCh.textContent);
    };
    window.addEventListener('scroll', rhToggle, { passive: true });
    rhToggle();
  }

  /* --- Timeline: auto-built from chapter dates --- */
  if (toc && chapters.length > 2) {
    const points = chapters.map(ch => {
      const d = ch.querySelector('.chapter-dates');
      const t = ch.querySelector('h2');
      const m = d && d.textContent.match(/(\d{3})/);
      return m ? { id: ch.id, name: t ? t.textContent : ch.id, year: parseInt(m[1], 10) } : null;
    }).filter(Boolean);

    const oldest = points.length ? Math.max(...points.map(p => p.year)) : 0;
    const newest = points.length ? Math.min(...points.map(p => p.year)) : 0;
    if (points.length > 2 && oldest !== newest) {
      const tl = document.createElement('div');
      tl.className = 'book-timeline';
      tl.innerHTML = '<span class="tl-label">Timeline</span><div class="tl-track"></div>' +
        '<div class="tl-ends"><span>~' + oldest + ' BCE</span><span>~' + newest + ' BCE</span></div>';
      const track = tl.querySelector('.tl-track');
      points.forEach((p, i) => {
        const pct = Math.min(96, Math.max(4, ((oldest - p.year) / (oldest - newest)) * 100));
        const dot = document.createElement('a');
        dot.className = 'tl-dot ' + (i % 2 ? 'down' : 'up');
        dot.href = '#' + p.id;
        dot.style.left = pct + '%';
        dot.setAttribute('aria-label', p.name + ', born around ' + p.year + ' BCE');
        dot.innerHTML = '<span class="tl-name">' + p.name.split(' ')[0] + '</span>';
        track.appendChild(dot);
      });
      toc.insertAdjacentElement('afterend', tl);
    }
  }
});
