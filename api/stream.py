import json

def handler(request):
    query = request.get("query", {})
    kanal_adi = query.get("id")

    if not kanal_adi:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Kanal ID gerekli. Örnek: ?id=trt1"}),
            "headers": {"Content-Type": "application/json"}
        }

    try:
        with open("api/links.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "links.json bulunamadı."}),
            "headers": {"Content-Type": "application/json"}
        }

    if kanal_adi not in data:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"{kanal_adi} için link bulunamadı."}),
            "headers": {"Content-Type": "application/json"}
        }

    # Redirect yapıyoruz
    return {
        "statusCode": 302,
        "headers": {
            "Location": data[kanal_adi]["url"]
        },
        "body": ""
    }

handler.__name__ = "handler"
