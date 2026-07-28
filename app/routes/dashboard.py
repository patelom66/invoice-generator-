from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import mysql

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()

    # Total clients
    cur.execute("SELECT COUNT(*) as count FROM clients WHERE user_id = %s", (current_user.id,))
    total_clients = cur.fetchone()['count']

    # Invoice stats (we'll use 0 for now, invoices come in Week 3)
    total_invoices = 0
    paid_invoices = 0
    pending_invoices = 0
    overdue_invoices = 0
    total_revenue = 0

    cur.close()

    return render_template('dashboard.html',
        user=current_user,
        total_clients=total_clients,
        total_invoices=total_invoices,
        paid_invoices=paid_invoices,
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices,
        total_revenue=total_revenue
    )