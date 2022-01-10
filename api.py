from flask import Flask, render_template,request,redirect, url_for
import sqlite3
from sqlite3 import Error

connection = None

#path parameter is the path to the database to be created. 
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection,query = None,insert_values = None):
    cursor = connection.cursor()
    try:
        if query:
          cursor.execute(query)
          connection.commit()
          print("Query executed successfully!!")
        
        if insert_values:
          cursor.execute("INSERT INTO recipes (title, image, link) VALUES (?,?,?)", (insert_values[0],insert_values[1],insert_values[2]))
          connection.commit()
          print("Recipe added to DB successfully!!")
          
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

create_recipe_table = """
    CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    image TEXT NOT NULL,
    link  TEXT NOT NULL
);
"""
# recipes = [
#         {
#             "title": "BBQ Sweet and Sour Chicken Wings",
#             "image": "https://image.freepik.com/free-photo/chicken-wings-barbecue-sweetly-sour-sauce-picnic-summer-menu-tasty-food-top-view-flat-lay_2829-6471.jpg",
#             "link": "https://cookpad.com/us/recipes/347447-easy-sweet-sour-bbq-chicken"
#         },
        
#         {
#             "title": "Chicken dum biryani",
#             "image": "https://img-global.cpcdn.com/recipes/7a280653f37e857e/680x482cq70/chicken-dum-biryani-recipe-main-photo.webp",
#             "link": "https://cookpad.com/us/recipes/14350263-chicken-dum-biryani"
#         },
        
#         {
#             "title": "Chicken pasta",
#             "image": "https://image.freepik.com/free-photo/penne-pasta-tomato-sauce-with-chicken-tomatoes-wooden-table_2829-19739.jpg",
#             "link": "https://cookpad.com/us/recipes/15210882-garlic-chicken-penne-pasta-with-spicy-marinara?ref=search&search_term=chicken%20pasta"
#         }
#     ]

app = Flask(__name__)

@app.route('/')
def home():
    connection = create_connection("recipes.db")
    query = "SELECT * FROM recipes"
    recipes = execute_read_query(connection,query)

    return render_template("home.html",recipes=recipes) 
  
@app.route('/about/')
def about():
    return render_template("about.html") 

@app.route('/recipe/', methods=['POST'])
def create_recipe():
    form = request.form

    recipe = (form['title'],form['image'],form['link'])
    connection = create_connection("recipes.db")
    execute_query(connection,insert_values=recipe)
    return form
  
if __name__ == '__main__':
  connection = create_connection("recipes.db")
  execute_query(connection,create_recipe_table)
  app.run(debug=True)
  

  
