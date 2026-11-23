## Summary

將揪團活動列表改為由瀏覽器以 AJAX 取得活動資料，並加入有界分頁與完整的載入、空結果及錯誤狀態。

## Motivation

目前 `EventListView` 在伺服器端一次渲染所有符合條件的活動。資料量成長時，回應與畫面都會變重；換頁與搜尋也必須重新載入整頁，且沒有獨立的等待或請求失敗體驗。

## Proposed Solution

- 保留活動列表頁作為外框與搜尋介面，新增同源 JSON 資料端點供前端取得活動與分頁資訊。
- 以 `q` 與 `page` 表示搜尋與頁碼，每頁 20 筆，並讓網址反映目前條件以支援重新整理與分享。
- 在初始載入及切頁時提供骨架等待畫面；載入中停用分頁操作。
- 區分空結果與請求錯誤；錯誤提供重試，且切頁失敗時保留前一次成功資料。
- 新增共用規格 `ajax-list-data`，規定未來呈現持久化資料集合的列表採 AJAX、分頁與完整狀態處理。

## Non-Goals

- 不新增前端框架或第三方 API。
- 不變更活動建立、詳情、登入或資料模型規則。
- 不將靜態清單或一次性表單選項改為 AJAX。

## Impact

- Affected specs: new `ajax-list-data`
- Affected code: `apps/chillme/views.py`, `apps/chillme/urls.py`, `apps/chillme/templates/chillme/event_list.html`, related tests and static JavaScript/CSS assets
