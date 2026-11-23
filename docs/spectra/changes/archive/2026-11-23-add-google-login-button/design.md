## Context

專案已在設定中啟用 django-allauth 的 Google provider，資料庫也有連結目前網站的 Google `SocialApp`。不過 `templates/account/login.html` 只呈現帳號密碼表單，使用者無法從此頁啟動已設定的 Google OAuth 流程。

## Goals / Non-Goals

**Goals:**

- 讓訪客可在登入頁直接啟動 Google OAuth 登入。
- 清楚區分帳號密碼登入與 Google 登入，並在 Google 按鈕上呈現可辨識的 Google 標誌。
- 保持既有登入表單、註冊連結與登入完成後的導向行為。

**Non-Goals:**

- 不新增或變更 Google OAuth 用戶端憑證、同意畫面或已設定的 `SocialApp`。
- 不修改註冊頁、帳號連結管理頁或其他第三方登入方式。
- 不自行實作 OAuth callback、帳號建立或帳號合併邏輯；沿用 django-allauth。

## Decisions

### Use django-allauth provider URL in the login template

登入頁使用 django-allauth 的 `provider_login_url` 模板標籤產生 Google 登入入口，而非硬編 OAuth URL 或自行建立 view。此方式沿用現有 provider 設定、網站綁定與 callback 管理。

替代方案是在專案內新增 Google OAuth view；這會複製 allauth 已提供的流程並增加憑證與 callback 維護面，因此不採用。

### Place a branded Google action below the password form

Google 登入動作放在帳號密碼登入按鈕下方，以「或」作為視覺分隔。按鈕以文字「使用 Google 登入」與內嵌 Google 標誌呈現；內嵌 SVG 不增加外部圖片載入或新增靜態資產。

替代方案是只提供文字連結；雖然功能相同，但不符合使用者要求的明確登入選項與適當 Google 標誌，因此不採用。

### Verify rendered entry rather than the external OAuth exchange

自動化測試確認匿名訪客取得登入頁時，頁面具有 Google 登入文字與由 allauth 產生的 Google provider URL。測試不呼叫 Google 或驗證憑證，避免把第三方網路與私密設定納入本地測試。

## Implementation Contract

- **Behavior:** 未登入訪客在 `/accounts/login/` 可見既有帳號密碼登入表單與「使用 Google 登入」動作；啟動該動作時，請求交由已設定的 Google allauth provider 處理。
- **Interface:** 模板透過 django-allauth 的 socialaccount 模板標籤產生 Google provider URL；按鈕使用內嵌 SVG 標誌，不需要新的 HTTP endpoint、資料表或前端套件。
- **Failure modes:** 如果部署環境未設定或未將 Google `SocialApp` 綁定目前網站，allauth 的既有設定錯誤行為維持不變；本變更不以假按鈕或替代 OAuth 流程掩蓋設定問題。
- **Acceptance criteria:** 對 `account_login` 的匿名請求回傳 200，包含「使用 Google 登入」及 Google provider 登入 URL；既有帳密 form action 與註冊連結仍存在。
- **In scope:** 登入模板和針對該頁的測試。
- **Out of scope:** OAuth 憑證、Google Cloud 設定、資料庫 migration、註冊頁、登入後重導邏輯與其他社群 provider。

## Risks / Trade-offs

- [Google `SocialApp` 未綁定部署網站] → 在部署前於 Django admin 確認 Google 應用程式已綁定正確網域與 callback URL。
- [Google 品牌圖示與頁面樣式不一致] → 使用簡潔的彩色 Google SVG，並採用與既有登入按鈕相容的按鈕尺寸和鍵盤焦點樣式。
