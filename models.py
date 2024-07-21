from sqlalchemy import Boolean, Column, Integer, String,Float, ForeignKey,DateTime,func, JSON
from database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(50),nullable=False)
    lastName = Column(String(50),nullable=False)
    mobile = Column(String(15),unique=True)
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


#billing 
class BillingDetails(Base):
    __tablename__ = "billing_details"   
    id = Column(Integer, primary_key=True)
    amount=Column(Float)
    discount=Column(Float)
    tax=Column(Float)
    total_amount=Column(Float)
    currency = Column(String(15)) 
    order_type = Column(String(100)) 
    subscription_type = Column(String(100)) 
    description = Column(String(100)) 
    status = Column(String(100))
    invoice_number=Column(String(100))
    is_offer=Column(Boolean)
    charge_id = Column(String(100), nullable=True) #FK
    refund_id = Column(String(100), nullable=True) 
    user_id = Column(Integer, nullable=False)  #FK
    initiated_on = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    authorized_on = Column(DateTime(timezone=True), default=func.now(), nullable=True)
    failed_on = Column(DateTime(timezone=True), nullable=True)
    paid_on = Column(DateTime(timezone=True), nullable=True)
    canceled_on = Column(DateTime(timezone=True), nullable=True)
    refunded_on = Column(DateTime(timezone=True), nullable=True)



#charge 

class Charge(Base):
    __tablename__ = 'charges'

    id = Column(String(15), primary_key=True)
    object = Column(String(50))
    live_mode = Column(Boolean)
    customer_initiated = Column(Boolean)
    api_version = Column(String(50))
    method = Column(String(50))
    status = Column(String(50))
    amount = Column(Integer)
    currency = Column(String(50))
    threeDSecure = Column(Boolean)
    card_threeDSecure = Column(Boolean)
    save_card = Column(Boolean)
    product = Column(String(50))
    reference = Column(JSON)
    response = Column(JSON)
    card_security = Column(JSON)
    security = Column(JSON)
    acquirer = Column(JSON)
    gateway = Column(JSON)
    card = Column(JSON)
    receipt = Column(JSON)
    customer = Column(JSON)
    merchant = Column(JSON)
    source = Column(JSON)
