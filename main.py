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
    return render_template('sales.html')

@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if request.method == 'POST':
        print(request.form)
        trans_num = request.form.get('transactionNumber')
        if trans_num: 
            results = {}
            results['items'] = get_items(trans_num)
            if not results['items']:
                return render_template('sales.html', error=True)
            server = get_server(trans_num)
            results['server_name'] = server['server_name']
            results['employee_id'] = server['employee_id']
            results['sub_total'] = get_sub_total(trans_num) 
            results['tip'] = get_tip(trans_num) 
            results['date'] =  get_date(trans_num)
            results['transaction_number'] = trans_num
            print(results)
            return render_template('sales.html', ticket=results)
        else:
            return render_template('sales.html', error=True)
 
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        print(request.form)
        begin_dt = request.form.get('beforeDate')
        end_dt = request.form.get('endDate')
        if begin_dt and end_dt:
            data = db.query('SELECT * FROM ticket WHERE date(transaction_datetime) <= "{}" AND date(transaction_datetime) >= "{}"'.format(end_dt, begin_dt))
            print(data)
            results = data.as_dict()
            return render_template('sales.html', data=results) 
        else:
            return render_template('sales.html', error=True)

def get_items(trans_num):
    items = db.query('SELECT *, quantity * price as "sub_total" FROM (select item_name, quantity FROM contains WHERE transaction_number={}) as t1 NATURAL JOIN menu_items'.format(trans_num))
    return items.as_dict()


def get_server(trans_num):
    name = db.query('SELECT employee_id, concat (first_name, " ", last_name) as server_name FROM employee NATURAL JOIN ticket WHERE transaction_number={}'.format(trans_num))
    return name.as_dict()[0]

def get_sub_total(trans_num):
    sub_total = db.query('SELECT SUM(sub_total) AS total FROM (SELECT *, quantity * price AS "sub_total" FROM (SELECT item_name, quantity FROM contains WHERE transaction_number={}) as t1 NATURAL JOIN menu_items) as t2'.format(trans_num))
    return sub_total.as_dict()[0]['total']

def get_tip(trans_num):
    tip = db.query('SELECT tip FROM ticket WHERE transaction_number={}'.format(trans_num))
    return tip.as_dict()[0]['tip']

def get_date(trans_num):
    date = db.query('SELECT transaction_datetime FROM ticket WHERE transaction_number={}'.format(trans_num))
    return date.as_dict()[0]['transaction_datetime']


