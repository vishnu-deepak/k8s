from flask import Flask, render_template, request, redirect
import boto3
import json
import os
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# AWS SQS configuration
region = os.environ.get('AWS_REGION')
queue_url = os.environ.get('QUEUE_URL')

# Create an SQS client
sqs = boto3.client('sqs', region_name=region)

# Define Prometheus Metrics
REQUEST_COUNT = Counter('flask_app_request_count', 'Total number of requests')

# Function to store data in SQS
def store_data_in_sqs(name, email, additional_data):
    data = {
        'name': name,
        'email': email,
        'additionalData': additional_data
    }

    message_body = json.dumps(data)

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )

    return response

# Homepage route
@app.route('/')
def index():
    REQUEST_COUNT.inc()
    return render_template('index.html')

# Store data route
@app.route('/store_data', methods=['POST'])
def store_data():
    name = request.form.get('name')
    email = request.form.get('email')
    additional_data = request.form.get('additional_data')

    response = store_data_in_sqs(name, email, additional_data)
    print("Data inserted successfully")

    return "success"

# Create Prometheus WSGI Middleware
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app_dispatch)
