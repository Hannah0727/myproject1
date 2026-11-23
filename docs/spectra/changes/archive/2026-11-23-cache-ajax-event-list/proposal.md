## Summary

為活動列表的非同步資料 API 加入伺服器端快取，並在建立新活動且交易成功後立即使列表快取失效。

## Motivation

活動列表的頁面殼已由瀏覽器透過 Ajax 請求資料，但每一個相同的搜尋與分頁請求仍會重新查詢資料庫。專案已配置 Redis 快取；將它用於列表 API 可降低重複查詢，同時必須確保新活動建立後，下一次列表請求不會取得建立前的資料。

## Proposed Solution

- 對活動列表資料 API 的成功 JSON 回應套用伺服器端快取，並以標準化搜尋條件、頁碼與列表快取版本區分內容。
- 保持目前預設快取有效期，讓相同 Ajax 請求可重用快取回應。
- 在任何 `Event` 新增且資料庫交易提交成功後，使活動列表的快取版本更新；下一次任一搜尋或分頁請求必須建立新的快取內容。
- 增加測試，驗證相同 API 請求會讀取快取，以及建立活動後清除所有查詢／頁碼變體的舊列表資料。

## Non-Goals (optional)

- 不快取活動詳情頁、建立活動表單或瀏覽器端 JavaScript 狀態。
- 不改變活動列表的輸入參數、JSON 結構、分頁大小或搜尋規則。
- 不為既有 Redis 快取設定以外的後端新增相容性承諾。

## Alternatives Considered (optional)

- 以萬用字元逐筆刪除所有列表快取鍵：捨棄，因為搜尋條件與頁碼組合不受限，且會依賴 Redis 專屬的鍵掃描／刪除行為。
- 僅在 `EventCreateView` 清除快取：捨棄，因為 Django Admin、shell 或未來其他建立入口會留下舊資料。

## Impact

- Affected specs: ajax-list-data
- Affected code:
  - Modified: apps/chillme/views.py
  - Modified: apps/chillme/models.py
  - Modified: apps/chillme/apps.py
  - Modified: apps/chillme/tests.py
  - New: apps/chillme/signals.py
  - Removed: none
