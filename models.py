from sqlalchemy import Boolean, Column, Integer, String,Float, ForeignKey,DateTime
from database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    posts = relationship("Post", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")


class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String(100))
    quantity = Column(Integer)
    price = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="purchases")
    #invoice = relationship("Invoice", uselist=False, back_populates="purchase")


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, unique=True)
    #purchase = relationship("Purchase", back_populates="invoice")
    sub_total =Column(Float)
    total = Column(Float)
    tax = Column(Float)
    customer_name = Column(String(50))
    customer_email = Column(String(50))