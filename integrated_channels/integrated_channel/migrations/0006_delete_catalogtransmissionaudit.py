# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrated_channel', '0005_auto_20180306_1251'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CatalogTransmissionAudit',
        ),
    ]
