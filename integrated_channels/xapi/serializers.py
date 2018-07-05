# -*- coding: utf-8 -*-

"""
Serializers for xAPI data.
"""
from __future__ import absolute_import, unicode_literals

from rest_framework import serializers

from enterprise.models import EnterpriseCustomerUser


class LearnerInfoSerializer(serializers.Serializer):
    """
    Serializer for Learner info.

    Model: User
    """
    lms_user_id = serializers.IntegerField(source='id')
    user_username = serializers.CharField(source='username')
    user_email = serializers.EmailField(source='email')
    user_country_code = serializers.CharField(source='profile.country.code')
    user_account_creation_date = serializers.DateTimeField(source='date_joined')

    enterprise_user_id = serializers.SerializerMethodField()
    enterprise_sso_uid = serializers.SerializerMethodField()

    def get_enterprise_user_id(self, obj):
        try:
            enterprise_learner = EnterpriseCustomerUser.objects.get(user_id=obj.id)
        except EnterpriseCustomerUser.DoesNotExist:
            return

        return enterprise_learner.id

    def get_enterprise_sso_uid(self, obj):
        try:
            enterprise_learner = EnterpriseCustomerUser.objects.get(user_id=obj.id)
        except EnterpriseCustomerUser.DoesNotExist:
            return

        return enterprise_learner.enterprise_customer.identity_provider


class CourseInfoSerializer(serializers.Serializer):
    """
    Serializer for course info.

    Model: CourseOverview
    """
    course_id = serializers.CharField(source='id')
    course_title = serializers.CharField(source='display_name')
    course_description = serializers.CharField(source='short_description')
    course_details_url = serializers.CharField(source='marketing_url')
    course_effore = serializers.CharField(source='effort')
    course_duration = serializers.SerializerMethodField()

    def get_course_duration(self, obj):
        return obj.end - obj.start if obj.start and obj.end else None
