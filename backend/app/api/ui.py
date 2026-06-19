from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["ui"])


@router.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse(url="/payments-ui")


@router.get("/payments-ui", response_class=HTMLResponse, include_in_schema=False)
def payments_ui() -> str:
    return """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MetPay - поступившие платежи</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #697386;
      --line: #d9deea;
      --accent: #2457d6;
      --review: #fff4d6;
      --matched: #e8f8ef;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111827;
        --card: #182235;
        --text: #e7ecf5;
        --muted: #9aa8bd;
        --line: #2c3950;
        --accent: #7aa2ff;
        --review: #493b16;
        --matched: #163b2a;
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
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px;
    }
    header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 20px;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 28px;
    }
    .muted { color: var(--muted); }
    .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
      overflow: hidden;
    }
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px;
      border-bottom: 1px solid var(--line);
    }
    .filters {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    select, button {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 9px 12px;
      background: var(--card);
      color: var(--text);
      font: inherit;
    }
    button {
      cursor: pointer;
      background: var(--accent);
      color: white;
      border-color: var(--accent);
      font-weight: 600;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }
    .stat {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }
    .stat strong {
      display: block;
      margin-top: 6px;
      font-size: 22px;
    }
    .table-wrap { overflow-x: auto; }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 980px;
    }
    th, td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      background: color-mix(in srgb, var(--card), var(--bg) 35%);
    }
    tr.needs_review { background: var(--review); }
    tr.matched { background: var(--matched); }
    .badge {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 9px;
      background: var(--bg);
      border: 1px solid var(--line);
      font-weight: 600;
      white-space: nowrap;
    }
    .amount {
      font-weight: 700;
      white-space: nowrap;
    }
    .empty {
      padding: 32px;
      text-align: center;
      color: var(--muted);
    }
    @media (max-width: 760px) {
      header, .toolbar { align-items: stretch; flex-direction: column; }
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Поступившие платежи</h1>
        <div class="muted">Фактические оплаты ЕРИП, принятые через ArtPay</div>
      </div>
      <button type="button" id="refresh">Обновить</button>
    </header>

    <section class="stats" aria-label="Сводка">
      <div class="stat">
        <span class="muted">Всего платежей</span>
        <strong id="paymentsCount">0</strong>
      </div>
      <div class="stat">
        <span class="muted">Привязано</span>
        <strong id="matchedCount">0</strong>
      </div>
      <div class="stat">
        <span class="muted">На проверке</span>
        <strong id="reviewCount">0</strong>
      </div>
      <div class="stat"><span class="muted">Сумма</span><strong id="totalAmount">0.00</strong></div>
    </section>

    <section class="panel">
      <div class="toolbar">
        <div class="filters">
          <label for="statusFilter" class="muted">Статус</label>
          <select id="statusFilter">
            <option value="">Все</option>
            <option value="matched">Привязано</option>
            <option value="needs_review">На проверке</option>
            <option value="received">Получено</option>
            <option value="ignored">Игнорировано</option>
            <option value="duplicate">Дубликат</option>
          </select>
        </div>
        <div class="muted" id="lastUpdated">Еще не обновлялось</div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Дата</th>
              <th>Статус</th>
              <th>Сумма</th>
              <th>ФИО из платежа</th>
              <th>Ученик</th>
              <th>ЕРИП транзакция</th>
              <th>Счет / услуга</th>
            </tr>
          </thead>
          <tbody id="paymentsBody"></tbody>
        </table>
        <div class="empty" id="emptyState" hidden>Платежей пока нет</div>
      </div>
    </section>
  </main>

  <script>
    const statusFilter = document.querySelector("#statusFilter");
    const paymentsBody = document.querySelector("#paymentsBody");
    const emptyState = document.querySelector("#emptyState");
    const lastUpdated = document.querySelector("#lastUpdated");

    const statusLabels = {
      received: "Получено",
      matched: "Привязано",
      needs_review: "На проверке",
      ignored: "Игнорировано",
      duplicate: "Дубликат"
    };

    function formatDate(value) {
      if (!value) return "-";
      return new Intl.DateTimeFormat("ru-RU", {
        dateStyle: "short",
        timeStyle: "short"
      }).format(new Date(value));
    }

    function cell(value, className) {
      const td = document.createElement("td");
      if (className) td.className = className;
      td.textContent = value || "-";
      return td;
    }

    function renderStats(payments) {
      const total = payments.reduce((sum, payment) => sum + Number(payment.amount || 0), 0);
      document.querySelector("#paymentsCount").textContent = payments.length;
      document.querySelector("#matchedCount").textContent =
        payments.filter((payment) => payment.status === "matched").length;
      document.querySelector("#reviewCount").textContent =
        payments.filter((payment) => payment.status === "needs_review").length;
      document.querySelector("#totalAmount").textContent = total.toFixed(2) + " BYN";
    }

    function renderPayments(payments, studentsById) {
      paymentsBody.replaceChildren();
      emptyState.hidden = payments.length > 0;

      for (const payment of payments) {
        const row = document.createElement("tr");
        row.className = payment.status || "";
        const status = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = statusLabels[payment.status] || payment.status || "-";
        status.appendChild(badge);

        row.append(
          cell(String(payment.id)),
          cell(formatDate(payment.paid_at || payment.created_at)),
          status,
          cell(`${payment.amount} ${payment.currency}`, "amount"),
          cell(payment.payer_full_name),
          cell(studentsById.get(payment.student_id) || "Не привязан"),
          cell(payment.ap_erip_trn_id),
          cell([payment.ap_erip_invoice_id, payment.ap_erip_service_no].filter(Boolean).join(" / "))
        );
        paymentsBody.appendChild(row);
      }
    }

    async function loadPayments() {
      const status = statusFilter.value;
      const paymentsUrl = status
        ? `/api/payments?status=${encodeURIComponent(status)}`
        : "/api/payments";
      const [paymentsResponse, studentsResponse] = await Promise.all([
        fetch(paymentsUrl),
        fetch("/api/students")
      ]);

      if (!paymentsResponse.ok || !studentsResponse.ok) {
        throw new Error("Не удалось загрузить данные");
      }

      const payments = await paymentsResponse.json();
      const students = await studentsResponse.json();
      const studentsById = new Map(students.map((student) => [student.id, student.full_name]));

      renderStats(payments);
      renderPayments(payments, studentsById);
      lastUpdated.textContent = "Обновлено: " + formatDate(new Date().toISOString());
    }

    document.querySelector("#refresh").addEventListener("click", () => {
      loadPayments().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    statusFilter.addEventListener("change", () => {
      loadPayments().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });

    loadPayments().catch((error) => {
      lastUpdated.textContent = error.message;
    });
  </script>
</body>
</html>
"""
