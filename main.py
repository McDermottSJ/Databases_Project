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

@app.route('/employee',)
def employee():
    employees = get_employees()
    servers = get_servers()
    managers = get_managers() 
    return render_template('employee.html', employees=employees, managers=managers, servers=servers)

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

def get_employees():
    employees = db.query('SELECT * FROM employee WHERE employee_id NOT IN (SELECT * FROM manager) AND employee_id NOT IN (SELECT * FROM server) AND end_date IS NULL')
    return employees.as_dict()

def get_servers():
    servers = db.query('SELECT * FROM server NATURAL JOIN employee')
    return servers.as_dict()

def get_managers():
    managers = db.query('SELECT * FROM manager NATURAL JOIN employee')
    return managers.as_dict()

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


@app.route('/equipment')
def equipment():
	return render_template('Equipment.html', equip=getEquip(), overdue=getOverdue())

def getEquip():
	equip = db.query('SELECT * FROM equipment')
	return equip.as_dict()
def getOverdue():
	overdue = db.query('select * from equipment where datediff(sysdate(), last_maintenanced) >= maintenance_frequency')
	return overdue.as_dict()

@app.route('/equipment/req', methods=['POST'])
def reqMaint():
	serialnum = request.form.get('serialNum')
	return render_template('Equipment.html', equip=getEquip(), overdue=getOverdue(), mech=getMech(serialnum))
def getMech(serial):
	mech = db.query('select employee_id, concat(first_name, " ", last_name) as name from employee natural join maintains where serial_num = {}'.format(serial))
	return mech.as_dict()

@app.route('/equipment', methods =['POST'])
def subMaint():
	serialnum = request.form.get('serialNumSub')
	db.query('update equipment set last_maintenanced = date(sysdate()) where serial_num = {}'.format(serialnum))
	return render_template('Equipment.html', equip=getEquip(), overdue=getOverdue())

