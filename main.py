from fastapi import FastAPI, HTTPException, Depends, status, Response
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime
from fpdf import FPDF
from fastapi.responses import FileResponse, StreamingResponse
from io import BytesIO





app = FastAPI()




models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    username: str
    email: str
 

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int


class PurchaseBase(BaseModel):
    item: str
    quantity: int
    price: float
    user_id: int


class InvoiceBase(BaseModel):
    purchase_id: int
    sub_total: float
    total: float
    tax: float
    customer_name: str 
    customer_email: str
    

class BillingDetails(BaseModel):
    id: int
    amount: float  
    discount: float 
    tax: float 
    total_amount: float
    currency: str 
    order_type: str 
    subscription_type: str 
    description: str 
    status: str 
    invoice_number: str 
    is_offer: bool 
    charge_id: str 
    refund_id: str
    user_id: int 
    initiated_on: datetime 
    authorized_on: datetime 
    failed_on: datetime
    paid_on: datetime 
    canceled_on: datetime
    refunded_on: datetime

class Charge(BaseModel):
    id: str
    object: str
    live_mode: bool
    customer_initiated: bool
    api_version: str
    method: str
    status: str
    amount: int
    currency: str
    threeDSecure: bool
    card_threeDSecure: bool
    save_card: bool
    product: str
    reference: dict
    response: dict
    card_security: dict
    security: dict
    acquirer: dict
    gateway: dict
    card: dict
    receipt: dict
    customer: dict
    merchant: dict
    source: dict





def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]



#Create charge
@app.post("/charges/", status_code=status.HTTP_201_CREATED)
async def create_charge(charge: Charge, db: db_dependency):
    db_charge = models.Charge(**charge.dict())
    db.add(db_charge)
    db.commit()
    db.refresh(db_charge) 


#Create billing 
@app.post("/billing/", status_code=status.HTTP_201_CREATED)
async def create_billing(billing: BillingDetails, db: db_dependency):
    db_billing = models.BillingDetails(**billing.dict())
    db.add(db_billing)
    db.commit()
    db.refresh(db_billing)
    return db_billing



#Dawnlaod the invoice  








#user CRUD operations


@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def createUser (user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()


@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def retrieveUser (user_id: int):
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user



@app.put("/users/{userId}", response_model= UserBase)
async def upadte(user_id: int, user: UserBase, db: db_dependency):
    db_user = db.query(models.User).get(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    db.query(models.User).filter(models.User.id == user_id).update(user.dict())
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}",status_code=status.HTTP_200_OK)
async def deleteUser(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(user)
    db.commit()




#Post CRUD operations



@app.post("/post/", status_code=status.HTTP_201_CREATED)
async def createPost (post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()


@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def retrievePost (post_id: int):
    db = SessionLocal()
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    return post



@app.put("/posts/{postId}", response_model= PostBase)
async def upadte(post_id: int, post: PostBase, db: db_dependency):
    db_post = db.query(models.Post).get(post_id)
    if post_id is None:
        raise HTTPException(status_code=404, detail='Post not found')
    db.query(models.Post).filter(models.Post.id == post_id).update(post.dict())
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}",status_code=status.HTTP_200_OK)
async def deleteUser(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    db.delete(post)
    db.commit()




#Get all posts of specific user 


@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int, db: db_dependency):
    posts = db.query(models.Post).filter(models.Post.user_id == user_id).all()
    return posts



#Delete all post of specific user 


@app.delete("/users/delete/{user_id}")
async def delete_user_with_posts(user_id: int, db: db_dependency):
    user = db.query(models.User).get(user_id)
    db.query(models.Post).filter(models.Post.user_id == user_id).delete()
    db.delete(user)
    db.commit()



#Retrieve user and associated posts

@app.get("/users/{user_id}/posts/both/")
async def get_user_with_posts(user_id: int, db: db_dependency):
    user_with_posts = (
        db.query(models.User)
        .join(models.Post)
        .filter(models.User.id == user_id)
        .options(joinedload(models.User.posts))
        .first()
    )
    return user_with_posts



#Create purchase and invoice


@app.post("/purchases/")
async def create_purchase(purchase: PurchaseBase, db: db_dependency):
    db_purchase = models.Purchase(**purchase.dict())
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    save_invoice(db_purchase, db)
   

def save_invoice(db_purchase: PurchaseBase, db):
    user = db.query(models.User).get(db_purchase.user_id)

    sub_total = db_purchase.price * db_purchase.quantity
    tax = sub_total * 0.15
    total = tax + sub_total

    db_invoice = models.Invoice(
        customer_email=user.email,
        customer_name=user.username,
        purchase_id=db_purchase.id,
        sub_total=sub_total,
        tax = tax,
        total=total
    )

    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)



@app.get('/generate-invoice/{billing_id}')
def generate_invoice(billing_id: int, db: db_dependency):
    
    billing_info = db.query(models.BillingDetails).filter(models.BillingDetails.id == billing_id).first()

    if billing_info is None:
        raise HTTPException(status_code=404, detail="Billing information not found")
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.multi_cell(0, 5, 'Ringneck AI Company for\nInformation Technology,\nKACST, Al Raed Dist,\nKing Abdullah Road', align='R')
            self.ln(10)
            self.image('/Users/reema/Desktop/Najla- Projects/pics/ringnecklogo.jpg', x=10, y=10, w=40)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', '', 8)
            self.cell(0, 5, 'If you have question abount the invoice, Please contact:', 0, 0, 'C')
            self.ln(5)  
            self.cell(0, 5, 'info@ringneck.ai', 0, 0, 'C')
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
            self.set_y(-10)
           

        def add_invoice_info(self, title, value):
            
            self.set_font('Arial', 'B', 12)
            self.cell(60, 10, title, align='L')
            self.cell(0, 10, value, align='L')
            self.ln(10)

        def add_table_row(self, left_column, right_column):
            
            self.set_font('Arial', '', 12)
            self.cell(60, 10, left_column, border=1)
            self.cell(0, 10, right_column, border=1)
            self.ln(10)

    pdf = PDF()
    pdf.add_page()

   
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Invoice', ln=True, align='C')
    pdf.ln(10)

    pdf.add_invoice_info('Invoice Number:', billing_info.invoice_number)
    pdf.add_invoice_info("User ID: ",str(billing_info.user_id))
    pdf.add_invoice_info('Date:', str(billing_info.initiated_on))
    pdf.ln(20)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Pyament Details', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.add_table_row('Amount:', str(billing_info.amount))
    pdf.add_table_row('Discount:', str(billing_info.discount))
    pdf.add_table_row('Tax:', str(billing_info.tax))
    
    
    total_amount = billing_info.amount + (billing_info.amount * (billing_info.tax / 100))
    if billing_info.discount > 0:
        total_amount -= total_amount * billing_info.discount / 100

    pdf.add_table_row('Total Amount:', str(total_amount))
    pdf.add_table_row('Currency:', billing_info.currency)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Order Details', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.add_table_row('Order Type:', billing_info.order_type)
    pdf.add_table_row('Subscription Type:', billing_info.subscription_type)
    pdf.add_table_row('Status:', billing_info.status)
    pdf.ln(10)

    pdf_bytes = pdf.output(dest='S')

    return StreamingResponse(
        BytesIO(bytes(pdf_bytes)),
        media_type='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=invoice.pdf'}
    )