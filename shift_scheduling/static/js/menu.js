document.addEventListener('DOMContentLoaded', function () {
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  const closeBtn = document.getElementById('closeMenu');
  const main = document.getElementById('mainContent');

  function openMenu() {
    sidebar.classList.add('is-open');
    menuToggle.setAttribute('aria-expanded', 'true');
    sidebar.setAttribute('aria-hidden', 'false');
    // trap focus / consider adding focus management for a11y in larger projects
  }
  function closeMenu() {
    sidebar.classList.remove('is-open');
    menuToggle.setAttribute('aria-expanded', 'false');
    sidebar.setAttribute('aria-hidden', 'true');
  }

  if (menuToggle) menuToggle.addEventListener('click', openMenu);
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);

  // close when clicking outside (mobile)
  main.addEventListener('click', function (e) {
    if (sidebar.classList.contains('is-open')) closeMenu();
  });

  // close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar.classList.contains('is-open')) closeMenu();
  });
});
