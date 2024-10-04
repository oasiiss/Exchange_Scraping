import http.client
import json, re, ast, gzip
from bs4 import BeautifulSoup
from io import BytesIO
from yahooquery import Ticker


def GetAllCompany(token):
    try:
        conn = http.client.HTTPSConnection("fintables.com")

        headers = {
            'Cookie': f'auth-token={token};',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0'
        }

        conn.request("GET", "/radar", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        soup = BeautifulSoup(data, 'html.parser')

        script_elements = soup.find_all('script')
        
        if not script_elements:
            return [False, "Script Elementi Bulunamadı"]

        script_element = script_elements[-1].string

        script_element = str(script_element).replace("self.__next_f.push(", "")
        son_parantez_index = script_element.rfind(')')

        if son_parantez_index != -1:
            script_element = script_element[:son_parantez_index] + script_element[son_parantez_index + 1:]  # Son ')' hariç olan metni oluştur

        script_element = ast.literal_eval(script_element)

        matches = re.findall(r'{"code":".*?}.*?}', script_element[1])
        company_list = []
        type_list = []
        for match in matches:
            try:
                company_json = json.loads(match)
                if company_json["type"] not in type_list:
                    type_list.append(company_json["type"])

                if company_json["type"] == "equity":
                    company_list.append(company_json)
            except json.JSONDecodeError as e:
                pass

        if len(company_list) > 0:
            return [True, company_list]
        else:
            return [False, "Şirketler Listesi Boş"]
    
    except Exception as err:
        return [False, err]
    
def GetRatioAnalysis(company_name, token):
    host = "fintables.com"
    path = f"/sirketler/{company_name}/oran-analizi/rasyo-analiz-tablosu"

    try:
        connection = http.client.HTTPSConnection(host)

        headers = {
            "Host": host,
            "Cookie": f"auth-token={token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
    except Exception as e:
        connection.close()
        return [False, None]

    if response.status == 200:
        try:
            data = response.read().decode("utf-8")
            soup = BeautifulSoup(data, 'lxml')

            tables = soup.find_all("table", class_="w-full")
            if len(tables) < 2:
                connection.close()
                return [False, None]

            table = tables[1]
            tbody = table.find_all("tbody")[-1]

            favok_div = tbody.find('div', string='FAVÖK Marjı')
            if not favok_div:
                connection.close()
                return [False, None]

            favok_marj_raw = favok_div.find_next('td').text.strip()
            favok_marj_value = favok_marj_raw.split('%')[-1].strip()

            connection.close()
            return [True, favok_marj_value]

        except Exception as e:
            connection.close()
            return [False, None]
    else:
        connection.close()
        return [False, None]
    
def GetCompanyInfo(company_name, token):
    try:
        host = "fintables.com"
        path = f"/sirketler/{company_name}/sirket-bilgileri"

        connection = http.client.HTTPSConnection(host)

        headers = {
            "Host": host,
            "Cookie": f"auth-token={token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        connection.request("GET", path, headers=headers)
        response = connection.getresponse()

        if response.status == 200:
            data = response.read().decode("utf-8")
            soup = BeautifulSoup(data, 'lxml')

            table = soup.find("table", class_="min-w-full")
            sermaye_pay = None

            if table:
                total_row = table.find('td', string='TOPLAM')
                if total_row:
                    total_row = total_row.parent
                    sermaye_pay = total_row.find_all('td')[1].text.strip()
                    return [True, sermaye_pay]
                else:
                    return [False, None]
            else:
                return [False, None]
        else:
            return [False, None]

    except Exception as err:
        return [False, None]
    
def GetCompanyDetail(company_name, token):
    try:
        response_data = {"date" : None, "hisse_adi" : None, "f_k" : None, "fd_favök" : None, "pd_dd" : None, "peg" : None, "net_borc" : None, "sektör" : None, "fiili_dolasim" : None, "hisse_basina_kar" : None, "odenmis_sermaye" : None, "piyasa_degeri" : None, "satislar" : None, "esas_faaliyet_kari" : None, "favök" : None, "net_dönem_kari" : None, "öz_kaynaklar" : None}
        host = "fintables.com"
        path = f"/sirketler/{company_name}"

        def make_request(host, path, token):
            connection = http.client.HTTPSConnection(host)

            headers = {
                "Host": host,
                "Cookie": f"auth-token={token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
            }

            connection.request("GET", path, headers=headers)
            response = connection.getresponse()
            return connection, response

        connection, response = make_request(host, path, token)

        if response.status == 308:
            new_path = response.getheader('Location')
            if new_path:
                hisse_adi = new_path.split("/")[2]
                connection, response = make_request(host, new_path, token)
        else:
            hisse_adi = company_name

        response_data["hisse_adi"] = hisse_adi
        if response.status == 200:
            data = response.read().decode("utf-8")
            soup = BeautifulSoup(data, 'lxml')

            tbodies = soup.findAll('tbody', class_='divide-y divide-stroke-02 text-foreground-02')
            w_full_tables = soup.findAll('table', class_='w-full')
            if tbodies:
                try:
                    multipliers_info_rows = tbodies[0].find_all('tr')
                    for row in multipliers_info_rows:
                        try:
                            title = row.find('td').strong.text
                            value = row.find_all('td')[1].text.strip()

                            title = str(title).lower().strip()
                            value = str(value).lower().strip()

                            if "f/k" in title:
                                response_data["f_k"] = value
                            elif "fd/favök" in title:
                                response_data["fd_favök"] = value
                            elif "pd/dd" in title:
                                response_data["pd_dd"] = value
                            elif "peg" in title:
                                response_data["peg"] = value
                            elif "net borç" in title:
                                response_data["net_borc"] = value
                        except Exception as err:
                            pass
                            # print(f"Bir çarpan verisi atlandı.{err}")
                except:
                    pass
                    # print("Çarpanlar verisi çekilemedi")
            else:
                return [False, "Çarpanlar tablosu bulunamadı"]


            if len(tbodies) > 1:
                try:
                    cmp_info_rows = tbodies[1].find_all('tr')

                    for row in cmp_info_rows:
                        try:
                            title_element = row.find('td').strong
                            title = title_element.text.strip() if title_element else None
                            if title is None:
                                continue
                            title = str(title).lower().strip()
                            if title == "sektörler":
                                sector_td = row.find('td', class_="px-3 md:px-4 text-sm py-3 whitespace-nowrap text-right")
                                sector_div = sector_td.find('div')
                                if sector_div:
                                    sector_elements = sector_div.find_all('a')
                                    if sector_elements:
                                        sectors = [sector.get_text(strip=True) for sector in sector_elements]
                                        response_data["sektör"] = ' - '.join(sectors)
                                    else:
                                        pass
                                else:
                                    pass

                            elif "fiili" in title:
                                value = row.find_all('td')[1].text.strip()
                                response_data["fiili_dolasim"] = value
                            elif "hisse" in title:
                                value = row.find_all('td')[1].text.strip()
                                response_data["hisse_basina_kar"] = value
                            elif "sermaye" in title:
                                value = row.find_all('td')[1].text.strip()
                                response_data["odenmis_sermaye"] = value
                            elif "piyasa" in title:
                                value = row.find_all('td')[1].text.strip()
                                response_data["piyasa_degeri"] = value

                        except:
                            pass
                            # print(f"Bir şirket detayı atlandı.")
                except Exception as e:
                    pass
                    # print(f"Şirket detayları verisi çekilemedi: {e}")
            else:
                return [False, "Şirket detayları tablosu bulunamadı"]

            if w_full_tables:
                try:
                    tbody = w_full_tables[0].find("tbody")
                    rows = tbody.find_all('tr')

                    year_headers = []
                    header_divs = rows[0].find_all('div', class_='flex-1')
                    for div in header_divs:
                        year = div.find('span').text.strip()
                        year_headers.append(year)

                    latest_year = year_headers[0]

                    response_data["date"] = latest_year

                    for row in rows:
                        try:
                            title_div = row.find('div', class_='font-semibold')
                            title = title_div.text.strip() if title_div else None

                            if title is None:
                                continue

                            title = str(title).lower().strip()

                            latest_div = row.find_all('div', class_='flex-1')[0]
                            value = latest_div.find_next('br').next_sibling.strip() if latest_div.find_next('br') else None

                            if "satışlar" in title:
                                response_data["satislar"] = value
                            elif "faaliyet" in title:
                                response_data["esas_faaliyet_kari"] = value
                            elif "favök" in title:
                                response_data["favök"] = value
                            elif "dönem" in title:
                                response_data["net_dönem_kari"] = value
            
                        except:
                            pass
                            # print(f"Bir gelir tablosu satırı atlandı.")
                except Exception as e:
                    pass
                    # print(f"Gelir tablosu verisi çekilemedi: {e}")
            else:
                return [False, "Gelir tablosu bulunamadı"]
            
            if len(w_full_tables) > 2:
                try:
                    tbody = w_full_tables[2].find("tbody")
                    rows = tbody.find_all('tr')

                    year_headers = []
                    header_divs = rows[0].find_all('div', class_='flex-1')
                    for div in header_divs:
                        year = div.find('span').text.strip()
                        year_headers.append(year)

                    latest_year = year_headers[0]

                    for row in rows:
                        try:
                            title_div = row.find('div', class_='font-semibold')
                            title = title_div.text.strip() if title_div else None

                            if title is None:
                                continue

                            title = str(title).lower().strip()

                            latest_div = row.find_all('div', class_='flex-1')[0]
                            value = latest_div.find('br').next_sibling.strip() if latest_div.find('br') else None


                            if "özkaynaklar" in title:
                                response_data["öz_kaynaklar"] = value
                                break
                        except:
                            pass
                            # print(f"Bir bilanço satırı atlandı.")

                except Exception as e:
                    pass
                    # print(f"Bilanço verisi çekilemedi: {e}")
            else:
                return [False, "Bilanço tablosu bulunamadı"]
            
            return [True, response_data]
            
        else:
            error_data = response.read().decode("utf-8")
            return [False, f"İstek başarısız. Durum Kodu: {response.status}\nSunucudan dönen hata mesajı: {error_data}"]
        
    except Exception as err:
        return [False, err]


def GetFDSell(company_name):
    host = "www.isyatirim.com.tr"
    path = f"/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse={company_name}"

    try:
        connection = http.client.HTTPSConnection(host)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
            "Accept-Encoding": "gzip, deflate, br"
        }
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
    except Exception as e:
        return [False, [None, None]]

    if response.status == 200:
        try:
            data = response.read()
            if response.getheader('Content-Encoding') == 'gzip':
                with gzip.GzipFile(fileobj=BytesIO(data)) as f:
                    data = f.read()

            soup = BeautifulSoup(data, 'lxml')

            tab_items = soup.find_all("div", class_="tab-item")
            if not tab_items or len(tab_items) < 7:
                connection.close()
                return [False, [None, None]]

            first_tab_item = tab_items[6]

            table = first_tab_item.find("table", class_="excelexport")
            if not table:
                connection.close()
                return [False, [None, None]]

            tbody = table.find('tbody')
            row = tbody.find('tr')

            try:
                fd_satislar = row.find_all('td')[4].text.strip()
                son_donem = row.find_all('td')[6].text.strip()

                return [True, [fd_satislar, son_donem]]

            except IndexError:
                connection.close()
                return [False, [None, None]]

        except Exception as e:
            connection.close()
            return [False, [None, None]]
        
    else:
        connection.close()
        return [False, [None, None]]
    
def BilancoSplit(value):
    parts = value.split('/')
    
    if len(parts) != 2:
        raise ValueError(f"Geçersiz format: {value}")

    first = int(parts[0])
    second = int(parts[1])
    if first > 12:
        year = first
        month_or_quarter = second
    else:
        year = second
        month_or_quarter = first
    
    return year, month_or_quarter

def CompareBilanco(a, b):
    try:
        if a is None or b is None:
            return False
        
        year_a, period_a = BilancoSplit(a)
        year_b, period_b = BilancoSplit(b)

        return year_a == year_b and period_a == period_b
    except:
        return False
    

def GetLastPrice(company_name):
    try:
        cmp = Ticker(f'{company_name}.IS')
        last_price = cmp.price[f'{company_name}.IS']['regularMarketPrice']
        return [True, last_price]
    except:
        return [False, None]

