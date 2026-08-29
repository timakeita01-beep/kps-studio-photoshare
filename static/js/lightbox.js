function openLightbox(url) {
  const lightbox = document.getElementById('lightbox');
  const img = document.getElementById('lightbox-img');
  if (!lightbox || !img) return;
  img.src = url;
  lightbox.classList.add('is-open');
}

function closeLightbox() {
  const lightbox = document.getElementById('lightbox');
  if (!lightbox) return;
  lightbox.classList.remove('is-open');
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') closeLightbox();
});
