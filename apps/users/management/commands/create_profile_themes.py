from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import ProfileTheme

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates ProfileTheme for all existing users that do not have one'

    def handle(self, *args, **options):
        users = User.objects.filter(profile_theme__isnull=True)
        count = 0
        for user in users:
            ProfileTheme.objects.create(user=user)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Created {count} profile theme(s)'))
