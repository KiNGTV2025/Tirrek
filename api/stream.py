import json
import os

def handler(request):
    # Query parametreden id al
    kanal = request.args.get("id") if hasattr(request, "args") else request.get("query", {}).get("id")
    if not kanal:
        return {"statusCode": 400, "body": "id parametresi gerekli"}

    try:
        base = os.path.dirname(__file__)
        data = json.load(open(os.path.join(base, "links.json"), "r", encoding="utf-8"))
    except Exception as e:
        return {"statusCode": 500, "body": f"links.json okunamadı: {e}"}

    if kanal not in data:
        return {"statusCode": 404, "body": "Kanal bulunamadı"}

    return {"statusCode": 302, "headers": {"Location": data[kanal]["url"]}, "body": ""}

handler.__name__ = "handler"
