## Why

目前登入頁只提供帳號密碼表單。專案已啟用 Google OAuth provider 並設定對應的社群應用程式，卻沒有可讓使用者啟動 Google 登入的介面入口，造成既有登入方式無法使用。

## What Changes

- 在登入頁提供清楚標示的「使用 Google 登入」按鈕，讓使用者可直接開始 Google OAuth 登入流程。
- 在按鈕上加入適當的 Google 標誌，並維持既有帳號密碼登入與註冊導引。
- 為登入頁的 Google 登入入口補上自動化驗證。

## Capabilities

### New Capabilities

- `google-social-login`: 使用者可從登入頁啟動已設定的 Google OAuth 登入流程。

### Modified Capabilities

- 無。

## Impact

- `templates/account/login.html` 的登入頁介面與 allauth 模板標籤使用方式。
- `apps/core/tests.py` 的登入頁驗證。
- 沿用既有 django-allauth、Google provider、`SocialApp` 與 OAuth 憑證設定；不新增套件、資料表或外部 API。
