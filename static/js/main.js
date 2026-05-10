// ── Live Clock ──────────────────────────────────
function updateClock() {
    const el = document.getElementById('clock');
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-US', { hour12: false });
}
updateClock();
setInterval(updateClock, 1000);

// ── Confirm Action ──────────────────────────────
function confirmAction(label) {
    return confirm(`⚠️ Are you sure you want to ${label}?\nThis is a simulation and data is backed up.`);
}

// ── Auto-dismiss flash messages ─────────────────
document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(f => {
        setTimeout(() => {
            f.style.transition = 'opacity 0.5s';
            f.style.opacity = '0';
            setTimeout(() => f.remove(), 500);
        }, 4000);
    });
});
