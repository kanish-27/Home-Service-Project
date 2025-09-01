from django.core.management.base import BaseCommand
from django.conf import settings
import pymongo


class Command(BaseCommand):
    help = 'Clear all bookings from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all bookings',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL bookings from the database.\n'
                    'Use --confirm flag to proceed: python manage.py clear_bookings --confirm'
                )
            )
            return

        try:
            # Connect to MongoDB
            client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]

            # Clear bookings collection
            bookings_result = db['services_booking'].delete_many({})
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {bookings_result.deleted_count} bookings from MongoDB'
                )
            )

            # Clear payments collection
            payments_result = db['services_payment'].delete_many({})
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {payments_result.deleted_count} payments from MongoDB'
                )
            )

            # Clear invoices collection if exists
            try:
                invoices_result = db['services_invoice'].delete_many({})
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Deleted {invoices_result.deleted_count} invoices from MongoDB'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'No invoices collection found or error: {e}')
                )

            # Clear reviews collection if exists
            try:
                reviews_result = db['services_review'].delete_many({})
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Deleted {reviews_result.deleted_count} reviews from MongoDB'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'No reviews collection found or error: {e}')
                )

            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ All bookings and related data have been cleared successfully!'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing bookings: {e}')
            )
