const tabs = document.querySelector('#cv-tabs');
const status = document.querySelector('#catalog-status');
const frame = document.querySelector('#cv-frame');
const title = document.querySelector('#current-title');
const download = document.querySelector('#download-cv');
const open = document.querySelector('#open-cv');
const print = document.querySelector('#print-cv');
const languageButtons = [...document.querySelectorAll('.language-button')];
let profiles = [];
let selectedKey = location.hash.slice(1) || 'ogolne';
let selectedLang = localStorage.getItem('cv-language') || 'pl';

const supplementalProfiles = [
  {
    key: 'bank-pocztowy-junior-credit-risk',
    versions: {
      en: {
        title: 'Bank Pocztowy: Junior Credit Risk Specialist',
        description: 'SQL, Python, Power BI, data analysis, modelling, data quality and machine learning',
        path: './jobs/bank-pocztowy-junior-credit-risk-en.html',
        downloadPath: './jobs/bank-pocztowy-junior-credit-risk-en.html'
      },
      pl: {
        title: 'Bank Pocztowy: Młodszy Specjalista ds. ryzyka kredytowego',
        description: 'SQL, Python, Power BI, analiza danych, modelowanie, data quality i machine learning',
        path: './jobs/bank-pocztowy-junior-credit-risk.html',
        downloadPath: './jobs/bank-pocztowy-junior-credit-risk.html'
      }
    }
  },
  {
    key: 'pko-faktoring-data-analyst',
    versions: {
      en: {
        title: 'PKO Faktoring: Data Analyst',
        description: 'SQL, Power BI, reporting, risk analytics, modelling, automation and data quality',
        path: './jobs/pko-faktoring-data-analyst-en.html',
        downloadPath: './jobs/pko-faktoring-data-analyst-en.html'
      },
      pl: {
        title: 'PKO Faktoring: Analityk / Analityczka Danych',
        description: 'SQL, Power BI, raportowanie, analiza ryzyka, modelowanie, automatyzacja i data quality',
        path: './jobs/pko-faktoring-data-analyst.html',
        downloadPath: './jobs/pko-faktoring-data-analyst.html'
      }
    }
  },
  {
    key: 'focus-research-junior-analyst',
    versions: {
      en: {
        title: 'FOCUS Research: Junior Analyst',
        description: 'Excel, SQL, business data analysis, reporting, databases, data quality and automation',
        path: './jobs/focus-research-junior-analyst-en.html',
        downloadPath: './jobs/focus-research-junior-analyst-en.html'
      },
      pl: {
        title: 'FOCUS Research: Młodszy/a Analityk',
        description: 'Excel, SQL, analiza danych biznesowych, raportowanie, bazy danych, data quality i automatyzacja',
        path: './jobs/focus-research-junior-analyst.html',
        downloadPath: './jobs/focus-research-junior-analyst.html'
      }
    }
  },
  {
    key: 'kolomolo-referral-data-ai-bi',
    versions: {
      en: {
        title: 'Kolomolo: Referral Vacancy — Data / BI / AI',
        description: 'SQL, Power BI, Python, Data Analytics, ETL, RAG, AI/ML and automation',
        path: './jobs/kolomolo-referral-data-ai-bi-en.html',
        downloadPath: './jobs/kolomolo-referral-data-ai-bi-en.html'
      },
      pl: {
        title: 'Kolomolo: Referral Vacancy — Data / BI / AI',
        description: 'SQL, Power BI, Python, analiza danych, ETL, RAG, AI/ML i automatyzacja',
        path: './jobs/kolomolo-referral-data-ai-bi.html',
        downloadPath: './jobs/kolomolo-referral-data-ai-bi.html'
      }
    }
  }
];

const currentVersion = profile => profile.versions[selectedLang] || profile.versions.pl || profile.versions.en;

function showProfile(profile, button, updateUrl = true) {
  selectedKey = profile.key;
  document.querySelectorAll('.tab').forEach(tab => tab.setAttribute('aria-selected', 'false'));
  button?.setAttribute('aria-selected', 'true');
  const cv = currentVersion(profile);
  frame.src = cv.path;
  title.textContent = cv.title;
  download.href = cv.downloadPath;
  download.download = `Witold_Grzesiak_${profile.key}_${selectedLang.toUpperCase()}.html`;
  open.href = cv.path;
  if (updateUrl) history.replaceState(null, '', `#${profile.key}`);
}

function renderTabs() {
  tabs.replaceChildren();
  profiles.forEach(profile => {
    const cv = currentVersion(profile);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'tab';
    button.setAttribute('role', 'tab');
    button.setAttribute('aria-selected', String(profile.key === selectedKey));
    button.innerHTML = `<strong>${cv.title}</strong><span>${cv.description}</span>`;
    button.addEventListener('click', () => showProfile(profile, button));
    tabs.append(button);
  });
  const selected = profiles.find(profile => profile.key === selectedKey) || profiles[0];
  showProfile(selected, tabs.querySelector('[aria-selected="true"]') || tabs.firstElementChild, false);
}

languageButtons.forEach(button => button.addEventListener('click', () => {
  selectedLang = button.dataset.lang;
  localStorage.setItem('cv-language', selectedLang);
  languageButtons.forEach(item => item.classList.toggle('active', item === button));
  renderTabs();
}));
languageButtons.forEach(button => button.classList.toggle('active', button.dataset.lang === selectedLang));
frame.addEventListener('load', () => {
  try { frame.contentDocument.body.classList.add('embedded'); } catch {}
});
print.addEventListener('click', () => {
  try { frame.contentWindow.focus(); frame.contentWindow.print(); }
  catch { window.open(open.href, '_blank', 'noopener'); }
});

fetch('./jobs/manifest.json')
  .then(response => {
    if (!response.ok) throw new Error('Nie udało się pobrać listy CV.');
    return response.json();
  })
  .then(data => {
    profiles = data;
    supplementalProfiles.forEach(profile => {
      if (!profiles.some(item => item.key === profile.key)) profiles.push(profile);
    });
    status.hidden = true;
    renderTabs();
  })
  .catch(error => { status.textContent = error.message; });
