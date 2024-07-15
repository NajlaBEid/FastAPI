from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    username: str
    email: str

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int




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
    return {"id": user_id, **user.dict()}


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
    return {"id": post_id, **post.dict()}


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





    













