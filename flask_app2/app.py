from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

import boto3

sqs = boto3.client('sqs',
                   aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                   aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                   region_name=os.getenv("AWS_REGION"))

app = Flask(__name__)

@app.route("/send/<msg>")
def send_sqs_msg(msg):
    queue_url = 'https://sqs.us-east-1.amazonaws.com/556856552954/saurabh-test-queue'

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=f'Hello from Python SQS! {msg}'
    )
    return f"Message ID:, {response['MessageId']}"

@app.route("/receive/")
def receive_sqs_msg():
    queue_url = 'https://sqs.us-east-1.amazonaws.com/556856552954/saurabh-test-queue'

    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=5,
        WaitTimeSeconds=10,
    )
    
    messages = response.get('Messages', [])
    if messages:
        msg_list = []
        for msg in messages:
            # Optional: delete after reading
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
            msg_list.append(msg['Body'])
        return msg_list
    else:
        return "No messages received."
