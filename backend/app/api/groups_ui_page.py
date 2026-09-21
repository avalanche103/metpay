GROUPS_UI_HTML = """
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
      --ok: #15803d;
      --warn: #b45309;
      --bad: #b91c1c;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111827;
        --card: #182235;
        --text: #e7ecf5;
        --muted: #9aa8bd;
        --line: #2c3950;
        --accent: #7aa2ff;
        --ok: #4ade80;
        --warn: #fbbf24;
        --bad: #f87171;
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
    button, select, input[type="text"], input[type="number"] {
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
      color: #fff;
      border-color: var(--accent);
      font-weight: 600;
    }
    button.btn-secondary {
      background: var(--card);
      color: var(--text);
      border-color: var(--line);
      font-weight: 500;
    }
    button.btn-icon {
      padding: 4px 10px;
      font-size: 12px;
      line-height: 1.2;
      white-space: nowrap;
    }
    .header-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
      overflow: hidden;
      margin-bottom: 16px;
    }
    .group-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      background: color-mix(in srgb, var(--card), var(--bg) 35%);
    }
    .group-head-main {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      min-width: 0;
    }
    .group-head h2 {
      margin: 0;
      font-size: 1.1rem;
    }
    .group-meta {
      color: var(--muted);
      font-size: 13px;
    }
    .group-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .table-wrap {
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      background: color-mix(in srgb, var(--card), var(--bg) 20%);
    }
    tr:last-child td { border-bottom: none; }
    .student-link {
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
    }
    .student-link:hover { text-decoration: underline; }
    .status {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 9px;
      border: 1px solid var(--line);
      font-weight: 600;
      font-size: 12px;
      white-space: nowrap;
    }
    .status-ok {
      color: var(--ok);
      background: color-mix(in srgb, var(--ok), transparent 90%);
      border-color: color-mix(in srgb, var(--ok), transparent 55%);
    }
    .status-partial {
      color: var(--warn);
      background: color-mix(in srgb, var(--warn), transparent 90%);
      border-color: color-mix(in srgb, var(--warn), transparent 55%);
    }
    .status-none {
      color: var(--bad);
      background: color-mix(in srgb, var(--bad), transparent 90%);
      border-color: color-mix(in srgb, var(--bad), transparent 55%);
    }
    .amount { font-weight: 700; white-space: nowrap; }
    .expected {
      color: var(--bad);
      font-weight: 700;
      white-space: nowrap;
    }
    .summary-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 16px;
    }
    .summary-card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px 16px;
      min-width: 200px;
      flex: 1;
    }
    .summary-card strong {
      display: block;
      margin-top: 4px;
      font-size: 22px;
    }
    .summary-card.expected-total strong {
      color: var(--bad);
    }
    .empty {
      padding: 24px;
      text-align: center;
      color: var(--muted);
    }
    .footer-note {
      padding: 12px 16px;
      color: var(--muted);
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
      width: min(480px, 100%);
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 20px 40px rgba(15, 23, 42, 0.18);
    }
    .modal-card h3 { margin: 0 0 6px; }
    .modal-field {
      display: grid;
      gap: 6px;
      margin: 14px 0;
    }
    .modal-field input,
    .modal-field select {
      width: 100%;
    }
    .modal-field-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .modal-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
      margin-top: 16px;
    }
    .modal-error {
      color: var(--bad);
      font-size: 13px;
      min-height: 1.2em;
    }
    @media (max-width: 760px) {
      header { flex-direction: column; align-items: stretch; }
    }
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
        <div class="muted" id="pageSubtitle">Состав групп и оплата за текущий месяц</div>
      </div>
      <div class="header-actions">
        <button type="button" id="addGroupBtn">Добавить группу</button>
        <button type="button" id="refresh" class="btn-secondary">Обновить</button>
      </div>
    </header>
    <section class="summary-bar" aria-label="Сводка по неоплаченным">
      <div class="summary-card expected-total">
        <span class="muted">Ожидаем к оплате (не оплачено)</span>
        <strong id="expectedTotal">0.00 BYN</strong>
        <div class="muted" id="expectedTotalMeta">0 учеников</div>
      </div>
    </section>
    <div id="groupsList"></div>
    <div class="panel" id="ungroupedPanel" hidden>
      <div class="group-head">
        <div class="group-head-main">
          <h2>Без группы</h2>
          <span class="group-meta" id="ungroupedMeta"></span>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ученик</th>
              <th id="ungroupedMonthHead">Оплата</th>
              <th>Сумма</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="ungroupedBody"></tbody>
        </table>
      </div>
    </div>
    <div class="empty" id="emptyState" hidden>Группы не найдены</div>
    <div class="footer-note" id="lastUpdated">Еще не обновлялось</div>
  </main>

  <div id="groupEditor" class="modal" hidden>
    <div class="modal-card" role="dialog" aria-labelledby="groupEditorTitle">
      <h3 id="groupEditorTitle">Редактирование группы</h3>
      <label class="modal-field">
        <span>Название</span>
        <input id="groupName" type="text" autocomplete="off" placeholder="например 2015">
      </label>
      <label class="modal-field">
        <span>Ежемесячный взнос, BYN</span>
        <input id="groupFee" type="number" min="0" step="0.01" placeholder="120.00">
      </label>
      <label class="modal-field modal-field-row">
        <input id="groupActive" type="checkbox" checked>
        <span>Активна</span>
      </label>
      <div class="modal-error" id="groupEditorError"></div>
      <div class="modal-actions">
        <button type="button" id="groupEditorSave">Сохранить</button>
        <button type="button" id="groupEditorClose" class="btn-secondary">Отмена</button>
      </div>
    </div>
  </div>

  <div id="memberEditor" class="modal" hidden>
    <div class="modal-card" role="dialog" aria-labelledby="memberEditorTitle">
      <h3 id="memberEditorTitle">Добавить в группу</h3>
      <p class="muted" id="memberEditorGroup"></p>
      <label class="modal-field">
        <span>Ученик без группы</span>
        <select id="memberStudentSelect"></select>
      </label>
      <div class="muted" style="margin: 8px 0;">или создайте нового:</div>
      <label class="modal-field">
        <span>Новый ученик (ФИО)</span>
        <input id="memberNewName" type="text" autocomplete="off" placeholder="Иванов Иван Иванович">
      </label>
      <div class="modal-error" id="memberEditorError"></div>
      <div class="modal-actions">
        <button type="button" id="memberEditorSave">Добавить</button>
        <button type="button" id="memberEditorClose" class="btn-secondary">Отмена</button>
      </div>
    </div>
  </div>

  <script>
    const MONTH_NAMES = [
      "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
      "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ];

    const groupsList = document.querySelector("#groupsList");
    const emptyState = document.querySelector("#emptyState");
    const lastUpdated = document.querySelector("#lastUpdated");
    const ungroupedPanel = document.querySelector("#ungroupedPanel");
    const ungroupedBody = document.querySelector("#ungroupedBody");
    const ungroupedMeta = document.querySelector("#ungroupedMeta");
    const ungroupedMonthHead = document.querySelector("#ungroupedMonthHead");
    const pageSubtitle = document.querySelector("#pageSubtitle");

    const groupEditor = document.querySelector("#groupEditor");
    const groupEditorTitle = document.querySelector("#groupEditorTitle");
    const groupNameInput = document.querySelector("#groupName");
    const groupFeeInput = document.querySelector("#groupFee");
    const groupActiveInput = document.querySelector("#groupActive");
    const groupEditorError = document.querySelector("#groupEditorError");
    const groupEditorSave = document.querySelector("#groupEditorSave");

    const memberEditor = document.querySelector("#memberEditor");
    const memberEditorTitle = document.querySelector("#memberEditorTitle");
    const memberEditorGroup = document.querySelector("#memberEditorGroup");
    const memberStudentSelect = document.querySelector("#memberStudentSelect");
    const memberNewName = document.querySelector("#memberNewName");
    const memberEditorError = document.querySelector("#memberEditorError");
    const memberEditorSave = document.querySelector("#memberEditorSave");

    let editorGroupId = null;
    let memberTargetGroupId = null;
    let cachedStudents = [];
    let cachedGroups = [];
    let paidByStudentId = new Map();
    let currentPeriod = "";
    let currentPeriodLabel = "";

    function formatDate(value) {
      if (!value) return "-";
      return new Intl.DateTimeFormat("ru-RU", {
        dateStyle: "short",
        timeStyle: "short"
      }).format(new Date(value));
    }

    function formatFee(value) {
      if (value == null || value === "") return "—";
      return Number(value).toFixed(2);
    }

    function detectCurrentPeriod() {
      const now = new Date();
      const month = String(now.getMonth() + 1).padStart(2, "0");
      currentPeriod = `${now.getFullYear()}-${month}`;
      currentPeriodLabel = `${MONTH_NAMES[now.getMonth()]} ${now.getFullYear()}`;
      pageSubtitle.textContent =
        `Состав групп и оплата за ${currentPeriodLabel.toLowerCase()}`;
      ungroupedMonthHead.textContent = currentPeriodLabel;
    }

    function paymentMonthKey(payment) {
      if (payment.payment_for && payment.payment_for !== "tournament") {
        return payment.payment_for;
      }
      if (!payment.paid_at) return null;
      const paid = new Date(payment.paid_at);
      if (Number.isNaN(paid.getTime())) return null;
      return `${paid.getFullYear()}-${String(paid.getMonth() + 1).padStart(2, "0")}`;
    }

    function buildPaidByStudent(payments) {
      const map = new Map();
      for (const payment of payments) {
        if (!payment.student_id) continue;
        if (paymentMonthKey(payment) !== currentPeriod) continue;
        const prev = map.get(payment.student_id) || 0;
        map.set(payment.student_id, prev + Number(payment.amount));
      }
      return map;
    }

    function paymentStatus(amount, monthlyFee) {
      const paid = Number(amount) || 0;
      const fee = monthlyFee == null || monthlyFee === "" ? null : Number(monthlyFee);
      if (paid <= 0) {
        return { label: "Не оплачено", className: "status-none", amount: paid };
      }
      if (fee != null && paid + 0.001 >= fee) {
        return { label: "Оплачено", className: "status-ok", amount: paid };
      }
      if (fee != null && paid > 0) {
        return { label: "Частично", className: "status-partial", amount: paid };
      }
      return { label: "Есть оплата", className: "status-ok", amount: paid };
    }

    function closeGroupEditor() {
      groupEditor.hidden = true;
      editorGroupId = null;
      groupEditorError.textContent = "";
    }

    function openGroupEditor(group) {
      editorGroupId = group ? group.id : null;
      groupEditorTitle.textContent = group ? "Редактирование группы" : "Новая группа";
      groupNameInput.value = group ? group.name : "";
      groupFeeInput.value = group && group.monthly_fee != null ? group.monthly_fee : "120.00";
      groupActiveInput.checked = group ? Boolean(group.active) : true;
      groupEditorError.textContent = "";
      groupEditor.hidden = false;
      groupNameInput.focus();
    }

    async function saveGroup() {
      const name = groupNameInput.value.trim();
      if (!name) {
        groupEditorError.textContent = "Укажите название группы";
        return;
      }
      const feeRaw = groupFeeInput.value.trim();
      const payload = {
        name,
        active: groupActiveInput.checked,
        monthly_fee: feeRaw === "" ? null : feeRaw,
      };
      groupEditorSave.disabled = true;
      groupEditorError.textContent = "";
      try {
        const response = await fetch(
          editorGroupId ? `/api/groups/${editorGroupId}` : "/api/groups",
          {
            method: editorGroupId ? "PATCH" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          }
        );
        const body = await response.json().catch(() => ({}));
        if (!response.ok) {
          const detail =
            typeof body.detail === "string" ? body.detail : "Не удалось сохранить группу";
          throw new Error(detail);
        }
        closeGroupEditor();
        await loadGroups();
      } catch (error) {
        groupEditorError.textContent = error.message;
      } finally {
        groupEditorSave.disabled = false;
      }
    }

    function closeMemberEditor() {
      memberEditor.hidden = true;
      memberTargetGroupId = null;
      memberEditorError.textContent = "";
      memberNewName.value = "";
    }

    function openMemberEditor(group) {
      memberTargetGroupId = group.id;
      memberEditorTitle.textContent = "Добавить в группу";
      memberEditorGroup.textContent = `Группа: ${group.name}`;
      memberEditorError.textContent = "";
      memberNewName.value = "";
      const ungrouped = cachedStudents
        .filter((student) => student.active && !student.group_id)
        .sort((a, b) => a.full_name.localeCompare(b.full_name, "ru"));
      memberStudentSelect.replaceChildren();
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = ungrouped.length
        ? "Выберите ученика"
        : "Нет учеников без группы";
      memberStudentSelect.appendChild(placeholder);
      for (const student of ungrouped) {
        const option = document.createElement("option");
        option.value = String(student.id);
        option.textContent = student.full_name;
        memberStudentSelect.appendChild(option);
      }
      memberEditor.hidden = false;
      memberStudentSelect.focus();
    }

    async function saveMember() {
      if (!memberTargetGroupId) return;
      const selectedId = memberStudentSelect.value;
      const newName = memberNewName.value.trim();
      if (!selectedId && !newName) {
        memberEditorError.textContent = "Выберите ученика или введите новое ФИО";
        return;
      }
      memberEditorSave.disabled = true;
      memberEditorError.textContent = "";
      try {
        let response;
        if (newName) {
          response = await fetch("/api/students", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              full_name: newName,
              group_id: memberTargetGroupId,
              active: true,
            }),
          });
        } else {
          response = await fetch(`/api/students/${selectedId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ group_id: memberTargetGroupId }),
          });
        }
        const body = await response.json().catch(() => ({}));
        if (!response.ok) {
          const detail =
            typeof body.detail === "string" ? body.detail : "Не удалось добавить ученика";
          throw new Error(detail);
        }
        closeMemberEditor();
        await loadGroups();
      } catch (error) {
        memberEditorError.textContent = error.message;
      } finally {
        memberEditorSave.disabled = false;
      }
    }

    async function removeFromGroup(studentId) {
      const response = await fetch(`/api/students/${studentId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ group_id: null }),
      });
      if (!response.ok) {
        throw new Error("Не удалось убрать ученика из группы");
      }
      await loadGroups();
    }

    function createStatusCell(student, monthlyFee) {
      const td = document.createElement("td");
      const status = paymentStatus(paidByStudentId.get(student.id) || 0, monthlyFee);
      const badge = document.createElement("span");
      badge.className = `status ${status.className}`;
      badge.textContent = status.label;
      td.appendChild(badge);
      return td;
    }

    function createAmountCell(student, monthlyFee) {
      const td = document.createElement("td");
      const paid = paidByStudentId.get(student.id) || 0;
      const status = paymentStatus(paid, monthlyFee);
      if (status.className === "status-none" && monthlyFee != null && monthlyFee !== "") {
        td.className = "expected";
        td.textContent = formatFee(monthlyFee);
        td.title = `Ожидаемая сумма: ${formatFee(monthlyFee)} BYN`;
      } else {
        td.className = "amount";
        td.textContent = formatFee(paid);
      }
      return td;
    }

    function createStudentRow(student, monthlyFee, { showRemove }) {
      const row = document.createElement("tr");
      const nameTd = document.createElement("td");
      const link = document.createElement("a");
      link.className = "student-link";
      link.href = `/students-ui/${student.id}`;
      link.textContent = student.full_name;
      nameTd.appendChild(link);
      row.append(
        nameTd,
        createStatusCell(student, monthlyFee),
        createAmountCell(student, monthlyFee)
      );
      const actions = document.createElement("td");
      if (showRemove) {
        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "btn-secondary btn-icon";
        removeBtn.textContent = "Убрать";
        removeBtn.addEventListener("click", () => {
          removeFromGroup(student.id).catch((error) => {
            lastUpdated.textContent = error.message;
          });
        });
        actions.appendChild(removeBtn);
      }
      row.appendChild(actions);
      return row;
    }

    function unpaidExpected(student, monthlyFee) {
      const status = paymentStatus(paidByStudentId.get(student.id) || 0, monthlyFee);
      if (status.className !== "status-none") return 0;
      if (monthlyFee == null || monthlyFee === "") return 0;
      return Number(monthlyFee) || 0;
    }

    function renderGroups(groups, students) {
      groupsList.replaceChildren();
      emptyState.hidden = groups.length > 0;
      const byGroup = new Map();
      const ungrouped = [];
      for (const student of students) {
        if (!student.active) continue;
        if (!student.group_id) {
          ungrouped.push(student);
          continue;
        }
        if (!byGroup.has(student.group_id)) byGroup.set(student.group_id, []);
        byGroup.get(student.group_id).push(student);
      }

      let totalExpected = 0;
      let totalUnpaidPeople = 0;

      for (const group of groups) {
        const panel = document.createElement("section");
        panel.className = "panel";

        const head = document.createElement("div");
        head.className = "group-head";
        const main = document.createElement("div");
        main.className = "group-head-main";
        const title = document.createElement("h2");
        title.textContent = group.name;
        const meta = document.createElement("span");
        meta.className = "group-meta";
        const groupStudents = (byGroup.get(group.id) || []).sort((a, b) =>
          a.full_name.localeCompare(b.full_name, "ru")
        );
        const paidCount = groupStudents.filter((student) => {
          const status = paymentStatus(
            paidByStudentId.get(student.id) || 0,
            group.monthly_fee
          );
          return status.className === "status-ok";
        }).length;
        const unpaidStudents = groupStudents.filter((student) => {
          const status = paymentStatus(
            paidByStudentId.get(student.id) || 0,
            group.monthly_fee
          );
          return status.className === "status-none";
        });
        const groupExpected = unpaidStudents.reduce(
          (sum, student) => sum + unpaidExpected(student, group.monthly_fee),
          0
        );
        totalExpected += groupExpected;
        totalUnpaidPeople += unpaidStudents.length;

        meta.textContent =
          `${formatFee(group.monthly_fee)} BYN/мес · ${groupStudents.length} уч. · ` +
          `оплатили ${paidCount}` +
          (unpaidStudents.length
            ? ` · не оплатили ${unpaidStudents.length}, ожидаем ${formatFee(groupExpected)} BYN`
            : "") +
          (group.active ? "" : " · неактивна");
        main.append(title, meta);

        const actions = document.createElement("div");
        actions.className = "group-actions";
        const addBtn = document.createElement("button");
        addBtn.type = "button";
        addBtn.className = "btn-icon";
        addBtn.textContent = "Добавить ученика";
        addBtn.addEventListener("click", () => openMemberEditor(group));
        const editBtn = document.createElement("button");
        editBtn.type = "button";
        editBtn.className = "btn-secondary btn-icon";
        editBtn.textContent = "Изменить";
        editBtn.addEventListener("click", () => openGroupEditor(group));
        actions.append(addBtn, editBtn);
        head.append(main, actions);
        panel.appendChild(head);

        if (!groupStudents.length) {
          const empty = document.createElement("div");
          empty.className = "empty";
          empty.textContent = "Нет привязанных учеников";
          panel.appendChild(empty);
        } else {
          const wrap = document.createElement("div");
          wrap.className = "table-wrap";
          const table = document.createElement("table");
          const thead = document.createElement("thead");
          const headRow = document.createElement("tr");
          for (const label of ["Ученик", currentPeriodLabel, "Сумма / ожидаем", ""]) {
            const th = document.createElement("th");
            th.textContent = label;
            headRow.appendChild(th);
          }
          thead.appendChild(headRow);
          const tbody = document.createElement("tbody");
          for (const student of groupStudents) {
            tbody.appendChild(
              createStudentRow(student, group.monthly_fee, { showRemove: true })
            );
          }
          table.append(thead, tbody);
          wrap.appendChild(table);
          panel.appendChild(wrap);
        }
        groupsList.appendChild(panel);
      }

      document.querySelector("#expectedTotal").textContent =
        `${formatFee(totalExpected)} BYN`;
      document.querySelector("#expectedTotalMeta").textContent =
        `${totalUnpaidPeople} ученик(ов) без оплаты за ${currentPeriodLabel.toLowerCase()}`;

      ungrouped.sort((a, b) => a.full_name.localeCompare(b.full_name, "ru"));
      ungroupedPanel.hidden = ungrouped.length === 0;
      ungroupedMeta.textContent = `${ungrouped.length} ученик(ов)`;
      ungroupedBody.replaceChildren();
      for (const student of ungrouped) {
        ungroupedBody.appendChild(
          createStudentRow(student, null, { showRemove: false })
        );
      }
    }

    async function loadGroups() {
      detectCurrentPeriod();
      const [groupsResponse, studentsResponse, paymentsResponse] = await Promise.all([
        fetch("/api/groups"),
        fetch("/api/students"),
        fetch("/api/payments"),
      ]);
      if (!groupsResponse.ok || !studentsResponse.ok || !paymentsResponse.ok) {
        throw new Error("Не удалось загрузить данные");
      }
      cachedGroups = await groupsResponse.json();
      cachedStudents = await studentsResponse.json();
      const payments = await paymentsResponse.json();
      paidByStudentId = buildPaidByStudent(payments);
      renderGroups(cachedGroups, cachedStudents);
      lastUpdated.textContent = "Обновлено: " + formatDate(new Date().toISOString());
    }

    document.querySelector("#refresh").addEventListener("click", () => {
      loadGroups().catch((error) => {
        lastUpdated.textContent = error.message;
      });
    });
    document.querySelector("#addGroupBtn").addEventListener("click", () => openGroupEditor(null));
    document.querySelector("#groupEditorClose").addEventListener("click", closeGroupEditor);
    groupEditorSave.addEventListener("click", () => {
      saveGroup().catch((error) => {
        groupEditorError.textContent = error.message;
      });
    });
    groupEditor.addEventListener("click", (event) => {
      if (event.target === groupEditor) closeGroupEditor();
    });
    document.querySelector("#memberEditorClose").addEventListener("click", closeMemberEditor);
    memberEditorSave.addEventListener("click", () => {
      saveMember().catch((error) => {
        memberEditorError.textContent = error.message;
      });
    });
    memberEditor.addEventListener("click", (event) => {
      if (event.target === memberEditor) closeMemberEditor();
    });

    loadGroups().catch((error) => {
      lastUpdated.textContent = error.message;
    });
  </script>
</body>
</html>
"""
