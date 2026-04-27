import json
import boto3

bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}

def lambda_handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({})}

    try:
        body = json.loads(event.get("body", "{}"))
        feedback = body.get("feedback")

        if not feedback:
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "No feedback"})}

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