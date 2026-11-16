## Context

首頁模板 `my-django-site/apps/core/templates/core/home.html` 原本在 `<head>` 內包含自訂 CSS，且同時使用 Tailwind CDN utility class。Django 可由 app 專屬 `static/` 目錄收集與提供資產；採用 `static/myproject1/` 命名空間可避免日後不同 app 的同名檔案互相覆蓋。本次只處理 `core` 的首頁，因為已確認的 `chillme` 模板沒有內嵌 CSS 或 JavaScript。審查後發現空的 JS 目錄不會被 Git 保存，且測試將靜態 URL 前綴寫死。

## Goals / Non-Goals

目標：將首頁自訂 CSS 移至可獨立維護的靜態檔，建立可被 Git 保存的 JavaScript 資產位置，並讓測試適用於不同的 Django 靜態 URL 設定。

非目標：不改變首頁可見內容、連結、表單送出、Django 模板語法、Tailwind CDN 或任何 `chillme` 頁面；不新增無行為用途的 JavaScript 檔。

## Decisions

- 使用 `my-django-site/apps/core/static/myproject1/css/home.css` 作為首頁專用樣式檔。這讓資產位於擁有模板的 `core` app 中，且透過 `myproject1` 命名空間避免靜態檔名稱衝突。
- 在模板開頭載入 Django `static` 標籤，並以 `{% static 'myproject1/css/home.css' %}` 產生 CSS URL。這可相容開發與部署環境的靜態檔設定。
- 保留 `<script src="https://cdn.tailwindcss.com"></script>`。本次要拆出的是手寫 CSS；將 Tailwind 改為建置流程是獨立的相依性與工具鏈變更。
- 使用 `my-django-site/apps/core/static/myproject1/js/.gitkeep` 保存 JavaScript 資產目錄；它不是腳本，不會被模板載入。
- 首頁測試以 Django `static("myproject1/css/home.css")` 產生預期 URL，避免將目前 `STATIC_URL` 的 `/static/` 前綴視為固定契約。

## Implementation Contract

- `home.html` 不再包含內嵌 `<style>` 區塊，且會在 `<head>` 載入首頁外部 CSS。
- 新 CSS 檔完整保留既有自訂選擇器、CSS 變數、資料 URI 圖示、hover 行為、媒體查詢與最終覆寫規則，確保首頁渲染結果不變。
- 靜態資產路徑必須使用 Django `{% static %}`，不得硬編碼開發伺服器 URL。
- `js/.gitkeep` 必須存在且不可被首頁載入，讓 Git 能保存 JavaScript 目錄而不新增空白 JavaScript 請求。
- 首頁測試必須從 Django 靜態資產工具取得預期 CSS URL。
- 頁面仍可載入 Tailwind CDN；所有既有 Django URL、登入／註冊連結與搜尋表單維持不變。
- 這是可維護性重構，能力層級的可觀察行為不變。

## Risks / Trade-offs

- [移動時遺漏或改動 CSS 字元會造成視覺差異] -> 將原 `<style>` 內容逐字遷移，並以 Django 開發伺服器或測試 client 請求首頁，確認回應含外部 stylesheet URL 且不含內嵌樣式。
- [靜態路徑未經 `{% static %}` 解析，在部署時可能失效] -> 模板使用 `{% load static %}` 和 `{% static 'myproject1/css/home.css' %}`，測試以 Django `static()` 產生預期 URL。
- [空目錄在提交後消失] -> 在 `js/` 內加入 `.gitkeep`，並確認它存在且首頁沒有新增 script 載入。

## Migration Plan

1. 新增 CSS 檔、JavaScript 目錄與 `.gitkeep`。
2. 更新首頁模板，載入靜態標籤並以 stylesheet link 取代內嵌樣式。
3. 更新首頁測試，改由 Django `static()` 產生預期 CSS URL。
4. 執行專案既有測試；啟動開發伺服器或以 Django 測試 client 請求首頁，確認 CSS URL 可解析並檢查首頁的主要連結與表單仍存在。
5. 若外部樣式無法載入，還原模板為內嵌樣式並檢查靜態檔設定與命名空間路徑；此變更沒有資料遷移。

## Open Questions

無。範圍已限定為 `core` 首頁；日後若其他模板出現內嵌資產，應以獨立變更評估是否共用或建立頁面專屬資產。
