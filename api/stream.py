import json

def handler(request):
    params = request.get("query", {})
    kanal_adi = params.get("id")

    if not kanal_adi:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Kanal ID gerekli. Örnek: ?id=trt1"})
        }

    try:
        with open("api/links.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "links.json bulunamadı."})
        }

    if kanal_adi not in data:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"{kanal_adi} için link bulunamadı."})
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data[kanal_adi])
    }

# Vercel uyumluluğu
handler.__name__ = "handler"
