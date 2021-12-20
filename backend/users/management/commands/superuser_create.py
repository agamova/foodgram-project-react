from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

User = get_user_model()
SUPERUSER = settings.SUPERUSER_ADMIN


class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            admin = User.objects.create_superuser(**SUPERUSER)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin account can only be initialized if no Accounts exist')
