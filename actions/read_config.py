import json

def ReadConfig():
    try:
        with open("./settings/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        username = config.get("username")
        password = config.get("password")
        all_cmp = config.get("all_cmp")

        if not all_cmp:
            companies = ReadFile("./settings/sirketler.txt")
        else:
            companies = []
        
        if len(username) > 0 and len(password) > 0:
            return [True, {"username" : username, "password" : password, "all_cmp" : all_cmp, "companies" : companies}]
        else:
            return [False, "Config Dosyasında Boş Ayarlar var"]
    except Exception as err:
        return [False, f"Config Okunamadı : {err}"]
    

def ReadFile(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines if len(line.strip()) > 0]
        return lines
    except FileNotFoundError:
        print(f"{filename} bulunamadı.")
        return []

def AppendText(filename, text_to_append):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []
    lines.append(text_to_append + '\n')
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def WriteListToFile(filename, data_list):
    with open(filename, 'w', encoding='utf-8') as file:
        for item in data_list:
            file.write(item + '\n')