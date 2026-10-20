import os
import time
import requests
from urllib.parse import urlparse, unquote

FICHIER = "30thExtra.txt"
DOSSIER = "30thExtra"
if not os.path.exists(FICHIER):
    FICHIER = "30thExtra"   # au cas où le fichier n'a pas d'extension

os.makedirs(DOSSIER, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

with open(FICHIER, encoding="utf-8") as f:
    urls = [l.strip() for l in f if l.strip()]

print(f"{len(urls)} liens trouvés")
erreurs = []
correspondance = []

for i, url in enumerate(urls, start=1):
    nom = f"CC{i:03d}.webp"
    chemin = os.path.join(DOSSIER, nom)
    # nom d'origine de la carte (décodé), gardé pour la correspondance
    origine = unquote(urlparse(url).path.split("/")[-2])
    correspondance.append(f"{nom}\t{origine}")

    if os.path.exists(chemin):
        print("Déjà là :", nom)
        continue

    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        with open(chemin, "wb") as out:
            out.write(r.content)
        print("OK :", nom, "<-", origine)
    except requests.RequestException as e:
        print("Erreur :", nom, e)
        erreurs.append(url)

    time.sleep(1)

# fichier de correspondance CCxxx -> nom d'origine
with open(os.path.join(DOSSIER, "correspondance.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(correspondance))

if erreurs:
    with open("erreurs_30thExtra.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(erreurs))
    print(f"{len(erreurs)} échec(s), listés dans erreurs_30thExtra.txt")
else:
    print("Tout est téléchargé.")