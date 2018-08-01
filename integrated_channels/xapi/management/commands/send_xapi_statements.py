# -*- coding: utf-8 -*-
"""
Send xAPI statements to the LRS configured via admin.
"""

from __future__ import absolute_import, unicode_literals

from logging import getLogger

from django.core.management.base import BaseCommand, CommandError

from enterprise.models import EnterpriseCustomer

LOGGER = getLogger(__name__)


class Command(BaseCommand):
    """
    Send xAPI statements to all Enterprise Customers.
    """

    def add_arguments(self, parser):
        """
        Add required arguments to the parser.
        """
        parser.add_argument(
            '--days',
            dest='days',
            required=False,
            type=int,
            default=1,
            help='Send xAPI analytics for learners who enrolled during last this number of days.'
        )
        parser.add_argument(
            '--enterprise_customer_uuid',
            dest='enterprise_customer_uuid',
            type=str,
            required=False,
            help='Only send xAPI analytics for this enterprise customer.'
        )
        super(Command, self).add_arguments(parser)

    @staticmethod
    def parse_arguments(*args, **options):
        """
        Parse and validate arguments for send_xapi_statements command.

        Args:
            *args: Positional arguments passed to the update_assets command
            **options: optional arguments passed to the update_assets command
        Returns:
            A tuple containing parsed values for
            1. days (int): Integer showing number of days to lookup enterprise enrollments,
                course completion etc and send to xAPI LRS
            2. enterprise_customer_uuid (EnterpriseCustomer): Enterprise Customer if present then
                send xAPI statements just for this enterprise.
        """
        days = options.get('days', 1)
        enterprise_customer_uuid = options.get('enterprise_customer_uuid')
        enterprise_customer = None

        if enterprise_customer_uuid:
            try:
                enterprise_customer = EnterpriseCustomer.objects.get(uuid=enterprise_customer_uuid)
            except EnterpriseCustomer.DoesNotExist:
                raise CommandError('Enterprise customer with uuid "{enterprise_customer_uuid}" does not exist.'.format(
                    enterprise_customer_uuid=enterprise_customer_uuid
                ))

        return days, enterprise_customer

    def handle(self, *args, **options):
        """
        Send xAPI statements.
        """
        days, enterprise_customer = self.parse_arguments(*args, **options)

        print(days, enterprise_customer)
