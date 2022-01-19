from flask import Flask, render_template,request,redirect, url_for, make_response
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

create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
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

#Home page route
@app.route('/')
def home():
    
    cookie = request.cookies.get('userid')
   
    if cookie in (None,''):
        msg = 'Sorry you are not logged in to store recipes. If you are a first time user, please register first.'
        return render_template('home.html',msg=msg)
     
    query = "SELECT * FROM recipes"
    recipes = execute_read_query(get_db_connection(),query)

    return render_template("home.html",recipes=recipes) 

#About page route
@app.route('/about/')
def about():
    return render_template("about.html") 

@app.route('/recipe/', methods=['POST','GET'])
def create_recipe():
    
    cookie = request.cookies.get('userid')
    
    if cookie in (None,''):
        msg = 'Sorry you are not logged in to store recipes. If you are a first time user, please register first.'
        return render_template('home.html',msg=msg)
    
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

@app.route('/login/', methods=['POST','GET'])
def login():
    
    form = CreateLoginForm() #instantiate the form to send when the request.method != POST
    if request.method == 'POST':
        form = CreateLoginForm(request.form)
        
        if form.validate():
            username = form.username.data #access the form data
            password = form.password.data
            
            validate_user_sql = '''SELECT * FROM users WHERE username = ? AND password = ?'''
            
            form_data = (username,password)
            
            user_rec = execute_read_query(get_db_connection(), validate_user_sql, form_data)
            
            if user_rec:
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('userid', str(user_rec[0][0]))
                return resp
            else:       
                msg = 'Invalid username and/or password!'         
                return render_template('login.html',msg=msg,form=form)
        
    return render_template('login.html',form=form)

@app.route('/register/', methods=['POST','GET'])
def register():
    
    form = CreateRegisterForm() #instantiate the form to send when the request.method != POST
    if request.method == 'POST':
        form = CreateRegisterForm(request.form)
        
        if form.validate():
            username = form.username.data #access the form data
            password = form.password.data
            
            insert_user = '''INSERT INTO users (username, password) VALUES (?,?)'''
           
            execute_query(get_db_connection(),insert_user,(username,password))
            
            msg = 'Successfully registered! Please log in.'
            form.username.data = None
            form.password.data = None
            return redirect(url_for('login',msg=msg, form=form, registered=True))
        
    return render_template('register.html',form=form)

@app.route('/logout/', methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('about')))
    resp.set_cookie('userid', '')
    return resp
        
class CreateRecipeForm(Form):
    title = StringField('Recipe Title', [validators.Length(min=4, max=50)])
    image = StringField('Image Address', [validators.Length(min=10)])
    link = StringField('Recipe Link', [validators.Length(min=10)])
    
class CreateLoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50)])
    password = StringField('Password', [validators.Length(min=6)])
    
class CreateRegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50)])
    password = StringField('Password', [validators.Length(min=6)])
      
if __name__ == '__main__':
  execute_query(get_db_connection(),create_recipe_table)
  
  execute_query(get_db_connection(),create_users_table)
  
  app.run(debug=True)
  

  
