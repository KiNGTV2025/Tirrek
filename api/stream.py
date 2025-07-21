import json
import os

def handler(request):
    try:
        base_path = os.path.dirname(__file__)
        json_path = os.path.join(base_path, "links.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Dosya okunamadı: {str(e)}"}),
            "headers": {"Content-Type": "application/json"}
        }

    query = request.get("query", {})
    kanal_adi = query.get("id")
    if not kanal_adi:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Kanal ID gerekli. Örnek: ?id=trt1"}),
            "headers": {"Content-Type": "application/json"}
        }

    if kanal_adi not in data:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"{kanal_adi} için link bulunamadı."}),
            "headers": {"Content-Type": "application/json"}
        }

    # Redirect yapalım:
    return {
        "statusCode": 302,
        "headers": {"Location": data[kanal_adi]["url"]},
        "body": ""
    }

handler.__name__ = "handler"
