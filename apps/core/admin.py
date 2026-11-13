from django.contrib import admin
from .models import OnlineClass, Ticket


admin.site.register(OnlineClass)


class TicketReplyInline(admin.TabularInline):
    model = Ticket
    fk_name = "parent"
    extra = 1


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketReplyInline]