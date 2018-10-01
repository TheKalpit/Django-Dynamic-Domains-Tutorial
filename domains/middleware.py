from django.utils.deprecation import MiddlewareMixin


class CurrentDomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        from .models import Domain
        request.domain = Domain.objects.get_current(request)