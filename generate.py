import sys
import collections
from crossword import *
from copy import deepcopy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self, interleave):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack_inference(dict()) if interleave == 1 else self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop through each variable in domain
        for var in self.domains:

            # Loop through each word in variable's domain
            for word in self.domains[var].copy():

                # Check the unary constraints consistency
                # Check the length of word in domain match with length of variable or not
                if len(word) != var.length:

                    # Remove word that its length is different from the length of variable
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Create Boolean variable to check if a revision was made
        # Set this to False since we haven't made any revisions
        revision = False

        # Check if two variables are overlap or not
        # If they overlap then we need to check all the word in X domain
        if self.crossword.overlaps[x, y]:

            # Get index of each variable where they overlap
            x_index, y_index = self.crossword.overlaps[x, y]

            # Get the constraint for X and Y
            # Loop through each word in domain of variable Y to get the character that word in X domains need to match
            constraint = [word[y_index] for word in self.domains[y]]

            # Loop through each word in domain of variable X
            for word in self.domains[x].copy():

                # Check if the character is match or not
                if word[x_index] not in constraint:

                    # Remove word that does not satisfy constraint since it will cause the conflict
                    self.domains[x].remove(word)

                    # Set the revision boolean variable to True since we made the revision
                    revision = True

        # Return the revision boolean variable after check all the words in X domain
        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Check if 'arcs' is None or not to begin with initial list of all arcs in the problem
        if not arcs:

            # Create initial list of all arcs
            queue = collections.deque()

            # Loop through each variable in domains to get the first variable for tuple
            for var_x in self.domains:

                # Loop through each variable in domains again to get the second variable for tuple
                for var_y in self.domains:

                    # Make sure two variables are different
                    if var_x != var_y:

                        # Add tuple to the queue
                        queue.append((var_x, var_y))

        # Otherwise, use `arcs` as the initial list of arcs to make consistent
        else:

            # update arcs to the queue
            queue = collections.deque(arcs)

        # Once we add all the arcs to the queue
        # Make a loop to consider all arcs in the queue
        while queue:

            # Remove arcs from the queue
            x, y = queue.popleft()

            # Check if arc is consistent or not
            if self.revise(x, y):

                # Check is domain of x is empty or not
                if not self.domains[x]:

                    # return False as domain of X is empty which means unsolvable
                    return False

                # Check if all the arcs associated with X are still consistent except y since we already consider it
                for neighbor in self.crossword.neighbors(x) - {y}:

                    # Add to the queue
                    queue.append((neighbor, x))

        # Return True once we made all necessary changes
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if all crossword variable in assignment dictionary
        return True if self.crossword.variables == set(assignment.keys()) else False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Loop through each variable in assignment dictionary
        for var in assignment:

            # Check if the length of the word is match with variable length
            if var.length != len(assignment[var]):
                return False

            # Check if there are any conflicts between neighboring variables
            # Loop through all neighbors of variable that also in assignment dictionary
            for neighbor in self.crossword.neighbors(var).intersection(assignment.keys()):

                # Get the index where they overlap
                i, j = self.crossword.overlaps[neighbor, var]

                # Check if there any conflicts
                if assignment[neighbor][i] != assignment[var][j]:
                    return False

        # Return True after checking all requirements
        return True if len(set(assignment.values())) == len(list(assignment.values())) else False

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Create a dictionary to store all the word in variable domain with heuristic value
        d = {word: 0 for word in self.domains[var]}

        # Loop through each word in variable domain:
        for word in self.domains[var]:

            # Loop through each neighbor of variable
            for neighbor in self.crossword.neighbors(var):

                # Check if neighbor in assignment or not
                # Neighbor in assignment already has a value so it shouldn't be counted
                if neighbor not in assignment:

                    # Get the index where they overlap
                    i, j = self.crossword.overlaps[var, neighbor]

                    # Loop through each word in neighbor domain
                    for neighbor_word in self.domains[neighbor]:

                        # Increase heuristic value by 1 everytime a word is not qualified which means removed
                        d[word] += 1 if word[i] != neighbor_word[j] else 0

        # Return word in asc order of heuristic value
        return [word for word in sorted(d, key=lambda x:d[x])]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get the unassigned variable list
        unassigned_var = list(set(self.domains.keys() - assignment.keys()))

        # Return variable from the sorted list with order of minimum number of remaining values then highest degree
        return sorted(unassigned_var, key=lambda x:(len(self.domains[x]), -len(self.crossword.neighbors(x))))[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check the assignment is complete or not
        if self.assignment_complete(assignment):

            # Return that completed assignment
            return assignment

        # Get the variable that not assigned any value yet
        var = self.select_unassigned_variable(assignment)

        # Loop through domain to try assign a value to variable
        for value in self.order_domain_values(var, assignment):

            # Create a copy of assignment to attempt value
            new_assignment = deepcopy(assignment)

            # Attempt to add value to copy of assignment
            new_assignment[var] = value

            # Check the consistency of new assignment after adding value to variable
            if self.consistent(new_assignment):

                # Get the result with latest update by recursively backtracking with backtrack function
                result = self.backtrack(new_assignment)

                # Check the latest result
                if result:

                    # Return result once it's satisfied
                    return result

        # Return None if no satisfying assignment is possible
        return None

    def backtrack_inference(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        Improve efficiency by interleave searching with inference - using AC-3 algorithm
        (as by maintaining arc consistency every time you make a new assignment)

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check the assignment is complete or not
        if self.assignment_complete(assignment):

            # Return that completed assignment
            return assignment

        # Get the variable that not assigned any value yet
        var = self.select_unassigned_variable(assignment)

        # Loop through domain to try assign a value to variable
        for value in self.order_domain_values(var, assignment):

            # Create a copy of assignment to attempt value
            new_assignment = deepcopy(assignment)

            # Attempt to add value to copy of assignment
            new_assignment[var] = value

            # Check the consistency of new assignment after adding value to variable
            if self.consistent(new_assignment):

                # Make a backup copy of domain to reset if value is not satified later
                backup_domains = deepcopy(self.domains)

                # Attempt to set value to the variable in domain
                self.domains[var] = {value}

                # Using AC-3 algorithm to enforce arc consistency whenever a decision is made for a variable
                if self.ac3(arcs=collections.deque((neighbor, var) for neighbor in self.crossword.neighbors(var))):

                    # Get the result with latest update by recursively backtracking with backtrack function
                    result = self.backtrack_inference(new_assignment)

                    # Check the latest result
                    if result:

                        # Return result once it's satisfied
                        return result

                # If the value leads to failure then reset the domains back to make new attempt
                self.domains = backup_domains

        # Return None if no satisfying assignment is possible
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4, 5]:
        sys.exit("Usage: python generate.py structure words interleave(Yes/No) [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    interleave = 1 if len(sys.argv) == 4 and sys.argv[3].lower() == "yes" else 0
    output = sys.argv[4] if len(sys.argv) == 5 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve(interleave)

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
