import argparse
import json
from pathlib import Path
import bisect

# 2-3 Tree Node Class
class TwoThreeNode:
    def __init__(self):
        self.keys = []  # up to 2 keys (permuterms)
        self.vals = []  # corresponding original terms
        self.children = []  # up to 3 children (other nodes)
        self.parent = None  # reference to parent node

    def is_leaf(self):
        return len(self.children) == 0

    def arity(self):
        return len(self.keys)

# 2-3 Tree Class
class TwoThreeTree:
    def __init__(self):
        self.root = TwoThreeNode()  # Start with an empty root node

    def insert(self, key: str, val: str):
        node = self.root
        while not node.is_leaf():
            if node.arity() == 1:
                if key < node.keys[0]:
                    node = node.children[0]
                else:
                    node = node.children[1]
            else:
                if key < node.keys[0]:
                    node = node.children[0]
                elif key < node.keys[1]:
                    node = node.children[1]
                else:
                    node = node.children[2]
        # Once leaf node is found, insert the key
        self._insert_into_node(node, key, val)
        # Fix the tree if necessary (split nodes if full)
        self._fixup(node)
    def _insert_into_node(self, node: TwoThreeNode, key: str, val: str):
        if len(node.keys) < 2:
            node.keys.append(key)
            node.vals.append(val)
            node.keys, node.vals = zip(*sorted(zip(node.keys, node.vals)))  # Sort keys and values
            node.keys = list(node.keys)  # Convert tuple back to list
            node.vals = list(node.vals)  # Convert tuple back to list
        else:
            middle_key = node.keys[1]
            middle_val = node.vals[1]

            left_node = TwoThreeNode()
            right_node = TwoThreeNode()

            left_node.keys = [node.keys[0]]
            left_node.vals = [node.vals[0]]
            right_node.keys = [node.keys[2]] if len(node.keys) > 2 else []  # Check for the third key
            right_node.vals = [node.vals[2]] if len(node.vals) > 2 else []  # Check for the third value

            node.keys = [middle_key]
            node.vals = [middle_val]
            node.children = [left_node, right_node]

            left_node.parent = node
            right_node.parent = node

        self._fixup(node)
    def _fixup(self, node: TwoThreeNode):
        """Fix the tree after insertion by splitting nodes or propagating keys up."""
        # Base case: If node has no parent, it's the root, and no fix-up is needed.
        if node.parent is None:
            return

        # If node has 2 keys, it needs to be split
        if len(node.keys) == 2:
            # We can insert the middle key into the parent
            self.insert(node.keys[1], node.vals[1])

        # If node has 3 keys, it has been split, so propagate upward to the parent node
        elif len(node.keys) == 3:
            # Perform a split and move the middle key upwards
            middle_key = node.keys[1]
            middle_val = node.vals[1]

            # Split the node into two
            left_node = TwoThreeNode()
            right_node = TwoThreeNode()

            # Assign values to the left and right node
            left_node.keys = [node.keys[0]]
            left_node.vals = [node.vals[0]]
            right_node.keys = [node.keys[2]]
            right_node.vals = [node.vals[2]]

            # If the node is the root, we need to handle it specially
            if node.parent is None:
                new_root = TwoThreeNode()
                new_root.keys = [middle_key]
                new_root.vals = [middle_val]
                new_root.children = [left_node, right_node]

                left_node.parent = new_root
                right_node.parent = new_root

                self.root = new_root
            else:
                node.parent.keys.append(middle_key)
                node.parent.vals.append(middle_val)

                # Sort the parent keys and values
                node.parent.keys, node.parent.vals = zip(*sorted(zip(node.parent.keys, node.parent.vals)))
                node.parent.keys = list(node.parent.keys)
                node.parent.vals = list(node.parent.vals)

                # Propagate the changes upward
                self._fixup(node.parent)


    def search(self, query: str) -> list[str]:
        """Search the 2-3 tree for permuterms that match the given query"""
        prefix = wildcard_to_prefix(query)  # Convert wildcard query to permuterm prefix
        return self._search_node(self.root, prefix)

    def _search_node(self, node: TwoThreeNode, prefix: str) -> list[str]:
        """Recursively search the node and its children"""
        results = []
        if node.is_leaf():
            # Binary search for matching keys in the leaf node
            for i, key in enumerate(node.keys):
                if key.startswith(prefix):
                    results.append(node.vals[i])
        else:
            # Binary search for matching children in internal nodes
            for i, key in enumerate(node.keys):
                if prefix < key:
                    results.extend(self._search_node(node.children[i], prefix))
                if prefix == key:
                    results.extend(self._search_node(node.children[i + 1], prefix))
        return results

# Generate permuterms
def gen_permuterms(term: str) -> list[str]:
    w = term + "$"
    return [w[i:] + w[:i] for i in range(len(w))]

# Build the permuterm dictionary and populate the 2-3 tree
def build_perm_map(terms: list[str]) -> TwoThreeTree:
    tree = TwoThreeTree()
    for term in terms:
        for perm in gen_permuterms(term):
            tree.insert(perm, term)
    return tree

# Convert wildcard query to permuterm prefix
def wildcard_to_prefix(query: str) -> str:
    """Convert the wildcard query into a permuterm prefix."""
    print(f"Original query: '{query}'")  # Debugging line
    # If the query contains no '*' wildcard, treat it normally by appending '$'
    if "*" not in query:
        return f"{query}$"
    
    # Otherwise, the query must contain exactly one '*'
    if query.count("*") != 1:
        raise ValueError(f"Invalid query: '{query}'. Only one '*' wildcard is supported.")
    
    # Split the query by '*' into prefix and suffix
    pre, suf = query.split("*", 1)
    print(f"Split query - Prefix: '{pre}', Suffix: '{suf}'")  # Debugging line
    
    # Return the permuterm prefix (suffix + '$' + prefix)
    return f"{suf}${pre}"

# Search for matching permuterms using the 2-3 tree
def search_permuterms(query: str, tree: TwoThreeTree) -> list[str]:
    prefix = wildcard_to_prefix(query)
    print(f"Query: '{query}' converted to permuterm prefix: '{prefix}'")
    results = tree.search(prefix)
#debug for wildcard
    if results:
        print(f"Found {len(results)} matches:")
        for res in results:
            print(f"Match found: '{res}'")
        else:
            print("No matches found.")
   
        
    return results

def main():
    ap = argparse.ArgumentParser(description="Permuterm index with wildcard search")
    ap.add_argument("--inverted", required=True, help="Inverted index JSON from Part 3")
    ap.add_argument("--query", help="Wildcard query with exactly one * (e.g., pre*suf, S*, *S)")
    ap.add_argument("--name", default="YourName", help="Name for TREC output column 6")
    ap.add_argument("--rankval", default="0", help="Column 4 (rank). Spec says 0 for Boolean.")
    args = ap.parse_args()

    # Load the inverted index
    inv = json.load(open(args.inverted, encoding="utf-8"))
    vocab = sorted(inv.keys())  # Sorted list of terms (vocabulary)
    perm_map = build_perm_map(vocab)

    if args.query:
        # Perform wildcard search
        print(f"Received query: {args.query}") #NOT TRIGGERING
        terms = search_permuterms(args.query, perm_map)
        for term in terms:
            doc_ids = inv.get(term, {}).get("postings", [])
            for doc_id in doc_ids:
                print(f"0 1 {doc_id} {args.rankval} 1.0 {args.name}")

if __name__ == "__main__":
    main()
