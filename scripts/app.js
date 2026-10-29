// ── Booty Catalog — Main Application Logic ──
// Last update: 2026-10-26

const APP = {
  games: [],
  filtered: [],
  state: {
    filter: 'all',
    category: null,
    search: '',
    sort: 'newest',
    view: 'grid',
    selectedGame: null,
    installDir: 'C:\\Games',
    theme: 'dark',
    repacker: null,
  },

  // ── Initialize ──
  async init() {
    await this.loadGames();
    this.bindEvents();
    this.renderLatestBanner();
    this.renderGameGrid();
    this.updateCounts();
    this.checkTheme();
    this.setupHeroInteraction();
  },

  // ── Setup Hero Interaction ──
  setupHeroInteraction() {
    // Hero navigation dots
    const dots = document.querySelectorAll('.hero-dots .dot');
    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => {
        const sections = document.querySelectorAll('main > section[id]');
        if (sections[i]) {
          sections[i].scrollIntoView({ behavior: 'smooth' });
        }
      });
    });

    // Update count in initial check
    const countEl = document.getElementById('count-all');
    if (countEl && this.games.length) {
      countEl.textContent = this.games.length;
    }
  },

  // ── Load games.json ──
  async loadGames() {
    try {
      const resp = await fetch('data/games.json');
      this.games = await resp.json();
    } catch (e) {
      // Fallback: try loading from root
      try {
        const resp = await fetch('games.json');
        this.games = await resp.json();
      } catch (e2) {
        this.games = [];
      }
    }
    this.filtered = [...this.games];
  },

  // ── Render Latest Banner (Just Dropped) ──
  renderLatestBanner() {
    const container = document.getElementById('latest-scroll');
    const latest = this.games.filter(g => g.isJustDropped).slice(0, 8);
    if (!latest.length) return;

    container.innerHTML = latest.map((g, i) => `
      <div class="latest-item" data-id="${g.id}" style="animation-delay: ${i * 50}ms">
        <div class="latest-item-title">${g.title}</div>
        <div class="latest-item-time">⚡ ${this.timeAgo(g.crackedDate)}</div>
      </div>
    `).join('');

    container.querySelectorAll('.latest-item').forEach(el => {
      el.addEventListener('click', () => this.openGame(el.dataset.id));
    });
  },

  // ── Render Game Grid ──
  renderGameGrid() {
    const grid = document.getElementById('game-grid');
    const empty = document.getElementById('empty-state');

    if (!this.filtered.length) {
      grid.innerHTML = '';
      empty.hidden = false;
      return;
    }

    empty.hidden = true;
    grid.innerHTML = this.filtered.map((g, i) => this.createCard(g, i)).join('');

    // Animate cards in
    grid.querySelectorAll('.game-card').forEach((card, i) => {
      card.style.animationDelay = `${i * 40}ms`;
    });

    // Bind card clicks
    grid.querySelectorAll('.game-card').forEach(card => {
      card.addEventListener('click', () => {
        const id = card.dataset.id;
        this.openGame(id);
      });
    });

    // Bind repacker filter clicks
    grid.querySelectorAll('.repacker-filter').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleRepackerFilter(btn.dataset.repacker);
      });
    });
  },

  // ── Create Card HTML ──
  createCard(g, index) {
    const badges = [];
    if (g.isJustDropped) badges.push(`<span class="card-badge new">NEW</span>`);
    if (g.isUpcoming) badges.push(`<span class="card-badge upcoming">UPCOMING</span>`);
    if (g.isLatest) badges.push(`<span class="card-badge cracked">CRACKED</span>`);

    const repacker = g.repack ? `
      <div class="repacker-badge fitgirl">
        <span>📦</span> ${g.repack.title}: ${g.repack.size}
      </div>
    ` : '';

    const sources = g.sources ? g.sources.map(s =>
      `<span class="source-tag">${s}</span>`
    ).join('') : '';

    const gradientStyle = g.imageGradient
      ? `background: ${g.imageGradient};`
      : `background: linear-gradient(135deg, #1a2744, #2c3e6b);`;

    const repackerClass = g.repack ?
      (g.repack.title.includes('FitGirl') ? 'fitgirl' :
       g.repack.title.includes('DODI') ? 'dodi' :
       g.repack.title.includes('CODEX') ? 'codex' : 'skidrow')
      : '';

    return `
      <div class="game-card" data-id="${g.id}" data-genre="${g.genre}"
           style="animation-delay: ${index * 40}ms">
        <div class="card-image" style="${gradientStyle}">
          <div class="card-image-placeholder">
            <span class="emoji-placeholder" style="filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));">
              ${this.getGameEmoji(g.genre)}
            </span>
          </div>
          <div class="card-badges">${badges.join('')}</div>
        </div>
        <div class="card-body">
          <div class="card-genre">${g.genreLabel}</div>
          <div class="card-title">${g.title}</div>
          <div class="card-desc">${g.description}</div>
          <div class="card-footer">
            <div class="card-meta">
              <span class="card-meta-item">📅 <span>${g.crackedDate}</span></span>
              <span class="card-meta-item">👾 <span>${g.crackedBy}</span></span>
            </div>
            <span class="card-size">${g.size}</span>
          </div>
          <div class="source-tags">${sources}</div>
          ${repacker}
          ${g.rating > 0 ? `<div class="card-meta" style="margin-top:8px;">
            <span class="card-meta-item">⭐ ${g.rating.toFixed(1)}</span>
          </div>` : ''}
        </div>
      </div>
    `;
  },

  // ── Game Emoji by Genre ──
  getGameEmoji(genre) {
    const emojis = {
      rpg: '🧙', action: '⚔️', strategy: '♟️', simulation: '🏗️',
      survival: '🧟', adventure: '🗺️', mecha: '🤖', racing: '🏎️',
    };
    return emojis[genre] || '🎮';
  },

  // ── Open Game Details (Download Panel) ──
  openGame(id) {
    const game = this.games.find(g => g.id === id);
    if (!game) return;
    this.state.selectedGame = game;

    const panel = document.getElementById('download-panel');
    const overlay = document.getElementById('overlay');

    // Fill preview
    const preview = document.getElementById('panel-preview');
    preview.style.background = game.imageGradient || 'linear-gradient(135deg, #1a2744, #2c3e6b)';

    // Fill info
    document.getElementById('info-size').textContent = game.size;
    document.getElementById('info-version').textContent = game.version;
    document.getElementById('info-crack').textContent = game.crackedBy;
    document.getElementById('info-uploaded').textContent = game.uploadedDate;

    // Fill install dir
    document.getElementById('install-dir-input').value = this.state.installDir;

    // Show panel
    panel.classList.add('open');
    overlay.classList.add('active');
  },

  // ── Close Download Panel ──
  closePanel() {
    const panel = document.getElementById('download-panel');
    const overlay = document.getElementById('overlay');
    panel.classList.remove('open');
    overlay.classList.remove('active');
  },

  // ── Apply Filters ──
  applyFilters() {
    let result = [...this.games];

    // Filter by type (All, Just Cracked, Upcoming)
    if (this.state.filter === 'cracked') {
      result = result.filter(g => g.isJustDropped);
    } else if (this.state.filter === 'upcoming') {
      result = result.filter(g => g.isUpcoming);
    }

    // Filter by category
    if (this.state.category) {
      result = result.filter(g => g.genre === this.state.category);
    }

    // Filter by repacker source
    if (this.state.repacker) {
      result = result.filter(g =>
        g.sources && g.sources.includes(this.state.repacker)
      );
    }

    // Filter by search
    if (this.state.search) {
      const q = this.state.search.toLowerCase();
      result = result.filter(g =>
        g.title.toLowerCase().includes(q) ||
        g.genreLabel.toLowerCase().includes(q) ||
        g.crackedBy.toLowerCase().includes(q) ||
        g.tags.some(t => t.toLowerCase().includes(q) ||
        g.description.toLowerCase().includes(q)
      );
    }

    // Sort
    result = this.sortGames(result);
    this.filtered = result;
    this.renderGameGrid();
    this.updateCounts();
  },

  // ── Sort ──
  sortGames(games) {
    const sorted = [...games];
    switch (this.state.sort) {
      case 'newest':
        sorted.sort((a, b) => new Date(b.crackedDate) - new Date(a.crackedDate));
        break;
      case 'oldest':
        sorted.sort((a, b) => new Date(a.crackedDate) - new Date(b.crackedDate));
        break;
      case 'name':
        sorted.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case 'size':
        sorted.sort((a, b) => b.sizeBytes - a.sizeBytes);
        break;
      case 'cracked':
        sorted.sort((a, b) => b.rating - a.rating);
        break;
      default:
        break;
    }
    return sorted;
  },

  // ── Toggle Repacker Filter ──
  toggleRepackerFilter(repacker) {
    this.state.repacker = this.state.repacker === repacker ? null : repacker;
    document.querySelectorAll('.repacker-filter').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.repacker === this.state.repacker);
    });
    this.applyFilters();
  },

  // ── Update Counts ──
  updateCounts() {
    document.getElementById('count-all').textContent = this.games.length;
    document.getElementById('count-cracked').textContent =
      this.games.filter(g => g.isJustDropped).length;
    document.getElementById('count-upcoming').textContent =
      this.games.filter(g => g.isUpcoming).length;
    document.getElementById('count-action').textContent =
      this.games.filter(g => g.genre === 'action').length;
    document.getElementById('count-rpg').textContent =
      this.games.filter(g => g.genre === 'rpg').length;
    document.getElementById('count-strategy').textContent =
      this.games.filter(g => g.genre === 'strategy').length;
    document.getElementById('count-simulation').textContent =
      this.games.filter(g => g.genre === 'simulation').length;
    document.getElementById('count-indie').textContent =
      this.games.filter(g => g.tags && g.tags.includes('indie')).length;
    document.getElementById('count-racing').textContent =
      this.games.filter(g => g.genre === 'racing').length;
  },

  // ── Check Theme ──
  checkTheme() {
    const saved = localStorage.getItem('booty-catalog-theme');
    if (saved) {
      this.state.theme = saved;
      document.documentElement.setAttribute('data-theme', saved);
    }
  },

  // ── Toggle Theme ──
  toggleTheme() {
    this.state.theme = this.state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', this.state.theme);
    localStorage.setItem('booty-catalog-theme', this.state.theme);
    showToast(this.state.theme === 'dark' ? '🏴 Back to the shadows' : '☀️ Light mode activated', 'info');
  },

  // ── Time Ago helper ──
  timeAgo(dateStr) {
    const date = new Date(dateStr);
    const now = new Date('2026-10-26');
    const diffMs = now - date;
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return `${Math.floor(days / 365)} year${days / 365 > 1 ? 's' : ''} ago`;
  },

  // ── Bind Events ──
  bindEvents() {
    // Sidebar nav items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        item.classList.add('active');
        document.querySelectorAll('.nav-item').forEach(i => {
          if (i !== item) i.classList.remove('active');
        });

        const filter = item.dataset.filter;
        const category = item.dataset.category;
        const action = item.dataset.action;

        if (filter) {
          this.state.filter = filter;
          this.state.category = null;
          this.state.repacker = null;
          this.state.search = '';
          document.getElementById('search-input').value = '';
          const titleMap = { all: 'All Games', cracked: 'Just Cracked', upcoming: 'Upcoming' };
          document.getElementById('header-title').textContent = titleMap[filter];
          this.applyFilters();
        }

        if (category) {
          this.state.category = category;
          this.state.filter = 'all';
          document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
          item.classList.add('active');
          document.getElementById('header-title').textContent = category.charAt(0).toUpperCase() + category.slice(1);
          this.applyFilters();
        }

        if (action === 'install-dir') {
          this.browseInstallDir();
        }

        if (action === 'clear') {
          localStorage.clear();
          showToast('🧹 Cache cleared! Fresh start, matey.', 'success');
          this.renderLatestBanner();
          this.renderGameGrid();
          this.updateCounts();
        }
      });
    });

    // Search input
    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchClear.style.opacity = e.target.value ? '0.7' : '0';
      searchTimeout = setTimeout(() => {
        this.state.search = e.target.value;
        this.state.category = null;
        this.state.repacker = null;
        this.state.filter = 'all';
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.querySelector('[data-filter="all"]').classList.add('active');
        document.getElementById('header-title').textContent =
          e.target.value ? `"${e.target.value}"` : 'All Games';
        this.applyFilters();
      }, 300);
    });
    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      searchClear.style.opacity = '0';
      this.state.search = '';
      this.state.category = null;
      this.state.repacker = null;
      this.applyFilters();
    });

    // Sort button
    document.getElementById('sort-btn').addEventListener('click', () => {
      const modal = document.getElementById('sort-modal');
      modal.hidden = false;
      requestAnimationFrame(() => {
        document.getElementById('sort-overlay').classList.add('active');
        modal.classList.add('active');
      });
    });

    document.getElementById('sort-overlay').addEventListener('click', () => {
      document.getElementById('sort-modal').classList.remove('active');
      document.getElementById('sort-overlay').classList.remove('active');
    });

    document.querySelectorAll('.sort-option').forEach(opt => {
      opt.addEventListener('click', () => {
        this.state.sort = opt.dataset.sort;
        document.getElementById('sort-label').textContent = opt.querySelector('span:last-child')?.textContent || opt.dataset.sort;
        document.querySelectorAll('.sort-option').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
        document.getElementById('sort-modal').classList.remove('active');
        document.getElementById('sort-overlay').classList.remove('active');
        this.applyFilters();
      });
    });

    // View toggle
    document.getElementById('view-toggle').addEventListener('click', () => {
      const grid = document.getElementById('game-grid');
      if (this.state.view === 'grid') {
        this.state.view = 'list';
        grid.classList.add('list-view');
        document.getElementById('view-icon').textContent = '▤';
      } else {
        this.state.view = 'grid';
        grid.classList.remove('list-view');
        document.getElementById('view-icon').textContent = '▦';
      }
    });

    // Close panel
    document.getElementById('panel-close').addEventListener('click', () => {
      this.closePanel();
    });
    document.getElementById('overlay').addEventListener('click', () => {
      this.closePanel();
    });

    // Install dir browse
    document.getElementById('install-dir-btn').addEventListener('click', () => {
      this.browseInstallDir();
    });

    // Empty reset
    document.getElementById('empty-reset').addEventListener('click', () => {
      this.state.category = null;
      this.state.repacker = null;
      this.state.search = '';
      document.getElementById('search-input').value = '';
      document.getElementById('search-clear').style.opacity = '0';
      document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
      document.querySelector('[data-filter="all"]').classList.add('active');
      document.getElementById('header-title').textContent = 'All Games';
      this.applyFilters();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closePanel();
        const modal = document.getElementById('sort-modal');
        if (!modal.hidden) {
          modal.classList.remove('active');
          document.getElementById('sort-overlay').classList.remove('active');
        }
      }
      if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });

    // Mobile sidebar toggle
    document.getElementById('menu-toggle').addEventListener('click', () => {
      document.getElementById('sidebar').classList.toggle('open');
    });
  },

  // ── Browse Install Dir ──
  async browseInstallDir() {
    try {
      if (navigator.storage && navigator.storage.getDirectory) {
        const dir = await navigator.storage.getDirectory();
        this.state.installDir = 'FileSystem Storage';
        document.getElementById('install-dir-input').value = this.state.installDir;
      } else {
        this.state.installDir = prompt('Enter install folder:', this.state.installDir) || this.state.installDir;
        document.getElementById('install-dir-input').value = this.state.installDir;
      }
    } catch (e) {
      this.state.installDir = prompt('Enter install folder:', this.state.installDir) || this.state.installDir;
      document.getElementById('install-dir-input').value = this.state.installDir;
    }
  },
};

// ── Boot! ──
document.addEventListener('DOMContentLoaded', () => APP.init());

// ── Hero navigation function ──
function scrollToSection(dotElement) {
  const heroSection = document.getElementById('hero-section');
  const latestBanner = document.getElementById('latest-banner');
  const gameGrid = document.getElementById('game-grid');

  if (dotElement.classList.contains('dot-1')) {
    heroSection.scrollIntoView({ behavior: 'smooth' });
  } else if (dotElement.classList.contains('dot-2')) {
    latestBanner.scrollIntoView({ behavior: 'smooth' });
  } else if (dotElement.classList.contains('dot-3')) {
    gameGrid.scrollIntoView({ behavior: 'smooth' });
  }
}

// ── Toast notifications ──
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('visible'));
  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ── Export for download.js ──
window.APP = APP;
