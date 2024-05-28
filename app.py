from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from joblib import load
from sqlalchemy import text
import pandas as pd


# Load the machine learning model
model = load('isolation_forest_model.joblib')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(6), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    approved = db.Column(db.Float, nullable=True)
    backend_reversed = db.Column(db.Float, nullable=True)
    denied = db.Column(db.Float, nullable=True)
    failed = db.Column(db.Float, nullable=True)
    processing = db.Column(db.Float, nullable=True)
    refunded = db.Column(db.Float, nullable=True)
    reversed = db.Column(db.Float, nullable=True)
    total = db.Column(db.Float, nullable=True)
    success_rate = db.Column(db.Float, nullable=True)
    denial_rate  = db.Column(db.Float, nullable=True)
    reversal_rate = db.Column(db.Float, nullable=True)
    failure_rate = db.Column(db.Float, nullable=True)
    z_score = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    # Receive transaction data from the request
    transaction_data = request.get_json()

    # Extract data from the received JSON
    time = transaction_data.get('time')
    hour = transaction_data.get('hour')
    minute = transaction_data.get('minute')
    approved = transaction_data.get('approved')
    backend_reversed = transaction_data.get('backend_reversed')
    denied = transaction_data.get('denied')
    failed = transaction_data.get('failed')
    processing = transaction_data.get('processing')
    refunded = transaction_data.get('refunded')
    reversed = transaction_data.get('reversed')
    total = transaction_data.get('total')
    success_rate = transaction_data.get('success_rate')
    denial_rate = transaction_data.get('denial_rate')
    reversal_rate = transaction_data.get('reversal_rate')
    failure_rate = transaction_data.get('failure_rate')

    # Prepare data for prediction in the correct order
    feature_dict = {
        'approved': [approved],
        'backend_reversed': [backend_reversed],
        'denied': [denied],
        'failed': [failed],
        'processing': [processing],
        'reversed': [reversed],
        'total': [total],
        'success_rate': [success_rate],
        'reversal_rate': [reversal_rate],
        'denial_rate': [denial_rate],
        'failure_rate': [failure_rate],
        'hour': [hour],
        'minute': [minute]
    }
    feature_df = pd.DataFrame(feature_dict)
    feature_df = feature_df.fillna(0)
    print(feature_df)
    # Make a prediction
    prediction = model.decision_function(feature_df)
    # Create a new Transaction object
    new_transaction = Transaction(
        time=time,
        hour=hour,
        minute=minute,
        approved=approved,
        backend_reversed=backend_reversed,
        denied=denied,
        failed=failed,
        processing=processing,
        refunded=refunded,
        reversed=reversed,
        total=total,
        success_rate=success_rate,
        denial_rate=denial_rate,
        reversal_rate=reversal_rate,
        failure_rate=failure_rate,
        z_score=prediction[0]
    )

    # Construct the response
    response = {
        "time": str(time),
        "score_test": [
            {
                "is_anomalous": str(prediction[0] < 0),
                "value": float(prediction[0]),
                "description": "model score"
            }
        ],
        "reversal_test": [
            {
                "is_anomalous": str(reversal_rate > 0.10),
                "value": float(reversal_rate),
                "description": "reversal rate"
            }
        ],
        "failure_test": [
            {
                "is_anomalous": str(failure_rate > 0.001),
                "value": float(failure_rate),
                "description": "failure rate"
            }
        ],
        "denial_test": [
            {
                "is_anomalous": str(denial_rate > 0.1 and total >= 30),
                "value": float(denial_rate),
                "description": "denial rate. Triggers only if total >= 30."
            }
        ],
        "overall_test": [
            {
                "is_anomalous": str((denial_rate > 0.1 and total >= 30) or \
                                    failure_rate > 0.001 or \
                                       reversal_rate > 0.10 or \
                                        prediction[0] < 0),
                "description": "overalltest. True if any test is true"
            }
        ]
    }

    # Save the transaction to the database
    with app.app_context():
        db.session.add(new_transaction)
        db.session.commit()

    # Respond with the JSON message
    return jsonify(response), 200

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        # Query all transactions from the Transaction table
        transactions = Transaction.query.all()

        # Convert transactions to a list of dictionaries for JSON serialization
        transaction_list = []
        for transaction in transactions:
            transaction_dict = {
                'id': transaction.id,
                'time': transaction.time,
                'hour': transaction.hour,
                'minute': transaction.minute,
                'approved': transaction.approved,
                'backend_reversed': transaction.backend_reversed,
                'denied': transaction.denied,
                'failed': transaction.failed,
                'processing': transaction.processing,
                'refunded': transaction.refunded,
                'reversed': transaction.reversed,
                'total': transaction.total,
                'success_rate': transaction.success_rate,
                'denial_rate': transaction.denial_rate,
                'reversal_rate': transaction.reversal_rate,
                'failure_rate': transaction.failure_rate,
                'z_score': transaction.z_score
            }
            transaction_list.append(transaction_dict)

        # Return JSON response with transaction data
        return jsonify(transaction_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def check_alerts():
    try:
        # Query the latest transaction from the database
        latest_transaction = Transaction.query.order_by(Transaction.id.desc()).first()

        # Check if any triggers are true
        is_anomalous = latest_transaction.z_score < 0
        is_reversal_alert = latest_transaction.reversal_rate > 0.10
        is_failure_alert = latest_transaction.failure_rate > 0.001
        is_denial_alert = latest_transaction.denial_rate > 0.1 and latest_transaction.total >= 30

        # Construct the alert message
        alert_message = {
            "is_anomalous": is_anomalous,
            "is_reversal_alert": is_reversal_alert,
            "is_failure_alert": is_failure_alert,
            "is_denial_alert": is_denial_alert
        }

        # Example: Sending an email if any alert is true (replace with your actual alert method)
        if any(alert_message.values()):
            send_email_alert(alert_message)  # Implement this function

        # Return the alert status as JSON
        return jsonify(alert_message), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_email_alert(alert_message):
    # Example implementation: Sending an email using Flask-Mail or another library
    # Replace the placeholders with your email sending logic
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    sender_email = 'your_email@gmail.com'
    receiver_email = 'recipient_email@gmail.com'
    password = 'your_email_password'

    subject = 'Alert: Anomaly Detected in Transactions'
    body = f"Alert message: {alert_message}"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
