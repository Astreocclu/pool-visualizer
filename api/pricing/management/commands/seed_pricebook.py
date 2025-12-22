from django.core.management.base import BaseCommand
from api.pricing.models import Vertical, PriceBookCategory, PriceBookItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the price book with default values from config'

    def handle(self, *args, **options):
        self.stdout.write('Seeding price book...')

        # Create Pools vertical
        pools, _ = Vertical.objects.update_or_create(
            id='pools',
            defaults={
                'name': 'pools',
                'display_name': 'Swimming Pools',
                'calculation_unit': 'project',
            }
        )

        # Pool Sizes category
        sizes_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='pool_sizes',
            defaults={'name': 'Pool Sizes', 'sort_order': 1}
        )

        pool_sizes = [
            ('starter', 'Starter (12x24)', Decimal('50000')),
            ('classic', 'Classic (15x30)', Decimal('65000')),
            ('family', 'Family (16x36)', Decimal('75000')),
            ('resort', 'Resort (18x40)', Decimal('95000')),
        ]

        for item_id, name, price in pool_sizes:
            PriceBookItem.objects.update_or_create(
                category=sizes_cat,
                item_id=item_id,
                defaults={'name': name, 'base_price': price}
            )

        # Pool Shapes category
        shapes_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='pool_shapes',
            defaults={'name': 'Pool Shapes', 'sort_order': 2}
        )

        pool_shapes = [
            ('rectangle', 'Rectangle', Decimal('1.00')),
            ('roman', 'Roman', Decimal('1.05')),
            ('grecian', 'Grecian', Decimal('1.05')),
            ('kidney', 'Kidney', Decimal('1.10')),
            ('freeform', 'Freeform', Decimal('1.15')),
            ('lazy_l', 'Lazy L', Decimal('1.10')),
            ('oval', 'Oval', Decimal('1.05')),
        ]

        for item_id, name, multiplier in pool_shapes:
            PriceBookItem.objects.update_or_create(
                category=shapes_cat,
                item_id=item_id,
                defaults={'name': name, 'price_multiplier': multiplier}
            )

        # Interior Finishes category
        finishes_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='interior_finishes',
            defaults={'name': 'Interior Finishes', 'sort_order': 3}
        )

        finishes = [
            ('white_plaster', 'White Plaster', Decimal('0')),
            ('pebble_blue', 'Pebble Tec - Blue', Decimal('8000')),
            ('pebble_midnight', 'Pebble Tec - Midnight', Decimal('9000')),
            ('quartz_blue', 'Quartz - Ocean Blue', Decimal('6000')),
            ('quartz_aqua', 'Quartz - Caribbean', Decimal('6000')),
            ('glass_tile', 'Glass Tile', Decimal('15000')),
        ]

        for item_id, name, price in finishes:
            PriceBookItem.objects.update_or_create(
                category=finishes_cat,
                item_id=item_id,
                defaults={'name': name, 'base_price': price}
            )

        # Deck Materials category
        deck_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='deck_materials',
            defaults={'name': 'Deck Materials', 'sort_order': 4}
        )

        deck_materials = [
            ('travertine', 'Travertine', Decimal('18')),
            ('pavers', 'Pavers', Decimal('14')),
            ('brushed_concrete', 'Brushed Concrete', Decimal('8')),
            ('stamped_concrete', 'Stamped Concrete', Decimal('12')),
            ('flagstone', 'Flagstone', Decimal('22')),
            ('wood', 'Wood Deck', Decimal('25')),
        ]

        for item_id, name, price_per_sqft in deck_materials:
            PriceBookItem.objects.update_or_create(
                category=deck_cat,
                item_id=item_id,
                defaults={
                    'name': name,
                    'price_per_unit': price_per_sqft,
                    'unit_type': 'sqft'
                }
            )

        # Water Features category
        water_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='water_features',
            defaults={'name': 'Water Features', 'sort_order': 5}
        )

        water_features = [
            ('rock_waterfall', 'Rock Waterfall', Decimal('8000')),
            ('bubblers', 'Bubblers / Fountain Jets', Decimal('2500')),
            ('scuppers', 'Scuppers', Decimal('4500')),
            ('fire_bowls', 'Fire Bowls', Decimal('3500')),
            ('deck_jets', 'Deck Jets', Decimal('3000')),
        ]

        for item_id, name, price in water_features:
            PriceBookItem.objects.update_or_create(
                category=water_cat,
                item_id=item_id,
                defaults={'name': name, 'base_price': price}
            )

        # Built-In Features category
        builtin_cat, _ = PriceBookCategory.objects.update_or_create(
            vertical=pools,
            slug='built_in_features',
            defaults={'name': 'Built-In Features', 'sort_order': 6}
        )

        built_in_features = [
            ('tanning_ledge', 'Tanning Ledge (Baja Shelf)', Decimal('4500')),
            ('attached_spa', 'Attached Spa (Spillover)', Decimal('18000')),
        ]

        for item_id, name, price in built_in_features:
            PriceBookItem.objects.update_or_create(
                category=builtin_cat,
                item_id=item_id,
                defaults={'name': name, 'base_price': price}
            )

        self.stdout.write(self.style.SUCCESS('Price book seeded successfully!'))
        self.stdout.write(f'  - Created vertical: {pools.display_name}')
        self.stdout.write(f'  - Categories: {PriceBookCategory.objects.filter(vertical=pools).count()}')
        self.stdout.write(f'  - Items: {PriceBookItem.objects.filter(category__vertical=pools).count()}')
