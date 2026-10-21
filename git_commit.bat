@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: Vérifier si un message a été fourni en argument
if "%~1"=="" (
    echo [ERREUR] Vous devez spécifier un message de commit.
    echo Usage: %~nx0 "Votre message de commit"
    exit /b 1
)

:: Sauvegarder le message dans une variable
set "COMMIT_MSG=%~1"

:: Vérifier si on est dans un dépôt Git
if not exist .git (
    echo [ERREUR] Ce dossier n'est pas un dépôt Git.
    exit /b 1
)

:: Ajouter tous les fichiers modifiés
echo Ajout des fichiers...
git add .

:: Exécuter le commit avec le message passé en argument
echo Création du commit...
git commit -m "%COMMIT_MSG%"

:: On pushe sur le serveur distant
echo Push du commit...
git push

echo Terminé avec succès !
endlocal