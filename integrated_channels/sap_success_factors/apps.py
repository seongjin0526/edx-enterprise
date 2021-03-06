# -*- coding: utf-8 -*-
"""
Enterprise Integrated Channel SAP SuccessFactors Django application initialization.
"""
from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class SAPSuccessFactorsConfig(AppConfig):
    """
    Configuration for the Enterprise Integrated Channel SAP SuccessFactors Django application.
    """
    name = 'integrated_channels.sap_success_factors'
    verbose_name = "Enterprise SAP SuccessFactors Integration"
