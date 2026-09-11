import json
import os

import boto3

sqs_client = boto3.client("sqs")
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]


def lambda_handler(event, context):
    for record in event["Records"]:
        event_name = record["eventName"]
        new_image = record.get("dynamodb", {}).get("NewImage", {})
        old_image = record.get("dynamodb", {}).get("OldImage", {})
        message = {
            "eventName": event_name,
            "newImage": new_image,
            "oldImage": old_image,
        }

        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message),
        )
        print(f"Message envoye a SQS: {response['MessageId']}")

    return {"statusCode": 200, "body": "Processed records"}
