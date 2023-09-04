# import os
# import requests
# import random
# import string
# import webcolors
# import concurrent.futures

# # Define the API endpoint URLs
# api_url = "http://127.0.0.1:8000/products/"
# sku_url = "http://127.0.0.1:8000/products/sku?sku_id="

# valid_color_names = list(webcolors.CSS3_HEX_TO_NAMES.values())


# # Function to generate random string
# def random_string(length):
#     letters = string.ascii_letters
#     return "".join(random.choice(letters) for _ in range(length))


# # Function to generate random product data
# def generate_random_product():
#     random_color_name = random.choice(valid_color_names)

#     # Convert the color name to its hex representation
#     color_hex = webcolors.name_to_hex(random_color_name)

#     product_name = f"FruBay product title {random.randint(1, 100)}"
#     product_description = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
#     categories = ["fea6ed2843e9a71b12e6e683ef4ec596"]  # Replace with your category ID

#     return {
#         "product_name": product_name,
#         "product_description": product_description,
#         "color": random_color_name,
#         "color_hex": color_hex,
#         "categories": categories,
#     }


# # Function to send a POST request
# def send_post_request(url, data):
#     try:
#         response = requests.post(url, json=data)

#         # Check if the request was successful (status code 200)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             print("Request failed with status code:", response.status_code)
#             return None

#     except requests.exceptions.RequestException as e:
#         print("An error occurred:", e)
#         return None


# # Function to download an image with product-specific text
# def download_image(product_name, color, image_path):
#     placeholder_url = (
#         f"https://placehold.co/1080x1440/{color}/white/png?text={product_name}"
#     )
#     response = requests.get(placeholder_url)

#     if response.status_code == 200:
#         with open(image_path, "wb") as f:
#             f.write(response.content)
#         return True
#     else:
#         print(f"Failed to download image for product: {product_name}")
#         return False


# # Function to upload images
# def upload_images(product_id, image_paths):
#     upload_url = api_url + "images/?product_id=" + product_id

#     files = []
#     for image_path in image_paths:
#         files.append(("images", (image_path, open(image_path, "rb"), "image/jpeg")))

#     try:
#         response = requests.post(upload_url, files=files)
#         if response.status_code == 200:
#             print(f"Images uploaded for product: {product_id}")
#         else:
#             print("Failed to upload images for product:", product_id)
#     finally:
#         # Delete temporary image files
#         for image_path in image_paths:
#             pass
#             # os.remove(image_path)


# def create_product_variations(product_id, variations_data):
#     variation_url = api_url + "variation"

#     for variation_data in variations_data:
#         variation_data["product_id"] = product_id
#         response = send_post_request(variation_url, variation_data)
#         if response:
#             print(
#                 f"Variation added for product {product_id}: {variation_data.get('variation_name')}"
#             )


# # Create a temporary directory to store downloaded images
# temp_dir = "temp_images"
# if not os.path.exists(temp_dir):
#     os.makedirs(temp_dir)


# # Create 10 products
# def add_products_and_details():
#     # Generate and post the initial product to /products/ to get SKU ID
#     response_data = send_post_request(api_url, generate_random_product())
#     if response_data:
#         sku_id = response_data.get("sku_id")
#         print(f"Product added with SKU ID: {sku_id}")

#         # Download placeholder images with product-specific text
#         temp_image_paths = []
#         for i in range(4):
#             image_name = f"{sku_id}_{i}.jpg"
#             image_path = os.path.join(temp_dir, image_name)
#             if download_image(
#                 response_data.get("product_name"),
#                 response_data.get("color"),
#                 image_path,
#             ):
#                 temp_image_paths.append(image_path)

#         # Upload the downloaded images
#         upload_images(response_data.get("product_id"), temp_image_paths)

#         # Add variations to the product
#         product_variations = [
#             {
#                 "variation_name": "Select Size",
#                 "variation_items": [
#                     {
#                         "variation_item_name": "XS",
#                         "stock": 1000,
#                         "regular_price": 1499,
#                         "sale_price": 799,
#                     },
#                     {
#                         "variation_item_name": "S",
#                         "stock": 1000,
#                         "regular_price": 1599,
#                         "sale_price": 899,
#                     },
#                     {
#                         "variation_item_name": "M",
#                         "stock": 1000,
#                         "regular_price": 1699,
#                         "sale_price": 999,
#                     },
#                     {
#                         "variation_item_name": "L",
#                         "stock": 1000,
#                         "regular_price": 1799,
#                         "sale_price": 1099,
#                     },
#                 ],
#             }
#             # You can add more variations as needed
#         ]

#         create_product_variations(response_data.get("product_id"), product_variations)

#         # Add "Size & Fit" product details
#         size_fit_detail_data = {
#             "heading": "Size & Fit",
#             "product_id": response_data.get("product_id"),
#         }
#         size_fit_detail_response = send_post_request(
#             api_url + response_data.get("product_id") + "/details/",
#             size_fit_detail_data,
#         )
#         if size_fit_detail_response:
#             print(
#                 f"'Size & Fit' product detail added with ID: {size_fit_detail_response.get('detail_id')}"
#             )

#         # Add "Size & Fit" bullet points
#         size_fit_bullet_points_data = [
#             {"point": "The model (height 6') is wearing a size XL"}
#         ]
#         size_fit_bullet_points_response = send_post_request(
#             api_url
#             + "details/"
#             + size_fit_detail_response.get("detail_id")
#             + "/bulletpoints/",
#             size_fit_bullet_points_data,
#         )
#         if size_fit_bullet_points_response:
#             print(
#                 f"'Size & Fit' Bullet points added with IDs: {[bp.get('bullet_id') for bp in size_fit_bullet_points_response]}"
#             )

#         # Add "Material & Care" product details
#         material_care_detail_data = {
#             "heading": "Material & Care",
#             "product_id": response_data.get("product_id"),
#         }
#         material_care_detail_response = send_post_request(
#             api_url + response_data.get("product_id") + "/details/",
#             material_care_detail_data,
#         )
#         if material_care_detail_response:
#             print(
#                 f"'Material & Care' product detail added with ID: {material_care_detail_response.get('detail_id')}"
#             )

#         # Add "Material & Care" bullet points
#         material_care_bullet_points_data = [
#             {"point": "100% cotton"},
#             {"point": "Machine-wash"},
#         ]
#         material_care_bullet_points_response = send_post_request(
#             api_url
#             + "details/"
#             + material_care_detail_response.get("detail_id")
#             + "/bulletpoints/",
#             material_care_bullet_points_data,
#         )
#         if material_care_bullet_points_response:
#             print(
#                 f"'Material & Care' Bullet points added with IDs: {[bp.get('bullet_id') for bp in material_care_bullet_points_response]}"
#             )

#         for i in range(2):
#             response_data = send_post_request(
#                 sku_url + sku_id, generate_random_product()
#             )
#             if response_data:
#                 sku_id = response_data.get("sku_id")
#                 print(f"Product added with SKU ID: {sku_id}")

#                 # Download placeholder images with product-specific text
#                 temp_image_paths = []
#                 for i in range(4):
#                     image_name = f"{sku_id}_{i}.jpg"
#                     image_path = os.path.join(temp_dir, image_name)
#                     if download_image(
#                         response_data.get("product_name"),
#                         response_data.get("color"),
#                         image_path,
#                     ):
#                         temp_image_paths.append(image_path)

#                 # Upload the downloaded images
#                 upload_images(response_data.get("product_id"), temp_image_paths)

#                 # Add variations to the product
#                 product_variations = [
#                     {
#                         "variation_name": "SELECT SIZE",
#                         "variation_items": [
#                             {
#                                 "variation_item_name": "XS",
#                                 "stock": 1000,
#                                 "regular_price": 1499,
#                                 "sale_price": 799,
#                             },
#                             {
#                                 "variation_item_name": "S",
#                                 "stock": 1000,
#                                 "regular_price": 1599,
#                                 "sale_price": 899,
#                             },
#                             {
#                                 "variation_item_name": "M",
#                                 "stock": 1000,
#                                 "regular_price": 1699,
#                                 "sale_price": 999,
#                             },
#                             {
#                                 "variation_item_name": "L",
#                                 "stock": 1000,
#                                 "regular_price": 1799,
#                                 "sale_price": 1099,
#                             },
#                         ],
#                     }
#                     # You can add more variations as needed
#                 ]

#                 create_product_variations(
#                     response_data.get("product_id"), product_variations
#                 )

#                 # Add "Size & Fit" product details
#                 size_fit_detail_data = {
#                     "heading": "Size & Fit",
#                     "product_id": response_data.get("product_id"),
#                 }
#                 size_fit_detail_response = send_post_request(
#                     api_url + response_data.get("product_id") + "/details/",
#                     size_fit_detail_data,
#                 )
#                 if size_fit_detail_response:
#                     print(
#                         f"'Size & Fit' product detail added with ID: {size_fit_detail_response.get('detail_id')}"
#                     )

#                 # Add "Size & Fit" bullet points
#                 size_fit_bullet_points_data = [
#                     {"point": "The model (height 6') is wearing a size XL"}
#                 ]
#                 size_fit_bullet_points_response = send_post_request(
#                     api_url
#                     + "details/"
#                     + size_fit_detail_response.get("detail_id")
#                     + "/bulletpoints/",
#                     size_fit_bullet_points_data,
#                 )
#                 if size_fit_bullet_points_response:
#                     print(
#                         f"'Size & Fit' Bullet points added with IDs: {[bp.get('bullet_id') for bp in size_fit_bullet_points_response]}"
#                     )

#                 # Add "Material & Care" product details
#                 material_care_detail_data = {
#                     "heading": "Material & Care",
#                     "product_id": response_data.get("product_id"),
#                 }
#                 material_care_detail_response = send_post_request(
#                     api_url + response_data.get("product_id") + "/details/",
#                     material_care_detail_data,
#                 )
#                 if material_care_detail_response:
#                     print(
#                         f"'Material & Care' product detail added with ID: {material_care_detail_response.get('detail_id')}"
#                     )

#                 # Add "Material & Care" bullet points
#                 material_care_bullet_points_data = [
#                     {"point": "100% cotton"},
#                     {"point": "Machine-wash"},
#                 ]
#                 material_care_bullet_points_response = send_post_request(
#                     api_url
#                     + "details/"
#                     + material_care_detail_response.get("detail_id")
#                     + "/bulletpoints/",
#                     material_care_bullet_points_data,
#                 )
#                 if material_care_bullet_points_response:
#                     print(
#                         f"'Material & Care' Bullet points added with IDs: {[bp.get('bullet_id') for bp in material_care_bullet_points_response]}"
#                     )


# # Create a thread pool to run the function in parallel
# with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#     # Submit the function for execution 10 times (for 10 iterations)
#     futures = [executor.submit(add_products_and_details) for _ in range(100)]

# # Remove the temporary directory
# for image_path in os.listdir(temp_dir):
#     os.remove(os.path.join(temp_dir, image_path))
# os.rmdir(temp_dir)
