(function () {
  function apply(theme) {
    if (theme === 'light' || theme === 'dark') {
      document.documentElement.setAttribute('data-theme', theme);
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }

  function current() {
    var stored = localStorage.getItem('kps-theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  window.toggleTheme = function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    localStorage.setItem('kps-theme', next);
    apply(next);
    var label = document.getElementById('theme-label');
    if (label) label.textContent = next === 'dark' ? 'Sombre' : 'Clair';
  };

  document.addEventListener('DOMContentLoaded', function () {
    var label = document.getElementById('theme-label');
    if (label) label.textContent = current() === 'dark' ? 'Sombre' : 'Clair';
  });
})();
