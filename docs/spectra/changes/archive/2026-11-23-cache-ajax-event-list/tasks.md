## 1. 活動列表快取與失效

- [x] 1.1 在 `apps/chillme/views.py` 實作「以正規化請求參數與列表版本組成快取鍵」，使 `EventListDataView` 對相同正規化 `q` 與最終頁碼重用完整成功 JSON、保留既有回應形狀與 60 秒有效期，並在快取讀寫失敗時回退為原本的資料庫查詢；以新增或更新的 `EventListDataViewTests` 驗證快取命中與快取故障仍成功回應。
- [x] 1.2 在 `apps/chillme/signals.py` 與 `apps/chillme/apps.py` 實作「在 Event 建立的交易提交後推進列表版本」，使任何 ORM 建立的 `Event` 僅在交易提交後使所有搜尋與頁碼列表變體失效；以訊號與交易測試驗證提交後改用新版本、回滾時不改變版本。

## 2. 回歸驗證

- [x] 2.1 [after: 1.1, 1.2] 完成「快取內容包含完整成功 JSON」並驗證「Asynchronous event-list data is cached and invalidated after event creation」：在 `apps/chillme/tests.py` 覆蓋未篩選、搜尋與分頁快取在建立活動後均不讀取舊版本，並執行 `python manage.py test apps.chillme` 確認既有 API 輸入、分頁與 JSON 契約未回歸。
