from django.core.management.base import BaseCommand
from makale.models import HakemeYollamaKaydi, Makale
from django.db.models import Count

class Command(BaseCommand):
    help = 'Cleans up duplicate hakem assignments'

    def handle(self, *args, **options):
        # Find all makales with multiple assignments
        duplicates = HakemeYollamaKaydi.objects.values('makale').annotate(
            count=Count('id')).filter(count__gt=1)

        for dup in duplicates:
            makale_id = dup['makale']
            assignments = HakemeYollamaKaydi.objects.filter(
                makale_id=makale_id).order_by('tarih')
            
            # Keep the most recent assignment and delete others
            latest = assignments.last()
            assignments.exclude(id=latest.id).delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Cleaned up assignments for makale {makale_id}. Kept assignment to {latest.hakem.isim}'
                )
            ) 