from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Exécute tous les seeders de démonstration dans le bon ordre."

    def handle(self, *args, **options):
        call_command("seed_users")
        call_command("seed_formations_mg")
        call_command("seed_challenges_mg")
        call_command("seed_progressions_demo")
        self.stdout.write(self.style.SUCCESS("Tous les seeders ont été exécutés."))
