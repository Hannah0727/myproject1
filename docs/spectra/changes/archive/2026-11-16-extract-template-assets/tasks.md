## 1. 拆分首頁靜態資產

- [x] 1.1 在 `my-django-site/apps/core/static/myproject1/css/home.css` 建立首頁專用樣式，完整遷移 `home.html` 既有的自訂 CSS（含資料 URI 圖示、媒體查詢與最終覆寫規則），使外部樣式維持原有渲染規則；以內容比對確認原 `<style>` 的所有規則均存在於 CSS 檔。
- [x] 1.2 建立 `my-django-site/apps/core/static/myproject1/js/` 作為 `core` app 的 JavaScript 資產位置，且不建立或載入無行為用途的空白腳本；以目錄檢查與首頁 HTML 檢視確認目錄存在且沒有新增 script 載入。
- [x] 1.3 更新 `my-django-site/apps/core/templates/core/home.html`，載入 Django `static` 標籤並使用 `{% static 'myproject1/css/home.css' %}` 連結外部樣式，移除內嵌 `<style>`，同時保留 Tailwind CDN、模板 URL、搜尋表單與所有頁面內容；以 Django test client 或開發伺服器請求首頁，確認回應含解析後的 stylesheet URL、不含內嵌 `<style>`，且主要導覽連結與搜尋表單仍存在。[after: 1.1]

## 2. 驗證重構結果

- [x] 2.1 為首頁新增或更新 Django 測試，驗證 GET `/` 成功回應，且 HTML 含 `myproject1/css/home.css` 的靜態資產 URL、沒有首頁內嵌 `<style>` 區塊，並保留活動列表連結與搜尋輸入欄位；執行 `python manage.py test apps.core` 確認測試通過。[after: 1.3]
- [x] 2.2 執行 `python manage.py test`，確認完整測試套件通過；在瀏覽器開啟首頁，確認外部 CSS 成功載入且首頁沒有可見的樣式回歸、導覽與搜尋仍可使用。[after: 2.1]

## 3. 修正審查發現

- [x] 3.1 在 `my-django-site/apps/core/static/myproject1/js/.gitkeep` 建立 Git 可追蹤標記，讓 JavaScript 資產目錄會隨提交保留且首頁不新增 script 載入；更新 `my-django-site/apps/core/tests.py` 以 Django `static()` 產生 CSS URL 預期值，並執行 `python manage.py test apps.core` 和 `python manage.py test` 確認測試在目前靜態資產設定下通過。[after: 2.2]
