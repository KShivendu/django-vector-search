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

    # Add a field for autocomplete suggestions
    suggest = fields.CompletionField()

    class Index:
        name = "products"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Product
        # fields to include in the index:
        fields = [
            "description",
        ]

        # Ignore auto updating of the index when a model is saved/deleted
        # auto_refresh = False

    def prepare_suggest(self, instance: Product):
        # NOTE: The name 'suggest' matches the field name so that ES knows
        """Prepare data for autocomplete."""
        return [instance.name, instance.description]
