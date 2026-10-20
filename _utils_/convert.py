import json

cartes = []

with open("liste.txt", "r", encoding="utf-8") as fichier:
    for ligne in fichier:
        ligne = ligne.strip()

        if not ligne:
            continue

        parties = ligne.split("\t")

        if len(parties) < 3:
            continue

        cartes.append({
            "id": parties[0],
            "name": parties[1],
            "rarity": parties[2]
        })

data = {
    "set": "30th",
    "cartes": cartes
}

with open("cartes.json", "w", encoding="utf-8") as fichier:
    json.dump(data, fichier, ensure_ascii=False, indent=4)

print(f"{len(cartes)} cartes exportées.")