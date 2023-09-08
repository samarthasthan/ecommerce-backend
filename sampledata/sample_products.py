import os
import requests
import random
import string
import webcolors
import concurrent.futures

# Define the API endpoint URLs
api_url = "http://127.0.0.1:8000/product"
sku_url = "http://127.0.0.1:8000/product/sku?sku_id="

valid_color_names = list(webcolors.CSS3_HEX_TO_NAMES.values())

category_ids = [
    "1b88ac10dc6a173604cfbee44c48e5eb",
    "39a0003d8bf33194a028a43c0004f84f",
    "fe2bf24e07dd9eeba9c4669339910845",
    "3fc34808fe71bdec5d3efadfd658430a",
    "e002abf1a3eec335cd14cd289f955bf0",
    "f38a8bb08b3fc9ef6ada5b0e5f23bc97",
    "24a781fe1c2a510755b31221e0d698af",
    "54ff9f4aee91fcb162fdcb2a05673477",
    "ca482b1daab56b888e4ac78feeb1c755",
    "250de26430944ddb470a593db7cceb13",
    "1ebdcc662eeff9f14612c74eb63a847c",
    "21a93cd330942dbf0a2c06595b06d8a2",
    "7cbe1739dfed3d6a624eee4e76ee3c21",
    "63bfb5e55cfef9f2abd63c9f4190659a",
    "5213fffef863cb94f358abe875c58640",
    "a65e7ddb5d559bcaaa2df81b498b40b0",
    "c1033ba46b4c06324027f0707d399831",
    "23590f8506bd72266a44b17bbfdf2102",
    "a24b289bb8992579c3a9f17d6f74e47a",
    "1167a70de086753e4310f3af2214d673",
    "ad5d96db7e6b38a68d1cf3b060c5d8d3",
    "2a62ed3c2d3897e80af74a9449875c0b",
    "7fe1f93f59ae2d99252eaf388850618b",
    "a3a6a13f9c4467d86aa28ab87ca4d78b",
    "e874bee84ba3408bcf0679733aed2f9d",
    "ea8534cff48c17b9acd2ca84901d6db6",
    "3f155d62522851fa4a4c7dc91bfb7c78",
    "0ff0dab9f70bb560c8e40b16fd2a3bec",
    "a603e00c8e58e8fbe5eb174db271fbec",
    "8517048c52c66b0bcad74af633e7aa5d",
    "6c5867d85058dd5d591463b8fb2488c8",
    "9d6aa5d0b0ba73225164e161b4df2bda",
    "b4a2dc892f765248f3c2aeb8688b57af",
    "9d93c6d3810b7830c741c246c1c63a93",
    "42d0e339c414c60047bb155b982cc3cc",
    "ba5c2020b9bc62c61f7a167a8ea23b82",
    "bf997d89afbbd7073190f79d65f4a534",
    "6c949c86dddba203c011e057e0d392b8",
    "6a7771d53f8887974f907cf837dcb41f",
    "911da14216cfbc4a79a57fcd7a05ebc5",
    "5d74ff1ffd172c205946b8867247517c",
    "41b581ad85c92ddfba3fb1227af6283d",
    "e97728d555c1c2a96ac673b7baa95de6",
    "af4fa8d2bc4eb07d729c5a58d71e5e0c",
    "1c95507645718df13d6cb329fc69f6f4",
    "3c7f981c21e8f828c3298fa50a8edfbe",
    "a95464d4003ca5b03746d7f0361df0cc",
    "ff1efb45b942f2cb5a27129b44cdd5a9",
    "31789eff22f3da47ca514683b7008ad6",
    "e34bb01c4b7172f89157db59b062e2de",
    "2b189c2399349d2e45ac3cb5626c14b9",
    "9e6524b15aa9fedf7ea04db0eff2ad32",
    "f6715e137bb8d340b0461c660ad7810d",
    "88eba46d3be065707a6a9d95d5e36b53",
    "8bd2e544126669e037a8c096c18fce7d",
    "1dad896b72b70cbfd4ea9c0f0d4794df",
    "331bdea3d9914094e4cac62c4cbdfb84",
    "92d60e987644cf0848fb2c1541967d2e",
    "01f4f7c2ecf08fc22c9e0b4c7824f8a6",
    "b238b096764590ab2af2560c46c3631e",
]


# Function to generate random string
def random_string(length):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(length))


# Function to generate random product data
def generate_random_product():
    list = []
    for i in range(random.randint(1, 5)):
        list.append(random.choice(category_ids))
    random_color_name = random.choice(valid_color_names)

    # Convert the color name to its hex representation
    color_hex = webcolors.name_to_hex(random_color_name)

    product_name = f"FruBay product title {random.randint(1, 100)}"
    product_description = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
    categories = list  # Replace with your category ID

    return {
        "product_name": product_name,
        "product_description": product_description,
        "color": random_color_name,
        "color_hex": color_hex,
        "categories": categories,
    }


# Function to send a POST request
def send_post_request(url, data):
    try:
        response = requests.post(url, json=data)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json()
        else:
            print("Request failed with status code:", response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


# Function to download an image with product-specific text
def download_image(product_name, color, image_path):
    placeholder_url = (
        f"https://placehold.co/1080x1440/{color}/white/png?text={product_name}"
    )
    response = requests.get(placeholder_url)

    if response.status_code == 200:
        with open(image_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download image for product: {product_name}")
        return False


# Function to upload images
def upload_images(product_id, image_paths):
    upload_url = api_url + "/images?product_id=" + product_id

    files = []
    for image_path in image_paths:
        files.append(("images", (image_path, open(image_path, "rb"), "image/jpeg")))

    try:
        response = requests.post(upload_url, files=files)
        if response.status_code == 200:
            print(f"Images uploaded for product: {product_id}")
        else:
            print("Failed to upload images for product:", product_id)
    finally:
        # Delete temporary image files
        for image_path in image_paths:
            pass
            # os.remove(image_path)


def create_product_variations(product_id, variations_data):
    variation_url = api_url + "/variation"

    for variation_data in variations_data:
        variation_data["product_id"] = product_id
        response = send_post_request(variation_url, variation_data)
        if response:
            print(
                f"Variation added for product {product_id}: {variation_data.get('variation_name')}"
            )


# Create a temporary directory to store downloaded images
temp_dir = "temp_images"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)


def add_products_and_details():
    # Generate and post the initial product to /products/ to get SKU ID
    response_data = send_post_request(api_url, generate_random_product())
    if response_data:
        sku_id = response_data.get("sku_id")
        print(f"Product added with SKU ID: {sku_id}")

        # Download placeholder images with product-specific text
        temp_image_paths = []
        for i in range(4):
            image_name = f"{sku_id}_{i}.jpg"
            image_path = os.path.join(temp_dir, image_name)
            if download_image(
                response_data.get("product_name"),
                response_data.get("color"),
                image_path,
            ):
                temp_image_paths.append(image_path)

        # Upload the downloaded images
        upload_images(response_data.get("product_id"), temp_image_paths)

        # Add variations to the product
        product_variations = [
            {
                "variation_name": "Size",
                "variation_items": [
                    {
                        "variation_item_name": str(random.randint(28, 50)),
                        "stock": 1000,
                        "regular_price": 1499,
                        "sale_price": 799,
                    },
                    {
                        "variation_item_name": str(random.randint(28, 50)),
                        "stock": 1000,
                        "regular_price": 1599,
                        "sale_price": 899,
                    },
                    {
                        "variation_item_name": str(random.randint(28, 50)),
                        "stock": 1000,
                        "regular_price": 1699,
                        "sale_price": 999,
                    },
                    {
                        "variation_item_name": str(random.randint(28, 50)),
                        "stock": 1000,
                        "regular_price": 1799,
                        "sale_price": 1099,
                    },
                ],
            }
            # You can add more variations as needed
        ]

        create_product_variations(response_data.get("product_id"), product_variations)

        # Add "Size & Fit" product details
        size_fit_detail_data = {
            "heading": "Size & Fit",
            "product_id": response_data.get("product_id"),
        }
        size_fit_detail_response = send_post_request(
            api_url + "/" + response_data.get("product_id") + "/details",
            size_fit_detail_data,
        )
        if size_fit_detail_response:
            print(
                f"'Size & Fit' product detail added with ID: {size_fit_detail_response.get('detail_id')}"
            )

        # Add "Size & Fit" bullet points
        size_fit_bullet_points_data = [
            {"point": "The model (height 6') is wearing a size XL"}
        ]
        size_fit_bullet_points_response = send_post_request(
            api_url
            + "/details/"
            + size_fit_detail_response.get("detail_id")
            + "/bulletpoints",
            size_fit_bullet_points_data,
        )
        if size_fit_bullet_points_response:
            print(
                f"'Size & Fit' Bullet points added with IDs: {[bp.get('bullet_id') for bp in size_fit_bullet_points_response]}"
            )

        # Add "Material & Care" product details
        material_care_detail_data = {
            "heading": "Material & Care",
            "product_id": response_data.get("product_id"),
        }
        material_care_detail_response = send_post_request(
            api_url +"/"+ response_data.get("product_id") + "/details",
            material_care_detail_data,
        )
        if material_care_detail_response:
            print(
                f"'Material & Care' product detail added with ID: {material_care_detail_response.get('detail_id')}"
            )

        # Add "Material & Care" bullet points
        material_care_bullet_points_data = [
            {"point": "100% cotton"},
            {"point": "Machine-wash"},
        ]
        material_care_bullet_points_response = send_post_request(
            api_url
            + "/details/"
            + material_care_detail_response.get("detail_id")
            + "/bulletpoints",
            material_care_bullet_points_data,
        )
        if material_care_bullet_points_response:
            print(
                f"'Material & Care' Bullet points added with IDs: {[bp.get('bullet_id') for bp in material_care_bullet_points_response]}"
            )

        for i in range(2):
            response_data = send_post_request(
                sku_url + sku_id, generate_random_product()
            )
            if response_data:
                sku_id = response_data.get("sku_id")
                print(f"Product added with SKU ID: {sku_id}")

                # Download placeholder images with product-specific text
                temp_image_paths = []
                for i in range(4):
                    image_name = f"{sku_id}_{i}.jpg"
                    image_path = os.path.join(temp_dir, image_name)
                    if download_image(
                        response_data.get("product_name"),
                        response_data.get("color"),
                        image_path,
                    ):
                        temp_image_paths.append(image_path)

                # Upload the downloaded images
                upload_images(response_data.get("product_id"), temp_image_paths)

                # Add variations to the product
                product_variations = [
                    {
                        "variation_name": "Size",
                        "variation_items": [
                            {
                                "variation_item_name": str(random.randint(28, 50)),
                                "stock": 1000,
                                "regular_price": 1499,
                                "sale_price": 799,
                            },
                            {
                                "variation_item_name": str(random.randint(28, 50)),
                                "stock": 1000,
                                "regular_price": 1599,
                                "sale_price": 899,
                            },
                            {
                                "variation_item_name": str(random.randint(28, 50)),
                                "stock": 1000,
                                "regular_price": 1699,
                                "sale_price": 999,
                            },
                            {
                                "variation_item_name": str(random.randint(28, 50)),
                                "stock": 1000,
                                "regular_price": 1799,
                                "sale_price": 1099,
                            },
                        ],
                    }
                    # You can add more variations as needed
                ]

                create_product_variations(
                    response_data.get("product_id"), product_variations
                )

                # Add "Size & Fit" product details
                size_fit_detail_data = {
                    "heading": "Size & Fit",
                    "product_id": response_data.get("product_id"),
                }
                size_fit_detail_response = send_post_request(
                    api_url +"/"+ response_data.get("product_id") + "/details",
                    size_fit_detail_data,
                )
                if size_fit_detail_response:
                    print(
                        f"'Size & Fit' product detail added with ID: {size_fit_detail_response.get('detail_id')}"
                    )

                # Add "Size & Fit" bullet points
                size_fit_bullet_points_data = [
                    {"point": "The model (height 6') is wearing a size XL"}
                ]
                size_fit_bullet_points_response = send_post_request(
                    api_url
                    + "/details/"
                    + size_fit_detail_response.get("detail_id")
                    + "/bulletpoints",
                    size_fit_bullet_points_data,
                )
                if size_fit_bullet_points_response:
                    print(
                        f"'Size & Fit' Bullet points added with IDs: {[bp.get('bullet_id') for bp in size_fit_bullet_points_response]}"
                    )

                # Add "Material & Care" product details
                material_care_detail_data = {
                    "heading": "Material & Care",
                    "product_id": response_data.get("product_id"),
                }
                material_care_detail_response = send_post_request(
                    api_url +"/"+ response_data.get("product_id") + "/details",
                    material_care_detail_data,
                )
                if material_care_detail_response:
                    print(
                        f"'Material & Care' product detail added with ID: {material_care_detail_response.get('detail_id')}"
                    )

                # Add "Material & Care" bullet points
                material_care_bullet_points_data = [
                    {"point": "100% cotton"},
                    {"point": "Machine-wash"},
                ]
                material_care_bullet_points_response = send_post_request(
                    api_url
                    + "/details/"
                    + material_care_detail_response.get("detail_id")
                    + "/bulletpoints",
                    material_care_bullet_points_data,
                )
                if material_care_bullet_points_response:
                    print(
                        f"'Material & Care' Bullet points added with IDs: {[bp.get('bullet_id') for bp in material_care_bullet_points_response]}"
                    )


print("How many times you wanna run this? - ")
n = int(input())
for i in range(n):
    print(f"\n\nRunning for ${i+1}th time....\n\n")
    add_products_and_details()
    print(f"\n\nExcuted for ${i+1}th time....\n\n")

# Remove the temporary directory
for image_path in os.listdir(temp_dir):
    os.remove(os.path.join(temp_dir, image_path))
os.rmdir(temp_dir)
