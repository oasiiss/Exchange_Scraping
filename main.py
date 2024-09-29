import sqlite3
from actions.auth import Login
from actions.sector import GetSectors, GetSectorDetail
import sys

def setup_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS '2024_sektorler' (
        SEKTOR_ADI TEXT,
        SEKTOR_FK TEXT,
        SEKTOR_PD_DD TEXT,
        SEKTOR_FD_FAVOK TEXT,
        BIST_FK TEXT,
        BIST_PD_DD TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def clear_table():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM '2024_sektorler'")
    
    conn.commit()
    conn.close()

def main():
    setup_database()

    result = Login("oasiiss34@gmail.com", "Kmjgts_123")
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

    clear_table()

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
