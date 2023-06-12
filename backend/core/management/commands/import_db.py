import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipe.models import IngredientModel

main_dir = Path(__file__).parent.parent.parent.parent.parent

dict_model = {
    "ingredient": IngredientModel,
}


class Command(BaseCommand):
    help = 'Importing data into a database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-m',
            '--model',
            type=str,
            help='Выберете модель интеграции',
            choices=("ingredient", ),
            default="ingredient"
        )
        parser.add_argument(
            '-r',
            '--read',
            type=str,
            help='Database path (via /)',
            default="data/ingredients.csv",
        )

    def handle(self, *args, **options):

        def _write_bd_model():
            """Запись экз. моделей в базу данных."""
            with open(path_db) as file:
                file = csv.DictReader(file, delimiter=",")
                for dict_field in file:
                    inst_model = model(**dict_field)
                    list_model.append(inst_model)
            model.objects.bulk_create(list_model)

        list_dir = options['read'].split("/")
        model = dict_model[options['model']]
        path_db = Path(main_dir, *list_dir)
        list_model = []
        if not IngredientModel.objects.filter(id=1):
            inst_model = model(name="Какой-то ингредиент", measurement_unit="Что-то")
            list_model.append(inst_model)
        _write_bd_model()
        self.stdout.write("Ингредиенты интегрированны!")
