"""
Placeholder migration — the actual token_blacklist tables are created
by rest_framework_simplejwt.token_blacklist's own migrations.
This file just documents that we enabled BLACKLIST_AFTER_ROTATION in 0004.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_alter_user_avatar'),
    ]

    operations = []
