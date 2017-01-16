from flask import Flask, request, redirect, url_for, render_template, flash
import sqlite3
import random
from time import sleep

app = Flask(__name__)
app.secret_key = 'OUSTILLSUCKS'

connection = sqlite3.connect("game.db")
cursor = connection.cursor()
cursor.execute("SELECT name from login order by name")
users = cursor.fetchall()
index = 0
for u in users:
	users[index] = u[0]
	index += 1

name = ''
platoon = ''
user_class = ''
verified = False
correct_answers = [None] * 30
user_answers = [None] * 30
pic_used = [None] * 30
choices = []


@app.route('/')
def index():
	return render_template("index.html") 

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
	global correct_answers
	global user_answers
	global pic_used
	global choices

	correct_answers = [None] * 30
	user_answers = [None] * 30
	pic_used = [None] * 30
	choices = []
	
	if name != '' and verified:
		return render_template("homepage.html", name=name)
	else:
		return render_template("notLogged.html")


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
		sqlcommand = "UPDATE login SET pass = '" + pwd + "' WHERE name = '" + name + "'"
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
				if(r[1]==pwd):
					global verified
					global platoon
					global user_class
					verified = True
					platoon = r[2]
					user_class = r[3]
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
	global correct_answers
	global user_answers
	global pic_used
	global choices

	correct_answers = [None] * 30
	user_answers = [None] * 30
	pic_used = [None] * 30
	choices = []

	return render_template("instructions.html")

ships = ["Arleigh Burke Class Destroyer (DDG-51)", "Zumwalt Class Destroyer (DDG-1000)", "Cruiser (CG)", "Littoral Combat Ship (LCS)", "Dock Landing Ship (LSD)", "Landing Helicopter Assault (LHA)", "Landing Helicopter Dock (LHD)", "Aircraft Carrier (CVN)", "Amphibious Command Ship (LCC)", "Amphibious Transport Dock (LPD)", "Landing Craft Air Cushion (LCAC)", "Mine Counter Measures (MCM)", "Patrol Coastal Ship (PC)", "Submarine Tender (AS)"]
subs = ["Ohio-Class Ballistic or Guided Missile Submarine (SSBN or SSGN)", "Virginia-Class Fast Attack Submarine (SSN)", "Los Angeles-Class Fast Attack Submarine (SSN)", "Seawolf-Class Fast Attack Submarine (SSN)"]
fixed = ["C-2 Greyhound", "C-130 Hercules", "E-2 Hawkeye", "E-6B Mercury", "EA-6B Prowler", "EA-18G Growler", "EP-3E Aries", "FA-18C", "FA-18D", "FA-18E", "FA-18F", "P-8 Poseidon", "P-3 Orion", "T-6B Texan", "T-45 Goshawk", "F-35B Lightning", "F-35C Lightning", "MV-22 Osprey"]
rotary = ["CH-53 Sea Stallion", "MH-53 Sea Dragon", "MH-60S Seahawk", "MH-60R Seahawk", "TH-57 Sea Ranger", "MV-22 Osprey"]
unmanned = ["MQ-8 Fire Scout", "MQ-8C Fire Scout", "MQ-4C Triton", "X-47B"]
platforms = [ships, subs, fixed, rotary, unmanned]

@app.route('/game/<int:question_id>', methods=['GET', 'POST'])
def game(question_id):
	if(name==''):
		return "You are not logged in, please return to the frontpage and log in"
	if(question_id > 0):
		global user_answers
		if not user_answers[question_id-1]:
			user_answers[question_id-1] = request.form["answer"]
		else:
			flash("You already submitted an answer for that question")
	if(question_id == 30):
		return redirect(url_for('score'))

	path = ''
	old = "No"
	global pic_used
	if not pic_used[question_id]:

		print(question_id)
		# select random platform and create path to send to template
		randlist = [platforms[0]] * 30 + [platforms[1]] * 20 + [platforms[2]] * 20 + [platforms[3]] * 20 + [platforms[4]] * 5
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
		global choices
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

	else:
		path = pic_used[question_id]
		old = "Yes"

	return render_template("game.html", path=path, choices=choices, question_id=question_id, old=old)


@app.route('/score', methods=['GET', 'POST'])
def score():
	global correct_answers
	global user_answers
	global pic_used
	global choices
	
	score = 0
	for num in range(0,30):
		if(correct_answers[num] == user_answers[num]):
			score += 1
		else:
			score -= 3
	
	correct_answers = [None] * 30
	user_answers = [None] * 30
	pic_used = [None] * 30
	choices = []
	
	connection = sqlite3.connect("game.db")
	cursor = connection.cursor()
	cursor.execute("SELECT * from leaderboard WHERE name='" + name + "'")
	name_row = cursor.fetchone()
	status = ''
	if(not name_row):
		status = "Your new high score!"
		cursor.execute("DELETE FROM leaderboard WHERE name = '" + name + "'")
		if(user_class is None):
			sql_command = "INSERT INTO leaderboard(name, score, platoon) VALUES ('" + name + "', '" + str(score) + "', '" + platoon + "')"
		else:
			sql_command = "INSERT INTO leaderboard(name, score, platoon, class) VALUES ('" + name + "', '" + str(score) + "', '" + platoon + "', '" + user_class + "')"
		cursor.execute(sql_command)
		connection.commit()
	else:
		if(int(name_row[1]) < score):
			status = "Your new high score!"
			cursor.execute("DELETE FROM leaderboard WHERE name = '" + name + "'")
			if(user_class is None):
				sql_command = "INSERT INTO leaderboard(name, score, platoon) VALUES ('" + name + "', '" + str(score) + "', '" + platoon + "')"
			else:
				sql_command = "INSERT INTO leaderboard(name, score, platoon, class) VALUES ('" + name + "', '" + str(score) + "', '" + platoon + "', '" + user_class + "')"
			cursor.execute(sql_command)
			connection.commit()
		else:
			status = "Current high score: " + str(name_row[1])
	connection.close()

	return render_template("score.html", score=score, status=status)

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
	connection = sqlite3.connect("game.db")
	cursor = connection.cursor()
	cursor.execute("SELECT * from leaderboard order by score desc")
	lead_list = cursor.fetchall()
	index = 0
	for u in lead_list:
		plt = u[2]
		if(u[2] == "PC1"):
			plt = "Platoon 1"
		if(u[2] == "PC2"):
			plt = "Platoon 2"
		if(u[2] == "LNPC"):
			plt = "Leatherneck"
		lead_list[index] = [u[0], plt, u[1]]
		index += 1
	connection.close()
	return render_template("leaderboard.html", lead_list=lead_list)

@app.route ('/stats', methods=['GET', 'POST'])
def stats():
	plt1 = []
	plt2 = []
	ln = []
	bnstaff = []
	unstaff = []
	first = []
	second =[]
	third = []
	fourth = []
	mecep = []

	plt1_avg = 0
	tp_plt1 = ''
	plt2_avg = 0
	tp_plt2 = ''
	ln_avg = 0
	tp_ln = ''
	bnstaff_avg = 0
	tp_bn = ''
	unstaff_avg = 0
	tp_un = ''
	first_avg = 0
	tp_first = ''
	second_avg = 0
	tp_second = ''
	third_avg = 0
	tp_third = ''
	fourth_avg = 0
	tp_fourth = ''
	mecep_avg = 0
	tp_mecep = ''
	hs_plt1 = 0
	hs_plt2 = 0
	hs_ln = 0
	hs_bn = 0
	hs_un = 0
	hs_first = 0
	hs_second = 0
	hs_third = 0
	hs_fourth = 0
	hs_mecep = 0

	connection = sqlite3.connect("game.db")
	cursor = connection.cursor()
	cursor.execute("SELECT * from leaderboard order by score desc")
	stat_list = cursor.fetchall()
	index = 0
	for u in stat_list:
		if(u[2] == "PC1" and tp_plt1 == ''):
			tp_plt1 = u[0]
			hs_plt1 = int(u[1])
		if(u[2] == "PC2" and tp_plt2 == ''):
			tp_plt2 = u[0]
			hs_plt2 = int(u[1])
		if(u[2] == "LNPC" and tp_ln == ''):
			tp_ln = u[0]
			hs_ln = int(u[1])
		if(u[2] == "Staff" and tp_bn == ''):
			tp_bn = u[0]
			hs_bn = int(u[1])
		if(u[2] == "Unit Staff" and tp_un == ''):
			tp_un = u[0]
			hs_un = int(u[1])
		
		if(u[3] == "1/C" and tp_first == ''):
			tp_first = u[0]
			hs_first = int(u[1])
		if(u[3] == "2/C" and tp_second == ''):
			tp_second = u[0]
			hs_second = int(u[1])
		if(u[3] == "3/C" and tp_third == ''):
			tp_third = u[0]
			hs_third = int(u[1])
		if(u[3] == "4/C" and tp_fourth == ''):
			tp_fourth = u[0]
			hs_fourth = int(u[1])
		if(u[3] == "MECEP" and tp_mecep == ''):
			tp_mecep = u[0]
			hs_mecep = int(u[1])

		stat_list[index] = [int(u[1]), u[2], u[3]]
		index += 1

	connection.close()

	for u in stat_list:
		if(u[1] == "PC1"):
			plt1.append(u[0])
		if(u[1] == "PC2"):
			plt2.append(u[0])
		if(u[1] == "LNPC"):
			ln.append(u[0])
		if(u[1] == "Staff"):
			bnstaff.append(u[0])
		if(u[1] == "Unit Staff"):
			unstaff.append(u[0])
		
		if(u[2] == "1/C"):
			first.append(u[0])
		if(u[2] == "2/C"):
			second.append(u[0])
		if(u[2] == "3/C"):
			third.append(u[0])
		if(u[2] == "4/C"):
			fourth.append(u[0])
		if(u[2] == "MECEP"):
			mecep.append(u[0])

	if plt1:
		plt1_avg = sum(plt1)/float(len(plt1))
	else:
		plt1_avg = 0

	if plt2:
		plt2_avg = sum(plt2)/float(len(plt2))
	else:
		plt2_avg = 0

	if ln:
		ln_avg = sum(ln)/float(len(ln))
	else:
		ln_avg = 0

	if bnstaff:
		bnstaff_avg = sum(bnstaff)/float(len(bnstaff))
	else:
		bnstaff_avg = 0

	if unstaff:
		unstaff_avg = sum(unstaff)/float(len(unstaff))
	else:
		unstaff_avg = 0

	if first:
		first_avg = sum(first)/float(len(first))
	else:
		first_avg = 0

	if second:
		second_avg = sum(second)/float(len(second))
	else:
		second_avg = 0

	if third:
		third_avg = sum(third)/float(len(third))
	else:
		third_avg = 0

	if fourth:
		fourth_avg = sum(fourth)/float(len(fourth))
	else:
		fourth_avg = 0

	if mecep:
		mecep_avg = sum(mecep)/float(len(mecep))
	else:
		mecep_avg = 0

	return render_template("stats.html", plt1_avg=plt1_avg, plt2_avg=plt2_avg, ln_avg=ln_avg, bnstaff_avg=bnstaff_avg, unstaff_avg=unstaff_avg, first_avg=first_avg, second_avg=second_avg, third_avg=third_avg, fourth_avg=fourth_avg, mecep_avg=mecep_avg, tp_plt1=tp_plt1, tp_plt2=tp_plt2, tp_ln=tp_ln, tp_bn=tp_bn, tp_un=tp_un, tp_first=tp_first, tp_second=tp_second, tp_third=tp_third, tp_fourth=tp_fourth, tp_mecep=tp_mecep, hs_plt1=hs_plt1, hs_plt2=hs_plt2, hs_ln=hs_ln, hs_bn=hs_bn, hs_un=hs_un, hs_first=hs_first, hs_second=hs_second, hs_third=hs_third, hs_fourth=hs_fourth, hs_mecep=hs_mecep)


if __name__ == "__main__":
	app.run(debug=True)