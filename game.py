from flask import Flask, request, redirect, url_for, render_template, flash
import sqlite3


app = Flask(__name__)
app.secret_key = 'OUSTILLSUCKS'

users = [
	"Ashe, Cruz",
	"Barragan, Eric",
	"Bayliss, Stuart",
	"Bean, Kyle",
	"Beavers, Cecilia",
	"Bishop, Jacob",
	"Bohannon, Garrett",
	"Brock, Dylan",
	"Burds, Jeffrey",
	"Camacho,Sebastian",
	"Campbell, Mikah",
	"Carr, Ryan",
	"Casey, Chandler",
	"Cerf, Jeremy",
	"Corey, Matthew",
	"Couillard, Levi",
	"Delman, Cameron",
	"Douglas, Austin",
	"Ebarguen, Rene",
	"Eckstrom, James",
	"Escareno, Miryam",
	"Evans, Joshua",
	"Field, Hannah",
	"Gonzales, Hector",
	"Gonzalez, Cesar",
	"Gray, Paul",
	"Guerra, Christopher",
	"Hicks, Robby",
	"Kampa, Duane",
	"Kellogg, Samuel",
	"Ledesma, Gretchen",
	"Lewis, Destiny",
	"Marks, Joshua",
	"Martin, Conor",
	"Mascorro, Marc",
	"Mauk, Ryan",
	"McGuire, Corey",
	"McNiel, Marcus",
	"Murickan, Jobin",
	"Nash, Brendan",
	"Ortega, Veronica",
	"Packard, Casey",
	"Pagio, Rachel",
	"Penwell, Trevor",
	"Quach, Samuel",
	"Ravichandran, Jagannathan",
	"Rodriguez, Kevin",
	"Rogelstad, Megan",
	"Rost, Parker",
	"Rubalcaba, Priscilla",
	"Ruiz, Joshua",
	"Rusnak, Jonathan",
	"Ryan, Charles",
	"Sanchez Jr, Martin",
	"Sanchez, Luis",
	"Staton, Joshua",
	"Steele, Sam",
	"Summers, Benjamin",
	"Thompson, Alex",
	"VanderSchans, Mallory",
	"Waddingham, Matt",
	"Wagner, Tori",
	"Ward, Colin",
	"Wiseman, Offie",
	"Wright, Ashley"]

name = ''
verified = False

@app.route('/')
def index():
	return render_template("index.html") 

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
	if name != '':
		return render_template("homepage.html")
	else:
		return "You are not logged in, please return to the front page"


@app.route('/password', methods=['GET', 'POST'])
def password():
	connection = sqlite3.connect("game.db")
	cursor = connection.cursor()
	if request.method=='POST':
		global name 
		name = request.form["name"]
		cursor.execute("SELECT name FROM login")
		result = cursor.fetchall()
		contained = False
		for r in result:
			if(r[0]==name):
				contained = True
				break
		if(contained == False):
			connection.close()
			return render_template("createPass.html", name=name)
		else:
			connection.close()
			return render_template("password.html", name=name)

@app.route('/passcreate', methods=['GET', 'POST'])
def passcreate():
	connection = sqlite3.connect("game.db")
	cursor = connection.cursor()
	if request.method=='POST':
		pwd = request.form["password"]
		print(pwd)
		sqlcommand = "INSERT INTO login (name, pass) values ('" + name + "', '" + pwd + "')"
		print(sqlcommand)
		cursor.execute(sqlcommand)
		connection.commit()
		connection.close()
		return redirect(url_for('login'))

@app.route('/passverify', methods=['GET', 'POST'])
def passverify():
	connection = sqlite3.connect("game.db")
	cursor = connection.cursor()
	if request.method=='POST':
		pwd = request.form["password"]
		cursor.execute("SELECT * FROM login")
		result = cursor.fetchall()
		for r in result:
			if(r[0]==name):
				print(r[1])
				if(r[1]==pwd):
					connection.close()
					return render_template("homepage.html")
				else:
					connection.close()
					flash("Incorrect password, please try again")
					return render_template("login.html", users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
	return render_template("login.html", users=users)

@app.route('/game', methods=['GET', 'POST'])
def game():
	return "WELCOME TO THE GAME"

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
	return "LEADERBOARD"

if __name__ == "__main__":
	app.run(debug=True)