## Context

`EventListView` 目前以 Django 模板直接迭代所有活動。活動已按建立時間倒序，但沒有分頁。搜尋由 `q` 查詢參數執行。

## Decisions

### Use a dedicated same-origin JSON endpoint

活動列表頁仍回傳 HTML 外框；前端在載入、搜尋及換頁時向專用端點請求 JSON。資料端點回傳每筆活動顯示所需欄位，以及 `page`、`total_pages`、`has_previous`、`has_next`、`total_count` 與已套用的 `q`。這使模板與資料契約各自清楚，且無須引入新框架。

### Paginate deterministically at 20 items

後端以既有 `-created_at` 排序並使用 Django paginator，每頁 20 筆。非正整數頁碼安全地回到第一頁；超出範圍的頁碼回到最後有效頁。搜尋條件會隨每個換頁請求保留。

### Keep URL state in sync

成功載入後，瀏覽器網址反映 `q` 與 `page`，並支援瀏覽器上一頁與下一頁重新取得正確資料。搜尋只在使用者送出表單時請求，以避免輸入期間的競態與不必要流量。

### Model the list UI as explicit states

初始載入或換頁時，列表區顯示固定高度骨架並停用分頁控制。成功但無資料時顯示空結果。請求失敗時顯示可理解的錯誤與重試操作；若已有成功資料，保留資料並在其附近顯示錯誤，而非清空列表。

## Interface Contract

`GET` 資料端點接受可選的 `q` 與 `page`。成功回應為 JSON 且包含：

- `items`：活動 `id`、`name`、`code`、建立者顯示名稱及詳情 URL。
- `pagination`：`page`、`total_pages`、`total_count`、`has_previous`、`has_next`。
- `query`：正規化後的 `q`。

無效輸入不得造成 500 回應。前端對網路錯誤、非成功 HTTP 回應與無法解析的資料回應，都呈現相同可重試的錯誤狀態。

## Risks / Trade-offs

- JavaScript 不可用時無法呈現動態列表；本變更的產品規則明確要求列表資料以 AJAX 取得。
- 前後端資料欄位的重複定義可能漂移；以端點測試固定 JSON 回應形狀。
- 快速連續操作可能造成回應亂序；前端需取消或忽略過期請求。
