from fastapi import APIRouter, Depends, status, HTTPException, Response
from .. import schemas, utils, oauth
from ..config import settings
import mysql.connector
from mysql.connector import errorcode
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=['Authentication'])

## MYSQL Connection ##
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
  print ("Login database connection successful!")

cursor = mydb.cursor(dictionary=True) 
## Connection and cursor established ##

@router.post('/login', response_model=schemas.Token)
def login(entered_credentials: OAuth2PasswordRequestForm = Depends()):
  # Will return username and password attributes
  cursor.execute("SELECT * FROM users WHERE email = %s",(entered_credentials.username,))
  stored_credentials = cursor.fetchone()  

  # username does not exist
  if not stored_credentials:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid credentials entered")
  # incorrect password
  if not utils.verify(entered_credentials.password, stored_credentials['password']):
     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                         detail=f"Invalid credentials entered")
  
# If credentials verified, create Access Token
  access_token = oauth.create_access_token(payload=
                                           {"user_id": stored_credentials['id']}
                                           )

# Return Token
  return {"access_token" : access_token,
          "token_type" : "bearer"
          }
  
 