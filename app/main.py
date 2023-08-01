from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# import mysql.connector
# from mysql.connector import errorcode
from .routers import post, user, auth, vote
from .config import settings

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # specific HTTP methods e.g. only GET
    allow_headers=["*"],
)

#CONNECTING TO MYSQL DATABASE
""" def connect_mysql():
    try:
        mydb = mysql.connector.connect(user='root', password='Sf@7334p!',
                                host='localhost',
                                database='penguin1')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        print ("Database connection successful!")
    
    return mydb """







my_posts = [{"title": "title of Post 1", 
             "content":"content of Post 1", 
             "id":1
             },
            {"title": "favourite foods", 
             "content": "Hokkien Mee", 
             "id":2
             }
            ]

### functions 

""" def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
        
def find_post_index(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i """
    

app.include_router(post.router) # Check post.py for router paths
app.include_router(user.router) # Check user.py for router paths
app.include_router(auth.router) # Check user.py for router paths
app.include_router(vote.router)

### APIs

""" @app.get("/test")
def dummy_get():
    print (list(enumerate(my_posts)))

@app.get("/")
async def root():
    return {"message": "Welcome to Keith's root URL"}

@app.get("/posts", response_model=List[schemas.Post]) #use List when returning multiple posts
def get_posts():
    cursor.execute("SELECT * FROM posts")
    query_result = cursor.fetchall()
    return query_result

@app.get("/posts/{id}", response_model=schemas.Post)
def get_single_post(id: int, response: Response): # ":int" validates that param is an int and converts it if its not
    print (id)
    cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id:{id} was not found")
    return result
   # return {"details": my_posts[int(id)]}


# "Body" is from fastAPI that converts JSON payload into a Python dict
# payload can be named anything, but printing it makes it appear in terminal

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: schemas.PostCreate): # what is this : after argument
    cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s)",
                   (payload.title, payload.content, payload.published))
    # new_post = cursor.fetchone() 
    mydb.commit() #remember to commit to save the changes!!!!
    return f"Post created!"

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("DELETE FROM posts WHERE id = %s",(str(id),))
    # cursor.fetchone() can't be used because we do not have RETURNING in MySQL
    mydb.commit()

    # index = find_post_index(id)
    # if index == None:
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                        detail=f"post with id:{id} does not exist")
  
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id:int, payload: schemas.PostCreate):

    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s",
                   (payload.title, payload.content, payload.published, str(id)))
    # result = cursor.fetchone()
    mydb.commit()

    #if result == None:
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                        detail=f"post with id:{id} does not exist")
    # payload_dict = dict(payload) # turn payload into dict
    # payload_dict['id'] = id # payload may not have an ID, adding id:2 for example
    # my_posts[index] = payload_dict
    # return {"data":payload_dict}
    return {"data" : f"Post updated!"}


## AUTHENTICATION PATHS USING USERS
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate):
    #hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    #query with hashed password
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", 
                  (user.email, user.password))
    mydb.commit()
    return f"New user registered!"

@app.get("/users/{id}", response_model=schemas.UserInfo)
def get_user(id: int):
    cursor.execute("SELECT * FROM users WHERE id = %s", (str(id),))
    query_result = cursor.fetchone()

    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id:{id} was not found")
    
    return query_result """

