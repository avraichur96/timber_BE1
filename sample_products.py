# Sample Django ORM queries to create product data
# Run these commands in Django shell: python manage.py shell

from apps.organizations.models import Product

## Create [1] Creategestimate_header = EstimateHeader.objects.get(id=some_uuid)
# [2] Create Chairs
Product.objects.create(
    name="Wooden Office Chair",
    description="Comfortable office chair with wooden frame and cushioned seat"
)

Product.objects.create(
    name="Dining Chair Set",
    description="Set of 4 wooden dining chairs with ergonomic design"
)

Product.objects.create(
    name="Recliner Chair",
    description="Luxurious reclining chair with leather upholstery"
)

# [3] Create Sofas
Product.objects.create(
    name="Three-Seater Sofa",
    description="Spacious wooden frame sofa with fabric upholstery"
)

Product.objects.create(
    name="L-Shaped Sofa",
    description="Modern L-shaped sofa perfect for living rooms"
)

Product.objects.create(
    name="Sofa Cum Bed",
    description="Multi-functional sofa that can be converted into a bed"
)

# [4] Create Drawers
Product.objects.create(
    name="Bedside Drawer",
    description="Compact wooden drawer for bedroom storage"
)

Product.objects.create(
    name="Office Drawer Cabinet",
    description="Large drawer cabinet with multiple compartments"
)

Product.objects.create(
    name="Kitchen Drawer Set",
    description="Set of kitchen drawers with smooth sliding mechanism"
)

# [5] Create Tables
Product.objects.create(
    name="Dining Table",
    description="Large wooden dining table for 6-8 people"
)

Product.objects.create(
    name="Office Desk",
    description="Spacious office desk with drawer space"
)

Product.objects.create(
    name="Coffee Table",
    description="Elegant coffee table for living room"
)

Product.objects.create(
    name="Study Table",
    description="Compact study table for students"
)

Product.objects.create(
    name="Conference Table",
    description="Large conference table for meeting rooms"
)

print("Sample products created successfully!")
print(f"Total products created: {Product.objects.count()}")

# [6] List all created products
for product in Product.objects.all():
    print(f"ID: {product.id}, Name: {product.name}")
