from django.contrib import admin

from polls.models import PollOption, Poll


class PollOptionInline(admin.TabularInline):
    model = PollOption
    fields = ('value',)
    extra = 1


class PollAdmin(admin.ModelAdmin):
    inlines = (PollOptionInline,)
    fields = ('content', 'domain',)
    readonly_fields = ('domain',)

    def get_queryset(self, request):
        qs = Poll.objects.filter(domain=request.domain)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def save_model(self, request, obj, form, change):
        obj.domain = request.domain
        return super().save_model(request, obj, form, change)


admin.site.register(Poll, PollAdmin)
