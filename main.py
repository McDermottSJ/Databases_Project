from flask import Flask, url_for
from flask import render_template, redirect, request
import random
import records
app = Flask(__name__)


db = records.Database('mysql://admin:FlaskTask2018@aa1t78pyyq2oz9v.c4pbzdfasekc.us-east-1.rds.amazonaws.com:3306/ebdb')

@app.route('/')
def home():
    return redirect('/sales')
   
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    return render_template('sales.html')

@app.route('/employee')
def employee():
    employees = get_employees()
    servers = get_servers()
    managers = get_managers() 
    return render_template('employee.html', employees=employees, managers=managers, servers=servers, error=request.args.get('error'))

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

@app.route('/shifts')
def shifts():
    return render_template('shifts.html')

@app.route('/add_shift', methods=['POST'])
def add_shift():
    if request.method == 'POST':
        employee_id = request.form.get('employeeId')
        date = request.form.get('date')
        shift = request.form.get('shift')
        insert_shift(employee_id, date, shift)
        return redirect('shifts')
    else:
        return redirect('shifts')

@app.route('/lookup_shift', methods=['POST'])
def lookup_shift():
    if request.method == 'POST':
        date = request.form.get('date')
        shifts = request.form.get('shift')
        print('Shifts: {}'.format(shifts))
        if shifts == 'both':
            morning_shifts = find_morning_shifts(date)
            evening_shifts = find_evening_shifts(date)
            print('Morning Shifts: {}'.format(morning_shifts))
            print('Evening Shifts: {}'.format(evening_shifts))
            return render_template('shifts.html', morning=morning_shifts, evening=evening_shifts, date=date)
        elif shifts == 'morning':
            morning_shifts = find_morning_shifts(date)
            print('Morning Shifts: {}'.format(morning_shifts))
            return render_template('shifts.html', morning=morning_shifts, date=date)
        elif shifts == 'evening':
            evening_shifts = find_evening_shifts(date)
            print('Evening Shifts: {}'.format(evening_shifts))
            return render_template('shifts.html', evening=evening_shifts, date=date)
    return render_template('shifts.html', lookup=True)

@app.route('/hire', methods=['POST'])
def hire():
    if request.method == 'POST':
        employee_id = random.randint(100000,999999)
        position = request.form.get('position')
        pay = request.form.get('pay')
        last_name = request.form.get('lastName')
        first_name = request.form.get('firstName')
        phone = request.form.get('phone')
        add_employee(employee_id, first_name, last_name, phone, pay)
        if position == 'server':
            add_server(employee_id)
        elif position == 'manager':
            add_manager(employee_id)
        return redirect('/employee') 

@app.route('/terminate', methods=['POST'])
def terminate():
    if request.method == 'POST':
        employee_id = request.form.get('employeeId')
        position = request.form.get('position')
        if is_employee(employee_id):
            terminate_empoloyee(employee_id)
            return redirect('/employee')
        else: 
            return redirect(url_for('employee', error=True))

@app.route('/equipment', methods =['POST'])
def subMaint():
	serialnum = request.form.get('serialNumSub')
	db.query('update equipment set last_maintenanced = date(sysdate()) where serial_num = {}'.format(serialnum))
	return render_template('Equipment.html', equip=getEquip(), overdue=getOverdue())

@app.route('/equipment')
def equipment():
	return render_template('Equipment.html', equip=getEquip(), overdue=getOverdue())

@app.route('/equipment/req', methods=['POST'])
def reqMaint():
	serialnum = request.form.get('serialNum')
	return render_template('Equipment.html', equip=getEquip(), overdue=getOverdue(), mech=getMech(serialnum))

def terminate_empoloyee(employee_id):
    db.query('UPDATE employee SET end_date=sysdate() WHERE employee_id = {}'.format(employee_id))
    return

def get_employees():
    employees = db.query('SELECT * FROM employee WHERE employee_id NOT IN (SELECT * FROM manager) AND employee_id NOT IN (SELECT * FROM server) AND end_date IS NULL')
    return employees.as_dict()

def get_servers():
    servers = db.query('SELECT * FROM server NATURAL JOIN employee WHERE end_date IS NULL')
    return servers.as_dict()

def get_managers():
    managers = db.query('SELECT * FROM manager NATURAL JOIN employee WHERE end_date IS NULL')
    return managers.as_dict()

def get_items(trans_num):
    items = db.query('SELECT *, quantity * price as "sub_total" FROM (select item_name, quantity FROM contains WHERE transaction_number={}) as t1 NATURAL JOIN menu_items'.format(trans_num))
    return items.as_dict()

def get_employee_by_id(employee_id):
    employee = db.query('SELECT * FROM employee WHERE employee_id={}'.format(employee_id))
    return employee.as_dict()

def is_employee(employee_id):
    if employee:
        return True
    else:
        return False

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

def getEquip():
	equip = db.query('SELECT * FROM equipment')
	return equip.as_dict()
def getOverdue():
	overdue = db.query('select * from equipment where datediff(sysdate(), last_maintenanced) >= maintenance_frequency')
	return overdue.as_dict()

def getMech(serial):
	mech = db.query('select employee_id, concat(first_name, " ", last_name) as name from employee natural join maintains where serial_num = {}'.format(serial))
	return mech.as_dict()

def get_all_employee_ids():
    employee_ids = db.query('SELECT employee_id FROM employee')
    return employee_ids.as_dict()


@app.route('/menu')
def menu():
	return render_template('menu.html', data=getMenuItems())
def getMenuItems():
	data = db.query('select * from menu_items')
	return data.as_dict()
@app.route('/menu/sub', methods=['POST'])
def subItem():
	itemName = request.form.get('nameSubField')
	itemPrice = request.form.get('priceSubField')
	
	if itemName and itemPrice: 
		check = db.query('select * from menu_items where item_name = "{}"'.format(itemName))	
		if not check.as_dict():		
			db.query('insert into menu_items values ("{}", {})'.format(itemName, itemPrice))
			return render_template('menu.html', data=getMenuItems())
		else:
			return render_template('menu.html', data=getMenuItems(), error=True)
	else:
		return render_template('menu.html', data=getMenuItems(), error=True)

@app.route('/menu/del', methods=['POST'])
def delItem():
	itemName= request.form.get('nameDelField')
	db.query('delete from menu_items where item_name = "{}"'.format(itemName))
	return render_template('menu.html', data=getMenuItems())


@app.route('/orders')
def orders():
	return render_template('orders.html', orderList=getOrders())
def getOrders():
	orderList=db.query('select distinct last_name, order_number from orders natural join employee')
	return orderList.as_dict()
@app.route('/orders', methods=['POST'])
def orderDetails():
	orderNum = request.form.get('orderNum')
	managerNameQ = db.query('select last_name from orders natural join employee where order_number = {}'.format(orderNum)).as_dict()
	if managerNameQ:	
		return render_template('orders.html', orderList=getOrders(), orderInfo=getOrderDetails(orderNum), orderID= orderNum, managerName= managerNameQ[0]['last_name'])
	else:
		return render_template('orders.html', orderList=getOrders())
def getOrderDetails(orderNum):
	orderInfo = db.query('select stock_name, reorder_id from orders natural join employee natural join inventory where order_number = {}'.format(orderNum))
	return orderInfo.as_dict()


@app.route('/inventory')
def inventory():
	return render_template('Inventory.html', invList=getInvList())
def getInvList():
	data = db.query('select * from inventory natural join supplied_by natural join vendor')
	return data.as_dict()
@app.route('/inventory', methods=['POST'])
def vendDetails():
	vendID = request.form.get('vendorID')
	return render_template('Inventory.html', invList=getInvList(), vendor=getVendDetails(vendID))
def getVendDetails(vendID):
	data = db.query('select * from vendor where vendor_id = {}'.format(vendID))
	return data.as_dict()

def add_employee(employee_id, first_name, last_name, pay, phone):
    all_ids = get_all_employee_ids()
    db.query('INSERT INTO employee (employee_id, first_name, last_name, start_date, phone, hourly_pay) VALUES ({}, "{}", "{}", sysdate(), {}, "{}")'.format(employee_id, first_name, last_name, pay, phone)) 
    return

def add_server(employee_id):
    db.query('INSERT INTO server VALUES ({})'.format(employee_id))
    return


def add_manager(employee_id):
    db.query('INSERT INTO manager VALUES ({})'.format(employee_id))
    return

def find_morning_shifts(date):
    shifts = db.query('SELECT last_name, start_time, end_time  FROM shift NATURAL JOIN employee WHERE start_time = "08:00:00" AND shift_date = "{}"'.format(date))
    return shifts.as_dict() 

def find_evening_shifts(date):
    shifts = db.query('SELECT last_name, start_time, end_time  FROM shift NATURAL JOIN employee WHERE start_time = "16:00:00" AND shift_date = "{}"'.format(date))
    return shifts.as_dict() 

def insert_shift(employee_id, date, shift):
    if shift == 'morning':
        db.query('INSERT INTO shift VALUES ({}, "08:00:00", "16:00:00", "{}")'.format(employee_id, date))
    elif shift == 'evening':
        db.query('INSERT INTO shift VALUES ({}, "16:00:00", "22:00:00", "{}")'.format(employee_id, date))
    return

@app.route('/pay')
def wages():
	return render_template('pay.html');

@app.route('/pay', methods=['POST'])	
def getWages():	
	empID = request.form.get('idField')
	startDate = request.form.get('startDate')
	endDate = request.form.get('endDate')
	wage = fetchWages(empID, startDate, endDate)
	hour = fetchHours(empID, startDate, endDate)
	tip = fetchTips(empID, startDate, endDate)
	order = fetchOrders(empID, startDate, endDate)
	if wage and hour:	
		if order:
			return render_template('pay.html', wages = wage[0]['pay'], hours = hour[0]['hours'], tips = tip[0]['tip_total'], orders = order[0]['order_count']);
		else:
			return render_template('pay.html', wages = wage[0]['pay'], hours = hour[0]['hours']);
	else:
		return render_template('pay.html', error=True);

def fetchWages(empID, startDate, endDate):
	data = db.query('select time_to_sec(hours) * hourly_pay/(3600) as "pay" from (select employee_id, sec_to_time( sum(time_to_sec(shift_hours))) as "hours" from (select employee_id, timediff(end_time, start_time) as "shift_hours" from shift where employee_id = {} and shift_date <= "{}" and shift_date >= "{}") as t1) as t2 natural join employee'.format(empID, endDate, startDate))
	return data.as_dict()

def fetchHours(empID, startDate, endDate):
	data = db.query('select sec_to_time( sum(time_to_sec(shift_hours))) as "hours" from (select timediff(end_time, start_time) as "shift_hours" from shift where employee_id = {} and shift_date <= "{}" and shift_date >= "{}") as t1'.format(empID, endDate, startDate))
	return data.as_dict()

def fetchTips(empID, startDate, endDate):
	data = db.query('select sum(tip) as "tip_total" from (select * from ticket where employee_id = {} and date(transaction_datetime) <= "{}" and date(transaction_datetime) >= "{}") as t1'.format(empID, endDate, startDate))
	return data.as_dict()

def fetchOrders(empID, startDate, endDate):
	data = db.query('select count(*) as "order_count" from ticket where employee_id = "{}" and date(transaction_datetime) <= "{}" and date(transaction_datetime) >= "{}"'.format(empID, endDate, startDate))
	return data.as_dict()

