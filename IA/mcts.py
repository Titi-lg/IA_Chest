import random
import time
import math
from copy import deepcopy

class MCTSMeta:
    EXPLORATION = 1.41  # UCB1 exploration parameter
    
class GameMeta:
    INF = float('inf')
    DRAW = 0
    WIN = 1
    LOSS = -1
    ONGOING = None

class Node:
    def __init__(self, move, parent):
        self.move = move
        self.parent = parent
        self.N = 0  # Number of visits
        self.Q = 0  # Total score
        self.children = {}
        self.outcome = GameMeta.ONGOING

    def add_children(self, children: dict) -> None:
        for child in children:
            self.children[child.move] = child

    def value(self, explore: float = MCTSMeta.EXPLORATION):
        if self.N == 0:
            return 0 if explore == 0 else GameMeta.INF
        else:
            return self.Q / self.N + explore * math.sqrt(math.log(self.parent.N) / self.N)


class MCTS:
    def __init__(self, thinking_time=200):
        """Initialize the MCTS algorithm
        
        Args:
            thinking_time: Time to think in milliseconds
        """
        self.root = Node(None, None)
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0
        self.thinking_time = float(thinking_time/1000)  # Convert to seconds
        self.root_game = None
        self.current_player = None
    
    def get_move(self, game, player):
        """Get the best move according to the MCTS algorithm
        
        Args:
            game: The current game state (AbstractGame)
            player: The current player
            
        Returns:
            The best move
        """
        self.root_game = game.clone()
        self.current_player = player
        self.root = Node(None, None)
        
        # Check if game is already over
        if game.is_terminal():
            return -1
        
        # Run the MCTS algorithm
        self.search()
        
        # Get the best move
        return self.best_move()

    def select_node(self) -> tuple:
        """Select a node to expand or simulate
        
        Returns:
            A tuple (node, game_state)
        """
        node = self.root
        game = deepcopy(self.root_game)
        current_player = self.current_player

        # Traverse the tree until we find a node to expand or simulate
        while len(node.children) != 0:
            children = node.children.values()
            max_value = max(children, key=lambda n: n.value()).value()
            max_nodes = [n for n in children if n.value() == max_value]

            # Choose randomly among the best nodes
            node = random.choice(max_nodes)
            
            # Apply the move
            game.make_move(node.move, current_player)
            current_player = game.get_opponent(current_player)

            # If this node hasn't been visited, return it
            if node.N == 0:
                return node, game, current_player

        # If we reach a leaf node, try to expand it
        if self.expand(node, game, current_player):
            # Choose a child node randomly
            node = random.choice(list(node.children.values()))
            game.make_move(node.move, current_player)
            current_player = game.get_opponent(current_player)

        return node, game, current_player

    def expand(self, parent: Node, game, current_player) -> bool:
        """Expand a node by adding all possible child nodes
        
        Args:
            parent: The parent node to expand
            game: The current game state
            current_player: The player to move
            
        Returns:
            True if the node was expanded, False otherwise
        """
        if game.is_terminal():
            return False

        # Create a child node for each valid move
        children = [Node(move, parent) for move in game.get_valid_moves()]
        parent.add_children(children)

        return True

    def roll_out(self, game, current_player):
        """Simulate a random game from the current state until terminal
        
        Args:
            game: The current game state
            current_player: The player to move
            
        Returns:
            The outcome of the game from the perspective of the original player
        """
        original_player = self.current_player
        
        # Simulate random moves until the game is over
        while not game.is_terminal():
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break
            
            move = random.choice(valid_moves)
            game.make_move(move, current_player)
            current_player = game.get_opponent(current_player)
        
        # Determine the outcome
        if game.check_win(original_player):
            return GameMeta.WIN
        elif game.check_win(game.get_opponent(original_player)):
            return GameMeta.LOSS
        else:
            return GameMeta.DRAW

    def back_propagate(self, node: Node, outcome: int) -> None:
        """Update the statistics of the nodes in the path from the node to the root
        
        Args:
            node: The starting node
            outcome: The outcome of the simulation
        """
        # For win, add 1; for draw, add 0.5; for loss, add 0
        reward = 1.0 if outcome == GameMeta.WIN else (0.5 if outcome == GameMeta.DRAW else 0.0)

        # Update all nodes in the path
        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent
            # Flip the reward for opponent's perspective
            reward = 1.0 - reward

    def search(self):
        """Run the MCTS algorithm for a specified amount of time"""
        start_time = time.time()

        num_rollouts = 0
        while time.time() - start_time < self.thinking_time:
            node, game, current_player = self.select_node()
            outcome = self.roll_out(game, current_player)
            self.back_propagate(node, outcome)
            num_rollouts += 1

        run_time = time.time() - start_time
        self.run_time = run_time
        self.num_rollouts = num_rollouts

    def best_move(self):
        """Get the best move according to the most visited node
        
        Returns:
            The best move
        """
        if not self.root.children:
            return -1  # No valid moves
        
        # Choose the move with the highest number of visits
        max_visits = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_visits]
        best_child = max(max_nodes, key=lambda n: n.Q/n.N if n.N > 0 else 0)
        
        return best_child.move

    def statistics(self) -> tuple:
        """Get statistics about the last search
        
        Returns:
            A tuple (num_rollouts, run_time)
        """
        return self.num_rollouts, self.run_time
        
    def print_type(self):
        """Print the type of algorithm"""
        print("MCTS")
