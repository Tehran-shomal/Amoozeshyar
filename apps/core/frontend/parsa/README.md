# پارسا — امور مالی

## Page ownership

- `payments` - سوابق پرداخت
- `secure-payment` - پرداخت‌های قابل انجام
- `financial-aid` - درخواست‌های تسهیلات
- `tuition` - خلاصه مالی نیمسال‌ها

Financial pages read through `GET /api/portal/pages/<slug>/`; only aid applications currently write via `POST /api/portal/pages/financial-aid/`. The form uses the active student's profile and server-assigned status.

`selectors.py` filters payment and scholarship records to the selected student; payments also follow the selected term. `templates/parsa/finance.html` renders the financial summary and safe-payment limitation. No payment is recorded because this checkout has no connected gateway.

URLs: `/portal/payments/`, `/portal/secure-payment/`, `/portal/financial-aid/`, `/portal/tuition/`. See [team ownership](../../../../docs/TEAM_OWNERSHIP.md), [API contracts](../../../../docs/API_CONTRACTS.md), and [presentation](../../../../docs/presentation/03_Parsa.md).
