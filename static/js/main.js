/* ── Clock ─────────────────────────────────────────────────────────────────── */
function updateClock() {
  const el = document.getElementById('clock');
  if (!el) return;
  el.textContent = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}
updateClock();
setInterval(updateClock, 30000);

/* ── Sidebar Toggle ────────────────────────────────────────────────────────── */
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    if (window.innerWidth <= 768) {
      sidebar.classList.toggle('mobile-open');
    } else {
      sidebar.classList.toggle('collapsed');
      document.querySelector('.main-wrapper')?.classList.toggle('collapsed');
    }
  });
}

/* ── Auto-dismiss flash alerts ─────────────────────────────────────────────── */
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
    bsAlert?.close();
  }, 5000);
});

/* ── Confirm before delete ─────────────────────────────────────────────────── */
document.querySelectorAll('form[onsubmit]').forEach(form => {
  // handled inline via onsubmit attribute
});
