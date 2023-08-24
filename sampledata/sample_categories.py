import subprocess

categories_data = [
    {
        "category_name": "Fashion",
        "subcategories": [
            "Clothing",
            "Shoes",
            "Accessories",
            "Jewelry",
            "Watches"
        ]
    },
    {
        "category_name": "Electronics",
        "subcategories": [
            "Computers and Laptops",
            "Mobile Phones and Tablets",
            "Cameras and Photography",
            "Audio and Headphones",
            "TVs and Home Theater"
        ]
    },
    {
        "category_name": "Home and Furniture",
        "subcategories": [
            "Furniture",
            "Home Decor",
            "Kitchen and Dining",
            "Bedding and Bath",
            "Appliances"
        ]
    },
    {
        "category_name": "Beauty and Personal Care",
        "subcategories": [
            "Skincare",
            "Makeup",
            "Haircare",
            "Fragrances",
            "Personal Care Appliances"
        ]
    },
    {
        "category_name": "Books and Stationery",
        "subcategories": [
            "Books",
            "E-books",
            "Stationery",
            "Office Supplies",
            "Art and Craft Supplies"
        ]
    },
    {
        "category_name": "Sports and Outdoors",
        "subcategories": [
            "Sports Equipment",
            "Activewear",
            "Outdoor Recreation",
            "Camping and Hiking",
            "Biking and Cycling"
        ]
    },
    {
        "category_name": "Toys and Games",
        "subcategories": [
            "Toys for Kids",
            "Board Games",
            "Puzzles",
            "Outdoor Play Equipment",
            "Action Figures"
        ]
    },
    {
        "category_name": "Health and Wellness",
        "subcategories": [
            "Vitamins and Supplements",
            "Fitness Equipment",
            "Wellness Products",
            "Medical Supplies",
            "Sports Nutrition"
        ]
    },
    {
        "category_name": "Automotive",
        "subcategories": [
            "Auto Parts",
            "Car Accessories",
            "Tools and Equipment",
            "Motorcycle Gear",
            "Car Electronics"
        ]
    },
    {
        "category_name": "Grocery and Food",
        "subcategories": [
            "Fresh Produce",
            "Pantry Staples",
            "Snacks and Beverages",
            "Gourmet Foods",
            "Organic and Specialty Foods"
        ]
    }
]

# Posting categories and subcategories using subprocess and curl
for category_data in categories_data:
    # Create category
    category_create_command = [
        'curl',
        '-X', 'POST',
        'http://127.0.0.1:8000/categories/',
        '-H', 'accept: application/json',
        '-H', 'Content-Type: application/json',
        '-d', f'{{"category_name": "{category_data["category_name"]}", "category_description": "{category_data["category_name"]}", "parent_category_id": "6abda60ac52bfdad4d281dc19eb378f9"}}'
    ]
    subprocess.run(category_create_command, stdout=subprocess.PIPE)
    
    # Get the created category's ID
    category_id_command = ['curl', '-s', 'http://127.0.0.1:8000/categories/']
    response = subprocess.run(category_id_command, stdout=subprocess.PIPE, text=True)
    category_id = [cat['category_id'] for cat in eval(response.stdout) if cat['category_name'] == category_data["category_name"]][0]
    
    # Create subcategories
    for subcategory_name in category_data["subcategories"]:
        subcategory_create_command = [
            'curl',
            '-X', 'POST',
            'http://127.0.0.1:8000/categories/',
            '-H', 'accept: application/json',
            '-H', 'Content-Type: application/json',
            '-d', f'{{"category_name": "{subcategory_name}", "category_description": "{subcategory_name}", "parent_category_id": "{category_id}"}}'
        ]
        subprocess.run(subcategory_create_command, stdout=subprocess.PIPE)

print("Categories and subcategories created successfully!")
