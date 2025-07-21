import json

def handler(request):
    params = request.get("query", {})
    kanal_adi = params.get("id")

    if not kanal_adi:
        return {
            "statusCode": 400,
            "body": "Kanal ID gerekli. Örnek: ?id=trt1"
        }

    try:
        with open("api/links.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {
            "statusCode": 500,
            "body": "links.json bulunamadı."
        }

    if kanal_adi not in data:
        return {
            "statusCode": 404,
            "body": f"{kanal_adi} için link bulunamadı."
        }

    # Doğrudan yönlendirme (redirect)
    return {
        "statusCode": 302,
        "headers": {
            "Location": data[kanal_adi]["url"]
        },
        "body": ""
    }

handler.__name__ = "handler"
