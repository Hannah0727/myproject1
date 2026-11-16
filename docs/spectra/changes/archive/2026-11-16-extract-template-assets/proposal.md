## Why

`apps/core/templates/core/home.html` 將頁面結構與一整段自訂 CSS 寫在同一個檔案中，讓樣式難以獨立維護、檢視與重用。將首頁的自訂資產依 Django 慣例搬到 app 的靜態資產目錄，可在不改變頁面功能或視覺結果的前提下改善維護性。

## What Changes

- 在 `my-django-site/apps/core/static/myproject1/css/` 建立首頁樣式檔，遷移目前 `home.html` 的內嵌 `<style>` 規則。
- 在 `my-django-site/apps/core/static/myproject1/js/` 建立 JavaScript 資產目錄，並加入不會被網頁載入的 `.gitkeep`，使 Git 可保存此空目錄；本次不新增沒有行為用途的空白腳本檔。
- 更新 `my-django-site/apps/core/templates/core/home.html`，以 Django `{% load static %}` 與 `{% static %}` 載入外部 CSS，同時保留 Tailwind CDN 與現有模板內容、URL、表單及 class。
- 更新首頁測試，使預期 stylesheet URL 由 Django `static()` 產生，而非固定使用 `/static/` 前綴。

## Non-Goals (optional)

- 不更換、編譯或移除 Tailwind CDN；現有 Tailwind utility class 維持原樣。
- 不調整 `apps/chillme` 的活動頁；其模板沒有內嵌 CSS 或 JavaScript 可遷移。
- 不改變首頁文字、版面、導覽、搜尋、登入或註冊行為。
- 不為目前沒有互動需求的頁面建立空白 JavaScript 檔案。

## Impact

- Affected specs: none
- Affected code:
  - New: `my-django-site/apps/core/static/myproject1/css/home.css`、`my-django-site/apps/core/static/myproject1/js/.gitkeep`
  - Modified: `my-django-site/apps/core/templates/core/home.html`、`my-django-site/apps/core/tests.py`
  - Removed: (none)
- Compatibility: no capability-level observable behavior changes
