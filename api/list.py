import json
import os

def handler(request):
    try:
        file_path = os.path.join(os.path.dirname(__file__), "links.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(list(data.keys()), indent=2)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Hata: {str(e)}"})
        }

handler.__name__ = "handler"
