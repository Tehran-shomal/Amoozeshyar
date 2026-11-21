"""Page metadata owned by neyousha_pouya."""

# Page labels and any specialized renderer or script stay with this team.
PAGES = {'internship': {'title': 'کارآموزی',
                'subtitle': 'ثبت محل کارآموزی و پیگیری تأیید استاد و گزارش\u200cها',
                'group': 'برنامه آموزشی و امتحانات'},
 'notifications': {'title': 'مرکز اعلان\u200cها',
                   'subtitle': 'اعلان\u200cهای آموزشی، مالی و درخواست\u200cهای شما در یک محل',
                   'group': 'ارتباط و خدمات دانشجویی',
                   'template': 'neyousha_pouya/notifications.html'},
 'announcements': {'title': 'اطلاعیه\u200cهای اساتید',
                   'subtitle': '',
                   'group': 'ارتباط و خدمات دانشجویی',
                   'template': 'neyousha_pouya/notifications.html'},
 'calendar': {'title': 'تقویم آموزشی ترم', 'subtitle': '', 'group': 'برنامه آموزشی و امتحانات'},
 'schedule': {'title': 'برنامه هفتگی کامل', 'subtitle': '', 'group': 'برنامه آموزشی و امتحانات'},
 'settings': {'title': 'تنظیمات زبان و اعلان\u200cها',
              'subtitle': 'مدیریت زبان نمایش و روش دریافت اعلان\u200cها',
              'group': 'ارتباط و خدمات دانشجویی'}}

# The lead team owns the shared semester picker in the portal header.
COMPONENTS = ("term_picker",)
