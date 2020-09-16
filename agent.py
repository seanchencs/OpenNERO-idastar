from OpenNero import *
from common import *

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

"""
Sean Chen (sc53864)

To implement IDA*, I modified the DFS search agent that is built into OpenNERO.
I changed the adjacency lists (which function as lists of open nodes) to be
sorted by the heuristic (manhattan distance). This change means that when the
DFS algorithm is choosing which branch to explore first, it will choose the most
promising one first. Next, I implemented a bound for the heuristic. This
involves initalizing the bound on start to the heuristic at the starting
position. Then, as the agent begins choosing actions, I exclude potential
branches whose f(n) is greater than the bound by not adding them to the
adjacency list. As I exclude these branches, I keep track of the minimum f(n)
of excluded branches. If the algorithm backtracks to the start and has no more
options, I then restart the search with an increased bound of the mimnimum f(n)
that was excluded as tracked from the previous run.
"""

class IdaStarSearchAgent(SearchAgent):
    """
    IDA* algorithm
    """
    def __init__(self):
        """
        A new Agent
        """
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.visited = set([])
        self.adjlist = {}
        self.parents = {}
        self.heuristic = manhattan_heuristic
        self.min_next_bound = float('inf')

    
    def increment_limit(self):
        self.visited = set([])
        self.parents = {}
        self.backpointers = {}
        self.bound = self.min_next_bound
        self.min_next_bound = float('inf')
        return self.idastar_action(self.starting_observations)

    def idastar_action(self, observations):        
        r = observations[0]
        c = observations[1]
        current_cell = (r, c)
        # if we have not been here before, build a list of other places we can go
        if current_cell not in self.visited:
            tovisit = []
            for m, (dr, dc) in enumerate(MAZE_MOVES):
                r2, c2 = r + dr, c + dc
                if not observations[2 + m]: # can we go that way?
                    if (r2, c2) not in self.visited:
                        f = self.get_distance(r2, c2) + self.heuristic(r2, c2) # f(n) for potential next node
                        if f > self.bound:
                            if f < self.min_next_bound:
                                self.min_next_bound = f
                        else:
                            tovisit.append((r2, c2))
                            self.parents[(r2, c2)] = current_cell
            tovisit.sort(key=lambda x: self.heuristic(x[0], x[1])) # sort the adjlist by the heuristic
            # remember the cells that are adjacent to this one
            self.adjlist[current_cell] = tovisit
        # if we have been here before, check if we have other places to visit
        adjlist = self.adjlist[current_cell]
        k = 0
        while k < len(adjlist) and adjlist[k] in self.visited:
            k += 1
        # if we don't have other neighbors to visit, back up
        if k == len(adjlist):
            if current_cell == self.starting_pos: # no more options, increment limit
                return self.increment_limit()
            next_cell = self.parents[current_cell]
        else: # otherwise visit the next place
            next_cell = adjlist[k]
        self.visited.add(current_cell) # add this location to visited list
        if current_cell != self.starting_pos:
            get_environment().mark_maze_blue(r, c) # mark it as blue on the maze
        v = self.constraints.get_instance() # make the action vector to return
        dr, dc = next_cell[0] - r, next_cell[1] - c # the move we want to make
        v[0] = get_action_index((dr, dc))
        # remember how to get back
        if next_cell not in self.backpointers:
            self.backpointers[next_cell] = current_cell
        return v

    def initialize(self, init_info):
        self.constraints = init_info.actions
        return True

    def start(self, time, observations):
        # return action
        r = observations[0]
        c = observations[1]
        self.starting_pos = (r, c)
        self.starting_observations = observations
        self.bound = self.heuristic(r, c)
        get_environment().mark_maze_white(r, c)
        return self.idastar_action(observations)

    def reset(self):
        self.visited = set([])
        self.parents = {}
        self.backpointers = {}
        self.starting_pos = None

    def act(self, time, observations, reward):
        # return action
        return self.idastar_action(observations)

    def end(self, time, reward):
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        self.reset()
        return True

    def mark_path(self, r, c):
        get_environment().mark_maze_white(r,c)

    def destroy(self):
        """
        After one or more episodes, this agent can be disposed of
        """
        return True

