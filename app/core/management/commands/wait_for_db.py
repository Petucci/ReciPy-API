import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Cheching database status')
        db_connection = None

        while not db_connection:
            try:
                db_connection = connections['default']
            except OperationalError:
                self.stdout.write('database unavailable')
                time.sleep(1);

        self.stdout.write('Database available')