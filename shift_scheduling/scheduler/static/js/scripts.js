document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const closeBtn = document.getElementById('closeMenu');
    const overlay = document.getElementById('sidebar-overlay')

    function openMenu() {
        sidebar.classList.add('is-open');
        overlay.classList.add('is-open')

    }

    function closeMenu() {
        sidebar.classList.remove('is-open');
        overlay.classList.remove('is-open')
    }

    menuToggle.addEventListener('click', openMenu);
    closeBtn.addEventListener('click', closeMenu);
});