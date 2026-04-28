// Utility: Auto-dismiss flash messages after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
  const flashes = document.querySelectorAll('.flash, .auth-flash');
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 500);
    }, 4000);
  });

  // Active sidebar link highlighting (fallback for server-side)
  const links = document.querySelectorAll('.sidebar-nav a');
  links.forEach(function (link) {
    if (link.href === window.location.href) {
      link.classList.add('active');
    }
  });
});
