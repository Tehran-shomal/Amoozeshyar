# پارسا

## Page ownership

- `payments` - سوابق پرداخت
- `secure-payment` - پرداخت‌های قابل انجام
- `financial-aid` - درخواست‌های تسهیلات
- `tuition` - خلاصه مالی نیمسال‌ها

`pages.py` declares owned slugs and page-specific assets; `selectors.py` reads the records for those pages.
`forms.py` contains this group's forms, with ownership and validation enforced on the server.

`selectors.py` filters payment and scholarship records to the selected student; payments also follow the selected term. `templates/parsa/finance.html` supplies the PDF-style financial summary, transaction table, tuition totals, and safe-payment state. It never records a payment: the current project has no connected payment gateway, so that limitation is shown to the student.
