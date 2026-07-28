from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import mysql

settings = Blueprint('settings', __name__)

@settings.route('/settings', methods=['GET', 'POST'])
@login_required
def index():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        currency = request.form['currency']
        cur.execute("UPDATE users SET currency = %s WHERE id = %s",
                    (currency, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Settings saved!', 'success')
        return redirect(url_for('settings.index'))

    cur.execute("SELECT currency FROM users WHERE id = %s", (current_user.id,))
    user_data = cur.fetchone()
    cur.close()
    return render_template('settings.html', currency=user_data['currency'])