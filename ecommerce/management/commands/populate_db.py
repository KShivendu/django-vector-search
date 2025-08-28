from django.core.management.base import BaseCommand
from ecommerce.models import Product


class Command(BaseCommand):
    help = "Create sample products"

    def handle(self, *args, **options):
        # Create products
        for i in range(1, 6):
            Product.objects.get_or_create(
                name=f"Product {i}",
                description=f"Description for product {i}",
                price=10.0 * i,
            )

        self.stdout.write(self.style.SUCCESS("Sample data created successfully"))
