(function () {
  const app = document.getElementById("event-list-app");
  if (!app) return;
  const endpoint = app.dataset.endpoint;
  const form = document.getElementById("event-search-form");
  const input = document.getElementById("event-search-input");
  const status = document.getElementById("event-list-status");
  const error = document.getElementById("event-list-error");
  const results = document.getElementById("event-list-results");
  const pagination = document.getElementById("event-list-pagination");
  let controller; let lastRequest = 0; let hasResults = false; let retry;

  function paramsFromUrl() { const params = new URLSearchParams(window.location.search); return { query: params.get("q") || "", page: params.get("page") || "1" }; }
  function updateUrl(query, page, replace) { const url = new URL(window.location.href); query ? url.searchParams.set("q", query) : url.searchParams.delete("q"); page > 1 ? url.searchParams.set("page", page) : url.searchParams.delete("page"); window.history[replace ? "replaceState" : "pushState"]({}, "", url); }
  function setLoading(loading) {
    pagination.querySelectorAll("button").forEach((button) => { button.disabled = loading; });
    if (loading && !hasResults) results.innerHTML = '<li class="animate-pulse py-4"><div class="h-4 w-2/3 rounded bg-slate-200"></div><div class="mt-2 h-3 w-1/3 rounded bg-slate-100"></div></li><li class="animate-pulse py-4"><div class="h-4 w-1/2 rounded bg-slate-200"></div><div class="mt-2 h-3 w-1/4 rounded bg-slate-100"></div></li><li class="animate-pulse py-4"><div class="h-4 w-3/4 rounded bg-slate-200"></div><div class="mt-2 h-3 w-1/3 rounded bg-slate-100"></div></li>';
  }
  function showError(message) { error.replaceChildren(document.createTextNode(`${message} `)); const button = document.createElement("button"); button.type = "button"; button.className = "font-bold underline"; button.textContent = "重新載入"; button.addEventListener("click", () => retry && retry()); error.append(button); error.classList.remove("hidden"); }
  function renderItems(items) {
    results.replaceChildren();
    if (!items.length) { const item = document.createElement("li"); item.className = "py-4 text-slate-500"; item.textContent = "目前沒有符合條件的揪團活動。"; results.append(item); return; }
    items.forEach((event) => { const item = document.createElement("li"); item.className = "py-4"; const link = document.createElement("a"); link.href = event.detail_url; link.className = "font-medium text-blue-600 hover:underline"; link.textContent = event.name; const code = document.createElement("p"); code.className = "mt-1 text-sm text-slate-500"; code.textContent = `活動代碼：${event.code}`; const owner = document.createElement("p"); owner.className = "mt-1 text-sm text-slate-500"; owner.textContent = `建立者：${event.owner_name}`; item.append(link, code, owner); results.append(item); });
  }
  function renderPagination(data, query) {
    pagination.replaceChildren(); const summary = document.createElement("span"); summary.className = "text-sm text-slate-500"; summary.textContent = `第 ${data.page} / ${data.total_pages} 頁，共 ${data.total_count} 筆`; const controls = document.createElement("div"); controls.className = "flex gap-2";
    [["上一頁", data.page - 1, data.has_previous], ["下一頁", data.page + 1, data.has_next]].forEach(([label, page, enabled]) => { const button = document.createElement("button"); button.type = "button"; button.textContent = label; button.disabled = !enabled; button.className = "rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"; button.addEventListener("click", () => load(query, page)); controls.append(button); }); pagination.append(summary, controls);
  }
  async function load(query, page, options = {}) {
    const requestId = ++lastRequest; if (controller) controller.abort(); controller = new AbortController(); retry = () => load(query, page, { replace: true }); error.classList.add("hidden"); status.textContent = "正在載入活動…"; setLoading(true); const params = new URLSearchParams({ page: String(page) }); if (query) params.set("q", query);
    try { const response = await fetch(`${endpoint}?${params}`, { signal: controller.signal, headers: { Accept: "application/json" } }); if (!response.ok) throw new Error("Request failed"); const data = await response.json(); if (requestId !== lastRequest || !Array.isArray(data.items) || !data.pagination) throw new Error("Invalid response"); input.value = data.query; renderItems(data.items); renderPagination(data.pagination, data.query); hasResults = true; status.textContent = data.items.length ? "活動已載入。" : "沒有符合條件的活動。"; if (!options.fromHistory) updateUrl(data.query, data.pagination.page, options.replace); }
    catch (exception) { if (exception.name === "AbortError" || requestId !== lastRequest) return; status.textContent = "活動載入失敗。"; showError("無法載入活動，請確認網路連線後再試一次。"); }
    finally { if (requestId === lastRequest) setLoading(false); }
  }
  form.addEventListener("submit", (event) => { event.preventDefault(); load(input.value.trim(), 1); });
  window.addEventListener("popstate", () => { const { query, page } = paramsFromUrl(); load(query, page, { fromHistory: true }); });
  const { query, page } = paramsFromUrl(); load(query, page, { replace: true });
}());
