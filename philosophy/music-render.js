/* ============================================================
   MUSIC JOURNAL — RENDERER
   Reads MUSIC_DATA / GENRE_ORDER / MUSIC_STATS from music-data.js
   and builds the two genre grids. You should never need to edit
   this file — only music-data.js.
   ============================================================ */
(function () {
  'use strict';

  function escapeHTML(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* Sort genres by GENRE_ORDER; anything unlisted falls to the end,
     alphabetically, so a brand-new genre still renders. */
  function orderGenres(genres) {
    var known = (typeof GENRE_ORDER !== 'undefined') ? GENRE_ORDER : [];
    var ranked = [], rest = [];
    genres.forEach(function (g) {
      (known.indexOf(g) !== -1 ? ranked : rest).push(g);
    });
    ranked.sort(function (a, b) { return known.indexOf(a) - known.indexOf(b); });
    rest.sort(function (a, b) { return a.localeCompare(b); });
    return ranked.concat(rest);
  }

  function buildGrid(container, artists, showDays) {
    if (!container) return;

    /* group by genre */
    var groups = {};
    artists.forEach(function (a) {
      var g = a.genre || 'Uncategorised';
      (groups[g] = groups[g] || []).push(a);
    });

    var genres = orderGenres(Object.keys(groups));

    if (!genres.length) {
      container.innerHTML =
        '<p style="color:var(--c-text-dim); text-align:center; grid-column:1/-1;">Nothing here yet.</p>';
      return;
    }

    var html = genres.map(function (g) {
      var items = groups[g].slice().sort(function (a, b) {
        return a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });
      });

      var lis = items.map(function (a) {
        var badge = (showDays && a.days)
          ? ' <span class="days">' + a.days + 'd</span>'
          : '';
        return '<li>' + escapeHTML(a.name) + badge + '</li>';
      }).join('\n            ');

      return '' +
        '<div class="genre-card reveal">\n' +
        '          <h4><span class="genre-tag">' + escapeHTML(g) + '</span></h4>\n' +
        '          <ul>\n            ' + lis + '\n          </ul>\n' +
        '        </div>';
    }).join('\n\n        ');

    container.innerHTML = html;
  }

  /* main.js wires up its scroll-reveal observer before these cards exist,
     so give the newly created ones their own observer. */
  function revealNewCards(root) {
    var cards = root.querySelectorAll('.reveal:not(.visible)');
    if (!cards.length) return;

    if (!('IntersectionObserver' in window)) {
      cards.forEach(function (el) { el.classList.add('visible'); });
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });

    cards.forEach(function (el) { io.observe(el); });
  }

  function setStat(id, value) {
    var el = document.getElementById(id);
    if (el && value !== undefined && value !== null) el.textContent = value;
  }

  function init() {
    if (typeof MUSIC_DATA === 'undefined') {
      console.error('music-data.js did not load — check the <script> order.');
      return;
    }

    var heard = MUSIC_DATA.filter(function (a) { return a.heard; });
    var unheard = MUSIC_DATA.filter(function (a) { return !a.heard; });

    buildGrid(document.getElementById('heard-grid'), heard, true);
    buildGrid(document.getElementById('unheard-grid'), unheard, false);

    /* artist total is always derived; the rest come from MUSIC_STATS */
    setStat('stat-artists', MUSIC_DATA.length);
    if (typeof MUSIC_STATS !== 'undefined') {
      setStat('stat-albums', MUSIC_STATS.albums);
      setStat('stat-playlists', MUSIC_STATS.playlists);
      setStat('stat-days', MUSIC_STATS.days);
    }

    revealNewCards(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
