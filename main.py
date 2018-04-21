from flask import Flask
from flask import render_template, redirect, request
import records
app = Flask(__name__)


db = records.Database('mysql://admin:FlaskTask2018@aa1t78pyyq2oz9v.c4pbzdfasekc.us-east-1.rds.amazonaws.com:3306/ebdb')

@app.route('/')
def home():
    rows = db.query('select * from test')
    for r in rows:
            print(r.one, r.two)
    return redirect('/sales')
   
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'POST':
        print(request.form)
        trans_num = request.form.get('transactionNumber')
        begin_dt = request.form.get('beforeDate')
        end_dt = request.form.get('endDate')
        if trans_num:
            results = transaction_num_search(trans_num)
            return render_template('sales.html', data=results)
        elif begin_dt and end_dt:
            results = transaction_date_search(begin_dt, end_dt)
            return render_template('sales.html', data=results) 
        else:
            return render_template('error.html')
    print("idk wtf happened")
    return render_template('sales.html')

def transaction_num_search(trans_num):
    data = db.query('SELECT * FROM ticket WHERE transaction_number={}'.format(trans_num))
    print(data)
    return data.as_dict()

def transaction_date_search(begin_dt, end_dt):
    data = db.query('SELECT * FROM ticket WHERE date(transaction_datetime) <= "{}" AND date(transaction_datetime) >= "{}"'.format(end_dt, begin_dt))
    print(data)
    return data.as_dict()

