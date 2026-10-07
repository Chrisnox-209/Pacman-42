# Textures géométriques Pac-Man

22 images PNG, 1254 × 1254 pixels, fond transparent (RGBA).
Créées avec l’outil de génération d’images intégré, le 7 octobre 2026.

## Aperçu

Ouvrir `preview.html` dans un navigateur. La galerie fonctionne hors ligne et montre les trois états des fantômes, les deux pacgums et l’animation de Pac-Man.

## Direction artistique

Formes géométriques simples, couleurs vives, contours bleu nuit et petits reflets clairs.

| Fantôme | Forme | Couleur normale | Dossier |
| --- | --- | --- | --- |
| Athos | Carré arrondi | Rouge | `ghosts/athos/` |
| Porthos | Rond | Rose | `ghosts/porthos/` |
| Aramis | Triangle | Cyan | `ghosts/aramis/` |
| Dartagnan | Croix + | Orange | `ghosts/dartagnan/` |

Chaque dossier contient :

- `normal.png` : apparence normale.
- `frightened.png` : corps indigo, bordure de la couleur du fantôme et expression inquiète.
- `returning.png` : yeux et contour coloré, intérieur transparent pour le retour au spawn.

## Pac-Man

Les 8 fichiers `pacman/frame_00.png` à `pacman/frame_07.png` vont de la bouche fermée à la bouche ouverte. Pac-Man regarde vers la gauche.

Pour ouvrir puis fermer la bouche, lire les images dans cet ordre :

`00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 06 → 05 → 04 → 03 → 02 → 01`

La galerie utilise 65 ms par image. Cette durée peut être ajustée à l’intégration.

Conserver une taille d’affichage et un centre communs à toutes les images. Ne pas recadrer chaque frame séparément. Les PNG sont des images générées : il reste de légères variations de contour entre certaines frames. Le rendu en jeu devra être ajusté à sa taille réelle.

La rotation des sprites permet les autres directions : gauche 0°, bas 90°, droite 180°, haut 270° avec Pygame.

## Pacgums

- `pellets/pacgum.png` : petite pastille crème.
- `pellets/super_pacgum.png` : grosse pastille dorée avec une étoile claire.

Les marges transparentes font partie des images ; la pacgum simple est volontairement plus petite que la super-pacgum.

## Fichiers

`manifest.json` donne les chemins des textures et l’ordre d’animation.
Les prompts exacts sont conservés dans les sous-dossiers.

Les PNG ont été inspectés ensemble dans la galerie et leur canal alpha a été contrôlé. Les 8 images de Pac-Man sont chargées par `ui.py`. Son animation en jeu utilise 20 ms par image et revient à la bouche fermée à l’arrêt. Les fantômes et les pacgums restent à intégrer.
