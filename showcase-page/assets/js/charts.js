// Chart.js-konfigurasjon og initialisering.

const DASHBOARD_COLORS = [
  '#38BDF8',
  '#22C55E',
  '#F59E0B',
  '#A78BFA',
  '#F43F5E',
  '#14B8A6',
  '#F97316',
  '#EAB308'
];

const formatPercent1 = (value) =>
  Number(value).toLocaleString('nb-NO', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }) + '%';

const formatPercent0 = (value) =>
  Number(value).toLocaleString('nb-NO', {
    maximumFractionDigits: 0
  }) + '%';

const formatMrd = (value) =>
  Number(value).toLocaleString('nb-NO', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }) + ' mrd';

function setChartDefaults() {
  Chart.defaults.color = '#94A3B8';
  Chart.defaults.borderColor = 'rgba(51,65,85,0.4)';
  Chart.defaults.font.family = "'DM Sans', sans-serif";
}

function createTrendChart(data) {
  const trendYMin = Math.floor(Math.min(...data.values) * 10) / 10;
  const trendYMax = Math.ceil(Math.max(...data.values) * 10) / 10;

  return new Chart(document.getElementById('chartTrend'), {
    type: 'line',
    data: {
      labels: data.years,
      datasets: [{
        data: data.values,
        borderColor: '#38BDF8',
        backgroundColor: 'rgba(56,189,248,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 3,
        pointBackgroundColor: '#38BDF8',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: {
          min: trendYMin,
          max: trendYMax,
          ticks: {
            stepSize: 0.2,
            callback: formatPercent1
          }
        }
      }
    }
  });
}

function createAgeDistributionChart(data) {
  return new Chart(document.getElementById('chartAlder'), {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: DASHBOARD_COLORS.slice(0, data.labels.length),
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: {
          ticks: {
            callback: (value) => {
              if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
              if (value >= 1000) return (value / 1000).toFixed(0) + 'k';
              return value;
            }
          }
        }
      }
    }
  });
}

function createTopMunicipalitiesChart(data) {
  return new Chart(document.getElementById('chartKommuner'), {
    type: 'bar',
    data: {
      labels: data.labels.slice().reverse(),
      datasets: [{
        data: data.values.slice().reverse(),
        backgroundColor: '#38BDF8',
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { callback: formatPercent1 } },
        y: { grid: { display: false } }
      }
    }
  });
}

function createIndustryChart(data) {
  return new Chart(document.getElementById('chartNaering'), {
    type: 'bar',
    data: {
      labels: data.labels.slice().reverse(),
      datasets: [{
        data: data.values.slice().reverse(),
        backgroundColor: '#22C55E',
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { callback: formatMrd } },
        y: { grid: { display: false } }
      }
    }
  });
}

function createAgeTrendChart(data) {
  const ageGroups = Object.keys(data.series);

  return new Chart(document.getElementById('chartAlderTrend'), {
    type: 'line',
    data: {
      labels: data.years,
      datasets: ageGroups.map((group, index) => ({
        label: group,
        data: data.series[group],
        borderColor: DASHBOARD_COLORS[index % DASHBOARD_COLORS.length],
        backgroundColor: DASHBOARD_COLORS[index % DASHBOARD_COLORS.length] + '66',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 1.5
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 12, padding: 16, font: { size: 11 } }
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          stacked: true,
          min: 0,
          max: 100,
          ticks: {
            stepSize: 20,
            callback: formatPercent0
          }
        }
      }
    }
  });
}

function initCharts() {
  const data = window.PENSJON_DATA;

  setChartDefaults();
  createTrendChart(data.trend);
  createAgeDistributionChart(data.alder);
  createTopMunicipalitiesChart(data.kommuner);
  createIndustryChart(data.naering);
  createAgeTrendChart(data.alderTrend);
}
