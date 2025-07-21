import json
import os

def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        kanal_adi = params.get("id")

        if not kanal_adi:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Kanal ID gerekli. Örnek: ?id=trt1"})
            }

        file_path = os.path.join(os.path.dirname(__file__), "links.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if kanal_adi not in data:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"{kanal_adi} için link bulunamadı."})
            }

        return {
            "statusCode": 302,
            "headers": {
                "Location": data[kanal_adi]["url"]
            },
            "body": ""
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Sunucu hatası: {str(e)}"})
        }
