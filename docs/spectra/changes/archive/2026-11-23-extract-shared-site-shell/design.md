## Context

首頁已在 `apps/core/templates/core/home.html` 提供品牌名稱、活動列表入口及首頁段落導覽；其 HTML 文件結構與 Tailwind CDN 載入未被其他模板重用。`apps/chillme/templates/chillme/` 的三個活動模板和 `templates/account/` 的帳號模板各自重複文件外框與 Tailwind 載入，且入口文字和配色不同。Django 已啟用 `APP_DIRS` 與專案層級 `templates/`，因此 core app 的模板可以成為所有這些頁面的父模板。

目前的 `redesign-homepage` 變更正在進行，並將活動與帳號頁的視覺重作列為非目標。本變更只建立一致的網站外框與導覽，不重排各頁主要內容。

## Goals / Non-Goals

**Goals:**

- 讓 Django 頁面透過一個 core 基礎模板共享文件外框、共用靜態資源與可覆寫區塊。
- 讓首頁、活動頁與帳號頁提供一致的品牌導覽與正確的跨頁連結。
- 使用既有 Django 認證狀態決定導覽中的帳號行動。

**Non-Goals:**

- 不改變活動搜尋、建立、詳情、登入、註冊或登出的後端規則與 URL 名稱。
- 不重作各頁 main 內容、表單欄位、活動資料或帳號流程。
- 不新增 JavaScript 導覽邏輯、外部套件或新的認證機制。
- 不改寫 `redesign-homepage` 的首頁內容設計；僅將其可共用部分抽離。

## Decisions

### Place the base template and navigation partial in core

建立 `core/base.html` 作為跨 app 父模板，並以 `core/includes/navbar.html` 承載可重用的導覽列。base 提供 `title`、`content` 與頁面可選擴充區塊；子模板使用 Django `{% extends %}` 與 `{% block %}`，不再各自輸出 `<!doctype html>`、`<head>` 與共用導覽。

選擇 core 是因為它已擁有首頁與靜態資源，且已在 `INSTALLED_APPS` 中，無需新增設定。替代方案是在專案根目錄 `templates/` 放置 base；不採用，因為品牌外框的所有權會離開既有核心 app，且不符合本次將共用資源整理到 core 的目的。

### Separate shared site styles from homepage-only styles

共用的字型、色彩變數、按鈕、卡片與導覽樣式移至 core 靜態檔的站點樣式；只服務首頁區段的選擇器仍留在首頁樣式。base 載入 Tailwind CDN 與站點樣式一次，子模板不重複載入。既有靜態 URL 一律使用 `{% static %}`。

替代方案是由 base 直接載入目前的 `home.css`；不採用，因為檔名與內容會讓非首頁頁面承擔首頁專屬選擇器，並模糊後續維護邊界。

### Use named routes and absolute homepage fragments in navigation

品牌連結指向 `core:home`；活動入口指向 `chillme:event-list`。只有首頁本身的段落導覽可使用 `#how` 與 `#categories`，共用 navbar 從其他頁面前往這些段落時必須使用 `{% url 'core:home' %}#how` 與 `{% url 'core:home' %}#categories`。所有 Django URL 以命名路由生成，避免硬編碼路徑。

替代方案是在所有頁面使用裸 `#how` 和 `#categories`；不採用，因為它們在活動與帳號頁只會定位到不存在的頁內目標。

### Render account actions from server-side authentication state

navbar 使用既有 `user.is_authenticated`：已登入者看到活動建立與登出行動；未登入者看到登入與註冊行動。登出仍使用 POST 表單及 CSRF token，不轉為 GET 連結。

替代方案是所有使用者看到相同行動或用 JavaScript 決定狀態；不採用，因為前者無法提供清楚的下一步，後者重複 Django 已提供的 request context 並增加閃爍風險。

## Implementation Contract

**Behavior:** 使用 base 的頁面 SHALL 只產生一組 HTML 文件外框、Tailwind 載入與 core 站點樣式載入，並在內容前顯示共用 navbar。首頁、活動列表、活動詳情、建立活動、登入、註冊及登出頁 SHALL 都能保留其原有主要內容與表單行為。

**Navigation:** navbar SHALL 提供首頁與活動列表入口；首頁段落入口從任何非首頁頁面 SHALL 解析為首頁 URL 加對應錨點。已登入使用者 SHALL 看到建立活動與安全的登出 POST 表單；匿名使用者 SHALL 看到登入與註冊入口。

**Failure and fallback:** 若共用 CSS 或 Tailwind 未載入，所有 navbar 連結與登出表單仍 SHALL 使用可操作的語意 HTML。若子模板未設定 `title` block，base SHALL 使用品牌預設標題。

**Acceptance criteria:** Django 模板測試 SHALL 驗證首頁、活動與帳號頁回應中只出現一組共用資源載入與預期導航 URL；匿名與登入狀態的測試 SHALL 驗證不同的 navbar 行動；手動檢查 SHALL 驗證從活動頁與帳號頁可前往首頁段落。

**Scope boundaries:** 範圍包含 core 的共用模板／靜態樣式，以及既有活動和帳號模板的繼承轉換。範圍不包含模型、views、URLconf、活動資料、搜尋邏輯與帳號驗證規則。

## Risks / Trade-offs

- [共用 CSS 與既有頁面 Tailwind class 的視覺衝突] → 僅提升已在首頁使用的通用 token 和元件樣式，並保留每頁 main 區域 class。
- [在 base 內新增 navbar 會影響緊湊型登入表單的垂直空間] → 帳號頁保留自身 main 置中規則，並在桌面與窄螢幕進行手動檢查。
- [登出被誤做為 GET 連結] → navbar partial 明確保留 POST method 與 `{% csrf_token %}`，並在模板測試驗證表單存在。
