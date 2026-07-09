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

/* Multi-timeline builder: master + grouped timelines */
/* Small multiples timeline: one row per thinker with visible names */
(function buildSmallMultiplesTimeline() {
  if (!toc) return;

  // collect chapters (ensure chapters NodeList exists)
  const chapterEls = Array.from(chapters || document.querySelectorAll('.chapter'));
  const thinkers = chapterEls.map(ch => {
    // ensure id
    if (!ch.id) {
      const h = ch.querySelector('h2');
      ch.id = h ? h.textContent.trim().toLowerCase().replace(/\s+/g,'-') : '';
    }
    // prefer explicit data-start/data-end
    let start = ch.dataset.start ? parseInt(ch.dataset.start, 10) : null;
    let end   = ch.dataset.end   ? parseInt(ch.dataset.end, 10)   : null;

    // fallback parse from .chapter-dates
    if (start == null || end == null) {
      const raw = (ch.querySelector('.chapter-dates')?.textContent || '');
      const nums = raw.match(/\d{2,4}/g) || [];
      const isBCE = /BCE|BC/i.test(raw);
      const sign = isBCE ? -1 : 1;
      if (nums.length >= 1 && start == null) start = sign * parseInt(nums[0], 10);
      if (nums.length >= 2 && end == null) end = sign * parseInt(nums[1], 10);
      if (nums.length === 1 && end == null) end = start;
    }

    if (start == null || end == null) return null;

    const h = ch.querySelector('h2');
    return {
      id: ch.id,
      name: h ? h.textContent.trim() : ch.id,
      start: Math.min(start, end),
      end: Math.max(start, end),
      el: ch
    };
  }).filter(Boolean);

  if (thinkers.length <= 1) return;

  // compute global range
  const minYear = Math.min(...thinkers.map(t => t.start));
  const maxYear = Math.max(...thinkers.map(t => t.end));
  if (minYear === maxYear) return;
  const totalSpan = maxYear - minYear;

  // create containers if not present
  const wrapper = document.getElementById('timelines-wrapper') || document.createElement('div');
  const master = document.getElementById('timeline-master') || document.createElement('div');
  const multiples = document.getElementById('timeline-multiples') || document.createElement('div');

  master.id = 'timeline-master';
  multiples.id = 'timeline-multiples';
  wrapper.id = 'timelines-wrapper';
  wrapper.classList.add('timelines-wrapper');

  // ensure wrapper is inserted after toc
  if (!document.getElementById('timelines-wrapper')) {
    toc.insertAdjacentElement('afterend', wrapper);
    wrapper.appendChild(master);
    wrapper.appendChild(multiples);
  }

  // helper: convert year to percent
  function yearToPct(y) {
    return ((y - minYear) / totalSpan) * 100;
  }

  // render master overview (compact)
  master.innerHTML = '<div class="tl-label">Overview</div><div class="tl-track" role="img" aria-label="Overview of thinkers timeline"></div>';
  const masterTrack = master.querySelector('.tl-track');
  thinkers.forEach(t => {
    const pct = yearToPct((t.start + t.end) / 2);
    const dot = document.createElement('span');
    dot.className = 'tl-span';
    dot.style.left = pct + '%';
    dot.title = `${t.name} (${Math.abs(t.start)}–${Math.abs(t.end)} ${t.start < 0 ? 'BCE' : 'CE'})`;
    masterTrack.appendChild(dot);
  });

  // clear multiples
  multiples.innerHTML = '';

  // render each thinker row
  thinkers.forEach((t) => {
    const row = document.createElement('div');
    row.className = 'timeline-row';
    row.setAttribute('role', 'listitem');
    row.dataset.id = t.id;

    const nameCol = document.createElement('div');
    nameCol.className = 'timeline-name';
    nameCol.textContent = t.name;

    const trackCol = document.createElement('div');
    trackCol.className = 'timeline-track';

    // compute left and width
    const leftPct = yearToPct(t.start);
    const rightPct = yearToPct(t.end);
    const widthPct = Math.max(0.6, rightPct - leftPct);

    const bar = document.createElement('button');
    bar.className = 'timeline-bar';
    bar.style.left = leftPct + '%';
    bar.style.width = widthPct + '%';
    bar.setAttribute('aria-label', `${t.name} lifespan ${Math.abs(t.start)} to ${Math.abs(t.end)} ${t.start<0?'BCE':'CE'}`);
    bar.tabIndex = 0;

    // label inside bar for hover/focus
    const barLabel = document.createElement('span');
    barLabel.className = 'bar-label';
    barLabel.textContent = `${t.name} — ${Math.abs(t.start)}–${Math.abs(t.end)} ${t.start<0?'BCE':'CE'}`;
    bar.appendChild(barLabel);

    // start/end dots
    const dotStart = document.createElement('span');
    dotStart.className = 'timeline-dot';
    dotStart.style.left = leftPct + '%';
    const dotEnd = document.createElement('span');
    dotEnd.className = 'timeline-dot';
    dotEnd.style.left = (leftPct + widthPct) + '%';

    // click/keyboard: highlight and scroll to chapter
    function activate() {
      document.querySelectorAll('.timeline-row.tl-active').forEach(r => r.classList.remove('tl-active'));
      row.classList.add('tl-active');
      // highlight corresponding chapter in page
      const target = document.getElementById(t.id);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    bar.addEventListener('click', activate);
    bar.addEventListener('keydown', (ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); activate(); } });

    trackCol.appendChild(bar);
    trackCol.appendChild(dotStart);
    trackCol.appendChild(dotEnd);

    row.appendChild(nameCol);
    row.appendChild(trackCol);
    multiples.appendChild(row);
  });

  // optional: highlight row when chapter enters viewport
  const observer = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        const id = en.target.id;
        document.querySelectorAll('.timeline-row.tl-active').forEach(r => r.classList.remove('tl-active'));
        const row = document.querySelector(`.timeline-row[data-id="${id}"]`);
        if (row) row.classList.add('tl-active');
      }
    });
  }, { threshold: 0.45 });

  thinkers.forEach(t => {
    const el = document.getElementById(t.id);
    if (el) observer.observe(el);
  });
// Compact mode toggle: enable when many thinkers or small viewport
    (function enableCompactTimelineMode() {
      const wrapper = document.getElementById('timelines-wrapper');
      if (!wrapper) return;

      // heuristics: enable compact if >12 thinkers or viewport height < 800px
      const count = document.querySelectorAll('.timeline-row').length;
      const smallViewport = window.innerHeight < 800;

      if (count > 12 || smallViewport) {
        wrapper.classList.add('compact');
      } else {
        wrapper.classList.remove('compact');
      }

      // allow manual toggle via data-attribute on wrapper
      if (wrapper.dataset.forceCompact === 'true') wrapper.classList.add('compact');

      // re-evaluate on resize (debounced)
      let t;
      window.addEventListener('resize', () => {
        clearTimeout(t);
        t = setTimeout(() => {
          if (window.innerHeight < 800 || document.querySelectorAll('.timeline-row').length > 12) {
            wrapper.classList.add('compact');
          } else {
            wrapper.classList.remove('compact');
          }
        }, 150);
      });
    })();

})();
/* ---------- Stadium Paradox ---------- */

document.querySelectorAll(".stadium-frame").forEach(frame=>{

    frame.addEventListener("click",()=>{

        const demo=frame.closest(".stadium-demo");

        demo.classList.add("started");

        demo.classList.remove("animate");

        void demo.offsetWidth;

        demo.classList.add("animate");

        setTimeout(()=>{

            demo.classList.remove("animate");

        },1200);

    });

});})