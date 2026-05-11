#!/usr/bin/env python3

"""
To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import json
from sqlalchemy import *
from sqlalchemy import text, exc
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify
from random import randint

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except Exception:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """
    user_id = request.args.get('id')
    script_dir = os.path.dirname(__file__)
    rel_path = "queries/vehicle_class.sql"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path, 'r') as f:
        query = f.read()
    cursor = g.conn.execute(text(query.rstrip()))
    rates = []
    for row in cursor:
        rates.append(list(row))
    if user_id is not None:
        query = "SELECT * FROM Addresses A WHERE A.uid={}".format(user_id)
        cursor = g.conn.execute(text(query))
        address = []
        address.append([0, 'null', 'Select a saved address'])
        for row in cursor:
            addr = list(row)
            final_addr = [
                addr[0],
                addr[1] + ' ' + addr[3] + ' ' + addr[4],
                addr[5] + ' - ' + addr[1] + ' ' + addr[3] + ' ' + addr[4]
            ]
            address.append(final_addr)
        data = {'rates': rates, 'id': user_id, 'addresses': address}
    else:
        data = {'rates': rates, 'id': user_id}
    return render_template("index.html", data=data)


@app.route('/reservations')
def reservations():
    user_id = request.args.get('id')
    data = {'id': user_id}
    return render_template("reservations.html", data=data)


@app.route('/confirm-user')
def confirm_user():
    user_id = request.args.get('id')
    query = (
        "SELECT Users.uid FROM "
        "(SELECT uid FROM Passengers UNION SELECT uid FROM Drivers) AS Users "
        "WHERE Users.uid={}".format(user_id)
    )
    cursor = g.conn.execute(text(query))
    record = cursor.fetchone()
    results = list(record) if record is not None else []
    return jsonify(data=results)


@app.route('/get-current')
def pass_current_reservations():
    user_id = request.args.get('id')
    query = (
        "SELECT to_char(T.date, 'YYYY-MM-DD') AS date, to_char(T.time, 'HH:MI:SS') AS time, "
        "T.type, T.distance, T.pick_addr, T.drop_addr, T.est_amount, T.tid, D.name, D.phone "
        "FROM Trips T, Drivers D "
        "WHERE T.passenger={} AND T.driver=D.uid AND T.status='reserved' "
        "ORDER BY T.date, T.time".format(user_id)
    )
    cursor = g.conn.execute(text(query))
    reservations = [list(row) for row in cursor]
    data = {'reservations': reservations, 'id': user_id}
    return jsonify(data=data)


@app.route('/get-past')
def pass_past_reservations():
    user_id = request.args.get('id')
    query = (
        "SELECT to_char(T.date, 'YYYY-MM-DD') AS date, to_char(T.time, 'HH:MI:SS') AS time, "
        "T.type, T.distance, T.pick_addr, T.drop_addr, T.est_amount, T.tid, T.drating "
        "FROM Trips T "
        "WHERE T.passenger={} AND T.status='completed' "
        "ORDER BY T.date, T.time".format(user_id)
    )
    cursor = g.conn.execute(text(query))
    reservations = [list(row) for row in cursor]
    data = {'reservations': reservations, 'id': user_id}
    return jsonify(data=data)


@app.route('/search-drivers')
def search_drivers():
    date = request.args.get('date')
    time1 = request.args.get('time1')
    time2 = request.args.get('time2')
    vclass = request.args.get('class')
    query = (
        "SELECT D.uid, D.name, D.rating, V.make, V.model, V.capacity "
        "FROM drivers D, vehicles V "
        "WHERE D.uid=V.uid AND V.cname='{}' "
        "AND D.uid NOT IN ("
        "  SELECT T.driver FROM Trips T "
        "  WHERE T.date='{}' AND T.time>='{}' AND T.time<='{}')"
        ";".format(vclass, date, time1, time2)
    )
    cursor = g.conn.execute(text(query))
    results = [list(row) for row in cursor]
    return jsonify(data=results)


@app.route('/create-user')
def create_user():
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    query = "INSERT INTO Passengers (name, email, phone) VALUES ('{}', '{}', '{}') RETURNING uid;".format(
        name, email, phone
    )
    try:
        cursor = g.conn.execute(text(query))
        record = cursor.fetchone()
        results = list(record)
        data = {'error': 0, 'data': results}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        data = {'error': 1, 'message': str(e)}
        return jsonify(data=data)


@app.route('/assign-rating')
def assign_rating():
    user = request.args.get('userid')
    trip = request.args.get('tripid')
    rating = request.args.get('rating')
    stmt2 = "UPDATE Trips SET (drating) = ({}) WHERE tid={}".format(rating, trip)
    try:
        g.conn.execute(text(stmt2))
        data = {'error': 0, 'data': None}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        data = {'error': 1, 'message': str(e)}
        return jsonify(data=data)


@app.route('/cancel-trip')
def cancel_trip():
    trip = request.args.get('tripid')
    stmt2 = "DELETE FROM Trips T WHERE T.tid={};".format(trip)
    try:
        g.conn.execute(text(stmt2))
        data = {'error': 0, 'data': None}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        data = {'error': 1, 'message': str(e)}
        return jsonify(data=data)


@app.route('/save-address')
def save_address():
    user = request.args.get('id')
    label = request.args.get('label').strip()
    addr = request.args.get('addr').strip()
    city = request.args.get('city').strip()
    state = request.args.get('state').strip()
    query = (
        "INSERT INTO Addresses (uid, street1, city, state, label) "
        "VALUES ({}, '{}', '{}', '{}', '{}') RETURNING uid;".format(user, addr, city, state, label)
    )
    try:
        cursor = g.conn.execute(text(query))
        record = cursor.fetchone()
        results = list(record)
        data = {'error': 0, 'data': results}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        data = {'error': 1, 'message': str(e)}
        return jsonify(data=data)


@app.route('/create-trip')
def create_trip():  # fixed typo: "craete_trip" -> "create_trip"
    user = request.args.get('pid')
    driver = request.args.get('did')
    paddr = request.args.get('paddr')
    daddr = request.args.get('daddr').strip()
    dist = request.args.get('dist')
    amt = request.args.get('amt')
    date = request.args.get('date')
    time = request.args.get('time')
    ftype = request.args.get('type')
    status = 'reserved'
    query = (
        "INSERT INTO Trips (date, time, distance, status, type, est_amount, pick_addr, drop_addr, driver, passenger) "
        "VALUES ('{}', '{}', {}, '{}', '{}', {}, '{}', '{}', {}, {}) RETURNING tid;".format(
            date, time, dist, status, ftype, amt, paddr, daddr, driver, user
        )
    )
    try:
        cursor = g.conn.execute(text(query))
        record = cursor.fetchone()
        results = list(record)
        data = {'error': 0, 'data': results}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        data = {'error': 1, 'message': str(e)}
        return jsonify(data=data)


# drivers page
@app.route('/drivers')
def drivers():
    user_id = request.args.get('id')
    data = {'id': user_id}
    return render_template("drivers.html", data=data)


# get driver's current reservations
@app.route('/get-current-reservations')
def get_current_reservations():
    user_id = request.args.get('id')
    # for reference, column indices are: 0=name, 1=phone, 2=date, 3=time, 4=type,
    # 5=distance, 6=pick_addr, 7=drop_addr, 8=est_amount, 9=tid
    query = (
        "SELECT P.name, P.phone, to_char(T.date, 'YYYY-MM-DD') AS date, "
        "to_char(T.time, 'HH:MI:SS') AS time, T.type, T.distance, T.pick_addr, T.drop_addr, "
        "T.est_amount, T.tid "
        "FROM Trips T, Passengers P "
        "WHERE T.driver={} AND T.passenger=P.uid AND T.status!='completed' "
        "ORDER BY T.date, T.time".format(user_id)
    )
    cursor = g.conn.execute(text(query))
    reservations = [list(row) for row in cursor]
    data = {'reservations': reservations, 'id': user_id}
    return jsonify(data=data)


# driver entering completed trip information
@app.route('/complete-trip')
def complete_trip():
    user_id = request.args.get('id')
    tid = request.args.get('comptid').rstrip()
    amount = request.args.get('tamtcharged').rstrip()
    paytype = request.args.get('tpaytype').rstrip()
    prating = request.args.get('tpassrating').rstrip()

    if paytype.lower() not in ['cash', 'amex', 'visa', 'mc']:
        message = "Invalid payment type; must be CASH, MC, VISA, or AMEX."
        data = {'error': 1, 'message': message, 'id': user_id}
        return jsonify(data=data)

    if paytype in ('AMEX', 'VISA', 'MC'):
        auth = randint(1, 2147483647)
        stmt = "INSERT INTO Transactions (pay_type, auth_id, amt_charged, tid) VALUES ('{}', {}, {}, {})".format(
            paytype, auth, amount, tid
        )
    else:
        stmt = "INSERT INTO Transactions (pay_type, amt_charged, tid) VALUES ('{}', {}, {})".format(
            paytype, amount, tid
        )
    try:
        g.conn.execute(text(stmt))
        stmt2 = "UPDATE Trips SET (status, prating) = ('completed', {}) WHERE tid={}".format(prating, tid)
        g.conn.execute(text(stmt2))
        data = {'error': 0, 'id': user_id}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        print(str(e))
        message = "Error entering trip information, check form entries."
        data = {'error': 1, 'message': message, 'id': user_id}
        return jsonify(data=data)


# driver getting completed trip info
@app.route('/get-past-trips')
def get_past_trips():
    user_id = request.args.get('id')
    start = request.args.get('start').rstrip()
    end = request.args.get('end').rstrip()

    base = (
        "SELECT P.name, to_char(T.date, 'YYYY-MM-DD') AS date, to_char(T.time, 'HH:MI:SS') AS time, "
        "T.est_amount, TR.amt_charged, T.drating, T.prating, T.tid "
        "FROM Trips T, Transactions TR, Passengers P "
        "WHERE T.status='completed' AND T.tid=TR.tid AND T.passenger=P.uid "
        "AND T.driver={}".format(user_id)
    )

    if start == '' and end == '':
        query = base
    elif start == '':
        query = base + " AND T.date <= '{}'".format(end)
    elif end == '':
        query = base + " AND T.date >= '{}'".format(start)
    else:
        query = base + " AND T.date >= '{}' AND T.date <= '{}'".format(start, end)

    try:
        cursor = g.conn.execute(text(query))
        trips = [list(row) for row in cursor]
        data = {'error': 0, 'id': user_id, 'trips': trips}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        print(str(e))
        message = "Error retrieving past trips, check date range formats."
        data = {'error': 1, 'message': message, 'id': user_id}
        return jsonify(data=data)


# show driver's vehicles
@app.route('/show-vehicles')
def show_vehicles():
    user_id = request.args.get('id')
    query = "SELECT V.plate_no, V.make, V.model, V.capacity, V.cname FROM Vehicles V WHERE V.uid={}".format(user_id)
    cursor = g.conn.execute(text(query))
    vehicles = [list(row) for row in cursor]
    data = {'id': user_id, 'vehicles': vehicles}
    return jsonify(data=data)


# add a vehicle
@app.route('/add-vehicle')
def add_vehicle():
    user_id = request.args.get('id')
    vplate = request.args.get('vplate').rstrip()
    vmake = request.args.get('vmake').rstrip()
    vmodel = request.args.get('vmodel').rstrip()
    vcapacity = request.args.get('vcapacity').rstrip()
    vclass = request.args.get('vclass').rstrip().lower()

    if vclass not in ['suplux', 'econ', 'lux', 'suv']:
        message = "Invalid vehicle class; must be econ, lux, suplux, or suv."
        data = {'error': 1, 'message': message, 'id': user_id}
        return jsonify(data=data)

    stmt = (
        "INSERT INTO Vehicles (plate_no, make, model, capacity, cname, uid) "
        "VALUES ('{}', '{}', '{}', {}, '{}', {})".format(vplate, vmake, vmodel, vcapacity, vclass, user_id)
    )
    try:
        g.conn.execute(text(stmt))
        data = {'error': 0, 'id': user_id}
        return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        print(str(e))
        message = "Error entering vehicle, check form entries. Note that drivers cannot share cars per company policy."
        data = {'error': 1, 'message': message, 'id': user_id}
        return jsonify(data=data)


# delete a vehicle
@app.route('/delete-vehicle')
def delete_vehicle():
    user_id = request.args.get('id')
    vplate = request.args.get('vplate').rstrip()
    stmt = "SELECT uid FROM Vehicles V WHERE V.plate_no='{}'".format(vplate)
    try:
        cursor = g.conn.execute(text(stmt))
        record = cursor.fetchone()
        if record is None:
            message = "Error: no vehicle matches entered license plate."
            data = {'error': 1, 'message': message, 'id': user_id}
            return jsonify(data=data)
        elif str(record[0]) != str(user_id):
            message = "Error: you can't delete a vehicle that doesn't belong to you!"
            data = {'error': 1, 'message': message, 'id': user_id}
            return jsonify(data=data)
        else:
            stmt = "DELETE FROM Vehicles V WHERE V.plate_no='{}'".format(vplate)
            g.conn.execute(text(stmt))
            data = {'error': 0, 'id': user_id}
            return jsonify(data=data)
    except exc.SQLAlchemyError as e:
        print(str(e))
        message = "Error deleting vehicle, check form entry."
        data = {'error': 1, 'message': message, 'id': user_id}
        return jsonify(data=data)


# show most frequent driver/passenger info and top/bottom rated driver info
@app.route('/admins')
def admins():
    user_id = request.args.get('id')
    query1 = (
        "SELECT P.uid, P.name, P.email, COUNT(P.uid), SUM(TR.amt_charged) "
        "FROM Passengers P, Trips T, Transactions TR "
        "WHERE P.uid=T.passenger AND T.tid=TR.tid "
        "GROUP BY P.uid, P.name, P.email ORDER BY COUNT(P.uid) DESC LIMIT 5"
    )
    query2 = (
        "SELECT D.uid, D.name, D.email, COUNT(D.uid), SUM(TR.amt_charged) "
        "FROM Drivers D, Trips T, Transactions TR "
        "WHERE D.uid=T.driver AND T.tid=TR.tid "
        "GROUP BY D.uid, D.name, D.email ORDER BY COUNT(D.uid) DESC LIMIT 5"
    )
    query3 = (
        "SELECT D.uid, D.name, D.email, D.rating, SUM(TR.amt_charged) "
        "FROM Drivers D, Trips T, Transactions TR "
        "WHERE D.uid=T.driver AND T.tid=TR.tid "
        "GROUP BY D.uid, D.name, D.email, D.rating ORDER BY D.rating DESC LIMIT 5"
    )
    query4 = (
        "SELECT D.uid, D.name, D.email, D.rating, SUM(TR.amt_charged) "
        "FROM Drivers D, Trips T, Transactions TR "
        "WHERE D.uid=T.driver AND T.tid=TR.tid "
        "GROUP BY D.uid, D.name, D.email, D.rating ORDER BY D.rating ASC LIMIT 5"
    )
    topfc = [list(row) for row in g.conn.execute(text(query1))]
    topfd = [list(row) for row in g.conn.execute(text(query2))]
    toprd = [list(row) for row in g.conn.execute(text(query3))]
    lowrd = [list(row) for row in g.conn.execute(text(query4))]
    data = {'topfc': topfc, 'topfd': topfd, 'toprd': toprd, 'lowrd': lowrd, 'id': user_id}
    return render_template("admins.html", data=data)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """
        HOST, PORT = host, port
        print(f"running on {HOST}:{PORT}")
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
