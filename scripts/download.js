// ── Booty Catalog — One-Click Download & Install ──
// Simulates the pirate experience with satisfying progress animations

const DL = {
  active: false,
  game: null,
  progress: 0,
  phase: 'idle',

  // ── Start Download ──
  async start() {
    if (this.active) return;
    this.active = true;
    this.game = APP.state.selectedGame;
    this.progress = 0;
    this.phase = 'downloading';

    const btn = document.getElementById('panel-download-btn');
    const status = document.getElementById('panel-status');
    const fill = document.getElementById('status-fill');
    const text = document.getElementById('status-text');
    const progress = document.getElementById('btn-progress');

    // Loading state
    btn.classList.add('loading');
    btn.querySelector('.btn-text').textContent = 'Downloading...';
    btn.querySelector('.btn-icon').textContent = '⏳';
    status.hidden = false;
    progress.style.width = '0%';

    // Phase 1: Download (60%)
    text.textContent = '📡 Connecting to pirate server...';
    await this.animate(0, 35, 2000, (p) => {
      fill.style.width = `${p}%`;
      progress.style.width = `${p * 0.6}%`;
    });
    text.textContent = '📥 Downloading files...';
    await this.animate(35, 60, 2000, (p) => {
      fill.style.width = `${p}%`;
      progress.style.width = `${p * 0.6}%`;
    });

    // Phase 2: Extract (30%)
    this.phase = 'extracting';
    text.textContent = '🔓 Extracting...';
    await this.animate(60, 80, 2000, (p) => {
      fill.style.width = `${p}%`;
      progress.style.width = `${30 + p * 0.3}%`;
    });

    // Phase 3: Crack (5%)
    this.phase = 'cracking';
    text.textContent = '🔑 Bypassing DRM...';
    await this.animate(80, 87, 1000, (p) => {
      fill.style.width = `${p}%`;
      progress.style.width = `${30 + p * 0.3}%`;
    });

    // Phase 4: Install (5%)
    this.phase = 'installing';
    text.textContent = `📂 Installing to ${APP.state.installDir}`;
    await this.animate(87, 95, 1500, (p) => {
      fill.style.width = `${p}%`;
      progress.style.width = `${30 + p * 0.3}%`;
    });

    // Phase 5: Verify (2%)
    this.phase = 'verifying';
    text.textContent = '✅ Verifying installation...';
    await this.animate(95, 98, 1000, (p) => {
      fill.style.width = `${p}%`;
      progress.style.width = `${30 + p * 0.3}%`;
    });

    // Phase 6: Activate (2%)
    this.phase = 'activating';
    text.textContent = '🏴 Activating pirated copy...';
    await this.animate(98, 100, 800, (p) => {
      fill.style.width = `${p}%`;
      progress.style.width = `${30 + p * 0.3}%`;
    });

    // Done!
    this.active = false;
    btn.classList.remove('loading');
    btn.querySelector('.btn-text').textContent = 'Download Complete!';
    btn.querySelector('.btn-icon').textContent = '⚡';
    fill.style.width = '100%';
    fill.style.background = 'linear-gradient(90deg, #7ec87e, #f6c847)';
    text.textContent = '✅ Ready to play!';

    showToast(`⚓ ${this.game.title} installed to ${APP.state.installDir}`, 'success');

    // Reset button after delay
    setTimeout(() => {
      btn.querySelector('.btn-text').textContent = 'One-Click Download & Install';
      btn.querySelector('.btn-icon').textContent = '⚡';
      btn.classList.remove('loading');
      status.hidden = true;
      fill.style.background = 'linear-gradient(90deg, var(--accent), var(--green))';
    }, 3000);
  },

  // ── Animate helper ──
  animate(from, to, duration, onProgress) {
    return new Promise(resolve => {
      const start = performance.now();
      const tick = (now) => {
        const elapsed = now - start;
        const t = Math.min(elapsed / duration, 1);
        const eased = t < 0.5
          ? 2 * t * t
          : 1 - Math.pow(-2 * t + 2, 2) / 2;
        const value = from + (to - from) * eased;
        onProgress(value);
        if (t < 1) requestAnimationFrame(tick);
        else resolve();
      };
      requestAnimationFrame(tick);
    });
  },
};

// ── Bind download button ──
document.getElementById('panel-download-btn')?.addEventListener('click', () => DL.start());

window.DL = DL;
