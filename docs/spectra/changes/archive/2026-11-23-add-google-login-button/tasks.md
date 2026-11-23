## 1. 登入頁 Google 入口

- [x] 1.1 實作「Use django-allauth provider URL in the login template」與「Place a branded Google action below the password form」：在 `templates/account/login.html` 保留帳密登入表單和註冊連結，並在其下加入含內嵌 Google SVG 的「使用 Google 登入」入口；入口必須使用 `provider_login_url` 指向既有 Google provider。以瀏覽器手動開啟 `/accounts/login/`，確認按鈕可見、帳密表單仍可使用，且 Google 動作的連結指向 Google provider 登入路徑。

## 2. 自動化驗證

- [x] 2.1 [after: 1.1] 實作「Verify rendered entry rather than the external OAuth exchange」測試，覆蓋「Google login entry is available on the login page」與「Password login remains available」：匿名請求 `account_login` 時，驗證 200 回應含「使用 Google 登入」、Google provider URL、既有帳密 form action 與註冊連結。以 `python manage.py test apps.core.tests` 驗證測試通過，且測試不連線至 Google。
