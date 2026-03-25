from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Set a user role to admin'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user.role = 'admin'
            user.save(update_fields=['role'])
            self.stdout.write(self.style.SUCCESS(f'✓ {username} is now admin'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
