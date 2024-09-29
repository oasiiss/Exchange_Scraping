import http.client
from bs4 import BeautifulSoup

def GetSectors(token):
    try:
        conn = http.client.HTTPSConnection("fintables.com")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Cookie': f'auth-token={token}'
        }

        conn.request("GET", "/sektorler", headers=headers)

        response = conn.getresponse()
        if response.status == 200:
            html_content = response.read().decode()

            soup = BeautifulSoup(html_content, 'html.parser')

            sector_div = soup.find(class_="divide-y divide-stroke-02 sm:divide-y-0 sm:grid sm:grid-cols-2")

            if sector_div:
                sectors = sector_div.find_all('a', class_='hover:bg-background-adaptive-02')
                if len(sectors) > 0:
                    sector_data = []
                    for sector in sectors:
                        title = sector.get('title') if sector.get('title') else None
                        description = sector.find('p').text.strip() if sector.find('p') else None
                        url = sector.get('href') if sector.get('href') else None

                        sector_data.append({"title" : title, "description" : description, "url" : url})

                        
                    return [True, sector_data]
                else:
                    return [False, "Sektör bulunamadı"]
        else:
            return [False, f"İstek başarısız, hata kodu: {response.status}"]
        
        conn.close()
    except Exception as err:
        return [False, err]
    

def GetSectorDetail(sektor_slug, token):

    try:
        conn = http.client.HTTPSConnection("fintables.com")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Cookie': f'auth-token={token}'
        }

        conn.request("GET", sektor_slug, headers=headers)

        response = conn.getresponse()
        if response.status == 200:
            html_content = response.read().decode()

            soup = BeautifulSoup(html_content, 'html.parser')

            div = soup.find('div', class_="align-middle inline-block min-w-full")
            table = div.find('table') if div else None

            if table:
                rows = table.find_all('tr')

                bist_100_fk = None
                bist_100_pddd = None
                medyan_fk = None
                medyan_pddd = None
                medyan_fd_favok = None

                for row in rows:
                    columns = row.find_all('td')

                    if len(columns) > 0:
                        title = columns[0].text.strip()

                        # BIST 100 satırını al
                        if title == "BIST 100":
                            bist_100_fk = columns[1].text.strip() if len(columns) > 1 else None
                            bist_100_pddd = columns[2].text.strip() if len(columns) > 2 else None

                        # Medyan satırını al
                        if title == "Medyan":
                            medyan_fk = columns[1].text.strip() if len(columns) > 1 else None
                            medyan_pddd = columns[2].text.strip() if len(columns) > 2 else None
                            medyan_fd_favok = columns[3].text.strip() if len(columns) > 3 else None

            conn.close()
            return [True, {"bist_fk" : bist_100_fk, "bist_pddd" : bist_100_pddd, "medyan_fk" : medyan_fk, "medyan_pddd" : medyan_pddd, "medyan_fd_favok" : medyan_fd_favok}]
            
        else:
            conn.close()
            return [False, f"İstek başarısız, hata kodu: {response.status}"]
        
    except Exception as err:
        return [False, err]