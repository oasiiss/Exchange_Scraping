import json

def ReadConfig():
    try:
        with open("./settings/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        username = config.get("username")
        password = config.get("password")
        all_cmp = config.get("all_cmp")
        
        if len(username) > 0 and len(password) > 0:
            return [True, {"username" : username, "password" : password, "all_cmp" : all_cmp}]
        else:
            return [False, "Config Dosyasında Boş Ayarlar var"]
    except Exception as err:
        return [False, f"Config Okunamadı : {err}"]