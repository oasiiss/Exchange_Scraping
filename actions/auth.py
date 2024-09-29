import http.client
import json

def Login(username, password):
    try:
        conn = http.client.HTTPSConnection("api.fintables.com")

        headers = {
            'Host': 'api.fintables.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Content-Type': 'application/json'
        }

        payload = {
            "email": username,
            "password": password
        }

        json_payload = json.dumps(payload)

        conn.request("POST", "/auth/token/", json_payload, headers)

        response = conn.getresponse()

        response_data = response.read().decode()
        data = json.loads(response_data)

        if "access" in data and "refresh" in data:
            return [True, data]
        else:
            if "detail" in data:
                return [False, data["detail"]]
            else:
                return [False, "Giriş Yapılamadı. Bilinmeyen Hata"]
        
    except Exception as err:
        return [False, str(err)]
