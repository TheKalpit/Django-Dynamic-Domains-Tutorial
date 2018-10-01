import sys

from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.utils.text import capfirst

from domains.models import Domain


class NotRunningInTTYException(Exception):
    pass


class Command(BaseCommand):
    help = 'Used to create a domain.'
    requires_migrations_checks = True
    stealth_options = ('stdin',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.DomainModel = Domain
        self.domain_field = self.DomainModel._meta.get_field('domain')
        self.name_field = self.DomainModel._meta.get_field('name')

    def add_arguments(self, parser):
        parser.add_argument(
            '--%s' % 'domain',
            dest='domain', default=None,
            help='Specifies the domain.',
        )
        parser.add_argument(
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )
        parser.add_argument(
            '--%s' % 'name', dest='name', default=None,
            help='Specifies the name',
        )

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        domain = options['domain']
        name = options['name']
        database = options['database']

        verbose_domain_field_name = self.domain_field.verbose_name
        verbose_name_field_name = self.name_field.verbose_name

        # Enclose this whole thing in a try/except to catch
        # KeyboardInterrupt and exit gracefully.
        try:

            if hasattr(self.stdin, 'isatty') and not self.stdin.isatty():
                raise NotRunningInTTYException("Not running in a TTY")

            while domain is None:
                input_msg = '%s: ' % capfirst(verbose_domain_field_name)
                domain = self.get_input_data(self.domain_field, input_msg)
                if not domain:
                    continue
                if self.domain_field.unique:
                    try:
                        self.DomainModel._default_manager.db_manager(database).get_by_natural_key(domain)
                    except self.DomainModel.DoesNotExist:
                        pass
                    else:
                        self.stderr.write("Error: That %s is already in use." % verbose_domain_field_name)
                        domain = None

            if not domain:
                raise CommandError('%s cannot be blank.' % capfirst(verbose_domain_field_name))

            while name is None:
                input_msg = '%s: ' % capfirst(verbose_name_field_name)
                name = self.get_input_data(self.name_field, input_msg)
                if not name:
                    continue

            if not name:
                raise CommandError('%s cannot be blank.' % capfirst(verbose_domain_field_name))

        except KeyboardInterrupt:
            self.stderr.write("\nOperation cancelled.")
            sys.exit(1)

        except NotRunningInTTYException:
            self.stdout.write(
                "Domain creation skipped due to not running in a TTY. "
            )

        if domain and name:
            domain_data = {
                'domain': domain,
                'name': name,
            }
            self.DomainModel(**domain_data).save()
            if options['verbosity'] >= 1:
                self.stdout.write("Domain created successfully.")

    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if default and raw_value == '':
            raw_value = default
        try:
            val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % '; '.join(e.messages))
            val = None

        return val
