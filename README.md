# Crossword: A crossword puzzles AI agent

Harvard CS50AI Project

## Description:

An AI program generate crossword puzzles using Backtracking algorithms with AC3-pruning.

## Tech Stack:

* Python

## Background:

How might you go about generating a crossword puzzle? Given the structure of a crossword puzzle (i.e., which squares of the grid are meant to be filled in with a letter), and a list of words to use, the problem becomes one of choosing which words should go in each vertical or horizontal sequence of squares. We can model this sort of problem as a constraint satisfaction problem. Each sequence of squares is one variable, for which we need to decide on its value (which word in the domain of possible words will fill in that sequence). 

## Project Specification:

### enforce_node_consistency
The enforce_node_consistency function should update self.domains such that each variable is node consistent.

### revise
The revise function should make the variable x arc consistent with the variable y.

### ac3
The ac3 function should, using the AC3 algorithm, enforce arc consistency on the problem. Recall that arc consistency is achieved when all the values in each variable’s domain satisfy that variable’s binary constraints.

### assignment_complete
The assignment_complete function should (as the name suggests) check to see if a given assignment is complete.

### consistent
The consistent function should check to see if a given assignment is consistent.

### order_domain_values
The order_domain_values function should return a list of all of the values in the domain of var, ordered according to the least-constraining values heuristic.

### select_unassigned_variable
The select_unassigned_variable function should return a single variable in the crossword puzzle that is not yet assigned by assignment, according to the minimum remaining value heuristic and then the degree heuristic.

### backtrack
The backtrack function should accept a partial assignment assignment as input and, using backtracking search, return a complete satisfactory assignment of variables to values if it is possible to do so.

## How to run

1. Clone this project
2. Run the Crossword game:
   ```
   python generate.py data/'dataset file 1' data/'dataset file 2' (Yes/No) output.png
   ```
   (You can use either `structure0.txt` or `structure1.txt` or `structure2.txt` for the dataset file 1)\
   (You can use either `words0.txt` or `words1.txt` or `words2.txt` for the dataset file 2)\
   (You can use either `Yes` for the ac3 interleave pruning or `No` for the normal ac3)\
   *Note: You'll need to install Pillow package to generate an image file corresponding to a given assignment
   ```
   pip install Pillow
   ```
   
