from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import mysql
from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
import os

invoices = Blueprint('invoices', __name__)

@invoices.route('/invoices')
@login_required
def list_invoices():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.*, c.name as client_name 
        FROM invoices i 
        JOIN clients c ON i.client_id = c.id
        WHERE i.user_id = %s
        ORDER BY i.created_at DESC
    """, (current_user.id,))
    all_invoices = cur.fetchall()
    cur.close()
    return render_template('invoices/list.html', invoices=all_invoices)

@invoices.route('/invoices/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        client_id = request.form['client_id']
        invoice_number = request.form['invoice_number']
        issue_date = request.form['issue_date']
        due_date = request.form['due_date']
        tax = request.form.get('tax', 0)
        notes = request.form.get('notes', '')
        status = 'draft'

        # Save invoice
        cur.execute("""
            INSERT INTO invoices (user_id, client_id, invoice_number, issue_date, due_date, tax, notes, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (current_user.id, client_id, invoice_number, issue_date, due_date, tax, notes, status))
        mysql.connection.commit()
        invoice_id = cur.lastrowid

        # Save line items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        units = request.form.getlist('unit[]')
        
        for i in range(len(descriptions)):
            if descriptions[i].strip():
                cur.execute("""
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit, unit_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (invoice_id, descriptions[i], quantities[i], units[i], unit_prices[i]))

        mysql.connection.commit()
        cur.close()
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('invoices.list_invoices'))

    # Get clients for dropdown
    cur.execute("SELECT * FROM clients WHERE user_id = %s", (current_user.id,))
    
    all_clients = cur.fetchall()
    cur.execute("SELECT * FROM products WHERE user_id = %s ORDER BY name", (current_user.id,))
    all_products = cur.fetchall()
    cur.close()

    # Generate invoice number
    import random
    invoice_number = f"INV-{random.randint(1000, 9999)}"

    return render_template('invoices/create.html', clients=all_clients, 
                       invoice_number=invoice_number, products=all_products)
@invoices.route('/invoices/view/<int:id>')
@login_required
def view_invoice(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.*, c.name as client_name, c.email as client_email,
               c.phone as client_phone, c.address as client_address
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE i.id = %s AND i.user_id = %s
    """, (id, current_user.id))
    invoice = cur.fetchone()

    cur.execute("SELECT * FROM invoice_items WHERE invoice_id = %s", (id,))
    items = cur.fetchall()
    cur.close()

    # Calculate totals
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * (invoice['tax'] / 100)
    total = subtotal + tax_amount

    return render_template('invoices/view.html', invoice=invoice, items=items,
                           subtotal=subtotal, tax_amount=tax_amount, total=total)

@invoices.route('/invoices/status/<int:id>/<string:status>')
@login_required
def update_status(id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE invoices SET status = %s WHERE id = %s AND user_id = %s",
                (status, id, current_user.id))
    mysql.connection.commit()
    cur.close()
    flash(f'Invoice marked as {status}!', 'success')
    return redirect(url_for('invoices.view_invoice', id=id))

@invoices.route('/invoices/delete/<int:id>')
@login_required
def delete_invoice(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM invoice_items WHERE invoice_id = %s", (id,))
    cur.execute("DELETE FROM invoices WHERE id = %s AND user_id = %s", (id, current_user.id))
    mysql.connection.commit()
    cur.close()
    flash('Invoice deleted!', 'success')
    return redirect(url_for('invoices.list_invoices'))

#pdf 

@invoices.route('/invoices/pdf/<int:id>')
@login_required
def download_pdf(id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.*, c.name as client_name, c.email as client_email,
               c.phone as client_phone, c.address as client_address
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE i.id = %s AND i.user_id = %s
    """, (id, current_user.id))
    invoice = cur.fetchone()

    cur.execute("SELECT * FROM invoice_items WHERE invoice_id = %s", (id,))
    items = cur.fetchall()
    cur.close()

    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * (invoice['tax'] / 100)
    total = subtotal + tax_amount

    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"INVOICE - {invoice['invoice_number']}", styles['Title']))
    elements.append(Spacer(1, 0.2*inch))

    # Invoice details
    details = [
        ['Issue Date:', str(invoice['issue_date']), 'Status:', invoice['status'].upper()],
        ['Due Date:', str(invoice['due_date']), '', ''],
    ]
    details_table = Table(details, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('TEXTCOLOR', (2,0), (2,-1), colors.grey),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 0.2*inch))

    # Bill To
    elements.append(Paragraph("Bill To:", styles['Heading2']))
    elements.append(Paragraph(f"<b>{invoice['client_name']}</b>", styles['Normal']))
    elements.append(Paragraph(invoice['client_email'] or '', styles['Normal']))
    elements.append(Paragraph(invoice['client_phone'] or '', styles['Normal']))
    elements.append(Paragraph(invoice['client_address'] or '', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Items table
    table_data = [['Description', 'Qty', 'Unit', 'Unit Price', 'Total']]
    for item in items:
        table_data.append([
            item['description'],
            str(item['quantity']),
            item['unit'] or 'sq ft',
            f"${item['unit_price']:.2f}",
            f"${item['quantity'] * item['unit_price']:.2f}"
        ])

    items_table = Table(table_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))

    # Totals
    totals_data = [
        ['', '', '', 'Subtotal:', f'${subtotal:.2f}'],
        ['', '', '', f'Tax ({invoice["tax"]}%):', f'${tax_amount:.2f}'],
        ['', '', '', 'TOTAL:', f'${total:.2f}'],
    ]
    totals_table = Table(totals_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    totals_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (3,2), (-1,2), 'Helvetica-Bold'),
        ('FONTSIZE', (3,2), (-1,2), 12),
        ('LINEABOVE', (3,2), (-1,2), 1, colors.black),
    ]))
    elements.append(totals_table)

    # Notes
    if invoice['notes']:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Notes:", styles['Heading3']))
        elements.append(Paragraph(invoice['notes'], styles['Normal']))

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Thank you for your business! Generated by InvoiceApp", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice-{invoice["invoice_number"]}.pdf'
    return response