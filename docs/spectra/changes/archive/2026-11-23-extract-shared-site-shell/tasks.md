## 1. 共用外框與樣式

- [x] 1.1 實作「Place the base template and navigation partial in core」與「Reusable site layout」：在 `apps/core/templates/core/` 提供可覆寫 title 與 content 的 base template，以及在內容前只渲染一次的 navbar partial；base 必須載入一次 Tailwind CDN、core 共用站點樣式並提供品牌預設標題。以 Django 測試確認首頁回應只有一組共用資源與 navbar。
- [x] 1.2 實作「Separate shared site styles from homepage-only styles」：將字型、色彩 token、按鈕、卡片及導覽規則整理為 `apps/core/static/myproject1/css/` 的共用站點樣式，保留首頁區段專屬選擇器於首頁樣式；以 `STATIC_URL` 覆寫測試確認 base 使用 `{% static %}` 產生正確 URL，並確認首頁關鍵控制項仍存在。

## 2. 導覽與模板轉換

- [x] 2.1 實作「Use named routes and absolute homepage fragments in navigation」與「Shared navigation links」：在共用 navbar 以 `core:home`、`chillme:event-list` 和首頁 URL 加 `#how`／`#categories` 產生跨頁連結；以模板回應測試驗證活動頁與帳號頁中的 href 均指向首頁 URL 加片段而非裸片段。
- [x] 2.2 將 `apps/core/templates/core/home.html`、`apps/chillme/templates/chillme/` 的活動頁及 `templates/account/` 的帳號頁遷移為繼承 base，讓「Reusable site layout」在這些頁面保留既有主要內容、表單 method 與命名 URL；以各 URL 的 Django client GET 回應和主要標題／表單存在性測試驗證。
- [x] 2.3 實作「Render account actions from server-side authentication state」與「Authentication-aware navigation actions」：navbar 對匿名訪客顯示登入與註冊，對已登入訪客顯示 `chillme:event-create` 和含 CSRF token 的 POST 登出表單；以匿名與已登入 Django client 測試驗證兩種狀態的內容及 logout form method。

## 3. 驗證

- [x] 3.1 執行相關 Django 測試並修正因模板繼承或靜態檔重整造成的失敗，使共用外框、跨頁導覽、匿名／登入導航與既有首頁搜尋控制項皆通過；以專案既有測試指令的成功結果驗證。
- [x] 3.2 在桌面與窄螢幕手動檢查首頁、活動列表與登入頁，確認 navbar 僅出現一次、文字與按鈕可讀，且從非首頁選擇「怎麼開始」或「探索類別」會到首頁對應段落；以瀏覽器導覽結果記錄驗證。
