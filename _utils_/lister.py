import os

DOSSIER = "."      # dossier à lister ("." pour le dossier courant)
SORTIE = "liste.txt"

noms = []
for nom in sorted(os.listdir(DOSSIER)):
    chemin = os.path.join(DOSSIER, nom)
    if os.path.isfile(chemin):
        noms.append(os.path.splitext(nom)[0])

with open(SORTIE, "w", encoding="utf-8") as f:
    f.write("\n".join(noms))

print(f"{len(noms)} fichiers listés dans {SORTIE}")