from flask import Flask
from flask import render_template
app = Flask(__name__)

import records

db = records.Database('mysql://admin:FlaskTask2018@aa1t78pyyq2oz9v.c4pbzdfasekc.us-east-1.rds.amazonaws.com:3306/ebdb')

@app.route('/')
def hello_world():
	rows = db.query('select * from test')
	for r in rows:
		print(r.one, r.two)
	

	return render_template('main.html')
    
