(function () {
  const form = document.getElementById('upload-form');
  if (!form) return;

  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const progressList = document.getElementById('progress-list');

  function uploadFiles(files) {
    if (!files || !files.length) return;

    const formData = new FormData();
    for (const file of files) {
      formData.append('images', file);
    }

    const item = document.createElement('div');
    item.className = 'progress-item';
    item.innerHTML = `Import de ${files.length} photo(s)…<div class="progress-bar"><div class="progress-bar__fill"></div></div>`;
    progressList.appendChild(item);
    const fill = item.querySelector('.progress-bar__fill');

    const xhr = new XMLHttpRequest();
    xhr.open('POST', form.action, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    xhr.setRequestHeader('X-CSRFToken', csrfToken);

    xhr.upload.onprogress = function (e) {
      if (e.lengthComputable) {
        fill.style.width = Math.round((e.loaded / e.total) * 100) + '%';
      }
    };

    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        window.location.reload();
      } else {
        item.innerHTML = "Échec de l'import. Merci de réessayer.";
      }
    };

    xhr.onerror = function () {
      item.innerHTML = "Erreur réseau pendant l'import.";
    };

    xhr.send(formData);
  }

  fileInput.addEventListener('change', function () {
    uploadFiles(fileInput.files);
  });

  ['dragenter', 'dragover'].forEach((eventName) => {
    dropzone.addEventListener(eventName, function (e) {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach((eventName) => {
    dropzone.addEventListener(eventName, function (e) {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', function (e) {
    uploadFiles(e.dataTransfer.files);
  });
})();
