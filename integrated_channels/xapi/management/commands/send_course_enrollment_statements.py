# -*- coding: utf-8 -*-
"""
Send xAPI statements to the LRS configured via admin.
"""

from __future__ import absolute_import, unicode_literals

import datetime

from logging import getLogger

from django.core.management.base import BaseCommand, CommandError

from enterprise.models import EnterpriseCustomer
from enterprise.utils import NotConnectedToOpenEdX
from integrated_channels.exceptions import ClientError
from integrated_channels.xapi.models import XAPILRSConfiguration
from integrated_channels.xapi.utils import send_course_enrollment_statement


try:
    from student.models import CourseEnrollment
except ImportError:
    CourseEnrollment = None


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
        Parse and validate arguments for send_course_enrollment_statements command.

        Arguments:
            *args: Positional arguments passed to the command
            **options: optional arguments passed to the command

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

        if enterprise_customer:
            try:
                lrs_configuration = XAPILRSConfiguration.objects.get(
                    enterprise_customer=enterprise_customer
                )
            except XAPILRSConfiguration.DoesNotExist:
                raise CommandError('No xAPI Configuration found for "{enterprise_customer}"'.format(
                    enterprise_customer=enterprise_customer.name
                ))

            # Send xAPI analytics data to the configured LRS
            self.send_xapi_statements(lrs_configuration, days)
        else:
            for lrs_configuration in XAPILRSConfiguration.objects.filter(active=True):
                self.send_xapi_statements(lrs_configuration, days)

    def send_xapi_statements(self, lrs_configuration, days):
        """
        Send xAPI analytics data of the enterprise learners to the given LRS.

        Arguments:
            lrs_configuration (XAPILRSConfiguration): Configuration object containing LRS configurations
                of the LRS where to send xAPI  learner analytics.
            days (int): Include course enrollment of this number of days.
        """
        for course_enrollment in self.get_course_enrollments(lrs_configuration.enterprise_customer, days):
            try:
                send_course_enrollment_statement(lrs_configuration, course_enrollment)
            except ClientError:
                LOGGER.exception(
                    'Client error while send course enrollment to xAPI for'
                    ' enterprise customer {enterprise_customer}.'.format(
                        enterprise_customer=lrs_configuration.enterprise_customer.name
                    )
                )

    def get_course_enrollments(self, enterprise_customer, days):
        """
        Get course enrollments for all the learners of given enterprise customer.

        Arguments:
            enterprise_customer (EnterpriseCustomer): Include Course enrollments for learners
                of this enterprise customer.
            days (int): Include course enrollment of this number of days.

        Returns:
            (list): A list of CourseEnrollment objects.
        """
        if not CourseEnrollment:
            raise NotConnectedToOpenEdX("This package must be installed in an OpenEdX environment.")

        return CourseEnrollment.objects.filter(
            created__gt=datetime.datetime.now() - datetime.timedelta(days=days)
        ).filter(
            user_id__in=enterprise_customer.enterprise_customer_users.values_list('user_id', flat=True)
        )
