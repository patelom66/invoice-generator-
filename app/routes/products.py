from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import mysql

products = Blueprint('products', __name__)

@products.route('/products')
@login_required
def list_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE user_id = %s ORDER BY name", (current_user.id,))
    all_products = cur.fetchall()
    cur.close()
    return render_template('products/list.html', products=all_products)

@products.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        unit_price = request.form['unit_price']
        stock = request.form['stock']
        unit = request.form['unit']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO products (user_id, name, description, unit_price, stock, unit)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (current_user.id, name, description, unit_price, stock, unit))
        mysql.connection.commit()
        cur.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products.list_products'))

    return render_template('products/add.html')

@products.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        unit_price = request.form['unit_price']
        stock = request.form['stock']
        unit = request.form['unit']

        cur.execute("""
            UPDATE products SET name=%s, description=%s, unit_price=%s, stock=%s, unit=%s
            WHERE id=%s AND user_id=%s
        """, (name, description, unit_price, stock, unit, id, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Product updated!', 'success')
        return redirect(url_for('products.list_products'))

    cur.execute("SELECT * FROM products WHERE id=%s AND user_id=%s", (id, current_user.id))
    product = cur.fetchone()
    cur.close()
    return render_template('products/edit.html', product=product)

@products.route('/products/delete/<int:id>')
@login_required
def delete_product(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s AND user_id=%s", (id, current_user.id))
    mysql.connection.commit()
    cur.close()
    flash('Product deleted!', 'success')
    return redirect(url_for('products.list_products'))

@products.route('/products/get/<int:id>')
@login_required
def get_product(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id=%s AND user_id=%s", (id, current_user.id))
    product = cur.fetchone()
    cur.close()
    if product:
        return jsonify({
            'name': product['name'],
            'description': product['description'],
            'unit_price': float(product['unit_price']),
            'unit': product['unit']
        })
    return jsonify({}), 404