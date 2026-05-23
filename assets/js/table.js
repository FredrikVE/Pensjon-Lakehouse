// Tabelllogikk: rendering, søk og sortering.

const tableState = {
  sortColumn: 3,
  sortAscending: false
};

const tableColumns = [
  'kommune',
  'innbyggere',
  'innbyggere_55_pluss',
  'andel_pst'
];

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatNumber(value) {
  return Number(value).toLocaleString('nb-NO');
}

function getFilteredRows() {
  const query = document.getElementById('tableSearch').value.toLowerCase();
  return window.PENSJON_DATA.tabell.filter((row) =>
    row.kommune.toLowerCase().includes(query)
  );
}

function sortRows(rows) {
  const key = tableColumns[tableState.sortColumn];

  return rows.sort((a, b) => {
    const valueA = a[key];
    const valueB = b[key];

    if (typeof valueA === 'string') {
      return tableState.sortAscending
        ? valueA.localeCompare(valueB, 'nb-NO')
        : valueB.localeCompare(valueA, 'nb-NO');
    }

    return tableState.sortAscending
      ? valueA - valueB
      : valueB - valueA;
  });
}

function renderSortIndicators() {
  document.querySelectorAll('#kommuneTable thead th[data-sort-column]').forEach((header) => {
    const columnIndex = Number(header.dataset.sortColumn);
    const isSortedColumn = columnIndex === tableState.sortColumn;
    const arrow = header.querySelector('.sort-arrow');

    header.classList.toggle('sorted', isSortedColumn);

    if (arrow) {
      arrow.textContent = isSortedColumn
        ? (tableState.sortAscending ? '↑' : '↓')
        : '↕';
    }
  });
}

function renderTable(rows) {
  const tbody = document.getElementById('tableBody');
  const maxShare = Math.max(...rows.map((row) => row.andel_pst), 1);

  tbody.innerHTML = rows.map((row) => `
    <tr>
      <td>${escapeHtml(row.kommune)}</td>
      <td class="num">${formatNumber(row.innbyggere)}</td>
      <td class="num">${formatNumber(row.innbyggere_55_pluss)}</td>
      <td class="num">
        <div class="andel-bar">
          <div class="bar" style="width:${row.andel_pst / maxShare * 60}px"></div>
          ${row.andel_pst}%
        </div>
      </td>
    </tr>
  `).join('');
}

function updateTable() {
  const rows = sortRows(getFilteredRows());
  renderSortIndicators();
  renderTable(rows);
}

function handleSortClick(event) {
  const column = Number(event.currentTarget.dataset.sortColumn);

  if (tableState.sortColumn === column) {
    tableState.sortAscending = !tableState.sortAscending;
  } else {
    tableState.sortColumn = column;
    tableState.sortAscending = column === 0;
  }

  updateTable();
}

function initTable() {
  document.getElementById('tableSearch').addEventListener('input', updateTable);

  document.querySelectorAll('#kommuneTable thead th[data-sort-column]').forEach((header) => {
    header.addEventListener('click', handleSortClick);
  });

  updateTable();
}
