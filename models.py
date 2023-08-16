from secrets import token_hex
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float
from sqlalchemy.orm import relationship
from database import Base

def generate_uuid():
    return token_hex(16)

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    role_title = Column(String, nullable=False)
    role_desc = Column(String, nullable=False)

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(Integer, nullable=False)
    role_id = Column(String, ForeignKey('roles.role_id'), default="1")
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    otp_secret = Column(String)
    otp_verified = Column(Boolean, default=False)

    primary_address_id = Column(String, ForeignKey('addresses.address_id'))
    primary_address = relationship("Address", foreign_keys=[primary_address_id])

    addresses = relationship("Address", back_populates="user")
    wishlists = relationship("Wishlist", back_populates="user")
    notifications = relationship("Notification", backref="user")

class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    user = relationship("User", back_populates="addresses")
    street = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    category_name = Column(String, nullable=False)
    category_description = Column(String)
    parent_category_id = Column(String, ForeignKey('categories.category_id'))
    parent_category = relationship("Category", remote_side=[category_id], backref="sub_categories")

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    product_name = Column(String, nullable=False)
    product_description = Column(String)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    category_id = Column(String, ForeignKey('categories.category_id'))
    category = relationship("Category", backref="products")

class ProductImage(Base):
    __tablename__ = "product_images"

    image_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    product_id = Column(String, ForeignKey('products.product_id'))
    image_type = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    product = relationship("Product", backref="images")

class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    user = relationship("User", backref="carts")

class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    cart_id = Column(String, ForeignKey('carts.cart_id'))
    product_id = Column(String, ForeignKey('products.product_id'))
    quantity = Column(Integer, nullable=False)
    product = relationship("Product")

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    user = relationship("User", backref="orders")
    order_date = Column(Date)

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    order_id = Column(String, ForeignKey('orders.order_id'))
    product_id = Column(String, ForeignKey('products.product_id'))
    quantity = Column(Integer, nullable=False)
    product = relationship("Product")

class Wishlist(Base):
    __tablename__ = "wishlists"

    wishlist_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    user = relationship("User", back_populates="wishlists")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    wishlist_item_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    wishlist_id = Column(String, ForeignKey('wishlists.wishlist_id'))
    product_id = Column(String, ForeignKey('products.product_id'))
    product = relationship("Product")

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    user = relationship("User", backref="notifications")
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(Date)

# Add more tables and columns as needed for your e-commerce platform.
