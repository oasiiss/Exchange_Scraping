import sqlite3
from actions.auth import FtLogin, MtLogin
from actions.sector import GetSectors, GetSectorDetail
from actions.read_config import ReadConfig, AppendText, WriteListToFile, ReadFile
from actions.company import GetAllCompany, GetCompanyDetail, GetCompanyInfo, GetRatioAnalysis, GetFDSell, CompareBilanco, GetLastPrice
from actions.mali_tablolar import AllCompany, CompanyDetail
import sys, time, os, platform
from tqdm import tqdm

import datetime

def get_current_year():
    return datetime.datetime.now().year

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def setup_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    current_year = get_current_year()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS '{current_year}_sektorler' (
        SEKTOR_ADI TEXT,
        SEKTOR_FK REAL,
        SEKTOR_PD_DD REAL,
        SEKTOR_FD_FAVOK REAL,
        BIST_FK REAL,
        BIST_PD_DD REAL
    )
    """)

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS '{current_year}_hisseler' (
        HISSE_ADI TEXT UNIQUE,
        DONEM TEXT,
        SEKTOR_ADI TEXT,
        SON_FIYAT REAL,
        ESAS_FAAL_KARI REAL,
        SATISLAR REAL,
        FAVOK REAL,
        FAVOK_MARJI REAL,
        FD_SATIS REAL,
        FD_FAVOK REAL,
        FK REAL,
        PD_DD REAL,
        PIYASA_DEGERI REAL,
        NET_KAR REAL,
        ODENMIS_SERMAYE REAL,
        OZKAYNAKLAR REAL,
        FIIL_DOL_ORANI REAL,
        SENET_SAYISI REAL,
        PEG REAL,
        NETBORC_FAVOK REAL,
        HBK REAL,
        SEKTOR2_ADI TEXT,
        SEKTOR3_ADI TEXT,
        SEKTOR4_ADI TEXT
    )
    """)


    sql_query = f"""
    CREATE TABLE IF NOT EXISTS '{current_year}_araci_kurum' (
        HISSE_ADI TEXT UNIQUE,
    """

    for i in range(1, 25 + 1):
        sql_query += f"""
        KURUM{i}_ADI TEXT,
        KURUM{i}_FIYAT REAL,
        KURUM{i}_TARIH TEXT,"""

    sql_query = sql_query.rstrip(',') + "\n);"

    cursor.execute(sql_query)
        
    conn.commit()
    conn.close()

def clear_table(table_name):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM '{table_name}'")
    conn.commit()
    conn.close()

def process_financial_data(cmp_data):
    keys = ["esas_faaliyet_kari", "satislar", "favök", "net_dönem_kari", "öz_kaynaklar"]

    for key in cmp_data:
        if key in keys:
            value = cmp_data.get(key)
            
            if value is None:
                continue
            else:
                value = str(value)
                value2 = value.replace(".", "")
                value2 = value2.replace(",", "")

                try:
                    float(value2)
                    cmp_data[key] = f"{value},000"
                except:
                    continue

    return cmp_data

def edit_data(cmp_data):
    for key in cmp_data:
        value = cmp_data.get(key)
        
        if value is None:
            continue
        else:
            value = str(value)
            value2 = value.replace(".", "")
            value2 = value2.replace(",", "")
            value2 = value2.replace("-", "")

            if value2.isnumeric():
                value = value.replace(".", ",")
                cmp_data[key] = value

    return cmp_data

def ReadTable(db, table):
    try:
        db_connection = sqlite3.connect(db)
        cursor = db_connection.cursor()

        cursor.execute(f"SELECT * FROM [{table}]")
        rows = cursor.fetchall()
        db_connection.close()

        if len(rows) > 0:
            rows = [row[0] for row in rows]
            return [True, rows]
        else:
            return [True, []]

    except sqlite3.Error as e:
        return [False]
    
def CompletSektor(values, sectors):
    results = []
    for value in values:
        if value is None:
            results.append(value)
            continue

        if "..." in value and len(sectors) > 0:
            matched = False
            for sector in sectors:
                if str(sector[:10]).lower() == str(value[:10]).lower():
                    results.append(sector)
                    matched = True
                    break

            if not matched:
                results.append(value)
        else:
            results.append(value)
    
    return results


def MainMenu():
    setup_database()

    result = ReadConfig()
    if not result[0]:
        print("Config Okunamadı ...")
        time.sleep(2)
        sys.exit(0)
    config = result[1]

    while True:

        while True:
            choice = input(f"\nAna Menü\n\n1 - Fintables\n2 - Malitablolar\n3 - DB'yi Dönüştür\n4 - Programı Sonlandır\n\nSeçimin : ")
            if choice.isnumeric():
                choice = int(choice)
                if choice == 1 or choice == 2 or choice == 3 or choice == 4:
                    break
        
        clear_screen()
        print("Lütfen Doğru Bir Seçim Yapınız.")

        if choice == 1:
            clear_screen()
            result = FtLogin(config["ft_username"], config["ft_password"])
            if not result[0]:
                clear_screen()
                print(f"\n{config['ft_username']} Mail Adresine Sahip Fintables Hesabına Giriş Yapılamadı.")
                continue

            FtMenu(result[1])
            continue

        elif choice == 2:
            clear_screen()
            result = MtLogin(config["mt_username"], config["mt_password"])
            if not result[0]:
                clear_screen()
                print(f"\n{config['mt_username']} Mail Adresine Sahip Malitablolar Hesabına Giriş Yapılamadı.")
                continue

            MtMenu(result[1])
            continue

        elif choice == 3:
            DBToTxt("data.db")
            continue

        elif choice == 4:
            clear_screen
            print("Program Sonlandırılıyor ...")
            time.sleep(0.5)
            sys.exit(0)






def FtMenu(login_data):
    clear_screen()
    while True:
        while True:
            choice = input("\nFintables Menü\n\n1 - Sektör Oku\n2 - Şirket Oku\n3 - Ana Menüye Dön\n\nSeçimin : ")
            if choice.isnumeric():
                choice = int(choice)
                if choice == 1 or choice == 2 or choice == 3:
                    break
            
            clear_screen()
            print("Lütfen Doğru Bir Seçim Yapınız.")

        if choice == 1:
            FtReadSectors(login_data)
            continue

        elif choice == 2:
            FtReadCompany(login_data)
            continue

        elif choice == 3:
            clear_screen()
            return



def MtMenu(login_data):
    clear_screen()
    while True:
        while True:
            choice = input("\nMalitablolar Menü\n\n1 - Aracı Kurumları Çek\n2 - Ana Menüye Dön\n\nSeçimin : ")
            if choice.isnumeric():
                choice = int(choice)
                if choice == 1 or choice == 2:
                    break
            
            clear_screen()
            print("Lütfen Doğru Bir Seçim Yapınız.")

        if choice == 1:
            MtReadFirms(login_data)
            continue

        elif choice == 2:
            clear_screen()
            return
        

def MtReadFirms(login_data):
    companies = None
    for i in range(3):
        result = AllCompany(login_data["asp_cookie"], login_data["mt_cookie"])
        if result[0]:
            companies = result[1]
            break

    if companies is None:
        clear_screen()
        print("Şirketler Çekilemedi.")
        return

    print(f"\n{len(companies)} Adet Şirket Bulundu.\n")

    error_list = []

    current_year = get_current_year()

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    for company in tqdm(companies, desc="Şirketin Aracı Kurum Detayları Çekiliyor", unit="Şirket"):
        info = None
        for i in range(3):
            result = CompanyDetail(company, "TL", login_data["asp_cookie"], login_data["mt_cookie"])
            if result[0]:
                info = result[1]
                break

        if info is None:
            error_list.append(f"\n{company} Kodlu Şirketin Aracı Kurum Bilgileri Çekilemedi.")
            continue

        column_names = ['HISSE_ADI']
        column_values = [company]

        for i in range(1, 26):
            if i <= len(info):
                kurum = info[i-1]
                kurum_adi = kurum.get('kurum_adi', None)
                kurum_fiyat = kurum.get('hedef_fiyat', None)
                kurum_tarih = kurum.get('tarih', None)
            else:
                kurum_adi = None
                kurum_fiyat = None
                kurum_tarih = None

            if kurum_adi is not None:
                kurum_adi = str(kurum_adi).lower()
                if "menkul değerler" in kurum_adi:
                    kurum_adi = kurum_adi.split("menkul değerler")[0]
                elif "menkul kıymetler" in kurum_adi:
                    kurum_adi = kurum_adi.split("menkul kıymetler")[0]
                elif "menkul kiymetler" in kurum_adi:
                    kurum_adi = kurum_adi.split("menkul kiymetler")[0]
                elif "yatırım bank" in kurum_adi:
                    kurum_adi = kurum_adi.split("yatırım bank")[0]

                kurum_adi = kurum_adi.capitalize()


                if " " in kurum_adi:
                    text_lst = []
                    for krm in kurum_adi.split(" "):
                        text_lst.append(krm.capitalize())

                    kurum_adi = " ".join(text_lst)

            

            column_names += [f'KURUM{i}_ADI', f'KURUM{i}_FIYAT', f'KURUM{i}_TARIH']
            column_values += [kurum_adi, kurum_fiyat, kurum_tarih]

        sql_query = f"""
        INSERT OR REPLACE INTO '{current_year}_araci_kurum' ({', '.join(column_names)}) 
        VALUES ({', '.join(['?'] * len(column_names))})
        """

        cursor.execute(sql_query, column_values)
        conn.commit()

    conn.close()

    if len(error_list) > 0:
        for error in error_list:
            print(f"{error}")




def FtReadCompany(login_data):
    sectors = []
    for i in range(3):
        result = ReadTable("data.db", "2024_sektorler")
        if result[0]:
            sectors = result[1]
            break

    clear_screen()
    while True:
        choice = input("\nŞirket Okuma Menü\n\n1 - Tüm Şirketleri Oku\n2 - Listelenen Şirketleri Oku\n3 - Okunamayan Şirketleri Oku\n\nSeçimin : ")
        if choice.isnumeric():
            choice = int(choice)
            if choice == 1 or choice == 2 or choice == 3:
                break

            clear_screen()
            print("Lütfen Doğru Bir Seçim Yapınız.")

    if choice == 1:
        companies = None
        for i in range(3):
            result = GetAllCompany(login_data["access"])
            if result[0]:
                companies = result[1]
                break
        
        if companies is None:
            clear_screen()
            print("Şirket İsimleri Çekilemedi.")
            return
        companies_code = [company['code'] for company in companies]
        WriteListToFile("././settings/sirketler.txt", companies_code)

    elif choice == 2:
        companies = ReadFile("././settings/sirketler.txt")
        companies = [{"code" : cmp} for cmp in companies]
        if not len(companies) > 0:
            clear_screen()
            print("sirketler.txt Dosyasının İçeriği Boş")
            time.sleep(0.5)
            return

    elif choice == 3:
        companies = ReadFile("././settings/okunamayan_sirketler.txt")
        if not len(companies) > 0:
            clear_screen()
            print("Okunamayan Şirket Bulunamadı.")
            time.sleep(0.5)
            return
        else:
            companies = [{"code" : company} for company in companies]

    WriteListToFile("././settings/okunan_sirketler.txt", [])
    WriteListToFile("././settings/okunamayan_sirketler.txt", [])
    WriteListToFile("././settings/bilgi.txt", [])
    clear_screen()
    print(f"\n{len(companies)} Adet Şirket Bulundu.\n")


    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    current_year = get_current_year()
    for company in tqdm(companies, desc="Şirket Detayları Çekiliyor", unit="Şirket"):
        cmp_data = None
        for i in range(3):
            result = GetCompanyDetail(company["code"], login_data["access"])
            if not result[0]:
                time.sleep(1)
                continue
            else:
                cmp_data = result[1]
                break

        if cmp_data is None:
            AppendText("././settings/okunamayan_sirketler.txt", company["code"])
            time.sleep(0.3)
            continue

        for i in range(3):
            result = GetRatioAnalysis(cmp_data["hisse_adi"], login_data["access"])
            if not result[0]:
                time.sleep(1)
                cmp_data["favök_marjı"] = None
                continue
            else:
                cmp_data["favök_marjı"] = result[1]
                break

        for i in range(3):
            result = GetFDSell(cmp_data["hisse_adi"])
            if not result[0]:
                time.sleep(1)
                cmp_data["fd_satislar"] = None
                cmp_data["son_donem"] = None
                continue
            else:
                cmp_data["fd_satislar"] = result[1][0]
                cmp_data["son_donem"] = result[1][1]
                break

        cmp_data = process_financial_data(cmp_data)
        cmp_data = edit_data(cmp_data)

        if not CompareBilanco(cmp_data["date"], cmp_data["son_donem"]):
            AppendText("././settings/bilgi.txt", f"{cmp_data['hisse_adi']} Kodlu Şirket İçin Dönem Farkı Var fintables : {cmp_data['date']} - İş Yatırım : {cmp_data['son_donem']}")

        last_price = None
        for i in range(3):
            result = GetLastPrice(cmp_data['hisse_adi'])
            if result[0]:
                last_price = result[1]
                break

        sector = CompletSektor(cmp_data["sektör"], sectors)
    
        cursor.execute(f"""
            INSERT OR REPLACE INTO '{current_year}_hisseler' 
            (HISSE_ADI, DONEM, SEKTOR_ADI, SON_FIYAT, ESAS_FAAL_KARI, SATISLAR, FAVOK, FAVOK_MARJI, FD_SATIS, FD_FAVOK, FK, PD_DD, PIYASA_DEGERI, NET_KAR, ODENMIS_SERMAYE, OZKAYNAKLAR, FIIL_DOL_ORANI, SENET_SAYISI, PEG, NETBORC_FAVOK, HBK, SEKTOR2_ADI, SEKTOR3_ADI, SEKTOR4_ADI) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cmp_data["hisse_adi"],
            cmp_data["date"],
            sector[0],
            last_price,
            cmp_data["esas_faaliyet_kari"],
            cmp_data["satislar"],
            cmp_data["favök"],
            cmp_data["favök_marjı"],
            cmp_data["fd_satislar"],
            cmp_data["fd_favök"],
            cmp_data["f_k"],
            cmp_data["pd_dd"],
            cmp_data["piyasa_degeri"],
            cmp_data["net_dönem_kari"],
            cmp_data["odenmis_sermaye"],
            cmp_data["öz_kaynaklar"],
            cmp_data["fiili_dolasim"],
            0,
            cmp_data["peg"],
            cmp_data["net_borc"],
            cmp_data["hisse_basina_kar"],
            sector[1],
            sector[2],
            sector[3]
        ))
        conn.commit()
        AppendText("././settings/okunan_sirketler.txt", cmp_data["hisse_adi"])
        cmp_data = None

    clear_screen()

    cmpiess = ReadFile("././settings/okunamayan_sirketler.txt")
    infoo = ReadFile("././settings/bilgi.txt")
    if len(cmpiess) > 0:
        print(f"\nOkunamayan Şirketler ;")
        for i in cmpiess:
            print(i)

    if len(infoo) > 0:
        print("\nDönem Farkı Olanlar ;\n")
        for i in infoo:
            print(i)

    conn.close()
    return




def FtReadSectors(login_data):
    for i in range(2):
        result = GetSectors(login_data["access"])
        if result[0]:
            break

    if not result[0]:
        clear_screen()
        print("Sektörler Çekilemedi.")
        return
    
    all_sectors = result[1]
    clear_screen()
    print(f"\n{len(all_sectors)} Adet Sektör Bulundu.\n")
    current_year = get_current_year()

    clear_table(f"{current_year}_sektorler")
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    for sector in tqdm(all_sectors, desc="Sektörler çekiliyor", unit="sektör"):
        for i in range(2):
            result = GetSectorDetail(sector["url"], login_data["access"])
            try:
                title = sector["title"]
                title = title.replace("Sektörü", "")
                sector["title"] = title
            except Exception as err:
                pass

            if result[0]:
                sector_detail = result[1]
                cursor.execute(f"""
                INSERT INTO '{current_year}_sektorler' (SEKTOR_ADI, SEKTOR_FK, SEKTOR_PD_DD, SEKTOR_FD_FAVOK, BIST_FK, BIST_PD_DD) 
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    sector["title"],
                    sector_detail.get("medyan_fk", None),
                    sector_detail.get("medyan_pddd", None),
                    sector_detail.get("medyan_fd_favok", None),
                    sector_detail.get("bist_fk", None),
                    sector_detail.get("bist_pddd", None)
                ))
                conn.commit()
                break
            else:
                continue

    clear_screen()
    conn.close()




          
def DBToTxt(db_name):
    try:
        folder_name = db_name.split(".")[0]
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            table_name = table_name[0]
            query = f'SELECT * FROM "{table_name}"'
          
            cursor.execute(query)
            rows = cursor.fetchall()
          
            column_names = [description[0] for description in cursor.description]
          
            txt_filename = os.path.join(folder_name, f"{table_name}.txt")
            with open(txt_filename, mode='w', encoding='utf-8') as file:
                file.write(";".join(column_names) + "\n")
              
                for row in rows:
                    file.write(";".join(str(value) for value in row) + "\n")
        conn.close()
        return [True]
    except Exception as err:
        print(err)
        return [False]



if __name__ == "__main__":
    MainMenu()
