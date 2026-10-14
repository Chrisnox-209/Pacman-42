# Atlas de police

Deux PNG transparents, avec la même police et la même taille pour tous les textes.
Préparés hors du jeu avec freesansbold.ttf, la police initiale du projet.

- `title.png` : jaune RGB (255, 224, 70), A-Z, espace, tiret et ?.
- `text.png` : blanc RGB (255, 255, 255), les 95 caractères ASCII imprimables : espace, A-Z, a-z, 0-9 et symboles ASCII.

## Dimensions et ordre

Chaque case mesure 20 × 24 pixels, avec 16 cases par ligne, de gauche à droite puis de haut en bas.
Police source : taille 30. Espacement horizontal fixe : 20 pixels.
`title.png` mesure 320 × 48 pixels ; `text.png` mesure 320 × 144 pixels.
Les cases inutilisées et l'espace sont transparents. Référence : fenêtre 800 × 600.

L'ordre et les dimensions sont définis directement dans `src/ui.py` :

```python
TITLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ -?"
TEXT_CHARACTERS = "".join(chr(code) for code in range(32, 127))
FONT_COLUMNS = 16
FONT_WIDTH = 20
FONT_HEIGHT = 24
```

## Intégration

`load_fonts()` charge les deux atlas au démarrage, copie chaque caractère dans une
image et adapte sa taille avec `scaled()` et `resize_image()`.
`render_text()` assemble ces images pour afficher le texte.
Les titres sont jaunes et convertis en majuscules ; tous les autres textes sont blancs.
Le symbole `>` indique l'option de menu sélectionnée.
Les caractères absents, notamment les accents, sont remplacés par `?`.
Aucun fichier JSON n'est nécessaire.
