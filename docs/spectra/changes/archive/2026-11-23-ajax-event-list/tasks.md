## 1. Backend data contract

- [x] 1.1 依「Use a dedicated same-origin JSON endpoint」實作 `apps/chillme/views.py` 的活動列表 JSON 端點，使「Asynchronous persisted-record lists」與「Bounded list pagination」回傳活動顯示資料、完整 pagination metadata 與保留的篩選條件；以 Django 測試驗證搜尋、首頁、最後頁、無效頁碼與空結果。
- [x] 1.2 在 `apps/chillme/urls.py` 加入命名資料端點，且不影響既有活動列表與詳情路由。

## 2. AJAX list experience

- [x] 2.1 調整 `apps/chillme/templates/chillme/event_list.html`，保留頁面外框與搜尋介面，加入可由 JavaScript 更新的列表、狀態區與分頁控制。
- [x] 2.2 依「Keep URL state in sync」新增前端資產以呼叫資料端點、渲染活動列、同步 `q`/`page` URL，並處理瀏覽器返回與前進；以手動瀏覽器歷史紀錄驗證搜尋與頁碼可還原。
- [x] 2.3 依「Model the list UI as explicit states」實作「Observable list request states」的初始載入及換頁骨架等待畫面，並於請求未完成時防止重複換頁；以手動連續點擊分頁驗證僅發出一個有效請求。
- [x] 2.4 實作空結果與錯誤狀態；錯誤提供重試，且既有成功結果在後續請求失敗時仍保留。
- [x] 2.5 處理連續搜尋或換頁造成的過期回應，確保只有最新請求可更新畫面。

## 3. Verification

- [x] 3.1 依「Paginate deterministically at 20 items」新增或更新 `apps/chillme/tests.py`，驗證 JSON 契約、每頁 20 筆、分頁邊界、搜尋條件與既有 HTML 頁可正常取得。
- [x] 3.2 手動驗證首次載入、搜尋、前後頁、空結果、網路失敗後重試、快速連續操作及瀏覽器歷史紀錄。
