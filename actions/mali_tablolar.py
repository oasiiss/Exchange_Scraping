from bs4 import BeautifulSoup
import http.client

def AllCompany(cookie, token):
    try:
        conn = http.client.HTTPSConnection("malitablolar.com")
        
        headers = {
            'Cookie': f'.AspNetCore.Cookies={cookie}; Malitablolar={token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Host': 'malitablolar.com',
            'Connection': 'keep-alive',
            'Accept': '*/*'
        }
        
        conn.request("GET", "/AraciKurumTahmin/GetAraciKurumTahminOrtamalari?kur=TL", headers=headers)
        
        res = conn.getresponse()
        data = res.read()
        
        soup = BeautifulSoup(data, 'html.parser')

        example_table = soup.find('table', id='example')
        
        if not example_table:
            return [False]
        
        tbody = example_table.find("tbody")

        if not tbody:
            return [False]
        
        company_names = []
        for row in tbody.find_all('tr'):
            try:
                span_tag = row.find_all('span')[-1]
                if span_tag:
                    company_name = span_tag.text.strip()
                    if len(company_name) > 0:
                        company_names.append(company_name)
            except:
                continue

        if len(company_names) > 0:
            return [True, company_names]
        else:
            return [False]
    except:
        return [False]
    
def CompanyDetail(cmp, kur, cookie, token):
    conn = http.client.HTTPSConnection("malitablolar.com")

    endpoint = f"/AraciKurumTahmin/GetAraciKurumTahminDetayBySirket?sirket={cmp}&kur={kur}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Cookie': f'.AspNetCore.Cookies={cookie}; Malitablolar={token}'
    }

    conn.request("GET", endpoint, headers=headers)

    response = conn.getresponse()
    data = response.read()

    conn.close()
    
    soup = BeautifulSoup(data, 'html.parser')

    table = soup.find('table', id="example2")
    if table:
        tbody = table.find('tbody')

        results = []

        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 0:
                kurum_adi = cols[0].text.strip()
                hedef_fiyat = cols[6].text.strip()
                tarih = cols[7].text.strip()

                if len(kurum_adi) <= 1:
                    kurum_adi = None

                if len(hedef_fiyat) <= 1:
                    hedef_fiyat = None

                if len(tarih) <= 1:
                    tarih = None


                result = {
                    "kurum_adi": kurum_adi,
                    "hedef_fiyat": hedef_fiyat,
                    "tarih": tarih
                }

                results.append(result)

        if len(results) == 1:
            if results[0]["hedef_fiyat"] is None:
                return [False]

        if len(results) > 0:
            return [True, results]
        else:
            return [False]
    else:
        return [False]