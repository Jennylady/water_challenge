import secrets
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.accounts.user.models import User
from apps.formation.models import Choix, IllustrationModule, Module, Question, Quiz
from apps.notifications.models import Notification
from apps.notifications.services import notifier


def _media_files(relative_directory, extensions):
    """Retourne uniquement les fichiers réellement présents dans MEDIA_ROOT."""
    directory = Path(settings.MEDIA_ROOT) / relative_directory
    if not directory.is_dir():
        return []

    allowed = {extension.lower() for extension in extensions}
    return sorted(
        path.relative_to(settings.MEDIA_ROOT).as_posix()
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in allowed
    )


def _random_file(files):
    return secrets.choice(files) if files else None


MODULES = [
    {
        "titre": "Ny rano sy ny maha-zava-dehibe azy",
        "resume": "Fampahafantarana ny anjara toeran'ny rano eo amin'ny fahasalamana sy ny fiainana.",
        "contenu": (
            "Ny rano dia fototry ny aina. Ilaina amin'ny fisotroana, fahadiovana, fambolena "
            "ary fiarovana ny tontolo iainana. Tokony hampiasaina amim-pitandremana izy mba "
            "hahazoan'ny taranaka rehetra rano madio sy ampy."
        ),
        "niveau": Module.Niveau.DEBUTANT,
        "questions": [
            ("Nahoana no zava-dehibe ny rano?", ["Satria fototry ny aina izy", "Satria tsy ilaina amin'ny fahasalamana", "Satria natao ho an'ny fambolena ihany"], 0),
            ("Inona no tokony hatao amin'ny rano?", ["Ampiasaina amim-pitandremana", "Avela hikoriana foana", "Araraka eny rehetra eny"], 0),
            ("Iza no mila rano madio?", ["Ny olon-drehetra", "Ny ankizy ihany", "Ny tantsaha ihany"], 0),
            ("Inona no sehatra iray mampiasa rano?", ["Fahasalamana", "Fandoroana plastika", "Fanariana fako"], 0),
            ("Inona no tanjona amin'ny fiarovana rano?", ["Ho ampy ho an'ny taranaka rehetra", "Hampitombo ny fandaniana", "Hampaloto ny loharano"], 0),
        ],
    },
    {
        "titre": "Fisorohana ny fandotoana ny rano",
        "resume": "Fomba tsotra hisorohana ny fako sy akora manimba tsy hiditra amin'ny rano.",
        "contenu": (
            "Ny fako, menaka, simika ary rano maloto dia mety handoto renirano sy loharano. "
            "Tsy tokony hariana anaty tatatra na rano ireo akora ireo. Ny fanasokajiana fako "
            "sy ny fanadiovana iombonana dia fomba mahomby hiarovana ny rano."
        ),
        "niveau": Module.Niveau.DEBUTANT,
        "questions": [
            ("Inona no mety handoto rano?", ["Menaka sy simika", "Rivotra madio", "Vato madio"], 0),
            ("Aiza no tsy tokony hanariana menaka?", ["Ao anaty tatatra", "Ao anaty fitoerana voatokana", "Any amin'ny mpanangona"], 0),
            ("Inona no fomba iray hiarovana rano?", ["Fanasokajiana fako", "Fanariana plastika anaty renirano", "Fandoroana fako eo amoron-drano"], 0),
            ("Iza no afaka mandray anjara?", ["Ny fiarahamonina rehetra", "Ny mpitondra ihany", "Ny mpianatra ihany"], 0),
            ("Nahoana no atao ny fanadiovana iombonana?", ["Hiaro ny tontolo sy ny rano", "Hampitombo ny loto", "Hanariana fako bebe kokoa"], 0),
        ],
    },
    {
        "titre": "Fitsitsiana rano ao an-tokantrano",
        "resume": "Fomba fampihenana ny fandaniana rano isan'andro ao an-trano.",
        "contenu": (
            "Azo ahena ny fandaniana rano amin'ny fanakatonana paompy rehefa tsy ampiasaina, "
            "fanamboarana ny fivoahan-drano, fampiasana siny ary fanangonana ranonorana. "
            "Ny fanaraha-maso tsy tapaka dia manampy hahafantarana ny fandaniana tafahoatra."
        ),
        "niveau": Module.Niveau.APPRENTI,
        "questions": [
            ("Inona no atao rehefa tsy ampiasaina ny paompy?", ["Akatona", "Avela hisokatra", "Esorina"], 0),
            ("Inona no tokony hatao amin'ny fivoahan-drano?", ["Amboarina haingana", "Avela ela", "Saromana lamba fotsiny"], 0),
            ("Inona no azo angonina hampiasaina?", ["Ranonorana", "Rano maloto", "Menaka"], 0),
            ("Inona no manampy hahita fandaniana tafahoatra?", ["Fanaraha-maso tsy tapaka", "Tsy firaharahiana", "Fanokafana paompy rehetra"], 0),
            ("Fitaovana inona no manampy amin'ny fitsitsiana?", ["Siny", "Fantsona vaky", "Tatatra misokatra"], 0),
        ],
    },
    {
        "titre": "Ny andraikitry ny mpandrindra rano",
        "resume": "Fomba fitarihana, fanentanana ary fanaraha-maso hetsika momba ny rano.",
        "contenu": (
            "Ny mpandrindra dia manomana hetsika, mizara andraikitra, mihaino ny olona ary "
            "manara-maso ny vokatra. Tokony hanome vaovao marina, hanaja ny fiarahamonina "
            "ary hitatitra ny zava-bita amin'ny fomba mazava."
        ),
        "niveau": Module.Niveau.ACTIF,
        "questions": [
            ("Inona no andraikitry ny mpandrindra?", ["Manomana sy manara-maso hetsika", "Miasa irery foana", "Manafina vaovao"], 0),
            ("Inona no tokony homena ny olona?", ["Vaovao marina", "Tsaho", "Toromarika tsy mazava"], 0),
            ("Ahoana no fizarana asa?", ["Amin'ny andraikitra mazava", "Tsy misy fandaminana", "Olona iray no manao rehetra"], 0),
            ("Inona no atao aorian'ny hetsika?", ["Mitatitra ny vokatra", "Manadino ny zava-bita", "Mamafa ny porofo"], 0),
            ("Inona no toetra ilaina?", ["Fihainoana sy fanajana", "Fandrahonana", "Fanavakavahana"], 0),
        ],
    },
]


class Command(BaseCommand):
    help = "Mamorona modules sy quiz feno amin'ny teny malagasy."

    @transaction.atomic
    def handle(self, *args, **options):
        moderators = User.objects.filter(
            role=User.Role.MODERATOR,
            is_active=True,
            is_email_verified=True,
        )

        cover_files = _media_files(
            "formation/modules/couvertures",
            {".jpg", ".jpeg", ".png", ".webp"},
        )
        illustration_files = _media_files(
            "formation/modules/illustrations",
            {".jpg", ".jpeg", ".png", ".webp"},
        )
        video_files = _media_files(
            "formation/modules/videos",
            {".mp4", ".mkv", ".avi", ".mov", ".webm"},
        )

        for index, data in enumerate(MODULES, start=1):
            module, created = Module.objects.update_or_create(
                slug=slugify(data["titre"]),
                defaults={
                    "titre": data["titre"],
                    "resume": data["resume"],
                    "contenu": data["contenu"],
                    "niveau": data["niveau"],
                    "ordre": index,
                    "est_publie": True,
                    "est_ouvert": True,
                    "image_couverture": _random_file(cover_files),
                    "video": _random_file(video_files),
                },
            )
            module.illustrations.all().delete()
            if illustration_files:
                count = min(secrets.randbelow(2) + 1, len(illustration_files))
                selected = secrets.SystemRandom().sample(illustration_files, k=count)
                IllustrationModule.objects.bulk_create(
                    [
                        IllustrationModule(
                            module=module,
                            image=image_path,
                            legende=f"Sary fanazavana — {module.titre}",
                            ordre=order,
                        )
                        for order, image_path in enumerate(selected, start=1)
                    ]
                )

            quiz, _ = Quiz.objects.update_or_create(
                module=module,
                defaults={
                    "titre": f"Fanadinana — {data['titre']}",
                    "score_de_reussite": 60,
                    "nombre_questions": len(data["questions"]),
                    "correction_automatique": True,
                },
            )

            for question_order, (text, choices, correct_index) in enumerate(data["questions"], start=1):
                question, _ = Question.objects.update_or_create(
                    quiz=quiz,
                    ordre=question_order,
                    defaults={
                        "texte": text,
                        "type_question": Question.TypeQuestion.CHOIX_UNIQUE,
                        "points": 1,
                        "explication": "Jereo tsara ny votoatin'ny lesona.",
                    },
                )
                question.choix.all().delete()
                Choix.objects.bulk_create(
                    [
                        Choix(
                            question=question,
                            texte=choice,
                            est_correct=(choice_index == correct_index),
                        )
                        for choice_index, choice in enumerate(choices)
                    ]
                )

            if created:
                for user in moderators:
                    notifier(
                        user,
                        Notification.Type.NOUVEAU_MODULE,
                        "Misy fiofanana vaovao",
                        f"Efa azo ianarana ny module « {module.titre} ».",
                        f"/formation/modules/{module.uuid}/",
                    )

        self.stdout.write(self.style.SUCCESS("Formations sy quiz seedés avec succès."))
