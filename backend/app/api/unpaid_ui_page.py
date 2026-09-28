UNPAID_UI_HTML = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MetPay - неоплаченные</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #697386;
      --line: #d9deea;
      --accent: #2457d6;
      --ok: #1f7a4d;
      --warn: #9a6700;
      --bad: #b42318;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111827;
        --card: #182235;
        --text: #e7ecf5;
        --muted: #9aa8bd;
        --line: #2c3950;
        --accent: #7aa2ff;
        --ok: #6ee7b7;
        --warn: #fbbf24;
        --bad: #fca5a5;
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main {
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px;
    }
    .muted { color: var(--muted); }
    .app-nav {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }
    .app-nav a {
      display: inline-flex;
      align-items: center;
      padding: 8px 14px;
      border-radius: 10px;
      border: 1px solid var(--line);
      text-decoration: none;
      color: var(--text);
      font-weight: 500;
    }
    .app-nav a.active {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }
    header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }
    h1 { margin: 0 0 6px; font-size: 28px; }
    button {
      cursor: pointer;
      border: 1px solid var(--accent);
      border-radius: 10px;
      padding: 9px 12px;
      background: var(--accent);
      color: #fff;
      font: inherit;
      font-weight: 600;
    }
    button.btn-secondary {
      background: var(--card);
      color: var(--text);
      border-color: var(--line);
      font-weight: 500;
    }
    button:disabled {
      opacity: 0.65;
      cursor: wait;
    }
    .filters {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: end;
      margin-bottom: 16px;
    }
    .field {
      display: grid;
      gap: 6px;
    }
    .field label {
      font-size: 12px;
      color: var(--muted);
      font-weight: 600;
    }
    select {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 8px 10px;
      background: var(--card);
      color: var(--text);
      font: inherit;
      min-width: 180px;
    }
    .summary-bar {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .stat {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px 16px;
    }
    .stat strong {
      display: block;
      font-size: 22px;
      margin-top: 4px;
    }
    .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
      overflow: hidden;
    }
    .table-wrap { overflow-x: auto; }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
    }
    th, td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      background: color-mix(in srgb, var(--card), var(--bg) 35%);
    }
    .amount { font-weight: 700; white-space: nowrap; }
    .empty {
      padding: 32px;
      text-align: center;
      color: var(--muted);
    }
    .status {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 3px 10px;
      font-size: 12px;
      font-weight: 600;
    }
    .status-unpaid {
      background: color-mix(in srgb, var(--bad), transparent 88%);
      color: var(--bad);
    }
    .status-partial {
      background: color-mix(in srgb, var(--warn), transparent 88%);
      color: var(--warn);
    }
    a.student-link {
      color: inherit;
      font-weight: 600;
      text-decoration: none;
    }
    a.student-link:hover { color: var(--accent); }
    .header-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    @media print {
      body { background: #fff; color: #000; }
      .app-nav, .header-actions, .filters button { display: none !important; }
      .panel, .stat { box-shadow: none; border-color: #ccc; }
      main { max-width: none; padding: 0; }
    }
    @media (max-width: 720px) {
      .summary-bar { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <nav class="app-nav" aria-label="Разделы">
      <a href="/payments-ui">Платежи</a>
      <a href="/groups-ui">Группы</a>
      <a href="/unpaid-ui" class="active">Неоплаченные</a>
    </nav>
    <header>
      <div>
        <h1>Отчёт по неоплаченным</h1>
        <div class="muted" id="pageSubtitle">Выберите месяц</div>
      </div>
      <div class="header-actions">
        <button type="button" class="btn-secondary" id="printBtn">Печать</button>
        <button type="button" id="refresh">Обновить</button>
      </div>
    </header>

    <div class="filters">
      <div class="field">
        <label for="periodSelect">Месяц</label>
        <select id="periodSelect"></select>
      </div>
      <div class="field">
        <label for="groupSelect">Группа</label>
        <select id="groupSelect">
          <option value="">Все группы</option>
        </select>
      </div>
      <div class="field">
        <label for="statusSelect">Статус</label>
        <select id="statusSelect">
          <option value="not_full" selected>Не оплатили полностью</option>
          <option value="unpaid">Не оплатили</option>
          <option value="partial">Частично</option>
        </select>
      </div>
      <button type="button" id="loadBtn">Сформировать</button>
      <div class="muted" id="lastUpdated">Еще не обновлялось</div>
    </div>

    <section class="summary-bar" aria-label="Сводка">
      <div class="stat">
        <span class="muted">Не оплатили</span>
        <strong id="unpaidCount">0</strong>
      </div>
      <div class="stat">
        <span class="muted">Частично</span>
        <strong id="partialCount">0</strong>
      </div>
      <div class="stat">
        <span class="muted">Ожидаем к оплате</span>
        <strong id="expectedTotal">0.00 BYN</strong>
      </div>
    </section>

    <section class="panel">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ученик</th>
              <th>Группа</th>
              <th>Статус</th>
              <th>Оплачено</th>
              <th>Ожидаем</th>
              <th>Взнос</th>
            </tr>
          </thead>
          <tbody id="reportBody"></tbody>
        </table>
        <div class="empty" id="emptyState">Выберите месяц и нажмите «Сформировать»</div>
      </div>
    </section>
  </main>

  <script>
    const CURRENT_SEASON = "2026/2027";
    const periodSelect = document.querySelector("#periodSelect");
    const groupSelect = document.querySelector("#groupSelect");
    const statusSelect = document.querySelector("#statusSelect");
    const loadBtn = document.querySelector("#loadBtn");
    const refreshBtn = document.querySelector("#refresh");
    const printBtn = document.querySelector("#printBtn");
    const pageSubtitle = document.querySelector("#pageSubtitle");
    const lastUpdated = document.querySelector("#lastUpdated");
    const unpaidCountEl = document.querySelector("#unpaidCount");
    const partialCountEl = document.querySelector("#partialCount");
    const expectedTotalEl = document.querySelector("#expectedTotal");
    const reportBody = document.querySelector("#reportBody");
    const emptyState = document.querySelector("#emptyState");

    const statusLabels = {
      unpaid: "Не оплачено",
      partial: "Частично",
    };
    const filterLabels = {
      not_full: "не оплатили полностью",
      unpaid: "не оплатили",
      partial: "частично",
    };

    function formatAmount(value) {
      if (value == null || value === "") return "—";
      return `${Number(value).toFixed(2)} BYN`;
    }

    function currentPeriod() {
      const now = new Date();
      return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
    }

    async function loadFilters() {
      const [optionsResponse, groupsResponse] = await Promise.all([
        fetch(`/api/payments/payment-for-options?season=${encodeURIComponent(CURRENT_SEASON)}`),
        fetch("/api/groups"),
      ]);
      if (!optionsResponse.ok) throw new Error("Не удалось загрузить месяцы");
      if (!groupsResponse.ok) throw new Error("Не удалось загрузить группы");
      const options = await optionsResponse.json();
      const groups = await groupsResponse.json();

      const selectedPeriod = periodSelect.value || currentPeriod();
      periodSelect.replaceChildren();
      for (const item of options) {
        if (item.value === "tournament") continue;
        const option = document.createElement("option");
        option.value = item.value;
        option.textContent = item.label;
        periodSelect.appendChild(option);
      }
      if ([...periodSelect.options].some((item) => item.value === selectedPeriod)) {
        periodSelect.value = selectedPeriod;
      }

      const selectedGroup = groupSelect.value;
      groupSelect.replaceChildren();
      const allOption = document.createElement("option");
      allOption.value = "";
      allOption.textContent = "Все группы";
      groupSelect.appendChild(allOption);
      for (const group of groups.filter((item) => item.active !== false)) {
        const option = document.createElement("option");
        option.value = String(group.id);
        option.textContent = group.name;
        groupSelect.appendChild(option);
      }
      if (selectedGroup) groupSelect.value = selectedGroup;
    }

    function renderReport(report) {
      const filterLabel = filterLabels[report.status_filter] || filterLabels.not_full;
      pageSubtitle.textContent =
        `${filterLabel[0].toUpperCase()}${filterLabel.slice(1)} за ${report.period_label.toLowerCase()}`;
      unpaidCountEl.textContent = String(report.unpaid_count);
      partialCountEl.textContent = String(report.partial_count);
      expectedTotalEl.textContent = formatAmount(report.expected_total);

      reportBody.replaceChildren();
      emptyState.hidden = report.items.length > 0;
      emptyState.textContent = "Нет учеников по выбранному фильтру";
      for (const item of report.items) {
        const row = document.createElement("tr");
        const nameCell = document.createElement("td");
        const link = document.createElement("a");
        link.className = "student-link";
        link.href = `/students-ui/${item.student_id}`;
        link.textContent = item.student_full_name;
        nameCell.appendChild(link);

        const statusCell = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = `status status-${item.status}`;
        badge.textContent = statusLabels[item.status] || item.status;
        statusCell.appendChild(badge);

        row.append(
          nameCell,
          Object.assign(document.createElement("td"), { textContent: item.group_name || "—" }),
          statusCell,
          Object.assign(document.createElement("td"), {
            textContent: formatAmount(item.paid_amount),
            className: "amount",
          }),
          Object.assign(document.createElement("td"), {
            textContent: formatAmount(item.expected_amount),
            className: "amount",
          }),
          Object.assign(document.createElement("td"), {
            textContent: formatAmount(item.monthly_fee),
            className: "amount",
          })
        );
        reportBody.appendChild(row);
      }
    }

    async function loadReport() {
      const period = periodSelect.value;
      if (!period) {
        lastUpdated.textContent = "Выберите месяц";
        return;
      }
      loadBtn.disabled = true;
      refreshBtn.disabled = true;
      try {
        const params = new URLSearchParams({
          period,
          status: statusSelect.value || "not_full",
        });
        if (groupSelect.value) params.set("group_id", groupSelect.value);
        const response = await fetch(`/api/reports/unpaid-by-month?${params}`);
        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new Error(
            typeof body.detail === "string" ? body.detail : "Не удалось сформировать отчёт"
          );
        }
        const report = await response.json();
        renderReport(report);
        lastUpdated.textContent = "Обновлено: " + new Intl.DateTimeFormat("ru-RU", {
          dateStyle: "short",
          timeStyle: "short",
        }).format(new Date());
      } finally {
        loadBtn.disabled = false;
        refreshBtn.disabled = false;
      }
    }

    loadBtn.addEventListener("click", () => {
      loadReport().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    refreshBtn.addEventListener("click", () => {
      loadFilters()
        .then(() => loadReport())
        .catch((error) => {
          lastUpdated.textContent = error.message;
        });
    });
    printBtn.addEventListener("click", () => window.print());
    periodSelect.addEventListener("change", () => {
      loadReport().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    groupSelect.addEventListener("change", () => {
      loadReport().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    statusSelect.addEventListener("change", () => {
      loadReport().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });

    loadFilters()
      .then(() => loadReport())
      .catch((error) => {
        lastUpdated.textContent = error.message;
      });
  </script>
</body>
</html>
"""
