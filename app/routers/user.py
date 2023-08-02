from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from .. import schemas, utils
from .. config import settings
import mysql.connector
from mysql.connector import errorcode
from typing import List


router = APIRouter(
   tags=['Users']
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
  print ("User database connection successful!")


cursor = mydb.cursor(dictionary=True) 

@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate):
    #hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    #query with hashed password
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", 
                  (user.email, user.password))
    cursor.execute("SELECT * FROM users WHERE id=%s",(cursor.lastrowid,))
    new_user = cursor.fetchone() 
    mydb.commit() #remember to commit to save the changes!!!!
    return f"New User ID:{new_user['id']} registered at {new_user['created_at']}."

@router.get("/users", response_model=List[schemas.UserInfo])
def get_user():
    cursor.execute("SELECT * FROM users")
    query_result = cursor.fetchall()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id:{id} was not found")
    
    return query_result

@router.get("/users/{id}", response_model=schemas.UserInfo)
def get_user(id: int):
    cursor.execute("SELECT * FROM users WHERE id = %s", (str(id),))
    query_result = cursor.fetchone()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id:{id} was not found")
    
    return query_result




@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("DELETE FROM users WHERE id = %s",(str(id),))
    # cursor.fetchone() can't be used because we do not have RETURNING in MySQL
    mydb.commit()