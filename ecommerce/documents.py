from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product


@registry.register_document
class ProductDocument(Document):
    # Define custom fields for better search
    name = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    price = fields.FloatField()

    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Product
        # fields to include in the index:
        fields = [
            'description',
        ]

        # Ignore auto updating of the index when a model is saved/deleted
        # auto_refresh = False


    def prepare_suggest(self, instance: Product):
        """Prepare data for autocomplete."""
        return {
            'input': [instance.name, instance.description],
            'weight': 10
        }
