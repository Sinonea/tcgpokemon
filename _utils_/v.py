import hashlib

for i in range(1, 123):
    num = f"{i:03d}"
    filename = f"Carte_Méga-Évolution_Chaos_Ascendant_{num}.webp" # ou .png selon le fichier source
    # MediaWiki utilise le MD5 du nom du fichier pour structurer les dossiers de hachage
    m = hashlib.md5(filename.encode('utf-8')).hexdigest()
    h1, h2 = m[0], m[0:2]
    
    url = f"https://holopocket.fr/img/pokepedia/{h1}/{h2}/Carte_M%C3%A9ga-%C3%89volution_Chaos_Ascendant_{num}/high.webp"
    print(url)