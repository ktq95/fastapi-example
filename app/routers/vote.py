from typing import List
from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from .. import schemas, oauth
from ..config import settings
import mysql.connector
from mysql.connector import errorcode


router = APIRouter(
   tags=['Votes']
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
  print ("Vote database connection successful!")


cursor = mydb.cursor(dictionary=True)

### POST VOTE ###
@router.post("/votes", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, current_user: int = Depends(oauth.get_current_user)):
  
  # check if post exists
  cursor.execute("SELECT * FROM posts WHERE id = %s",
                 (str(vote.post_id),))
  found_post = cursor.fetchone()

  if not found_post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post {vote.post_id} does not exist")
  
  # check if existing vote exists
  cursor.execute("SELECT * FROM votes WHERE post_id = %s AND user_id = %s",
                 (str(vote.post_id), str(current_user.id)))
  found_vote = cursor.fetchone()

  if (vote.dir == 1):
    if found_vote:
      raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                          detail=f"User {current_user.id} has already voted on post ID:{vote.post_id}.")
    cursor.execute("INSERT INTO votes VALUES (%s,%s)",
                   (str(vote.post_id),str(current_user.id)))
    mydb.commit()
    cursor.execute("SELECT * FROM votes WHERE post_id = %s AND user_id = %s",
                 (str(vote.post_id), str(current_user.id)))
    new_vote = cursor.fetchone()

    return f"New vote created at on post ID:{new_vote['post_id']}"
  
  else: # basically if it's an UNVOTE vote.dir == 0
    if not found_vote: # error if there is no existing vote
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"Vote does not exist")
    # if exists, execute the delete query
    cursor.execute("DELETE FROM votes WHERE post_id = %s AND user_id = %s",
                   (str(vote.post_id),str(current_user.id)))
    mydb.commit()
    return f"Vote successfully deleted"

