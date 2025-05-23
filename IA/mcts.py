import random
import time
import math

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
        self.untried_moves = []  # Store untried moves for faster expansion

    def add_children(self, children: dict) -> None:
        for child in children:
            self.children[child.move] = child

    def value(self, explore: float = MCTSMeta.EXPLORATION):
        if self.N == 0:
            return 0 if explore == 0 else GameMeta.INF
        else:
            return self.Q / self.N + explore * math.sqrt(math.log(self.parent.N) / self.N)

    def is_fully_expanded(self):
        """Check if all possible moves have been tried from this node"""
        return len(self.untried_moves) == 0


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
        
        # Performance monitoring
        self.nodes_created = 0
        self.total_playouts = 0
    
    def select_node(self) -> tuple:
        """Select a node to expand or simulate using UCB1"""
        node = self.root
        game = self.root_game.clone()  # Clone only once per selection
        current_player = self.current_player

        # Selection phase - traverse tree until we find a node to expand
        while not node.is_fully_expanded() and len(node.children) > 0:
            # Select child with highest UCB value
            children = list(node.children.values())
            if not children:  # Ensure we have children to evaluate
                break
                
            max_value = max(children, key=lambda n: n.value()).value()
            max_nodes = [n for n in children if n.value() == max_value]
            
            # Ensure max_nodes is not empty before choosing
            if not max_nodes:
                break
                
            # Choose randomly among the best nodes
            node = random.choice(max_nodes)
            
            # Apply the move
            game.make_move(node.move, current_player)
            current_player = game.get_opponent(current_player)

            # If this node hasn't been visited, return it
            if node.N == 0:
                return node, game, current_player

        # Expansion phase - if we reach a leaf node that's not fully expanded
        if not node.is_fully_expanded() and node.untried_moves:  # Check that untried_moves is not empty
            # Choose a random untried move
            move = random.choice(node.untried_moves)
            node.untried_moves.remove(move)
            
            # Apply the move
            game.make_move(move, current_player)
            current_player = game.get_opponent(current_player)
            
            # Create a new child node
            child = Node(move, node)
            child.untried_moves = game.get_valid_moves() or []  # Ensure it's never None
            node.children[move] = child
            self.nodes_created += 1
            
            return child, game, current_player

        return node, game, current_player

    def expand(self, parent: Node, game, current_player) -> bool:
        """Expand a node by adding all possible child nodes"""
        if game.is_terminal():
            return False

        # Get all valid moves for the current player
        if not hasattr(parent, 'untried_moves') or not parent.untried_moves:
            parent.untried_moves = game.get_valid_moves()
        
        if not parent.untried_moves:
            return False

        # Create a child node for each untried move
        for move in parent.untried_moves:
            child = Node(move, parent)
            parent.children[move] = child
            self.nodes_created += 1
        
        # Clear the untried moves list since all have been expanded
        parent.untried_moves = []
        return True

    def roll_out(self, game, current_player):
        """Simulate a random game from the current state until terminal"""
        original_player = self.current_player
        
        # Use a depth limit to avoid extremely long playouts
        max_playout_depth = 50
        depth = 0
        
        # Simulate random moves until the game is over
        while not game.is_terminal() and depth < max_playout_depth:
            valid_moves = game.get_valid_moves()
            if not valid_moves:  # This check is already here, which is good
                break
            
            move = random.choice(valid_moves)
            game.make_move(move, current_player)
            current_player = game.get_opponent(current_player)
            depth += 1
        
        self.total_playouts += 1
        
        # If we hit depth limit but game is not terminal, evaluate position
        if depth >= max_playout_depth and not game.is_terminal():
            score = game.evaluate(original_player)
            if score > 0:
                return GameMeta.WIN
            elif score < 0:
                return GameMeta.LOSS
            else:
                return GameMeta.DRAW
        
        # Determine the outcome
        if game.check_win(original_player):
            return GameMeta.WIN
        elif game.check_win(game.get_opponent(original_player)):
            return GameMeta.LOSS
        else:
            return GameMeta.DRAW

    def back_propagate(self, node: Node, outcome: int) -> None:
        """Update the statistics of the nodes in the path from the node to the root"""
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
            # 1. Selection and Expansion
            node, game, current_player = self.select_node()
            
            # 2. Simulation
            outcome = self.roll_out(game, current_player)
            
            # 3. Backpropagation
            self.back_propagate(node, outcome)
            num_rollouts += 1

        run_time = time.time() - start_time
        self.run_time = run_time
        self.num_rollouts = num_rollouts
        
        # Print statistics if requested
        # print(f"Nodes created: {self.nodes_created}, Rollouts: {self.total_playouts}, Time: {run_time:.3f}s")

    def best_move(self):
        """Get the best move according to the most visited node"""
        if not self.root.children:
            return -1  # No valid moves
        
        # Choose the move with the highest exploitation score (Q/N)
        best_child = max(self.root.children.values(), key=lambda n: n.Q/n.N if n.N > 0 else 0)
        return best_child.move

    def get_move(self, game, player):
        """Get the best move according to the MCTS algorithm"""
        self.root_game = game.clone()  # Only clone once at the beginning
        self.current_player = player
        self.root = Node(None, None)
        
        # Initialize root's untried moves
        valid_moves = self.root_game.get_valid_moves()
        self.root.untried_moves = valid_moves if valid_moves else []  # Ensure it's never None
        
        # Track nodes and playouts
        self.nodes_created = 1  # Root
        self.total_playouts = 0
        
        # Check if game is already over
        if game.is_terminal():
            return -1
        
        # Run the MCTS algorithm
        self.search()
        
        # Get the best move
        return self.best_move()

    def statistics(self) -> tuple:
        """Get statistics about the last search"""
        return self.num_rollouts, self.run_time, self.nodes_created
        
    def print_type(self):
        """Print the type of algorithm"""
        print("MCTS")
