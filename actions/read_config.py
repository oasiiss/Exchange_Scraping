import json

def ReadConfig():
    try:
        with open("./settings/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        ft_username = config.get("ft_username")
        ft_password = config.get("ft_password")
        mt_username = config.get("mt_username")
        mt_password = config.get("mt_password")
        
        if len(ft_username) > 0 and len(ft_password) > 0 and len(mt_username) > 0 and len(mt_password) > 0:
            return [True, {"ft_username" : ft_username, "ft_password" : ft_password, "mt_username" : mt_username, "mt_password" : mt_password}]
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