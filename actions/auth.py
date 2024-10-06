import http.client, json, urllib

def FtLogin(username, password):
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
    


def MtLogin(username, password):
    try:
        conn = http.client.HTTPSConnection("malitablolar.com")

        params = urllib.parse.urlencode({
            'Email': username,
            'Sifre': password
        })

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        conn.request("POST", "/Aut/Login?ReturnUrl=", body=params, headers=headers)
        response = conn.getresponse()

        cookies = response.getheader('Set-Cookie')
        cookie_dict = {}
        if cookies:
            cookie_items = cookies.split(', ')
            for item in cookie_items:
                parts = item.split(';')[0]
                if '=' in parts:
                    name, value = parts.split('=', 1)
                    cookie_dict[name] = value

        asp_cookie = cookie_dict.get('.AspNetCore.Cookies', None)
        mt_cookie = cookie_dict.get('Malitablolar', None)

        data = {"asp_cookie" : asp_cookie, "mt_cookie" : mt_cookie}
        if asp_cookie is not None and mt_cookie is not None:
            return [True, data]
        else:
            return [False]
    except:
        return [False]

