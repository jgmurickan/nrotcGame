from flask import Flask, request, redirect, url_for, render_template, flash
import sqlite3
import random


app = Flask(__name__)
app.secret_key = 'OUSTILLSUCKS'

connection = sqlite3.connect("game.db")
cursor = connection.cursor()
cursor.execute("SELECT name from login")
users = cursor.fetchall()
index = 0
for u in users:
	users[index] = u[0]
	index += 1


name = ''
verified = False


@app.route('/')
def index():
	return render_template("index.html") 

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
	if name != '':
		return render_template("homepage.html", name=name)
	else:
		return "You are not logged in, please return to the front page"


@app.route('/password', methods=['GET', 'POST'])
def password():
	connection = sqlite3.connect("game.db")
	cursor = connection.cursor()
	if request.method=='POST':
		global name 
		name = request.form["name"]
		cursor.execute("SELECT * FROM login")
		result = cursor.fetchall()
		contained = False
		for r in result:
			if(r[0]==name):
				if(r[1] != None):
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
					return render_template("homepage.html", name=name)
				else:
					connection.close()
					flash("Incorrect password, please try again")
					return render_template("login.html", users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
	return render_template("login.html", users=users)

@app.route('/instructions', methods=['GET', 'POST'])
def instructions():
	return render_template("instructions.html")

ships = ["Arleigh Burke Class Destroyer (DDG-51)", "Zumwalt Class Destroyer (DDG-1000)", "Cruiser (CG)", "Littoral Combat Ship (LCS)", "Dock Landing Ship (LSD)", "Landing Helicopter Assault (LHA)", "Landing Helicopter Dock (LHD)", "Aircraft Carrier (CVN)", "Amphibious Command Ship (LCC)", "Amphibious Transport Dock (LPD)", "Landing Craft Air Cushion (LCAC)", "Mine Counter Measures (MCM)", "Patrol Coastal Ship (PC)", "Submarine Tender (AS)"]
subs = ["Ohio-Class Ballistic or Guided Missile Submarine (SSBN or SSGN)", "Virginia-Class Fast Attack Submarine (SSN)", "Los Angeles-Class Fast Attack Submarine (SSN)", "Seawolf-Class Fast Attack Submarine (SSN)"]
fixed = ["C-2 Greyhound", "C-130 Hercules", "E-2 Hawkeye", "E-6B Mercury", "EA-6B Prowler", "EA-18G Growler", "EP-3E Aries", "FA-18C", "FA-18D", "FA-18E", "FA-18F", "P-8 Poseidon", "P-3 Orion", "T-6B Texan", "T-45 Goshawk", "F-35B Lightning", "F-35C Lightning", "MV-22 Osprey"]
rotary = ["CH-53 Sea Stallion", "MH-53 Sea Dragon", "MH-60S Seahawk", "MH-60R Seahawk", "TH-57 Sea Ranger", "MV-22 Osprey"]
unmanned = ["MQ-8 Fire Scout", "MQ-8C Fire Scout", "MQ-4C Triton", "X-47B"]
platforms = [ships, subs, fixed, rotary, unmanned]
correct_answers = [None] * 30
user_answers = [None] * 30
pic_used = [None] * 30

@app.route('/game/<int:question_id>', methods=['GET', 'POST'])
def game(question_id):
	if(name==''):
		return "You are not logged in, please return to the frontpage and log in"
	if(question_id > 0):
		global user_answers
		print(request.form["answer"])
		user_answers[question_id-1] = request.form["answer"]
	if(question_id == 30):
		return redirect(url_for('score'))

	# select random platform and create path to send to template
	randlist = [platforms[0]] * 30 + [platforms[1]] * 25 + [platforms[2]] * 20 + [platforms[3]] * 20 + [platforms[4]] * 5
	rand1 = random.choice(randlist)

	rand = 0

	for b in platforms:
		if(rand1 == b):
			if(b == ships):
				rand = 0
			if(b == subs):
				rand = 1
			if(b == fixed):
				rand = 2
			if(b == rotary):
				rand = 3
			if(b == unmanned):
				rand = 4

	length = len(platforms[rand])
	rand2 = random.randint(0, length-1)
	rand3 = random.randint(1, 5)
	answer = platforms[rand][rand2]
	path = answer + "/" + str(rand3)

	counter = 0
	while(path in pic_used):
		if(counter>10):
			store = rand2
			rand2 = random.randint(0, length-1)
			while(rand2 == store):
				rand2 = random.randint(0, length-1)
			answer = platforms[rand][rand2]
		rand3 = random.randint(1,5)
		path = answer + "/" + str(rand3)
		counter += 1
	pic_used[question_id] = path
	global correct_answers
	correct_answers[question_id] = answer

	# create list with random choices, with one of them being the correct answer in random order
	choices = [answer, "b", "c", "d"]
	randChoice = random.choice(platforms[rand])
	for index in range(1, 4):
		while(randChoice in choices):
			randChoice = random.choice(platforms[rand])
		choices[index] = randChoice


	num = random.randint(0,3)
	if(num != 0):
		temp = choices[num]
		choices[num] = answer
		choices[0] = temp

	return render_template("game.html", path=path, choices=choices, question_id=question_id)

@app.route('/score', methods=['GET', 'POST'])
def score():
	score = 0
	for num in range(0,30):
		if(correct_answers[num] == user_answers[num]):
			score += 1
		else:
			score -= 2

	return render_template("score.html", score=score)

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
	return render_template("leaderboard.html")

if __name__ == "__main__":
	app.run(debug=True)