"""Page metadata owned by mobina."""

# Page labels and any specialized renderer or script stay with this team.
PAGES = {'enrollment': {'title': 'انتخاب واحد',
                'subtitle': 'مرحلهٔ ۱ از ۲ • اطلاعات دانشجویی و آموزشی را بررسی کنید.',
                'group': 'ثبت\u200cنام و انتخاب واحد',
                'template': 'mobina/enrollment.html',
                'script': 'mobina/section.js'},
 'selected-courses': {'title': 'دروس انتخاب\u200cشده',
                      'subtitle': 'مرحلهٔ ۲ از ۲ • گروه\u200cهای درسی را انتخاب و برنامهٔ نیمسال '
                                  'خود را تکمیل کنید.',
                      'group': 'ثبت\u200cنام و انتخاب واحد',
                      'template': 'mobina/selected_courses.html',
                      'script': 'mobina/section.js'},
 'curriculum': {'title': 'چارت انتخاب واحد',
                'subtitle': 'مسیر دروس، پیش\u200cنیازها و میزان پیشرفت تحصیلی',
                'group': 'ثبت\u200cنام و انتخاب واحد'}}

# Login and dashboard are module pages outside the /portal/<slug>/ route.
SPECIAL_PAGES = {
    "login": {"template": "mobina/login.html"},
    "dashboard": {"template": "mobina/home.html"},
}
