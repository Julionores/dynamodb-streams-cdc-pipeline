"""Tests unitaires de la logique de traitement du stream DynamoDB."""

from unittest.mock import patch

from src.handler import lambda_handler


def _stream_record(
    event_name: str, new_image: dict | None = None, old_image: dict | None = None
):
    return {
        "eventName": event_name,
        "dynamodb": {
            "NewImage": new_image or {},
            "OldImage": old_image or {},
        },
    }


@patch("src.handler.sqs_client")
def test_insert_record_is_published_with_new_image(mock_sqs):
    mock_sqs.send_message.return_value = {"MessageId": "abc-123"}
    event = {
        "Records": [_stream_record("INSERT", new_image={"OrderID": {"S": "order-1"}})]
    }

    result = lambda_handler(event, context=None)

    assert result == {"statusCode": 200, "body": "Processed records"}
    mock_sqs.send_message.assert_called_once()
    _, kwargs = mock_sqs.send_message.call_args
    assert (
        kwargs["QueueUrl"]
        == "https://sqs.eu-west-1.amazonaws.com/123456789012/test-queue"
    )
    assert '"eventName": "INSERT"' in kwargs["MessageBody"]
    assert '"order-1"' in kwargs["MessageBody"]


@patch("src.handler.sqs_client")
def test_remove_record_is_published_with_old_image(mock_sqs):
    mock_sqs.send_message.return_value = {"MessageId": "abc-456"}
    event = {
        "Records": [_stream_record("REMOVE", old_image={"OrderID": {"S": "order-2"}})]
    }

    lambda_handler(event, context=None)

    _, kwargs = mock_sqs.send_message.call_args
    assert '"eventName": "REMOVE"' in kwargs["MessageBody"]
    assert '"order-2"' in kwargs["MessageBody"]


@patch("src.handler.sqs_client")
def test_multiple_records_are_each_published_once(mock_sqs):
    mock_sqs.send_message.return_value = {"MessageId": "abc-789"}
    event = {
        "Records": [
            _stream_record("INSERT", new_image={"OrderID": {"S": "order-1"}}),
            _stream_record("MODIFY", new_image={"OrderID": {"S": "order-1"}}),
            _stream_record("REMOVE", old_image={"OrderID": {"S": "order-1"}}),
        ]
    }

    lambda_handler(event, context=None)

    assert mock_sqs.send_message.call_count == 3


@patch("src.handler.sqs_client")
def test_no_records_publishes_nothing(mock_sqs):
    result = lambda_handler({"Records": []}, context=None)

    mock_sqs.send_message.assert_not_called()
    assert result["statusCode"] == 200
