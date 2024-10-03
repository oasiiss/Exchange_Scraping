import sqlite3
from actions.auth import Login
from actions.sector import GetSectors, GetSectorDetail
from actions.read_config import ReadConfig, AppendText, WriteListToFile, ReadFile
from actions.company import GetAllCompany, GetCompanyDetail, GetCompanyInfo, GetRatioAnalysis, GetFDSell, CompareBilanco
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
    
    conn.commit()
    conn.close()

def clear_table(table_name):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM '{table_name}'")
    conn.commit()
    conn.close()

def main():
    result = ReadConfig()
    if not result[0]:
        print("Config Okunamadı ...")
        time.sleep(2)
        sys.exit(0)
    config = result[1]

    setup_database()

    result = Login(config["username"], config["password"])
    if not result[0]:
        print("Giriş Yapılamadı ...")
        time.sleep(2)
        sys.exit(0)
    login_data = result[1]

    print(f"{config['username']} Hesaba Giriş Yapıldı")

    while True:
        clear_screen()
        while True:
            choice = input("\n1 - Sektörleri Çek\n2 - Hisseleri Çek\n3 - Programı Sonlandır\n\nSeçimin : ")
            if choice.isnumeric():
                choice = int(choice)
                if choice == 3:
                    print("Program Kaptılıyor...")
                    time.sleep(1)
                    sys.exit(0)
                elif choice == 1:
                    status = 1
                    break
                elif choice == 2:
                    status = 2
                    break
                else:
                    print("Lütfen Doğru Bir Seçim Yapınız ...")
                time.sleep(0.5)
                continue
            else:
                print("Lütfen Doğru Bir Seçim Yapınız ...")
                time.sleep(0.5)
                continue
        
        if status == 1:
            result = GetSectors(login_data["access"])
            if not result[0]:
                print("Sektörler Çekilemedi Tekrar Deneyiniz..")
                continue

            all_sectors = result[1]

            print(f"\n{len(all_sectors)} Adet Sektör Bulundu.\n")

            clear_table("2024_sektorler")

            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()

            for sector in tqdm(all_sectors, desc="Sektörler çekiliyor", unit="sektör"):
                for i in range(2):
                    result = GetSectorDetail(sector["url"], login_data["access"])
                    if result[0]:
                        sector_detail = result[1]
                        cursor.execute("""
                        INSERT INTO '2024_sektorler' (SEKTOR_ADI, SEKTOR_FK, SEKTOR_PD_DD, SEKTOR_FD_FAVOK, BIST_FK, BIST_PD_DD) 
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
                        print(f"{i}. Denemede {sector['title']} Başlıklı Sektörün bilgileri çekilemedi")
                        continue

            clear_screen()
            conn.close()

        elif status == 2:
            WriteListToFile("././settings/okunan_sirketler.txt", [])
            WriteListToFile("././settings/okunamayan_sirketler.txt", [])
            WriteListToFile("./bilgi.txt", [])
            if config["all_cmp"]:
                result = GetAllCompany(login_data["access"])
                if not result[0]:
                    print("Şirket İsimleri Çekilemedi Tekrar Deneyiniz.")
                    time.sleep(0.5)
                    continue

                companies = result[1]
                companies_code = [company['code'] for company in companies]
                WriteListToFile("././settings/sirketler.txt", companies_code)
            else:
                companies = ReadFile("././settings/sirketler.txt")
                companies = [{"code" : cmp} for cmp in companies]
                if not len(companies) > 0:
                    print("sirketler.txt Dosyasnın İçeriği Boş")
                    time.sleep(1)
                    continue

            print(f"\n{len(companies)} Adet Şirket Bulundu.\n")

            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()

            for company in tqdm(companies, desc="Şirket Detayları Çekiliyor", unit="Şirket"):
                result = GetCompanyDetail(company["code"], login_data["access"])
                if not result[0]:
                    clear_screen()
                    AppendText("././settings/okunamayan_sirketler.txt", company["code"])
                    cmp_data = None
                    time.sleep(0.3)
                    continue
                cmp_data = result[1]

                result = GetCompanyInfo(cmp_data["hisse_adi"], login_data["access"])
                if not result[0]:
                    cmp_data["senet_sayisi"] = None
                cmp_data["senet_sayisi"] = result[1]

                result = GetRatioAnalysis(cmp_data["hisse_adi"], login_data["access"])
                if not result[0]:
                    cmp_data["favök_marjı"] = None
                cmp_data["favök_marjı"] = result[1]

                result = GetFDSell(cmp_data["hisse_adi"])
                if not result[0]:
                    cmp_data["fd_satislar"] = None
                    cmp_data["son_donem"] = None

                cmp_data["fd_satislar"] = result[1][0]
                cmp_data["son_donem"] = result[1][1]

                if not CompareBilanco(cmp_data["date"], cmp_data["son_donem"]):
                    AppendText("./bilgi.txt", f"{cmp_data['hisse_adi']} Kodlu Şirket İçin Dönem Farkı Var fintables : {cmp_data['date']} - İş Yatırım : {cmp_data['son_donem']}")

                cursor.execute("""
                    INSERT OR REPLACE INTO '2024_hisseler' 
                    (HISSE_ADI, SEKTOR_ADI, SON_FIYAT, ESAS_FAAL_KARI, SATISLAR, FAVOK, FAVOK_MARJI, FD_SATIS, FD_FAVOK, FK, PD_DD, PIYASA_DEGERI, NET_KAR, ODENMIS_SERMAYE, OZKAYNAKLAR, FIIL_DOL_ORANI, SENET_SAYISI, PEG, NETBORC_FAVOK, HBK) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cmp_data["hisse_adi"],
                    cmp_data["sektör"],
                    "122",
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
                    cmp_data["senet_sayisi"],
                    cmp_data["peg"],
                    cmp_data["net_borc"],
                    cmp_data["hisse_basina_kar"]
                ))
                conn.commit()
                AppendText("././settings/okunan_sirketler.txt", cmp_data["hisse_adi"])
                cmp_data = None
            clear_screen()
            conn.close()


if __name__ == "__main__":
    main()
