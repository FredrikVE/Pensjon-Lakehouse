<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pensjon Lakehouse | GitHub Pages Showcase</title>
    <meta name="robots" content="noindex, nofollow">

    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="assets/css/main.css">
</head>
<body>

<div class="dashboard">

    <div class="header">
        <h1>Pensjon <span>Lakehouse</span></h1>
        <p>
            Pensjonsdemografi i Norge &middot;
            SSB 07459 + 11654 &middot;
            Bronze &rarr; Silver &rarr; Gold &middot;
            <a href="https://github.com/FredrikVE/Pensjon-Lakehouse" target="_blank" rel="noopener noreferrer">GitHub</a>
        </p>
    </div>

    <div class="kpi-row">
        <div class="kpi-card">
            <div class="label">Pensjonsandel 55+ ($kpi_year)</div>
            <div class="value">$kpi_pensjonsandel%</div>
        </div>
        <div class="kpi-card">
            <div class="label">Innbyggere 55+</div>
            <div class="value">$kpi_55_pluss</div>
        </div>
        <div class="kpi-card">
            <div class="label">Total befolkning</div>
            <div class="value">$kpi_total</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="widget">
            <h2>Pensjonsandel over tid</h2>
            <div class="chart-container"><canvas id="chartTrend"></canvas></div>
        </div>
        <div class="widget">
            <h2>Aldersfordeling</h2>
            <div class="chart-container"><canvas id="chartAlder"></canvas></div>
        </div>
    </div>

    <div class="grid-2">
        <div class="widget">
            <h2>Top 10 kommuner &mdash; andel 55+</h2>
            <div class="chart-container"><canvas id="chartKommuner"></canvas></div>
        </div>
        <div class="widget">
            <h2>Top 10 n&aelig;ringer &mdash; pensjonsvolum (mrd kr)</h2>
            <div class="chart-container"><canvas id="chartNaering"></canvas></div>
        </div>
    </div>

    <div class="grid-1">
        <div class="widget">
            <h2>Aldersgrupper over tid</h2>
            <div class="chart-container-wide"><canvas id="chartAlderTrend"></canvas></div>
        </div>
    </div>

    <div class="grid-1">
        <div class="widget">
            <h2>Kommune-detaljer</h2>

            <div class="search-box">
                <input type="text" id="tableSearch" placeholder="S&oslash;k kommune...">
            </div>

            <div class="table-wrapper">
                <table id="kommuneTable">
                    <thead>
                        <tr>
                            <th data-sort-column="0">Kommune <span class="sort-arrow">&udarr;</span></th>
                            <th data-sort-column="1" class="num">Innbyggere <span class="sort-arrow">&udarr;</span></th>
                            <th data-sort-column="2" class="num">55+ <span class="sort-arrow">&udarr;</span></th>
                            <th data-sort-column="3" class="num">Andel 55+ <span class="sort-arrow">&udarr;</span></th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="footer">
        Generert $generated_date &middot;
        Data:
        <a href="https://www.ssb.no/statbank/table/07459" target="_blank" rel="noopener noreferrer">SSB 07459</a> +
        <a href="https://www.ssb.no/statbank/table/11654" target="_blank" rel="noopener noreferrer">SSB 11654</a>
        &middot;
        <a href="https://github.com/FredrikVE/Pensjon-Lakehouse" target="_blank" rel="noopener noreferrer">FredrikVE/Pensjon-Lakehouse</a>
    </div>
</div>

<script src="assets/js/data.js" defer></script>
<script src="assets/js/charts.js" defer></script>
<script src="assets/js/table.js" defer></script>
<script src="assets/js/main.js" defer></script>

</body>
</html>