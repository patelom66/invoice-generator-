from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import mysql

clients = Blueprint('clients', __name__)

@clients.route('/clients')
@login_required
def list_clients():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clients WHERE user_id = %s", (current_user.id,))
    all_clients = cur.fetchall()
    cur.close()
    return render_template('clients/list.html', clients=all_clients)

@clients.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO clients (user_id, name, email, phone, address) VALUES (%s, %s, %s, %s, %s)",
                    (current_user.id, name, email, phone, address))
        mysql.connection.commit()
        cur.close()
        flash('Client added successfully!', 'success')
        return redirect(url_for('clients.list_clients'))

    return render_template('clients/add.html')

@clients.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        cur.execute("""UPDATE clients SET name=%s, email=%s, phone=%s, address=%s
                       WHERE id=%s AND user_id=%s""",
                    (name, email, phone, address, id, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Client updated!', 'success')
        return redirect(url_for('clients.list_clients'))

    cur.execute("SELECT * FROM clients WHERE id = %s AND user_id = %s", (id, current_user.id))
    client = cur.fetchone()
    cur.close()
    return render_template('clients/edit.html', client=client)

@clients.route('/clients/delete/<int:id>')
@login_required
def delete_client(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM clients WHERE id = %s AND user_id = %s", (id, current_user.id))
    mysql.connection.commit()
    cur.close()
    flash('Client deleted!', 'success')
    return redirect(url_for('clients.list_clients'))