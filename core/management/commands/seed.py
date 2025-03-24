from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin1').exists():
            User.objects.create_user(username='admin1', password='admin123', role='admin')
        if not User.objects.filter(username='cook1').exists():
            User.objects.create_user(username='cook1', password='1234', role='cook')
        if not User.objects.filter(username='stock1').exists():
            User.objects.create_user(username='stock1', password='1234', role='stockman')
        if not User.objects.filter(username='client1').exists():
            User.objects.create_user(username='client1', password='1234', role='client')

        self.stdout.write(self.style.SUCCESS('Тестовые пользователи созданы!'))
