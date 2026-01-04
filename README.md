# IA_Chest - Intelligence Artificielle pour Jeux de Stratégie

Un projet Python implémentant plusieurs algorithmes d'intelligence artificielle pour jouer aux échecs et au Connect 4. Ce projet compare les performances de différents algorithmes de recherche dans des jeux à deux joueurs à somme nulle.

## 🎮 Jeux Implémentés

- **Échecs** : Implémentation complète avec toutes les règles (roque, en passant, promotion, échec et mat)
- **Connect 4** : Jeu classique de puissance 4

## 🤖 Algorithmes d'IA

Le projet implémente trois algorithmes d'intelligence artificielle avec diverses optimisations :

### 1. Minimax
- Recherche en profondeur configurable
- Table de transposition pour éviter les recalculs
- Heuristique d'historique pour l'ordonnancement des coups
- Statistiques de performance (nœuds évalués, hits de cache)

### 2. Alpha-Beta
- Élagage alpha-bêta pour réduire l'espace de recherche
- **Killer moves** : mémorisation des coups qui causent des élagages
- **MVV-LVA** (Most Valuable Victim - Least Valuable Aggressor) pour l'ordonnancement des captures
- Heuristique d'historique
- Table de transposition
- Statistiques détaillées (nœuds évalués, élagages, hits de cache)

### 3. MCTS (Monte Carlo Tree Search)
- Algorithme basé sur la méthode de Monte Carlo
- UCB1 pour l'équilibre exploration/exploitation
- Temps de réflexion configurable
- Limite de profondeur pour les simulations
- Statistiques de performance (nœuds créés, rollouts, temps)

## 📁 Structure du Projet

```
IA_Chest/
├── game/                  # Implémentations des jeux
│   ├── abstract_game.py   # Interface abstraite pour les jeux
│   ├── chess_game.py      # Implémentation des échecs
│   └── connect4_game.py   # Implémentation du Connect 4
├── IA/                    # Algorithmes d'intelligence artificielle
│   ├── minimax.py         # Algorithme Minimax
│   ├── alphabeta.py       # Algorithme Alpha-Beta
│   └── mcts.py            # Algorithme MCTS
├── view/                  # Interfaces utilisateur
│   └── chessView.py       # Interface graphique pour les échecs
├── test_chess.py          # Tests et tournois pour les échecs
├── test_connect4.py       # Tests et tournois pour le Connect 4
├── main.py                # Point d'entrée principal
├── main_analys.py         # Script d'analyse de résultats
└── results_*.csv          # Résultats des tournois
```

## 🚀 Installation

### Prérequis

- Python 3.7 ou supérieur
- Les dépendances suivantes (optionnelles mais recommandées) :
  - `numpy` : pour les opérations sur les tableaux
  - `tqdm` : pour les barres de progression
  - `matplotlib` et `pandas` : pour l'analyse des résultats

### Installation des dépendances

```bash
pip install numpy tqdm matplotlib pandas
```

## 💻 Utilisation

### Lancement rapide

```bash
python main.py
```

Cela vous permettra de choisir entre :
1. Connect 4
2. Échecs

### Mode Échecs

```bash
python test_chess.py
```

Options disponibles :
1. **Match IA vs IA** : Comparez deux algorithmes
2. **Humain vs IA** : Jouez contre l'IA avec interface graphique
3. **Tournoi** : Organisez un tournoi entre plusieurs algorithmes

### Mode Connect 4

```bash
python test_connect4.py
```

Options disponibles :
1. **Match IA vs IA** : Comparez deux algorithmes
2. **Tournoi** : Tournoi en format ladder avec classement
3. **Humain vs IA** : Jouez contre l'IA

### Exemples d'utilisation

#### Match entre deux algorithmes (Échecs)
```python
from game.chess_game import ChessGame, WHITE, BLACK
from IA.alphabeta import Alphabeta
from IA.mcts import MCTS
from test_chess import play_game

# Créer les algorithmes
ai1 = Alphabeta(max_depth=3)
ai2 = MCTS(thinking_time=500)  # 500ms

# Jouer une partie
winner, moves = play_game(ai1, ai2, verbose=True)
```

#### Tournoi Connect 4
```python
from test_connect4 import tournament
from IA.minimax import Minimax
from IA.alphabeta import Alphabeta
from IA.mcts import MCTS

# Créer les algorithmes
algorithms = [
    Minimax(2),
    Minimax(3),
    Alphabeta(3),
    Alphabeta(4),
    MCTS(200)
]

# Lancer le tournoi
rankings, results = tournament(algorithms, num_iterations=5, verbose=False)
```

## 🎯 Fonctionnalités Avancées

### Optimisations pour les Échecs

- **Cache de coups** : Mémorisation des coups valides pour chaque position
- **Tables de pièces** : Évaluation positionnelle basée sur la position des pièces
- **Détection d'échec optimisée** : Utilisation de positions de rois mises en cache
- **Évaluation avancée** : Prend en compte le matériel, la position, la mobilité et la sécurité du roi

### Optimisations pour Connect 4

- **Ordre des coups** : Priorisation des colonnes centrales
- **Évaluation par fenêtre** : Analyse des configurations de 4 cases
- **Heuristique de position** : Évaluation basée sur les menaces et opportunités

## 📊 Analyse des Résultats

Le projet inclut un script d'analyse (`main_analys.py`) qui permet de :
- Comparer les performances des différents algorithmes
- Générer des statistiques sur les parties jouées
- Exporter les résultats en CSV

## 🔧 Configuration

### Paramètres des Algorithmes

**Minimax / Alpha-Beta** :
- `max_depth` : Profondeur de recherche (1-5 recommandé pour les échecs, 3-6 pour Connect 4)

**MCTS** :
- `thinking_time` : Temps de réflexion en millisecondes (100-2000ms recommandé)

### Exemple de configuration

```python
# Pour des parties rapides
ai_fast = Alphabeta(max_depth=2)

# Pour des parties plus réfléchies
ai_smart = Alphabeta(max_depth=4)

# Pour un équilibre temps/qualité
ai_balanced = MCTS(thinking_time=500)
```

## 📈 Performance

Les algorithmes sont optimisés avec :
- Tables de transposition
- Ordonnancement des coups (killer moves, history heuristic)
- Cache de positions
- Évaluation heuristique améliorée

## 🎓 Concepts Implémentés

- **Recherche adversariale** : Minimax et Alpha-Beta
- **Recherche stochastique** : Monte Carlo Tree Search
- **Optimisations** : Tables de transposition, killer moves, heuristiques d'historique
- **Évaluation de position** : Fonctions d'évaluation pour échecs et Connect 4

## 📝 Notes

- Les échecs implémentent toutes les règles standard (roque, en passant, promotion)
- Les algorithmes peuvent être facilement étendus à d'autres jeux via l'interface `AbstractGame`
- Les résultats des tournois sont sauvegardés automatiquement en CSV

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ajouter de nouveaux algorithmes
- Améliorer les fonctions d'évaluation
- Optimiser les performances
- Ajouter de nouveaux jeux

## 📄 Licence

Ce projet est fourni à des fins éducatives.

---

**Développé pour l'étude et la comparaison d'algorithmes d'intelligence artificielle dans les jeux de stratégie.**

