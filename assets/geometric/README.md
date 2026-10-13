# Textures géométriques Pac-Man

46 images PNG, 1254 × 1254 pixels, fond transparent (RGBA).
Les textures originales ont été créées avec l’outil de génération d’images intégré le 7 octobre 2026. Les directions de Pac-Man ont été préparées ensuite par rotation ou symétrie exacte des pixels, sans génération de nouveaux dessins.

## Fantômes

| Fantôme | Forme | Couleur normale | Dossier |
| --- | --- | --- | --- |
| Athos | Carré arrondi | Rouge | `ghosts/athos/` |
| Porthos | Rond | Rose | `ghosts/porthos/` |
| Aramis | Triangle | Cyan | `ghosts/aramis/` |
| Dartagnan | Croix + | Orange | `ghosts/dartagnan/` |

Chaque dossier contient `normal.png`, `frightened.png` et `returning.png`.
L’interface utilise déjà les textures normales et de fuite selon `game_state.frightened`. Le retour au spawn reste à intégrer.

## Pac-Man

Chaque direction possède huit images, de `frame_00.png` (bouche fermée) à `frame_07.png` (bouche ouverte) :

- `pacman/left/` : les huit images originales.
- `pacman/right/` : miroir horizontal des images de gauche, pour garder l’œil en haut.
- `pacman/up/` : rotation de 270° antihoraire.
- `pacman/down/` : rotation de 90° antihoraire.

Les fichiers sont déjà orientés. Aucune rotation n’est effectuée pendant le jeu et aucune dépendance de préparation des PNG n’est nécessaire pour le lancer.

Ordre de l’animation :

`00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 06 → 05 → 04 → 03 → 02 → 01 → 00`

L’interface utilise 20 ms par étape et ferme la bouche à l’arrêt.
Les marges transparentes et le centre des images sont conservés. Il reste de légères variations de contour entre les frames générées d’origine.

## Adaptation à l’écran

Au démarrage, `resize_image()` dans `src/ui.py` redimensionne les images de Pac-Man et des fantômes par copie des pixels au plus proche voisin. La transparence est conservée. Ce calcul remplace `pygame.transform.smoothscale()` et ne lisse pas les contours.

Les images sont ensuite réutilisées en mémoire. `draw_player()` choisit simplement `images[direction][animation_frame]`.

## Pacgums

- `pellets/pacgum.png` : petite pastille crème.
- `pellets/super_pacgum.png` : grosse pastille dorée avec une étoile claire.

Ces deux textures restent à intégrer. Les marges transparentes font partie des images ; la pacgum simple est volontairement plus petite.
