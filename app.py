from flask import Flask, render_template ,request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
app =  Flask(__name__)

# Flask Config to sqlite database ------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Todo_Project.db'
db = SQLAlchemy(app)



# Initialize Flask-Login
app.config['SECRET_KEY'] = 'krishna_lodhi_bk' 
app.config['SESSION_TYPE'] = 'filesystem'


# Create Users Table in Todo_Project Database ----------------
class User(db.Model):
	id =  db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String(255), nullable=False)
	email = db.Column(db.String(), nullable=False, unique=True)
	password = db.Column(db.String(), nullable=False)
	todos = db.relationship('Todo', backref='user', lazy=True)
	def set_password(self, password):
		self.password = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password, password)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100),nullable=False)
	description = db.Column(db.String(500),nullable=False)
	date_time = db.Column(db.DateTime,default=datetime.datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f'{self.user_id} -> {self.title}'




# Routing Start ---------------------------------------------

@app.route("/signup/", methods=['post','get'])
def signup():
	if request.method == 'POST':
		fullname = request.form.get('fullname')
		email = request.form.get('email')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm-password')
		if password != confirm_password:
			return render_template('register.html', error_message="Password and Confirm Password are not matched .*")

		if User.query.filter_by(email=email).first():	
			return render_template('register.html', error_message="This email already exists..*")

		user = User(fullname=fullname, email=email)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		session['message'] = 'Congratulation! You have successfully registered.'
		return redirect('/login')
	return render_template('register.html')




@app.route("/login", methods=['post','get'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')	
		password = request.form.get('password')

		user = User.query.filter_by(email=email).first()		
		if user and user.check_password(password):
			session['current_user'] = user.id
			return redirect('/')
		return render_template('login.html', error_message="Invalid Email or Password..")
	message = session.pop('message', '')	
	return render_template('login.html', message=message)

@app.route('/reset-passwrod-form', methods=['POST', 'GET'])	
def reset_passwrod_form():
	if request.method == 'POST':
		email= request.form.get("email")
		user = User.query.filter_by(email=email).first()
		if user :
			session['email'] = email
			return redirect('/reset-passwrod-form')
		session['error_message'] =  "Invalid Email Id. *"
		return redirect('/reset-passwrod-form')
	email= session.get('email')
	error_message= session.get('error_message')
	session.pop('email', None)
	session.pop('error_message', None)
	return render_template('reset.html', email=email, error_message=error_message)

@app.route('/reset-password', methods=['POST', 'GET'])	
def reset_passwrod():
	if request.method == 'POST':
		email= request.form.get("email")
		password= request.form.get("password")
		confirm_password= request.form.get("confirm-password")
		if password != confirm_password:
			session['error_message'] = "Password and Confirm Password are not matched .*"
			session['email'] = email
			return redirect('/reset-passwrod-form')
		user = User.query.filter_by(email=email).first()
		user.set_password(password)
		db.session.commit()		
		session.pop('email', None)
		session.pop('error_message', None)
		return redirect('/login')

	return redirect('/login')

@app.route('/' ,methods=['post','get'])
def index():
	if session.get('current_user') is None :
		return redirect('/login')

	if request.method == 'POST':
		title = request.form.get('title')
		description = request.form.get('description') 
		todo =  Todo(title=title, description=description, user=User.query.get(session.get('current_user')))
		db.session.add(todo)
		db.session.commit()
		return redirect('/')


	user = User.query.get(session.get('current_user'))
	todo_list = user.todos
	return render_template('index.html', todo_list=todo_list, user=user)

@app.route("/todo/delete/<int:id>/")
def todo_delete(id):
	todo = Todo.query.get(id)
	# todo = db.get_or_404(Todo_Data, id)
	db.session.delete(todo)
	db.session.commit()
	return redirect('/')



@app.route("/todo/update/<int:id>/", methods=["get", "post"])
def todo_update(id):

	if session.get('current_user') is None :
		return redirect('/login')
	todo = Todo.query.get(id)
	user = User.query.get(session.get('current_user'))
	print(user)
	if request.method == "POST":
		title = request.form.get('title')
		description = request.form.get('description')
		todo.title =title
		todo.description =description
		todo.date_time = datetime.datetime.now()
		db.session.commit()
		return redirect('/') 
	return render_template('update_todo.html', todo=todo, user=user)




@app.route('/logout')
def logout():
	if session.get('current_user') is None :
		return redirect('/login')
	session.clear()
	return redirect("/login")



# Routing end ------------------------------------------------


# Craete Database And All Tables -----------------------------------------
with app.app_context():
	db.create_all()




# Create a Server on 8000 Port. ===============================================================================
if __name__ == '__main__':
	app.run(debug=True, port=8000)