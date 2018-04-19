from flask import Flask
from flask import render_template
app = Flask(__name__)

import PyMySQL

cnx={'host': 'aa1t78pyyq2oz9v.c4pbzdfasekc.us-east-1.rds.amazonaws.com', 'username': 'admin', 'password': 'FlaskTask2018', 'db': 'ebdb'}

db = MySQLdb.connect(cnx['host'],cnx['username'],cnx['password'], cnx['db'])

@app.route('/')
def hello_world():
	cursor = db.cursor()
	sql  = """INSERT INTO test VALUES (4, 'asd')"""
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
	db.close()

	return render_template('main.html')
    
