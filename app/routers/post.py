from typing import List
from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from .. import schemas, oauth
from ..config import settings
import mysql.connector
from mysql.connector import errorcode




router = APIRouter(
   tags=['Posts']
)

try:
    mydb = mysql.connector.connect(user=settings.db_user,
                                   password=settings.db_pw,
                                   host=settings.db_hostname,
                                   database=settings.db_name)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  print ("Post database connection successful!")


cursor = mydb.cursor(dictionary=True)

@router.get("/")
async def root():
    return {"message": "Welcome to Keith's root URL"}

@router.get("/test")
def testfunc():
   print (cursor.lastrowid)

@router.get("/posts", response_model=List[schemas.PostResponse]) #use List when returning multiple posts
def get_posts():
    cursor.execute("WITH t1 AS (SELECT posts.*, users.email FROM posts LEFT JOIN users ON posts.user_id = users.id) SELECT t1.id, t1.title, t1.content, t1.created, t1.email, COUNT(votes.post_id) AS votes FROM t1 LEFT JOIN votes ON t1.id = votes.post_id GROUP BY t1.id")
    query_result = cursor.fetchall()
    return query_result

@router.get("/posts/{id}", response_model=schemas.PostResponse)
def get_single_post(id: int): # ":int" validates that param is an int and converts it if its not
    print (id)
    cursor.execute("WITH t1 AS (SELECT posts.*, users.email FROM posts LEFT JOIN users ON posts.user_id = users.id) SELECT t1.id, t1.title, t1.content, t1.created, t1.email, COUNT(votes.post_id) AS votes FROM t1 LEFT JOIN votes ON t1.id = votes.post_id WHERE t1.id = %s GROUP BY t1.id", (str(id),))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id:{id} was not found")
    return result
   # return {"details": my_posts[int(id)]}


# "Body" is from fastAPI that converts JSON payload into a Python dict
# payload can be named anything, but printing it makes it appear in terminal

@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: schemas.PostCreate, 
                user_id: int = Depends(oauth.get_current_user)): # what is this : after argument
    cursor.execute("INSERT INTO posts (title, content, published, user_id) VALUES (%s, %s, %s, %s)",
                   (payload.title, payload.content, payload.published, user_id.id))
    cursor.execute("SELECT * FROM posts WHERE id=%s",(cursor.lastrowid,))
    new_post = cursor.fetchone() 
    mydb.commit() #remember to commit to save the changes!!!!
    return f"New Post ID:{new_post['id']} created at {new_post['created']}."
    #return new_post



@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,
                user_id: int = Depends(oauth.get_current_user)):
    # Check if post exists
    cursor.execute("SELECT * FROM posts WHERE id = %s",(str(id),))
    selected_post = cursor.fetchone()
    if selected_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} does not exist")
    # Check if requester is creator as well
    if str(selected_post['user_id']) != user_id.id:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                           detail=f"Not authorised to perform requested action")
    # If no errors, execute query as follows
    cursor.execute("DELETE FROM posts WHERE id = %s",(str(id),))
    mydb.commit()
  
    return Response(status_code=status.HTTP_204_NO_CONTENT)




@router.put("/posts/{id}")
def update_post(id:int, 
                payload: schemas.PostCreate,
                user_id: int = Depends(oauth.get_current_user)):
    # Check if post exists
    cursor.execute("SELECT * FROM posts WHERE id=%s",(str(id),))
    post_to_update = cursor.fetchone() 
    if post_to_update == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} does not exist")
    # Check if requester is creator as well
    if str(post_to_update['user_id']) != user_id.id:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                           detail=f"Not authorised to perform requested action")
    # If no errors, execute query as follows
    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s",
                   (payload.title, payload.content, payload.published, str(id),))
    mydb.commit() #remember to commit to save the changes!!!!

    return f"Post ID:{post_to_update['id']} updated."
