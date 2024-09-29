import http.client
import json


def GetCompanyDetail(company_name, token):
    host = "fintables.com"
    path = f"/sirketler/{company_name}"

    connection = http.client.HTTPSConnection(host)

    headers = {
        "Host" : host,
        "Cookie": f"auth-token={token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    connection.request("GET", path, headers=headers)

    response = connection.getresponse()


    if response.status == 200:
        print("İstek başarılı!")
        data = response.read().decode("utf-8")
        print(data)
    else:
        print(f"İstek başarısız. Durum Kodu: {response.status}")
    connection.close()


data = {'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyNzY0OTY2MiwiaWF0IjoxNzI3NTYzMjYyLCJqdGkiOiI3YTNlMGIxZjg0YzM0MDczYTRhMjM0NDRlNGNiOWEzMCIsInVzZXJfaWQiOjMyODcwOX0.t5HOdv_LiJMiRzN9UkVyPk2XvdqROtSrl9yX4SexzJs', 'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyMTU5NTYzMjYyLCJpYXQiOjE3Mjc1NjMyNjIsImp0aSI6IjQyMzkxNmViOTE4MTQyOTZiZjdlZDdkNTMzMzg3ZDNkIiwidXNlcl9pZCI6MzI4NzA5fQ.qIUmAB2v5TkgnX2K26sowtF-jEhopHxSg-7ftwXkZJs'}


GetCompanyDetail("ZRGYO", data["access"])