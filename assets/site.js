const ruphoDataUrl = 'assets/rupho-data.json';

function getRuphoData() {
  if (window.ruphoData && typeof window.ruphoData === 'object') {
    return Promise.resolve(window.ruphoData);
  }
  return fetch(ruphoDataUrl).then(response => {
    if (!response.ok) {
      throw new Error('Unable to load data file.');
    }
    return response.json();
  });
}

function createLink(text, href, className = '') {
  const a = document.createElement('a');
  a.textContent = text;
  a.href = href;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.className = className;
  return a;
}

function normalizeLabel(item) {
  if (item.label) {
    return item.label;
  }
  return item.key.replace(/\.pdf$/i, '').replace(/_EN_2$/i, '');
}

function renderItem(item) {
  const card = document.createElement('article');
  card.className = 'item-card';

  const title = document.createElement('h3');
  title.textContent = normalizeLabel(item);
  card.appendChild(title);

  const links = document.createElement('div');
  links.className = 'item-links';

  if (item.problem) {
    links.appendChild(createLink('Problem', item.problem, 'item-link'));
  }
  if (item.solution) {
    links.appendChild(createLink('Solution', item.solution, 'item-link'));
  }
  if (!item.problem && !item.solution) {
    const empty = document.createElement('span');
    empty.textContent = 'No PDF available';
    links.appendChild(empty);
  }

  card.appendChild(links);
  return card;
}

function renderYearSection(year, items) {
  const section = document.createElement('section');
  section.className = 'year-section';

  const heading = document.createElement('h2');
  heading.textContent = year;
  section.appendChild(heading);

  const grid = document.createElement('div');
  grid.className = 'item-grid';

  items.forEach(item => grid.appendChild(renderItem(item)));
  section.appendChild(grid);
  return section;
}

function renderPage(sectionKey, sectionTitle) {
  const titleEl = document.getElementById('page-title');
  if (titleEl) titleEl.textContent = sectionTitle;

  const content = document.getElementById('page-content');

  getRuphoData()
    .then(data => {
      const sectionData = data[sectionKey];
      if (!sectionData) {
        content.textContent = 'No data found for this section.';
        return;
      }

      const yearKeys = Object.keys(sectionData).sort((a, b) => Number(b) - Number(a));
      if (yearKeys.length === 0) {
        content.textContent = 'No years available yet.';
        return;
      }

      yearKeys.forEach(year => {
        const yearSection = renderYearSection(year, sectionData[year]);
        content.appendChild(yearSection);
      });
    })
    .catch(error => {
      content.innerHTML = '<p class="error">Could not load the page data.</p>';
      console.error(error);
    });
}
