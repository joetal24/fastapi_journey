Final Challenge Before You Rest
Summarise the entire project in your own words — cover:

What each file does
What happens from the moment a request hits your API to the moment a response goes back
What you would do differently if you started again

If you can answer all three clearly — you genuinely understand FastAPI. Not tutorial understanding. Real understanding.


Qn1
Main.py
This file loads the fastapi class into app instatnce and also loads the routes, get, put, post and delete.
It also loads the other class from models, database,schemas while creating the database instance wen the server starts

schemas.py
This file contains classes that validates input and output of data
they r name three of them
Todocreate : Wic validates data being created by the put route
TodoResponse: Wic validates data thats the output of all the routes
TodoUpdate: Wic validates data thats created on existing data(update)

models.py
This file contains class that validates data entering the database (Todo)
"__tablename__ = "todos"" helps to create a table called todos in the database also called todos 

database.py
This file contains the engine that starts the db , creates a line wic is connected to the routes and db

dependencies.py
This file contains the session of calling the db 

qn2
Get request
wat happens a new object is created(title, completed) , is added to the db, then its saved inthe db , then reloaded and returned ajson object

others i dont know 

curl -X POST "http://127.0.0.1:8000/todos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.vLQds_TijpqxHjMCae4cCqn-o-TD9YP8VQrvlzFZqRk" \
  -d '{"title": "Buy milk", "completed": false}'

  curl -X GET "http://127.0.0.1:8000/todos/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyfQ.I3E9VKaHruORxY-xEQy8J0H0U7DO_FCtx9xsckFNlMg"