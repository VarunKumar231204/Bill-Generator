from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Fetch form data
        firm_name = request.form.get("firm_name")
        billed_to = request.form.get("billed_to", "")
        shipped_to = request.form.get("shipped_to", "")
        billing_address = request.form.get("billing_address", "")
        shipping_address = request.form.get("shipping_address", "")
        invoice_no = request.form.get("invoice_no", "0001")
        invoice_date = request.form.get("invoice_date", "")
        item_name = request.form.get("item_name", "")
        qty = int(request.form.get("qty", 0))
        rate = float(request.form.get("rate", 0.0))

        amount = qty * rate
        cgst = amount * 0.09
        sgst = amount * 0.09
        total_amount = amount + cgst + sgst

        # Generate PDF
        pdf_buffer = generate_invoice(
            firm_name, billed_to, shipped_to, billing_address,
            shipping_address, invoice_no, invoice_date, item_name,
            qty, rate, amount, cgst, sgst, total_amount
        )

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="invoice.pdf",
            mimetype="application/pdf"
        )

    return render_template("index.html")


def generate_invoice(firm_name, billed_to, shipped_to, billing_address, shipping_address,
                     invoice_no, invoice_date, item_name, qty, rate, amount, cgst, sgst, total_amount):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    start_y = height - 50  # Start position for elements

    # **Header Bar**
    c.setFillColor(colors.darkblue)
    c.rect(40, start_y, 520, 35, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(230, start_y + 10, "TAX INVOICE")
    
    # **Firm Details**
    start_y -= 50
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, start_y, firm_name)
    c.setFont("Helvetica", 10)
    c.drawString(50, start_y - 15, "ABC nagar , district, state")
    c.drawString(50, start_y - 30, "GSTIN: NAJEFAW48SAJDF | Mobile: 3215485464")
    
    # **Billing & Shipping Details**
    start_y -= 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, start_y, "Billed To:")
    c.drawString(300, start_y, "Shipped To:")
    c.setFont("Helvetica", 10)
    # Split long addresses into multiple lines
    billed_lines = billed_to.split("\n") + billing_address.split("\n")
    shipped_lines = shipped_to.split("\n") + shipping_address.split("\n")
    # Print Billed To address properly spaced
    for i, line in enumerate(billed_lines):
        c.drawString(50, start_y - 15 - (i * 15), line)
    # Print Shipped To address properly spaced
    for i, line in enumerate(shipped_lines):
        c.drawString(300, start_y - 15 - (i * 15), line)
    # Adjust `start_y` to prevent overlap below
    start_y -= max(len(billed_lines), len(shipped_lines)) * 15 + 20


    # **Invoice Info**
    start_y -= 50
    c.drawString(50, start_y, f"Invoice No: {invoice_no}")
    c.drawString(300, start_y, f"Invoice Date: {invoice_date}")

    # **Table Header**
    start_y -= 40
    c.setFillColor(colors.lightgrey)
    c.rect(40, start_y, 520, 25, fill=True, stroke=True)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, start_y + 8, "Sr.")
    c.drawString(90, start_y + 8, "Description")
    c.drawString(300, start_y + 8, "Qty")
    c.drawString(370, start_y + 8, "Rate")
    c.drawString(460, start_y + 8, "Amount")

    # **Table Content**
    start_y -= 25
    c.setFont("Helvetica", 10)
    c.rect(40, start_y, 520, 25, stroke=True, fill=False)
    c.drawString(50, start_y + 8, "1")
    c.drawString(90, start_y + 8, item_name)
    c.drawString(300, start_y + 8, str(qty))
    c.drawString(370, start_y + 8, f"{rate:.2f}")
    c.drawString(460, start_y + 8, f"{amount:.2f}")

    # **Taxes**
    start_y -= 30
    c.drawString(370, start_y, "CGST (9%):")
    c.drawString(460, start_y, f"{cgst:.2f}")
    start_y -= 15
    c.drawString(370, start_y, "SGST (9%):")
    c.drawString(460, start_y, f"{sgst:.2f}")

    # **Total Amount**
    start_y -= 30
    c.setFillColor(colors.lightgrey)
    c.rect(370, start_y, 190, 25, fill=True, stroke=True)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(380, start_y + 8, "Grand Total:")
    c.drawString(460, start_y + 8, f"₹{total_amount:.2f}")

    # **Authorized Signature**
    start_y -= 60
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, start_y, "Authorized Signatory")
    c.line(400, start_y - 5, 520, start_y - 5)

    # **Save PDF**
    c.save()
    buffer.seek(0)
    return buffer


if __name__ == "__main__":
    app.run(debug=True)
