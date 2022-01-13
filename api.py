from flask import Flask, render_template,request,redirect, url_for
import sqlite3
from sqlite3 import Error
from wtforms import Form, StringField, validators

def get_db_connection():
    return create_connection("recipes.db")
    
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

def execute_query(connection,query = None,params = None):
    cursor = connection.cursor()
    try: 
        if params:
          cursor.execute(query, params)        
        else:
          cursor.execute(query)
          
    except Error as e:
        print(f"The error '{e}' occurred")

    connection.commit()
    print("Query executed in DB successfully!!")
          
def execute_read_query(connection, query, id=None):
    cursor = connection.cursor()
    result = None
    try:
        if id:
            cursor.execute(query,id)
        else:
            cursor.execute(query)
            
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

app = Flask(__name__)

@app.route('/')
def home():
    query = "SELECT * FROM recipes"
    recipes = execute_read_query(get_db_connection(),query)
    
    return render_template("home.html",recipes=recipes) 
  
@app.route('/about/')
def about():
    return render_template("about.html") 

@app.route('/recipe/', methods=['POST','GET'])
def create_recipe():
    
    form = CreateRecipeForm() #instantiate the form to send when the request.method != POST
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        
        if form.validate():
            title = form.title.data #access the form data
            image = form.image.data
            link = form.link.data
            insert_recipe = '''INSERT INTO recipes (title, image, link) VALUES (?,?,?)'''
            form_data = (title, image, link)
            execute_query(get_db_connection(), insert_recipe, form_data)
            return redirect(url_for('home'))
        
    return render_template('create-recipe.html',form=form)

@app.route('/recipe/delete/<id>',methods=['POST'])
def delete_recipe(id):
    
    delete_recipe_sql = '''DELETE FROM recipes WHERE id = ?'''
    
    id = (id,)
    execute_query(get_db_connection(), delete_recipe_sql, id)
    
    return redirect(url_for('home')) 

@app.route('/recipe/<id>', methods=['POST','GET'])
def edit_recipe(id):
    
    if request.method == 'POST':
        form = CreateRecipeForm(request.form)
        
        if form.validate():
            title = form.title.data #access the form data
            image = form.image.data
            link = form.link.data
            update_recipe_sql = '''UPDATE recipes SET title=?, image=?, link=? WHERE id=?'''
            form_data = (title, image, link,id)
            execute_query(get_db_connection(), update_recipe_sql, form_data)
            return redirect(url_for('home'))
    
    id = (id,)
    query = "SELECT * FROM recipes WHERE id=?"
    
    recipe = execute_read_query(get_db_connection(),query,id=id)
                
    form = CreateRecipeForm(request.form) #instantiate the form to send when the request.method != POST
    
    #Populate form with the data of the recipe selected to be edited
    form.title.data = recipe[0][1]
    form.image.data = recipe[0][2]
    form.link.data = recipe[0][3]
    
    return render_template('edit-recipe.html',form=form,id=id)

class CreateRecipeForm(Form):
    title = StringField('Recipe Title', [validators.Length(min=4, max=50)])
    image = StringField('Image Address', [validators.Length(min=10)])
    link = StringField('Recipe Link', [validators.Length(min=10)])
  
if __name__ == '__main__':
  execute_query(get_db_connection(),create_recipe_table)
  app.run(debug=True)
  

  
