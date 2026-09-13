const tabs = document.querySelector('#cv-tabs');
const status = document.querySelector('#catalog-status');
const frame = document.querySelector('#cv-frame');
const title = document.querySelector('#current-title');
const download = document.querySelector('#download-cv');
const open = document.querySelector('#open-cv');
const print = document.querySelector('#print-cv');

function selectCv(cv, button, updateUrl = true) {
  document.querySelectorAll('.tab').forEach(tab => tab.setAttribute('aria-selected', 'false'));
  button?.setAttribute('aria-selected', 'true');
  frame.src = cv.path;
  title.textContent = cv.title;
  download.href = cv.path;
  download.download = `Witold_Grzesiak_${cv.slug}.html`;
  open.href = cv.path;
  if (updateUrl) history.replaceState(null, '', `#${cv.slug}`);
}

fetch('./jobs/manifest.json')
  .then(response => {
    if (!response.ok) throw new Error('Nie udało się pobrać manifestu CV.');
    return response.json();
  })
  .then(cvs => {
    status.hidden = true;
    const requested = location.hash.slice(1);
    let selectedButton;
    let selectedCv;
    cvs.forEach((cv, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'tab';
      button.setAttribute('role', 'tab');
      button.setAttribute('aria-selected', 'false');
      button.innerHTML = `<strong>${cv.title}</strong><span>${cv.description}</span>`;
      button.addEventListener('click', () => selectCv(cv, button));
      tabs.append(button);
      if (cv.slug === requested || (!selectedCv && index === 0)) {
        selectedCv = cv;
        selectedButton = button;
      }
    });
    selectCv(selectedCv, selectedButton, false);
  })
  .catch(error => { status.textContent = error.message; });

print.addEventListener('click', () => {
  try { frame.contentWindow.focus(); frame.contentWindow.print(); }
  catch { window.open(open.href, '_blank', 'noopener'); }
});
