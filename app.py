
from flask import Flask, request, jsonify, send_from_directory
import smtplib, os, base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

app = Flask(__name__)

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "a.Sayed@alfa-logistics.com")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/health')
def health():
    return "OK - ALFA Server Running"

@app.route('/send-excel', methods=['POST'])
def send_excel():
    try:
        data = request.get_json()
        to_emails = data.get('to', '')
        cc_emails = data.get('cc', '')
        client = data.get('client', 'No Name')
        receipt = data.get('receipt', '')
        file_name = data.get('fileName', 'Warehouse Putaway Report.xlsx')
        file_base64 = data.get('fileBase64', '')

        if not APP_PASSWORD:
            return jsonify({"success": False, "message": "السيرفر مش متظبط - APP_PASSWORD ناقص في Render"}), 500
        if not to_emails:
            return jsonify({"success": False, "message": "اكتب إيميل To"}), 400
        if not file_base64:
            return jsonify({"success": False, "message": "مفيش ملف"}), 400

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_emails
        if cc_emails:
            msg['Cc'] = cc_emails
        msg['Subject'] = f"Warehouse Putaway Report - {client} - {receipt} - {datetime.now().strftime('%d-%m-%Y %H:%M')}"

        body = f"""Hello,

Please find attached Warehouse Putaway Report.

Client: {client}
Receipt: {receipt}
Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
File: {file_name}

Sent by: Ahmed Sayed - 01009407471
Alfa Logistics - Auto-sent via Python Server (Mobile Ready)

This is an automated email.
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        file_data = base64.b64decode(file_base64.split(',')[1] if ',' in file_base64 else file_base64)
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        recipients = [e.strip() for e in to_emails.split(',')] + [e.strip() for e in cc_emails.split(',') if e.strip()]
        recipients = [r for r in recipients if r]
        
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        server.quit()

        return jsonify({"success": True, "message": f"✅ تم الإرسال بنجاح إلى {to_emails} من الموبايل!"})

    except Exception as e:
        return jsonify({"success": False, "message": f"❌ خطأ: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
