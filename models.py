from secrets import token_hex
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Date,
    Double,
    Table,
)
from database import Base
from sqlalchemy.orm import relationship


def generate_uuid():
    return token_hex(16)


product_category_association = Table(
    "product_category_association",
    Base.metadata,
    Column("product_id", String, ForeignKey("products.product_id")),
    Column("category_id", String, ForeignKey("categories.category_id")),
)


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
    role_id = Column(String, ForeignKey("roles.role_id"), default="1", nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    otp_secret = Column(String, nullable=False)
    otp_verified = Column(Boolean, default=False)

    addresses = relationship("Address", back_populates="user")
    cart = relationship("Cart", back_populates="user")


class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))

    name = Column(String, nullable=False)
    phone = Column(Integer, nullable=False)
    pincode = Column(Integer, nullable=False)
    state = Column(String, nullable=False)
    locality = Column(String, nullable=False)
    town = Column(Integer, nullable=False)
    city = Column(Integer, nullable=False)
    type = Column(Boolean, nullable=False)
    is_default = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="addresses")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    category_name = Column(String, nullable=False)
    category_description = Column(String)
    parent_category_id = Column(String, ForeignKey("categories.category_id"))

    parent_category = relationship(
        "Category", remote_side=[category_id], overlaps="sub_categories"
    )
    sub_categories = relationship(
        "Category", remote_side=[parent_category_id], overlaps="parent_category"
    )
    products = relationship("Product", back_populates="category")

    products = relationship(
        "Product", secondary=product_category_association, back_populates="categories"
    )


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    product_name = Column(String, nullable=False)
    product_description = Column(String)
    regular_price = Column(Float, nullable=False)
    sale_price = Column(Float)
    stock_quantity = Column(Integer, nullable=False)

    product_details = relationship("ProductDetail", back_populates="product")
    product_images = relationship("ProductImage", back_populates="product")
    carts = relationship("Cart", back_populates="product")

    categories = relationship(
        "Category", secondary=product_category_association, back_populates="products"
    )


class ProductDetail(Base):
    __tablename__ = "product_details"

    detail_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    product_id = Column(String, ForeignKey("products.product_id"))
    heading = Column(String, nullable=False)
    bullet_points = relationship("BulletPoint", back_populates="product_detail")
    product = relationship("Product", back_populates="product_details")


class BulletPoint(Base):
    __tablename__ = "bullet_points"

    bullet_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    detail_id = Column(String, ForeignKey("product_details.detail_id"))
    point = Column(String, nullable=False)
    product_detail = relationship("ProductDetail", back_populates="bullet_points")


class ProductImage(Base):
    __tablename__ = "product_images"

    image_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    product_id = Column(String, ForeignKey("products.product_id"))
    small_image_url = Column(String)  # New column for the small image URL
    medium_image_url = Column(String)  # New column for the medium image URL
    large_image_url = Column(String)  # New column for the large image URL
    product = relationship("Product", back_populates="product_images")


class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    quantity = Column(Integer, nullable=False)
    product_id = Column(String, ForeignKey("products.product_id"))
    user_id = Column(String, ForeignKey("users.user_id"))

    product = relationship("Product", back_populates="carts")
    user = relationship("User", back_populates="cart")



# App


class Page(Base):
    __tablename__ = "pages"
    page_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    page_title = Column(String, nullable=False)
    widgets = relationship("Widget", back_populates="page")


class Widget(Base):
    __tablename__ = "widgets"

    widget_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    widget_title = Column(String, nullable=False)
    widget_type = Column(String, nullable=False)
    rank = Column(Integer, autoincrement=True, nullable=False)
    page_id = Column(String, ForeignKey("pages.page_id"))
    has_header = Column(Boolean, nullable=False, default=True)
    has_background = Column(Boolean, nullable=False, default=False)
    header = Column(String)
    background = Column(String)
    items_height = Column(Double, nullable=False)
    items_width = Column(Double, nullable=False)
    page = relationship("Page", back_populates="widgets")
    widget_items = relationship("WidgetItem", back_populates="widget")


class WidgetItem(Base):
    __tablename__ = "widgetitems"

    widget_item_id = Column(String, primary_key=True, default=generate_uuid, index=True)
    image_url = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rank = Column(Integer, autoincrement=True, nullable=False)
    widget_id = Column(String, ForeignKey("widgets.widget_id"))
    widget = relationship("Widget", back_populates="widget_items")
