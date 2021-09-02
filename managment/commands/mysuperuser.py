import os
from django.core.management.base import BaseCommand
from accounts.models import Account

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Account.objects.filter(username='mehriddinnozimov05').exists():
            Account.objects.create_superuser('Mehriddin', 'Nozimov', 'mehriddinnozimov05@gmail.com', 'mehriddinnozimov05', 'nicolas11')