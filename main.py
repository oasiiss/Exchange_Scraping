import sqlite3
from actions.auth import Login
from actions.sector import GetSectors, GetSectorDetail
from actions.read_config import ReadConfig
import sys, time

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
        HISSE_ADI TEXT,
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
        time.sleep(5)
        sys.exit(0)
    
    config = result[1]

    setup_database()

    result = Login("", "")
    if not result[0]:
        print(result[1])
        sys.exit(0)
    login_data = result[1]

    print(login_data)

    result = GetSectors(login_data["access"])
    if not result[0]:
        print(result[1])
        sys.exit(0)
    all_sectors = result[1]

    clear_table("2024_sektorler")

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    for sector in all_sectors:
        result = GetSectorDetail(sector["url"], login_data["access"])
        if result[0]:
            sector_detail = result[1]
            print(sector["title"])
            print(sector_detail)

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

        else:
            print(sector["title"])
            print(result[1])

        print("")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
