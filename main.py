from flask import Flask
from flask import render_template
app = Flask(__name__)

import MySQLdb

cnx={'host': 'aa1t78pyyq2oz9v.c4pbzdfasekc.us-east-1.rds.amazonaws.com', 'username': 'admin', 'password': 'FlaskTask2018', 'db': 'ebdb'}

db = MySQLdb.connect(cnx['host'],cnx['username'],cnx['password'], cnx['db'])

@app.route('/')
def hello_world():
	db.query("""SELECT * FROM test;""")
	r = db.store_results()
	print(r.fetch_row())
	return render_template('main.html')
    
