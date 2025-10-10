from django.core.management.base import BaseCommand
from marketglobal.services import update_dashboard

class Command(BaseCommand):
    help = "Fetch market boxes (light or heavy)"

    def add_arguments(self, parser):
        parser.add_argument("--heavy", action="store_true", help="Also compute Altseason & Avg RSI")

    def handle(self, *args, **opts):
        data = update_dashboard(compute_heavy=opts["heavy"])
        self.stdout.write(self.style.SUCCESS(f"Updated: {', '.join(data.keys())}"))
