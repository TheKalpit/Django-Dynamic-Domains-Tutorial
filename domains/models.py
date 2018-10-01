import string

from django.core.exceptions import ValidationError
from django.db import models
from django.http.request import split_domain_port

DOMAINS_CACHE = {}


def _simple_domain_name_validator(value):
    if not value:
        return
    checks = ((s in value) for s in string.whitespace)
    if any(checks):
        raise ValidationError("The domain name cannot contain any spaces or tabs.",
                              code='invalid')


class DomainManager(models.Manager):
    use_in_migrations = True

    def _get_domain_by_id(self, domain_id):
        if domain_id not in DOMAINS_CACHE:
            domain = self.get(pk=domain_id)
            DOMAINS_CACHE[domain_id] = domain
        return DOMAINS_CACHE[domain_id]

    def _get_domain_by_request(self, request):
        host = request.get_host()
        try:
            if host not in DOMAINS_CACHE:
                DOMAINS_CACHE[host] = self.get(domain__iexact=host)
            return DOMAINS_CACHE[host]
        except Domain.DoesNotExist:
            domain, port = split_domain_port(host)
            if domain not in DOMAINS_CACHE:
                DOMAINS_CACHE[domain] = self.get(domain__iexact=domain)
            return DOMAINS_CACHE[domain]

    def get_current(self, request=None, domain_id=None):
        if domain_id:
            return self._get_domain_by_id(domain_id)
        elif request:
            return self._get_domain_by_request(request)

    def clear_cache(self):
        global DOMAINS_CACHE
        DOMAINS_CACHE = {}

    def get_by_natural_key(self, domain):
        return self.get(domain=domain)


class Domain(models.Model):
    domain = models.CharField(max_length=128, unique=True, validators=[_simple_domain_name_validator])
    name = models.CharField(max_length=128)

    objects = DomainManager()

    def __str__(self):
        return self.domain
