import os
import time
import requests
from urllib.parse import urlparse, unquote

FICHIERS = ["liste.txt"]
headers = {"User-Agent": "Mozilla/5.0"}

session = requests.Session()
session.headers.update(headers)

for fichier in FICHIERS:
    dossier = os.path.splitext(fichier)[0]
    os.makedirs(dossier, exist_ok=True)

    with open(fichier, encoding="utf-8") as f:
        urls = [ligne.strip() for ligne in f if ligne.strip()]

    print(f"\n== {fichier} : {len(urls)} liens ==")
    erreurs = []

    for url in urls:
        # Nom = avant-dernier segment de l'URL (ex. 001 ou Carte_..._001)
        segments = urlparse(url).path.rstrip("/").split("/")
        nom = unquote(segments[-2]) + ".webp"
        chemin = os.path.join(dossier, nom)

        if os.path.exists(chemin):
            print("Déjà là :", nom)
            continue

        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            with open(chemin, "wb") as out:
                out.write(r.content)
            print("OK :", nom)
        except requests.RequestException as e:
            print("Erreur :", nom, e)
            erreurs.append(url)

        time.sleep(1)  # pause pour ne pas surcharger le serveur

    if erreurs:
        with open(f"erreurs_{dossier}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(erreurs))
        print(f"{len(erreurs)} échec(s), listés dans erreurs_{dossier}.txt")