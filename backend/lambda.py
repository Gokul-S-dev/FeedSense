import json
import boto3
import base64

bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}

def lambda_handler(event, context):
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")

    if method == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({})}

    try:
        raw_body = event.get("body")

        if event.get("isBase64Encoded") and isinstance(raw_body, str):
            raw_body = base64.b64decode(raw_body).decode("utf-8")

        if isinstance(raw_body, str):
            raw_body = raw_body.strip()
            if raw_body:
                try:
                    body = json.loads(raw_body)
                except json.JSONDecodeError:
                    body = {"feedback": raw_body}
            else:
                body = {}
        elif isinstance(raw_body, dict):
            body = raw_body
        else:
            body = {}

        if not isinstance(body, dict):
            body = {}

        if not body.get("feedback") and isinstance(body.get("body"), str):
            nested_body = body.get("body", "").strip()
            if nested_body:
                try:
                    nested_payload = json.loads(nested_body)
                    if isinstance(nested_payload, dict):
                        body = nested_payload
                except json.JSONDecodeError:
                    body["feedback"] = nested_body

        feedback = (
            body.get("feedback")
            or event.get("feedback")
            or event.get("queryStringParameters", {}).get("feedback")
        )

        if not feedback or not str(feedback).strip():
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "No feedback"})}

        feedback = str(feedback).strip()

        # Prompt for Nova Micro
        prompt_text = f"""Analyze the following feedback and return ONLY a JSON object.
        JSON Keys: "summary" (2-line summary), "sentiment" (Positive, Neutral, or Negative).
        
        Feedback: "{feedback}"
        
        Output format:
        {{
            "summary": "...",
            "sentiment": "..."
        }}"""
        # Nova Micro uses the 'messages-v1' schema
        native_request = {
            "schemaVersion": "messages-v1",
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt_text}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 400,
                "temperature": 0.3
            }
        }

        response = bedrock.invoke_model(
            modelId="amazon.nova-micro-v1:0", # The updated 2026 Model ID
            contentType="application/json",
            accept="application/json",
            body=json.dumps(native_request)
        )

        response_body = json.loads(response.get("body").read())
        
        # Nova returns the answer in output -> message -> content
        output_text = response_body['output']['message']['content'][0]['text']

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"result": output_text})
        }

    except Exception as e:
        print(f"Deployment Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }