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
      width: 100%;
      max-width: 100%;
      margin: 0 auto;
      padding: 20px 16px 32px;
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
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
      padding: 16px;
      border-bottom: 1px solid var(--line);
    }
    .filters-scroll {
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      padding-bottom: 2px;
    }
    .filters {
      display: flex;
      flex-wrap: nowrap;
      gap: 10px;
      width: max-content;
      min-width: 100%;
    }
    .filter-field {
      display: flex;
      flex-direction: column;
      gap: 4px;
      flex: 0 0 auto;
      width: 124px;
    }
    .filter-field-wide {
      width: 152px;
    }
    .filter-field label {
      font-size: 12px;
    }
    .filter-field select {
      width: 100%;
      min-width: 0;
      padding: 7px 10px;
      font-size: 13px;
    }
    select, button {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 9px 12px;
      background: var(--card);
      color: var(--text);
      font: inherit;
    }
    .inline-select {
      min-width: 110px;
      padding: 6px 8px;
      font-size: 13px;
    }
    button {
      cursor: pointer;
      background: var(--accent);
      color: white;
      border-color: var(--accent);
      font-weight: 600;
    }
    button.btn-secondary {
      background: var(--card);
      color: var(--text);
      border-color: var(--line);
      font-weight: 500;
    }
    .student-cell {
      display: flex;
      align-items: center;
      gap: 6px;
      width: 100%;
    }
    .student-cell .student-link {
      flex: 1;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
    }
    .student-cell .student-link:hover {
      text-decoration: underline;
    }
    .btn-icon {
      flex-shrink: 0;
      padding: 4px 8px;
      font-size: 12px;
      line-height: 1.2;
      white-space: nowrap;
    }
    .modal {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.45);
      display: grid;
      place-items: center;
      padding: 20px;
      z-index: 20;
    }
    .modal[hidden] { display: none; }
    .modal-card {
      width: min(520px, 100%);
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 20px 40px rgba(15, 23, 42, 0.18);
    }
    .modal-card h3 {
      margin: 0 0 8px;
    }
    .modal-field {
      display: grid;
      gap: 6px;
      margin: 14px 0;
    }
    .modal-field input,
    .modal-field select {
      width: 100%;
    }
    .modal-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 18px;
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
    .table-wrap {
      overflow-x: auto;
      max-width: 100%;
      -webkit-overflow-scrolling: touch;
    }
    .payments-table-wrap {
      border-top: 1px solid var(--line);
    }
    th.sortable {
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }
    th.sortable:hover {
      color: var(--text);
    }
    th.sortable::after {
      content: "↕";
      display: inline-block;
      margin-left: 5px;
      font-size: 11px;
      opacity: 0.35;
    }
    th.sortable.sorted-asc::after {
      content: "↑";
      opacity: 1;
    }
    th.sortable.sorted-desc::after {
      content: "↓";
      opacity: 1;
    }
    .payments-table-wrap {
      border-top: 1px solid var(--line);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 900px;
    }
    th, td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
    }
    th.col-student,
    td.col-student {
      min-width: 200px;
      max-width: 280px;
    }
    th.col-payer,
    td.col-payer {
      min-width: 140px;
      max-width: 200px;
    }
    th.col-season,
    td.col-season {
      min-width: 88px;
      white-space: nowrap;
    }
    th.col-payment-for,
    td.col-payment-for {
      min-width: 132px;
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
    .app-nav {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
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
    .section-title {
      margin: 0 0 12px;
      font-size: 1.1rem;
    }
    @media (max-width: 760px) {
      header, .toolbar { align-items: stretch; flex-direction: column; }
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  </style>
</head>
<body>
  <main>
    <nav class="app-nav" aria-label="Разделы">
      <a href="/payments-ui" class="active">Платежи</a>
      <a href="/groups-ui">Группы</a>
    </nav>
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
        <div class="muted" id="lastUpdated">Еще не обновлялось</div>
      </div>
      <div class="table-wrap payments-table-wrap">
        <table>
          <thead>
            <tr>
              <th class="sortable" data-sort="id">ID</th>
              <th class="sortable" data-sort="date">Дата</th>
              <th class="sortable" data-sort="status">Статус</th>
              <th class="sortable" data-sort="amount">Сумма</th>
              <th class="sortable col-season" data-sort="season">Сезон</th>
              <th class="sortable col-payment-for" data-sort="payment_for">Оплата</th>
              <th class="sortable" data-sort="payer">ФИО из платежа</th>
              <th class="sortable col-student" data-sort="student">Ученик</th>
              <th class="sortable" data-sort="group">Группа</th>
            </tr>
          </thead>
          <tbody id="paymentsBody"></tbody>
        </table>
        <div class="empty" id="emptyState" hidden>Платежей пока нет</div>
      </div>
    </section>

    <section class="panel" aria-label="Отчёты">
      <h2 style="margin: 0 0 12px; font-size: 1.1rem;">Отчёты за сезон</h2>
      <div class="stats" style="margin-bottom: 16px;">
        <div class="stat" style="grid-column: 1 / -1;">
          <span class="muted">Поступления по месяцам</span>
        </div>
      </div>
      <div class="table-wrap" style="margin-bottom: 24px;">
        <table>
          <thead>
            <tr>
              <th>Месяц</th>
              <th>Платежей</th>
              <th>Сумма</th>
            </tr>
          </thead>
          <tbody id="monthsBody"></tbody>
        </table>
        <div class="empty" id="monthsEmpty" hidden>Нет данных</div>
      </div>
      <div class="stats" style="margin-bottom: 16px;">
        <div class="stat" style="grid-column: 1 / -1;">
          <span class="muted">Поступления по ученику</span>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ученик</th>
              <th>Группа</th>
              <th>Платежей</th>
              <th>Сумма</th>
            </tr>
          </thead>
          <tbody id="studentsBody"></tbody>
        </table>
        <div class="empty" id="studentsEmpty" hidden>Нет данных</div>
      </div>
    </section>
  </main>

  <div id="studentEditor" class="modal" hidden>
    <div class="modal-card" role="dialog" aria-labelledby="studentEditorTitle">
      <h3 id="studentEditorTitle">Редактирование ученика</h3>
      <p class="muted" id="editorPaymentInfo"></p>
      <label class="modal-field">
        <span>ФИО ученика</span>
        <input id="editorFullName" type="text" autocomplete="off">
      </label>
      <label class="modal-field">
        <span>Привязать платёж или объединить с</span>
        <select id="editorTargetStudent"></select>
      </label>
      <div class="modal-actions">
        <button type="button" id="editorSaveName">Сохранить ФИО</button>
        <button type="button" id="editorReassign" class="btn-secondary">Привязать платёж</button>
        <button type="button" id="editorMerge" class="btn-secondary">Объединить учеников</button>
        <button type="button" id="editorClose" class="btn-secondary">Закрыть</button>
      </div>
    </div>
  </div>

  <script>
    const paymentsBody = document.querySelector("#paymentsBody");
    const monthsBody = document.querySelector("#monthsBody");
    const studentsBody = document.querySelector("#studentsBody");
    const emptyState = document.querySelector("#emptyState");
    const monthsEmpty = document.querySelector("#monthsEmpty");
    const studentsEmpty = document.querySelector("#studentsEmpty");
    const lastUpdated = document.querySelector("#lastUpdated");

    const statusLabels = {
      received: "Получено",
      matched: "Привязано",
      needs_review: "На проверке",
      ignored: "Игнорировано",
      duplicate: "Дубликат"
    };

    const REPORT_SEASON = "2025/2026";

    let studentsById = new Map();
    let editorContext = null;
    let paymentForOptions = [];
    let paymentForLabels = new Map();
    let cachedPayments = [];
    let cachedGroups = [];
    let cachedReviewByPaymentId = new Map();
    let sortColumn = "date";
    let sortDirection = "desc";

    function compareSortValues(left, right) {
      if (left == null && right == null) return 0;
      if (left == null || left === "") return -1;
      if (right == null || right === "") return 1;
      if (typeof left === "number" && typeof right === "number") {
        return left - right;
      }
      return String(left).localeCompare(String(right), "ru", {
        numeric: true,
        sensitivity: "base",
      });
    }

    function paymentSortValue(payment, key, groupsById) {
      switch (key) {
        case "id":
          return payment.id;
        case "date": {
          const raw = payment.paid_at || payment.created_at;
          return raw ? new Date(raw).getTime() : 0;
        }
        case "status":
          return statusLabels[payment.status] || payment.status || "";
        case "amount":
          return Number(payment.amount || 0);
        case "season":
          return payment.season || "";
        case "payment_for":
          return paymentForLabels.get(payment.payment_for) || payment.payment_for || "";
        case "payer":
          return payment.payer_full_name || "";
        case "student": {
          const student = payment.student_id ? studentsById.get(payment.student_id) : null;
          return student?.full_name || "";
        }
        case "group": {
          const student = payment.student_id ? studentsById.get(payment.student_id) : null;
          if (!student?.group_id) return "";
          return groupsById.get(student.group_id)?.name || "";
        }
        default:
          return "";
      }
    }

    function sortPayments(payments, groups) {
      const groupsById = new Map(groups.map((group) => [group.id, group]));
      const direction = sortDirection === "asc" ? 1 : -1;
      return [...payments].sort((left, right) => {
        const cmp = compareSortValues(
          paymentSortValue(left, sortColumn, groupsById),
          paymentSortValue(right, sortColumn, groupsById)
        );
        if (cmp !== 0) return cmp * direction;
        return (left.id - right.id) * direction;
      });
    }

    function updateSortHeaders() {
      for (const header of document.querySelectorAll("th.sortable")) {
        header.classList.remove("sorted-asc", "sorted-desc");
        if (header.dataset.sort === sortColumn) {
          header.classList.add(sortDirection === "asc" ? "sorted-asc" : "sorted-desc");
        }
      }
    }

    function applySortAndRender() {
      const sorted = sortPayments(cachedPayments, cachedGroups);
      renderStats(cachedPayments);
      renderPayments(sorted, cachedGroups, cachedReviewByPaymentId);
    }

    async function loadPaymentForOptions(season) {
      const url = season
        ? `/api/payments/payment-for-options?season=${encodeURIComponent(season)}`
        : "/api/payments/payment-for-options";
      const response = await fetch(url);
      if (!response.ok) throw new Error("Не удалось загрузить периоды оплаты");
      return response.json();
    }

    function seasonCell(value) {
      const td = document.createElement("td");
      td.className = "col-season";
      td.textContent = value || "-";
      return td;
    }

    function createPaymentForSelect(payment) {
      const td = document.createElement("td");
      td.className = "col-payment-for";
      const select = document.createElement("select");
      select.className = "inline-select";
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "—";
      select.appendChild(empty);
      for (const item of paymentForOptions) {
        const option = document.createElement("option");
        option.value = item.value;
        option.textContent = item.label;
        if (payment.payment_for === item.value) option.selected = true;
        select.appendChild(option);
      }
      select.addEventListener("change", () => {
        const paymentFor = select.value || null;
        select.disabled = true;
        fetch(`/api/payments/${payment.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ payment_for: paymentFor }),
        })
          .then((response) => {
            if (!response.ok) throw new Error("Не удалось сохранить период оплаты");
            payment.payment_for = paymentFor;
          })
          .catch((error) => {
            lastUpdated.textContent = error.message;
            select.value = payment.payment_for || "";
          })
          .finally(() => {
            select.disabled = false;
          });
      });
      td.appendChild(select);
      return td;
    }

    const studentEditor = document.querySelector("#studentEditor");
    const editorPaymentInfo = document.querySelector("#editorPaymentInfo");
    const editorFullName = document.querySelector("#editorFullName");
    const editorTargetStudent = document.querySelector("#editorTargetStudent");

    function closeStudentEditor() {
      studentEditor.hidden = true;
      editorContext = null;
    }

    function fillTargetStudentOptions(currentStudentId) {
      editorTargetStudent.replaceChildren();
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "Выберите ученика";
      editorTargetStudent.appendChild(empty);
      for (const student of studentsById.values()) {
        if (!student.active || student.id === currentStudentId) continue;
        const option = document.createElement("option");
        option.value = String(student.id);
        option.textContent = student.full_name;
        editorTargetStudent.appendChild(option);
      }
    }

    function openStudentEditor(payment, student) {
      editorContext = { payment, student };
      editorPaymentInfo.textContent =
        `Платёж #${payment.id} · ${payment.payer_full_name || "без ФИО"}`;
      editorFullName.value = student.full_name;
      fillTargetStudentOptions(student.id);
      studentEditor.hidden = false;
      editorFullName.focus();
    }

    async function saveStudentName() {
      if (!editorContext) return;
      const response = await fetch(`/api/students/${editorContext.student.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: editorFullName.value }),
      });
      if (!response.ok) throw new Error("Не удалось сохранить ФИО");
      closeStudentEditor();
      await loadPayments();
    }

    async function reassignPayment() {
      if (!editorContext || !editorTargetStudent.value) {
        throw new Error("Выберите ученика для привязки");
      }
      const response = await fetch(`/api/payments/${editorContext.payment.id}/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: Number(editorTargetStudent.value) }),
      });
      if (!response.ok) throw new Error("Не удалось привязать платёж");
      closeStudentEditor();
      await loadPayments();
    }

    async function mergeStudents() {
      if (!editorContext || !editorTargetStudent.value) {
        throw new Error("Выберите ученика для объединения");
      }
      const sourceName = editorContext.student.full_name;
      const target = studentsById.get(Number(editorTargetStudent.value));
      const confirmed = window.confirm(
        `Объединить «${sourceName}» с «${target?.full_name || ""}»? ` +
          "Все платежи будут перенесены, текущая запись ученика будет деактивирована."
      );
      if (!confirmed) return;
      const response = await fetch(`/api/students/${editorContext.student.id}/merge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_student_id: Number(editorTargetStudent.value) }),
      });
      if (!response.ok) throw new Error("Не удалось объединить учеников");
      closeStudentEditor();
      await loadPayments();
    }

    document.querySelector("#editorSaveName").addEventListener("click", () => {
      saveStudentName().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    document.querySelector("#editorReassign").addEventListener("click", () => {
      reassignPayment().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    document.querySelector("#editorMerge").addEventListener("click", () => {
      mergeStudents().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    document.querySelector("#editorClose").addEventListener("click", closeStudentEditor);
    studentEditor.addEventListener("click", (event) => {
      if (event.target === studentEditor) closeStudentEditor();
    });

    async function assignGroup(studentId, groupId) {
      const response = await fetch(`/api/students/${studentId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ group_id: groupId }),
      });
      if (!response.ok) {
        throw new Error("Не удалось назначить группу");
      }
      const student = await response.json();
      studentsById.set(studentId, student);
    }

    function createGroupSelect(studentId, currentGroupId, groups) {
      const td = document.createElement("td");
      if (!studentId) {
        td.textContent = "—";
        return td;
      }

      const select = document.createElement("select");
      select.className = "inline-select";
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "—";
      select.appendChild(empty);

      for (const group of groups) {
        const option = document.createElement("option");
        option.value = String(group.id);
        option.textContent = group.name;
        if (group.id === currentGroupId) {
          option.selected = true;
        }
        select.appendChild(option);
      }

      select.addEventListener("change", () => {
        const groupId = select.value ? Number(select.value) : null;
        select.disabled = true;
        assignGroup(studentId, groupId)
          .catch((error) => {
            lastUpdated.textContent = error.message;
          })
          .finally(() => {
            select.disabled = false;
          });
      });

      td.appendChild(select);
      return td;
    }

    function createStudentCell(payment, reviewInfo) {
      const td = document.createElement("td");
      td.className = "col-student";
      const student = payment.student_id ? studentsById.get(payment.student_id) : null;
      if (student) {
        const wrap = document.createElement("div");
        wrap.className = "student-cell";
        const link = document.createElement("a");
        link.className = "student-link";
        link.href = `/students-ui/${student.id}`;
        link.textContent = student.full_name;
        link.title = "Все платежи ученика";
        const editBtn = document.createElement("button");
        editBtn.type = "button";
        editBtn.className = "btn-secondary btn-icon";
        editBtn.textContent = "Изменить";
        editBtn.addEventListener("click", () => openStudentEditor(payment, student));
        wrap.append(link, editBtn);
        td.appendChild(wrap);
        return td;
      }
      if (payment.status !== "needs_review") {
        td.textContent = "Не привязан";
        return td;
      }

      const select = document.createElement("select");
      select.className = "inline-select";
      select.style.width = "100%";
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "Выберите ученика";
      select.appendChild(empty);

      const candidateIds = reviewInfo?.candidate_student_ids || [];
      const listed = candidateIds.length
        ? candidateIds
            .map((id) => studentsById.get(id))
            .filter(Boolean)
        : Array.from(studentsById.values()).filter((item) => item.active);

      for (const item of listed) {
        const option = document.createElement("option");
        option.value = String(item.id);
        option.textContent = item.full_name;
        select.appendChild(option);
      }

      select.addEventListener("change", async () => {
        if (!select.value) return;
        select.disabled = true;
        try {
          const response = await fetch(`/api/payments/${payment.id}/match`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_id: Number(select.value) }),
          });
          if (!response.ok) {
            throw new Error("Не удалось привязать платёж");
          }
          await loadPayments();
        } catch (error) {
          lastUpdated.textContent = error.message;
          select.disabled = false;
        }
      });

      td.appendChild(select);
      return td;
    }

    function buildQuery(path, params) {
      const query = new URLSearchParams();
      for (const [key, value] of Object.entries(params)) {
        if (value === "" || value == null) continue;
        if (key === "ungrouped") {
          query.set(key, "true");
          continue;
        }
        query.set(key, value);
      }
      const suffix = query.toString();
      return suffix ? `${path}?${suffix}` : path;
    }

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

    function payerCell(value) {
      const td = document.createElement("td");
      td.className = "col-payer";
      td.textContent = value || "-";
      td.title = value || "";
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

    function renderPayments(payments, groups, reviewByPaymentId) {
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

        const student = payment.student_id ? studentsById.get(payment.student_id) : null;
        row.append(
          cell(String(payment.id)),
          cell(formatDate(payment.paid_at || payment.created_at)),
          status,
          cell(`${payment.amount} ${payment.currency}`, "amount"),
          seasonCell(payment.season),
          createPaymentForSelect(payment),
          payerCell(payment.payer_full_name),
          createStudentCell(payment, reviewByPaymentId.get(payment.id)),
          createGroupSelect(
            payment.student_id,
            student?.group_id ?? null,
            groups
          )
        );
        paymentsBody.appendChild(row);
      }
    }

    function renderMonthReport(months) {
      monthsBody.replaceChildren();
      monthsEmpty.hidden = months.length > 0;
      for (const item of months) {
        const row = document.createElement("tr");
        row.append(
          cell(item.month),
          cell(String(item.payments_count)),
          cell(`${item.total_amount} BYN`, "amount")
        );
        monthsBody.appendChild(row);
      }
    }

    function renderStudentReport(rows) {
      studentsBody.replaceChildren();
      studentsEmpty.hidden = rows.length > 0;
      for (const item of rows) {
        const row = document.createElement("tr");
        row.append(
          cell(item.student_full_name),
          cell(item.group_name || "—"),
          cell(String(item.payments_count)),
          cell(`${item.total_amount} BYN`, "amount")
        );
        studentsBody.appendChild(row);
      }
    }

    async function loadPayments() {
      const periodOptions = await loadPaymentForOptions(null);
      paymentForOptions = periodOptions;
      paymentForLabels = new Map(periodOptions.map((item) => [item.value, item.label]));
      const reportParams = { season: REPORT_SEASON };
      const responses = await Promise.all([
        fetch("/api/payments"),
        fetch("/api/students"),
        fetch("/api/groups"),
        fetch("/api/reports/needs-review"),
        fetch(buildQuery("/api/reports/by-month", reportParams)),
        fetch(buildQuery("/api/reports/by-student", reportParams)),
      ]);
      const [
        paymentsResponse,
        studentsResponse,
        groupsResponse,
        reviewResponse,
        monthResponse,
        byStudentResponse,
      ] = responses;

      if (!paymentsResponse.ok || !studentsResponse.ok || !groupsResponse.ok) {
        throw new Error("Не удалось загрузить данные");
      }

      const payments = await paymentsResponse.json();
      const students = await studentsResponse.json();
      const groups = await groupsResponse.json();
      const reviewItems = reviewResponse.ok ? await reviewResponse.json() : [];
      const months = monthResponse.ok ? await monthResponse.json() : [];
      const byStudent = byStudentResponse.ok ? await byStudentResponse.json() : [];
      studentsById = new Map(students.map((student) => [student.id, student]));
      cachedPayments = payments;
      cachedGroups = groups;
      cachedReviewByPaymentId = new Map(
        reviewItems.map((item) => [item.payment_id, item])
      );

      updateSortHeaders();
      applySortAndRender();
      renderMonthReport(months);
      renderStudentReport(byStudent);
      lastUpdated.textContent = "Обновлено: " + formatDate(new Date().toISOString());
    }

    document.querySelector("#refresh").addEventListener("click", () => {
      loadPayments().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    for (const header of document.querySelectorAll("th.sortable")) {
      header.addEventListener("click", () => {
        const key = header.dataset.sort;
        if (sortColumn === key) {
          sortDirection = sortDirection === "asc" ? "desc" : "asc";
        } else {
          sortColumn = key;
          sortDirection = "asc";
        }
        updateSortHeaders();
        applySortAndRender();
      });
    }

    loadPayments().catch((error) => {
      lastUpdated.textContent = error.message;
    });
  </script>
</body>
</html>
"""


@router.get("/students-ui/{student_id}", response_class=HTMLResponse, include_in_schema=False)
def student_payments_ui(student_id: int) -> str:
    return """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MetPay - платежи ученика</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #697386;
      --line: #d9deea;
      --accent: #2457d6;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111827;
        --card: #182235;
        --text: #e7ecf5;
        --muted: #9aa8bd;
        --line: #2c3950;
        --accent: #7aa2ff;
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
      max-width: 960px;
      margin: 0 auto;
      padding: 32px 20px;
    }
    .muted { color: var(--muted); }
    .app-nav {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
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
      min-width: 640px;
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
    select {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 6px 8px;
      background: var(--card);
      color: var(--text);
      font: inherit;
      font-size: 13px;
      min-width: 132px;
    }
    .amount { font-weight: 700; white-space: nowrap; }
    .empty {
      padding: 32px;
      text-align: center;
      color: var(--muted);
    }
    .toolbar {
      padding: 12px 18px;
      border-bottom: 1px solid var(--line);
    }
  </style>
</head>
<body>
  <main>
    <nav class="app-nav" aria-label="Разделы">
      <a href="/payments-ui">Платежи</a>
      <a href="/groups-ui">Группы</a>
    </nav>
    <header>
      <div>
        <h1 id="studentTitle">Платежи ученика</h1>
        <div class="muted" id="studentSummary">Загрузка…</div>
      </div>
      <button type="button" id="refresh">Обновить</button>
    </header>
    <section class="panel">
      <div class="toolbar muted" id="lastUpdated">Еще не обновлялось</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              <th>Сумма</th>
              <th>ФИО из платежа</th>
              <th>Сезон</th>
              <th>Оплата</th>
            </tr>
          </thead>
          <tbody id="paymentsBody"></tbody>
        </table>
        <div class="empty" id="emptyState" hidden>Платежей пока нет</div>
      </div>
    </section>
  </main>

  <script>
    const studentId = Number(window.location.pathname.split("/").pop());
    const studentTitle = document.querySelector("#studentTitle");
    const studentSummary = document.querySelector("#studentSummary");
    const paymentsBody = document.querySelector("#paymentsBody");
    const emptyState = document.querySelector("#emptyState");
    const lastUpdated = document.querySelector("#lastUpdated");
    const paymentForOptionsBySeason = new Map();

    function formatDate(value) {
      if (!value) return "-";
      return new Intl.DateTimeFormat("ru-RU", {
        dateStyle: "short",
        timeStyle: "short"
      }).format(new Date(value));
    }

    async function loadPaymentForOptions(season) {
      const key = season || "";
      if (paymentForOptionsBySeason.has(key)) {
        return paymentForOptionsBySeason.get(key);
      }
      const url = season
        ? `/api/payments/payment-for-options?season=${encodeURIComponent(season)}`
        : "/api/payments/payment-for-options";
      const response = await fetch(url);
      if (!response.ok) throw new Error("Не удалось загрузить периоды оплаты");
      const options = await response.json();
      paymentForOptionsBySeason.set(key, options);
      return options;
    }

    function createPaymentForSelect(payment, options) {
      const td = document.createElement("td");
      const select = document.createElement("select");
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "—";
      select.appendChild(empty);
      for (const item of options) {
        const option = document.createElement("option");
        option.value = item.value;
        option.textContent = item.label;
        if (payment.payment_for === item.value) option.selected = true;
        select.appendChild(option);
      }
      select.addEventListener("change", () => {
        const paymentFor = select.value || null;
        select.disabled = true;
        fetch(`/api/payments/${payment.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ payment_for: paymentFor }),
        })
          .then((response) => {
            if (!response.ok) throw new Error("Не удалось сохранить период оплаты");
            payment.payment_for = paymentFor;
          })
          .catch((error) => {
            lastUpdated.textContent = error.message;
            select.value = payment.payment_for || "";
          })
          .finally(() => {
            select.disabled = false;
          });
      });
      td.appendChild(select);
      return td;
    }

    async function renderPayments(payments) {
      paymentsBody.replaceChildren();
      emptyState.hidden = payments.length > 0;
      for (const payment of payments) {
        const options = await loadPaymentForOptions(payment.season || null);
        const row = document.createElement("tr");
        row.append(
          Object.assign(document.createElement("td"), {
            textContent: formatDate(payment.paid_at || payment.created_at)
          }),
          Object.assign(document.createElement("td"), {
            textContent: `${payment.amount} ${payment.currency}`,
            className: "amount"
          }),
          Object.assign(document.createElement("td"), {
            textContent: payment.payer_full_name || "-"
          }),
          Object.assign(document.createElement("td"), { textContent: payment.season || "-" }),
          createPaymentForSelect(payment, options)
        );
        paymentsBody.appendChild(row);
      }
    }

    async function loadStudentPayments() {
      if (!Number.isFinite(studentId)) {
        throw new Error("Некорректный идентификатор ученика");
      }
      const [studentResponse, paymentsResponse] = await Promise.all([
        fetch(`/api/students/${studentId}`),
        fetch(`/api/payments?student_id=${studentId}`),
      ]);
      if (!studentResponse.ok) throw new Error("Ученик не найден");
      if (!paymentsResponse.ok) throw new Error("Не удалось загрузить платежи");
      const student = await studentResponse.json();
      const payments = await paymentsResponse.json();
      studentTitle.textContent = student.full_name;
      const total = payments.reduce((sum, payment) => sum + Number(payment.amount || 0), 0);
      studentSummary.textContent =
        `${payments.length} платеж(ей) · всего ${total.toFixed(2)} BYN` +
        (student.group_name ? ` · группа ${student.group_name}` : "");
      await renderPayments(payments);
      lastUpdated.textContent = "Обновлено: " + formatDate(new Date().toISOString());
    }

    document.querySelector("#refresh").addEventListener("click", () => {
      loadStudentPayments().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    loadStudentPayments().catch((error) => {
      lastUpdated.textContent = error.message;
    });
  </script>
</body>
</html>
"""


@router.get("/groups-ui", response_class=HTMLResponse, include_in_schema=False)
def groups_ui() -> str:
    return """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MetPay - группы</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #172033;
      --muted: #697386;
      --line: #d9deea;
      --accent: #2457d6;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111827;
        --card: #182235;
        --text: #e7ecf5;
        --muted: #9aa8bd;
        --line: #2c3950;
        --accent: #7aa2ff;
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
      max-width: 900px;
      margin: 0 auto;
      padding: 32px 20px;
    }
    .muted { color: var(--muted); }
    .app-nav {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
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
    .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
      overflow: hidden;
    }
    table {
      width: 100%;
      border-collapse: collapse;
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
    .badge {
      display: inline-flex;
      border-radius: 999px;
      padding: 4px 9px;
      background: var(--bg);
      border: 1px solid var(--line);
      font-weight: 600;
    }
    .empty {
      padding: 32px;
      text-align: center;
      color: var(--muted);
    }
    .group-card {
      border-bottom: 1px solid var(--line);
      padding: 16px 18px;
    }
    .group-card:last-child { border-bottom: none; }
    .group-head {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }
    .group-head h2 {
      margin: 0;
      font-size: 1.15rem;
    }
    .group-meta {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }
    .student-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .student-link {
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      background: var(--bg);
      color: var(--accent);
      border-radius: 999px;
      padding: 6px 12px;
      font: inherit;
      text-decoration: none;
      font-weight: 500;
    }
    .student-link:hover {
      border-color: var(--accent);
      background: color-mix(in srgb, var(--accent), transparent 90%);
    }
    .students-empty {
      color: var(--muted);
      font-size: 13px;
    }
    .modal {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.45);
      display: grid;
      place-items: center;
      padding: 20px;
      z-index: 20;
    }
    .modal[hidden] { display: none; }
    .modal-card {
      width: min(720px, 100%);
      max-height: 85vh;
      overflow: auto;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 20px 40px rgba(15, 23, 42, 0.18);
    }
    .modal-card h3 { margin: 0 0 6px; }
    .modal-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 16px;
    }
    button.btn-secondary {
      background: var(--card);
      color: var(--text);
      border-color: var(--line);
      font-weight: 500;
    }
    .amount { font-weight: 700; white-space: nowrap; }
  </style>
</head>
<body>
  <main>
    <nav class="app-nav" aria-label="Разделы">
      <a href="/payments-ui">Платежи</a>
      <a href="/groups-ui" class="active">Группы</a>
    </nav>
    <header>
      <div>
        <h1>Группы</h1>
        <div class="muted">Когорты по году рождения. Нажмите на ФИО — история платежей.</div>
      </div>
      <button type="button" id="refresh">Обновить</button>
    </header>
    <section class="panel">
      <div id="groupsList"></div>
      <div class="empty" id="emptyState" hidden>Группы не найдены</div>
      <div class="muted" id="lastUpdated" style="padding: 12px 18px;">Еще не обновлялось</div>
    </section>
  </main>

  <script>
    const groupsList = document.querySelector("#groupsList");
    const emptyState = document.querySelector("#emptyState");
    const lastUpdated = document.querySelector("#lastUpdated");

    function formatDate(value) {
      if (!value) return "-";
      return new Intl.DateTimeFormat("ru-RU", {
        dateStyle: "short",
        timeStyle: "short"
      }).format(new Date(value));
    }

    function renderGroups(groups, students) {
      groupsList.replaceChildren();
      emptyState.hidden = groups.length > 0;
      const byGroup = new Map();
      for (const student of students) {
        if (!student.active || !student.group_id) continue;
        if (!byGroup.has(student.group_id)) byGroup.set(student.group_id, []);
        byGroup.get(student.group_id).push(student);
      }
      for (const group of groups) {
        const card = document.createElement("article");
        card.className = "group-card";
        const head = document.createElement("div");
        head.className = "group-head";
        const title = document.createElement("h2");
        title.textContent = group.name;
        const meta = document.createElement("div");
        meta.className = "group-meta";
        const groupStudents = (byGroup.get(group.id) || []).sort((a, b) =>
          a.full_name.localeCompare(b.full_name, "ru")
        );
        meta.textContent =
          `${group.monthly_fee} BYN/мес · ${groupStudents.length} ученик(ов)` +
          (group.active ? "" : " · неактивна");
        head.append(title, meta);
        card.appendChild(head);

        if (!groupStudents.length) {
          const empty = document.createElement("div");
          empty.className = "students-empty";
          empty.textContent = "Нет привязанных учеников";
          card.appendChild(empty);
        } else {
          const list = document.createElement("ul");
          list.className = "student-list";
          for (const student of groupStudents) {
            const item = document.createElement("li");
            const link = document.createElement("a");
            link.className = "student-link";
            link.href = `/students-ui/${student.id}`;
            link.textContent = student.full_name;
            link.title = "История платежей";
            item.appendChild(link);
            list.appendChild(item);
          }
          card.appendChild(list);
        }
        groupsList.appendChild(card);
      }
    }

    async function loadGroups() {
      const [groupsResponse, studentsResponse] = await Promise.all([
        fetch("/api/groups"),
        fetch("/api/students"),
      ]);
      if (!groupsResponse.ok || !studentsResponse.ok) {
        throw new Error("Не удалось загрузить данные");
      }
      const groups = await groupsResponse.json();
      const students = await studentsResponse.json();
      renderGroups(groups, students);
      lastUpdated.textContent = "Обновлено: " + formatDate(new Date().toISOString());
    }

    document.querySelector("#refresh").addEventListener("click", () => {
      loadGroups().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    loadGroups().catch((error) => {
      lastUpdated.textContent = error.message;
    });
  </script>
</body>
</html>
"""
