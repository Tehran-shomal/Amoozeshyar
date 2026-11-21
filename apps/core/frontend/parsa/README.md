# پارسا

## Page ownership

- `payments` - سوابق پرداخت
- `secure-payment` - پرداخت‌های قابل انجام
- `financial-aid` - درخواست‌های تسهیلات
- `tuition` - خلاصه مالی نیمسال‌ها

`pages.py` declares owned slugs and page-specific assets; the browser reads financial records through `/api/portal/pages/<slug>/`, backed by student-scoped selectors.
`forms.py` contains this group's forms, with ownership and validation enforced on the server.

`selectors.py` filters payment and scholarship records to the selected student; payments also follow the selected term. Form submissions use the same page API and existing Django form validation. `templates/parsa/finance.html` supplies the PDF-style financial summary, transaction table, tuition totals, and safe-payment state. It never records a payment: the current project has no connected payment gateway, so that limitation is shown to the student.
