import os
import re

DOSSIER = "liste"   # adaptez si votre dossier s'appelle autrement
SIMULATION = False       # True = affiche seulement, False = renomme vraiment

motif = re.compile(r"^.*?_(\d+)(\.\w+)$")

for nom in sorted(os.listdir(DOSSIER)):
    m = motif.match(nom)
    if not m:
        print("Ignoré :", nom)
        continue

    nouveau = m.group(1) + m.group(2)   # ex. 001.webp
    if nouveau == nom:
        continue

    ancien_chemin = os.path.join(DOSSIER, nom)
    nouveau_chemin = os.path.join(DOSSIER, nouveau)

    if os.path.exists(nouveau_chemin):
        print("Existe déjà, ignoré :", nouveau)
        continue

    print(f"{nom}  ->  {nouveau}")
    if not SIMULATION:
        os.rename(ancien_chemin, nouveau_chemin)

if SIMULATION:
    print("\nSimulation terminée. Passez SIMULATION = False pour renommer pour de bon.")