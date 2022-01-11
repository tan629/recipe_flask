from flask import Flask, render_template,request,redirect, url_for
import sqlite3
from sqlite3 import Error
from wtforms import Form, StringField, validators

#SQL for creating recipe table
create_recipe_table = """
    CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    image TEXT NOT NULL,
    link  TEXT NOT NULL
);
"""

#path parameter is the path to the database to be created. 
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection,query = None,insert_values = None, del_id = None):
    cursor = connection.cursor()
    try: 
        if insert_values:
          cursor.execute(query, (insert_values[0],insert_values[1],insert_values[2]))
          connection.commit()
          print("Recipe added to DB successfully!!")
        elif del_id:
          cursor.execute(query, del_id)
          connection.commit()
          print("Recipe deleted from DB successfully!!")  
        else:
          cursor.execute(query)
          connection.commit()
          print("Query executed successfully!!")
          
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

@app.route('/recipe/', methods=['POST','GET'])
def create_recipe():
    connection = create_connection("recipes.db")
    form = CreateRecipeForm() #instantiate the form to send when the request.method != POST
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        
        if form.validate():
            title = form.title.data #access the form data
            image = form.image.data
            link = form.link.data
            insert_recipe = '''INSERT INTO recipes (title, image, link) VALUES (?,?,?)'''
            form_data = (title, image, link)
            execute_query(connection, insert_recipe, form_data)
            return redirect(url_for('home'))
        
    return render_template('create-recipe.html',form=form)

@app.route('/recipe/delete/<id>',methods=['POST'])
def delete_recipe(id):
    
    connection = create_connection("recipes.db")
    
    delete_recipe = '''DELETE FROM recipes WHERE id = ?'''
    
    execute_query(connection, delete_recipe, del_id = id)
    
    return redirect(url_for('home')) 

class CreateRecipeForm(Form):
    title = StringField('Recipe Title', [validators.Length(min=4, max=50)])
    image = StringField('Image Address', [validators.Length(min=10)])
    link = StringField('Recipe Link', [validators.Length(min=10)])
  
if __name__ == '__main__':
  connection = create_connection("recipes.db")
  execute_query(connection,create_recipe_table)
  app.run(debug=True)
  

  
