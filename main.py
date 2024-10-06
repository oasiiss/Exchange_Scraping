import sqlite3
from actions.auth import FtLogin, MtLogin
from actions.sector import GetSectors, GetSectorDetail
from actions.read_config import ReadConfig, AppendText, WriteListToFile, ReadFile
from actions.company import GetAllCompany, GetCompanyDetail, GetCompanyInfo, GetRatioAnalysis, GetFDSell, CompareBilanco, GetLastPrice
import sys, time, os, platform
from tqdm import tqdm


def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def setup_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS '2024_sektorler' (
        SEKTOR_ADI TEXT,
        SEKTOR_FK REAL,
        SEKTOR_PD_DD REAL,
        SEKTOR_FD_FAVOK REAL,
        BIST_FK REAL,
        BIST_PD_DD REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS '2024_hisseler' (
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
        HBK REAL
    )
    """)


    sql_query = """
    CREATE TABLE IF NOT EXISTS '2024_araci_kurum' (
        HISSE_ADI TEXT,
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
    
def CompletSektor(value, sectors):
    if value is None:
        return value
    if "..." in value and len(sectors) > 0:
        for sector in sectors:
            if str(sector[:10]).lower() == str(value[:10]).lower():
                value = sector
                return value
    else:
        return value
    
    return value

def MainMenu():
    setup_database()

    result = ReadConfig()
    if not result[0]:
        print("Config Okunamadı ...")
        time.sleep(2)
        sys.exit(0)
    config = result[1]

    while True:
        choice = input(f"\nHangi Platformda İşlem Yapıcaksınız ?\n\n1 - fintables\n2 - malitablolar\n\nSeçimin : ")
        if choice.isnumeric():
            if choice == "1" or choice == "2":
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

        elif choice == 2:
            clear_screen()
            result = MtLogin(config["mt_username"], config["mt_password"])
            if not result[0]:
                clear_screen()
                print(f"\n{config['mt_username']} Mail Adresine Sahip Malitablolar Hesabına Giriş Yapılamadı.")
                continue

            MtMenu(result[1])






def FtMenu(login_data):
    pass



def MtMenu(login_data):
    pass




# def main():
#     setup_database()
#     result = ReadConfig()
#     if not result[0]:
#         print("Config Okunamadı ...")
#         time.sleep(2)
#         sys.exit(0)
#     config = result[1]


#     sectors = []
#     for i in range(3):
#         result = ReadTable("data.db", "2024_sektorler")
#         if result[0]:
#             sectors = result[1]
#             break

#     result = Login(config["username"], config["password"])
#     if not result[0]:
#         print("Giriş Yapılamadı ...")
#         time.sleep(2)
#         sys.exit(0)
#     login_data = result[1]

#     print(f"{config['username']} Hesaba Giriş Yapıldı")

#     while True:
#         while True:
#             choice = input("\n1 - Sektör Oku\n2 - Şirket Oku\n3 - Okunamıyanları Oku\n4 - DB'yi Dönüştür\n5 - Programı Sonlandır\n\nSeçimin : ")
#             if choice.isnumeric():
#                 choice = int(choice)
#                 if choice == 5:
#                     print("Program Kaptılıyor...")
#                     time.sleep(1)
#                     sys.exit(0)
#                 elif choice == 1:
#                     status = 1
#                     break
#                 elif choice == 2:
#                     status = 2
#                     break
#                 elif choice == 3:
#                     status = 3
#                     break
#                 elif choice == 4:
#                     status = 4
#                     break
#                 else:
#                     print("Lütfen Doğru Bir Seçim Yapınız ...")
#                 time.sleep(0.5)
#                 continue
#             else:
#                 print("Lütfen Doğru Bir Seçim Yapınız ...")
#                 time.sleep(0.5)
#                 continue
        
#         if status == 1:
#             result = GetSectors(login_data["access"])
#             if not result[0]:
#                 print("Sektörler Çekilemedi Tekrar Deneyiniz..")
#                 continue

#             all_sectors = result[1]

#             print(f"\n{len(all_sectors)} Adet Sektör Bulundu.\n")

#             clear_table("2024_sektorler")

#             conn = sqlite3.connect('data.db')
#             cursor = conn.cursor()

#             for sector in tqdm(all_sectors, desc="Sektörler çekiliyor", unit="sektör"):
#                 for i in range(2):
#                     result = GetSectorDetail(sector["url"], login_data["access"])
#                     try:
#                         title = sector["title"]
#                         title = title.replace("Sektörü", "")
#                         sector["title"] = title
#                     except Exception as err:
#                         pass

#                     if result[0]:
#                         sector_detail = result[1]
#                         cursor.execute("""
#                         INSERT INTO '2024_sektorler' (SEKTOR_ADI, SEKTOR_FK, SEKTOR_PD_DD, SEKTOR_FD_FAVOK, BIST_FK, BIST_PD_DD) 
#                         VALUES (?, ?, ?, ?, ?, ?)
#                         """, (
#                             sector["title"],
#                             sector_detail.get("medyan_fk", None),
#                             sector_detail.get("medyan_pddd", None),
#                             sector_detail.get("medyan_fd_favok", None),
#                             sector_detail.get("bist_fk", None),
#                             sector_detail.get("bist_pddd", None)
#                         ))
#                         conn.commit()
#                         break
#                     else:
#                         print(f"{i}. Denemede {sector['title']} Başlıklı Sektörün bilgileri çekilemedi")
#                         continue

#             clear_screen()
#             conn.close()

#         elif status == 2 or status == 3:

#             sectors = []
#             for i in range(3):
#                 result = ReadTable("data.db", "2024_sektorler")
#                 if result[0]:
#                     sectors = result[1]
#                     break
                
#             if status == 2:
#                 while True:
#                     choiceee = input("\n1 - Tüm Şirketler\n2 - Listelenen Şirketler\n\nSeçimin : ")
#                     if choiceee.isnumeric():
#                         choiceee = int(choiceee)
#                         if choiceee == 1 or choiceee == 2:
#                             break
#                         else:
#                             print("Lütfen Doğru Bir Seçim Yapınız.xxx")
#                             continue

#                     else:
#                         print("Lütfen Doğru Bir Seçim Yapınız.")
#                         continue

#                 if choiceee == 1:
#                     result = GetAllCompany(login_data["access"])
#                     if not result[0]:
#                         print("Şirket İsimleri Çekilemedi Tekrar Deneyiniz.")
#                         time.sleep(0.5)
#                         continue

#                     companies = result[1]
#                     companies_code = [company['code'] for company in companies]
#                     WriteListToFile("././settings/sirketler.txt", companies_code)
#                 elif choiceee == 2:
#                     companies = ReadFile("././settings/sirketler.txt")
#                     companies = [{"code" : cmp} for cmp in companies]
#                     if not len(companies) > 0:
#                         print("sirketler.txt Dosyasının İçeriği Boş")
#                         time.sleep(1)
#                         continue
#             else:
#                 cmpies = ReadFile("././settings/okunamayan_sirketler.txt")
#                 if not len(cmpies) > 0:
#                     print("Okunamayan Şirket Bulunamadı.")
#                     continue
#                 else:
#                     companies = [{"code" : company} for company in cmpies]

#             WriteListToFile("././settings/okunan_sirketler.txt", [])
#             WriteListToFile("././settings/okunamayan_sirketler.txt", [])
#             WriteListToFile("./bilgi.txt", [])

#             print(f"\n{len(companies)} Adet Şirket Bulundu.\n")

#             conn = sqlite3.connect('data.db')
#             cursor = conn.cursor()

#             for company in tqdm(companies, desc="Şirket Detayları Çekiliyor", unit="Şirket"):
#                 cmp_data = None

#                 for i in range(3):
#                     result = GetCompanyDetail(company["code"], login_data["access"])
#                     if not result[0]:
#                         time.sleep(1)
#                         continue
#                     else:
#                         cmp_data = result[1]
#                         break

#                 if cmp_data is None:
#                     AppendText("././settings/okunamayan_sirketler.txt", company["code"])
#                     time.sleep(0.3)
#                     continue

#                 for i in range(3):
#                     result = GetCompanyInfo(cmp_data["hisse_adi"], login_data["access"])
#                     if not result[0]:
#                         time.sleep(1)
#                         cmp_data["senet_sayisi"] = None
#                         continue
#                     else:
#                         cmp_data["senet_sayisi"] = result[1]
#                         break

#                 for i in range(3):
#                     result = GetRatioAnalysis(cmp_data["hisse_adi"], login_data["access"])
#                     if not result[0]:
#                         time.sleep(1)
#                         cmp_data["favök_marjı"] = None
#                         continue
#                     else:
#                         cmp_data["favök_marjı"] = result[1]
#                         break

#                 for i in range(3):
#                     result = GetFDSell(cmp_data["hisse_adi"])
#                     if not result[0]:
#                         time.sleep(1)
#                         cmp_data["fd_satislar"] = None
#                         cmp_data["son_donem"] = None
#                         continue
#                     else:
#                         cmp_data["fd_satislar"] = result[1][0]
#                         cmp_data["son_donem"] = result[1][1]
#                         break

#                 cmp_data = process_financial_data(cmp_data)
#                 cmp_data = edit_data(cmp_data)
#                 if not CompareBilanco(cmp_data["date"], cmp_data["son_donem"]):
#                     AppendText("./bilgi.txt", f"{cmp_data['hisse_adi']} Kodlu Şirket İçin Dönem Farkı Var fintables : {cmp_data['date']} - İş Yatırım : {cmp_data['son_donem']}")

#                 last_price = None
#                 for i in range(3):
#                     result = GetLastPrice(cmp_data['hisse_adi'])
#                     if result[0]:
#                         last_price = result[1]
#                         break

#                 sector = CompletSektor(cmp_data["sektör"], sectors)
        
#                 cursor.execute("""
#                     INSERT OR REPLACE INTO '2024_hisseler' 
#                     (HISSE_ADI, DONEM, SEKTOR_ADI, SON_FIYAT, ESAS_FAAL_KARI, SATISLAR, FAVOK, FAVOK_MARJI, FD_SATIS, FD_FAVOK, FK, PD_DD, PIYASA_DEGERI, NET_KAR, ODENMIS_SERMAYE, OZKAYNAKLAR, FIIL_DOL_ORANI, SENET_SAYISI, PEG, NETBORC_FAVOK, HBK) 
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 """, (
#                     cmp_data["hisse_adi"],
#                     cmp_data["date"],
#                     sector,
#                     last_price,
#                     cmp_data["esas_faaliyet_kari"],
#                     cmp_data["satislar"],
#                     cmp_data["favök"],
#                     cmp_data["favök_marjı"],
#                     cmp_data["fd_satislar"],
#                     cmp_data["fd_favök"],
#                     cmp_data["f_k"],
#                     cmp_data["pd_dd"],
#                     cmp_data["piyasa_degeri"],
#                     cmp_data["net_dönem_kari"],
#                     cmp_data["odenmis_sermaye"],
#                     cmp_data["öz_kaynaklar"],
#                     cmp_data["fiili_dolasim"],
#                     cmp_data["senet_sayisi"],
#                     cmp_data["peg"],
#                     cmp_data["net_borc"],
#                     cmp_data["hisse_basina_kar"]
#                 ))
#                 conn.commit()
#                 AppendText("././settings/okunan_sirketler.txt", cmp_data["hisse_adi"])
#                 cmp_data = None

#             cmpiess = ReadFile("././settings/okunamayan_sirketler.txt")
#             infoo = ReadFile("./bilgi.txt")

#             if len(cmpiess) > 0:
#                 print(f"\nOkunamayan Şirketler ;")
#                 for i in cmpiess:
#                     print(i)

#             if len(infoo) > 0:
#                 print("\nDönem Farkı Olanlar ;\n")
#                 for i in infoo:
#                     print(i)

#             conn.close()
#             continue

#         elif status == 4:
#             result = DBToTxt("data.db")
#             if result[0]:
#                 print("DB Dönüştürüldü.")
#                 continue
#             else:
#                 print("DB Dönüştürülemedi.")
#                 continue
            

# def DBToTxt(db_name):
#     try:
#         folder_name = db_name.split(".")[0]
#         conn = sqlite3.connect(db_name)
#         cursor = conn.cursor()

#         if not os.path.exists(folder_name):
#             os.makedirs(folder_name)

#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#         tables = cursor.fetchall()

#         for table_name in tables:
#             table_name = table_name[0]
#             query = f'SELECT * FROM "{table_name}"'
            
#             cursor.execute(query)
#             rows = cursor.fetchall()
            
#             column_names = [description[0] for description in cursor.description]
            
#             txt_filename = os.path.join(folder_name, f"{table_name}.txt")
#             with open(txt_filename, mode='w', encoding='utf-8') as file:
#                 file.write(";".join(column_names) + "\n")
                
#                 for row in rows:
#                     file.write(";".join(str(value) for value in row) + "\n")

#         conn.close()

#         return [True]
#     except Exception as err:
#         print(err)
#         return [False]



if __name__ == "__main__":
    MainMenu()
