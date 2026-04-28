import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource(
    "dynamodb",
    region_name="eu-north-1"
)

table = dynamodb.Table("FeedSenseFeedback")

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,GET"
}

def lambda_handler(event, context):
    method = (
        event.get("httpMethod")
        or event.get("requestContext",{}).get("http",{}).get("method")
    )

    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({})
        }

    try:
        response = table.scan()
        items = response.get("Items", [])

        positive = []
        negative = []
        neutral = []

        for item in items:
            sentiment = item.get("sentiment", "").lower()
            if sentiment == "positive":
                positive.append(item)
            elif sentiment == "negative":
                negative.append(item)
            elif sentiment == "neutral":
                neutral.append(item)

        result = {
            "total": len(items),
            "positive_count": len(positive),
            "negative_count": len(negative),
            "neutral_count": len(neutral),
            "positive": positive,
            "negative": negative,
            "neutral": neutral
        }
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(result)
        }
    except Exception as e:
        print("Error:", str(e))

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error":str(e)
            })
        }