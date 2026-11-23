## Why

目前首頁、活動頁與帳號頁各自維護 HTML 外框、Tailwind 載入與導覽入口，造成品牌導覽不一致，也讓新增或調整全站導覽時必須重複修改多個模板。現在已有首頁的品牌導覽與共用 CSS，適合將它整理為可被各 app 使用的網站外框。

## What Changes

- 在 `core` app 提供可跨 app 繼承的基礎模板，集中 HTML 文件結構、共用樣式載入與頁面內容區塊。
- 將首頁的品牌導覽列抽為共用元件，讓首頁、活動頁與帳號頁都有一致的首頁、活動探索與帳號入口。
- 讓導覽列依既有登入狀態顯示適當行動，並使從非首頁前往首頁段落的連結使用首頁 URL 加錨點。
- 將既有頁面改為繼承基礎模板，同時保留各頁既有的表單、活動內容、路由與後端行為。

## Capabilities

### New Capabilities

- `shared-site-shell`: Django 頁面可透過 core 提供的共用網站外框與登入感知導覽列，維持跨頁一致導覽。

### Modified Capabilities

- 無。

## Impact

- Affected code: `apps/core/templates/core/`、`apps/core/static/myproject1/css/`、`apps/chillme/templates/chillme/`、`templates/account/`。
- APIs: 無新增或變更。
- Dependencies: 使用既有 Django 模板繼承、命名 URL、認證 context processor 與 Tailwind CDN；不新增相依套件。
