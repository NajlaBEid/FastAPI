from fastapi import FastAPI, HTTPException, Depends, status, Response
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from fpdf import FPDF
import os
from fastapi.responses import FileResponse




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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


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


# Generate the invoice as a PDF
@app.get("/invoice/{invoice_id}")
async def get_invoice_as_pdf(invoice_id: int, db: db_dependency):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail='Invoice not found')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 20, "Invoice Details", align="C", ln=True) 
    pdf.cell(0, 10, f"Invoice ID: {invoice.id}", ln=True)

    pdf.cell(0, 10, f"Customer Name:  {invoice.customer_name}", ln=True)
    pdf.cell(0, 10, f"Customer Email:  {invoice.customer_email}", ln=True)
    pdf.cell(0, 10, f"Sub Total amount:  ${invoice.sub_total:.2f}", ln=True)
    pdf.cell(0, 10, f"Tax amount (15%):  ${invoice.tax:.2f}", ln=True)
    pdf.cell(0, 10, f"Total amount:  ${invoice.total:.2f}", ln=True)

    pdf_file = f"invoice_{invoice_id}.pdf"
    pdf.output(pdf_file)
    return FileResponse(pdf_file, media_type="application/pdf", filename=pdf_file)

