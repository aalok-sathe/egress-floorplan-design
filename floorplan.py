#!/usr/bin/env python3

'''
This program is Free Software

Introduction
---
A PySimpleGUI-based graphical grid that allows users to annotate locations for
many kinds of terrains/members:
    N (normal/none)
    F (fire/danger)
    P (people)
    W (wall)
    S (safe zone)

A square in the grid may be 
    0 or 1 of {N, F}
  AND 
    0 or 1 of {W, P}
If nothing, a square must have at least the 'N' attribute


Usage
---
1. Annotate
To annotate a square, click on a square in the grid. Click again to undo.

2. Select mode
To choose the attribute you wish to annotate with using Options > Editing mode.

3. Save to file
Choose File > Save in order to save the layout to txt (default: floor.txt)

4. Load and edit from file
(NotImplemented)
'''

import PySimpleGUI as sg
from random import randint
import argparse
from collections import defaultdict
import pickle
import pprint
from functools import lru_cache


pp = pprint.PrettyPrinter(indent=4)

class Grid:

    def __init__(self, R, C, args):
        self.mode = 'Walls'
        self.R = R
        self.C = C
        self.args = args
        self.window = None
        self.graph = None


    def setup(self):
        '''
        makes the initial setup of the floor plan with R rows and C cols
        '''
        mode, R, C = self.mode, self.R, self.C 
        layout = []
      
        menu_def = [['File', ['Reset', 'Open', 'Save', 'Exit']],      
                    ['Options', ['Editing mode', 
                                 ['Walls', 'Bottleneck', 'Danger'], ]],      
                    ['Help', '(NotImplemented) About...'], ]
        layout += [[sg.Menu(menu_def, tearoff=True)]]
        
        def button(i, j):
            '''
            short helper to create a button object with preset params
            '''
            r = max(1, int(((R+C)/2)**.1))
            a, b = R//2, C//2
            if i == 0 or i == R-1 or j == 0 or j == C-1:
                return sg.Button('S', button_color=('white', 'lightgreen'), 
                                 size=(1, 1), key=(i, j), pad=(0, 0))
            elif i in range(a-r, a+r) and j in range(b-r, b+r):
                return sg.Button('F', button_color=('white', 'red'), 
                                 size=(1, 1), key=(i, j), pad=(0, 0))
            return sg.Button('N', button_color=('white', 'lightgrey'), size=(1, 1), 
                             key=(i, j), pad=(0, 0))
     

        layout += [[button(i, j) for j in range(C)] for i in range(R)] 
        
        #bottomrow = [
        #    sg.Button('mode: walls', button_color=('white', 'darkblue'), 
        #              size=(10, 1), key='mode'),
        #    sg.SaveAs('Save'), sg.Cancel()
        #        ]
        #
        layout += [[sg.Text('editing mode: {}'.format(mode), key='mode', 
                            size=(30, 1))]]

        self.window = sg.Window('simulation floor layout designer', layout)
        return self.window


    def parse(self, floorlines):
        '''
        method that takes a string representation of the grid and constructs a graph
        useful for a simulation
        '''
        grid = []
        for row in floorlines:
            if not row: continue
            sqs = row.split(';')
            rowattrs = [set(sq.strip().split(',')) for sq in sqs]
            print(rowattrs)
            grid += [rowattrs]


        graph = defaultdict(lambda: {'attrs': dict(), 'nbrs': set()})
        meta = dict(bottleneck=set(), danger=set(), wall=set(), safe=set())

        R, C = len(grid), len(grid[0])
       
        for i in range(R):
            for j in range(C):
                attrs = grid[i][j]
                graph[(i,j)]['attrs'] = {att:int(att in attrs) for att in 'WSBFN'}
                
                for off in {-1, 1}:
                    if 0 <= i+off < R:
                        graph[(i,j)]['nbrs'].add((i+off, j))

                    if 0 <= j+off < C:
                        graph[(i,j)]['nbrs'].add((i, j+off))


        def bfs(target, pos): # iterative dfs
            if graph[pos]['attrs']['W']: return float('inf')
            q = [(pos, 0)]
            visited = set()
            while q:
                node, dist = q.pop()
                if node in visited: continue
                visited.add(node)

                node = graph[node]
                if node['attrs']['W']: continue
                if node['attrs'][target]: return dist

                for n in node['nbrs']:
                    if n in visited: continue
                    q = [(n, dist+1)] + q

            return float('inf')
                
        for i in range(R):
            for j in range(C):
                graph[(i,j)]['attrs']['distF'] = bfs('F', (i,j)) 
                graph[(i,j)]['attrs']['distS'] = bfs('S', (i,j))

         
        self.graph = dict(graph.items())
        return self.graph


    def save(self):
        '''
        saves the current layout to a text file for use by a simulation program
        (or just for your own viewing pleasure)
        '''
        print('saving to', self.args.output)
        window = self.window
        R, C = self.R, self.C

        gridstr = ''
        for i in range(R):
            txts = ['{: >4}'.format(window.Element((i,j)).ButtonText) 
                    for j in range(C)]
            gridstr += ';'.join(txts) + '\n'

        graph = self.parse(gridstr.split('\n'))

        with open(args.output+'.pkl', 'wb') as out:
            pickle.dump(graph, file=out)
        with open(args.output, 'w') as out:
            print(gridstr, file=out)


    def load(self, graph):
        '''
        loads from floor.txt.pkl
        '''
        window = self.window
        self.graph = graph 
        for loc, data in self.graph.items():
            square = window.Element(loc)
            attrs = {att for att in data['attrs'] if data['attrs'][att]}
            attrs.intersection_update(set('WSFBN'))
            if 'W' in attrs:
                color = 'grey'
            elif 'B' in attrs:
                color = 'lightblue' if 'F' not in attrs else 'orange'
            elif 'F' in attrs:
                color = 'red'
            elif 'S' in attrs:
                color = 'lightgreen'
            elif 'N' in attrs:
                color = 'lightgrey'
            elif 'P' in attrs:
                color = 'purple'
            square.Update(','.join(reversed(sorted(attrs))), 
                          button_color=('white', color))


    def loadtxt(self):
        '''
        '''
        with open(self.args.output+'.pkl', 'rb') as pklf:
            graph = pickle.load(pklf)
        self.load(graph) 


    def click(self, event, values):
        '''
        handles a click event on a square in a grid
        '''
        mode, R, C = self.mode, self.R, self.C
        window = self.window
        print('clicked:', event, values)
        
         
        if type(event) is tuple:
            i, j = event
            if i == 0 or i == R-1 or j == 0 or j == C-1:
                print('Cannot alter safe zone! (Tried editing {})'.format((i,j)))
                return
            square = window.Element(event)
            attrs = set(square.ButtonText.split(','))

            if mode == 'Walls':
                if 'W' in attrs:
                    color = 'lightgrey' if 'F' not in attrs else 'red'
                    attrs.remove('W')
                elif 'F' in attrs:
                    color = 'orange'
                    attrs.add('W')
                else:
                    color = 'grey'
                    attrs.add('W')

            elif mode == 'Bottleneck':
                if 'W' in attrs:
                    print('Can\'t place a bottleneck in a wall!')
                    return
                elif 'B' in attrs:
                    attrs.remove('B')
                    color = 'red' if 'F' in attrs else 'lightgrey'
                else:
                    attrs.add('B')
                    color = 'lightblue' if 'F' not in attrs else 'yellow'

            elif mode == 'Danger':
                if 'F' in attrs:
                    attrs.add('N')
                    attrs.remove('F')
                    color = 'grey' if 'W' in attrs else 'lightgrey'
                else:
                    attrs.difference_update({'B', 'N'})
                    attrs.add('F')
                    color = 'orange' if 'W' in attrs else 'red'

            square.Update(','.join(reversed(sorted(attrs))), 
                          button_color=('white', color))

        elif event == 'Save':
            self.save()
        
        elif event == 'Cancel':
            raise SystemExit
        
        elif event in ['Walls', 'Bottleneck', 'Danger']:
            #global mode
            window.Element('mode').Update('editing mode: {}'.format(event))
            self.mode = event

        elif event == 'Reset':
            for i in range(1, R-1):
                for j in range(1, C-1):
                    square = window.Element((i,j))
                    square.Update('N', button_color=('white', 'lightgrey'))

        elif event == 'Open':
            self.loadtxt()

        else:
            print('Unknown event:', event)


def main(args):
    '''
    main method: setup board, and handle the event lifecycle
    '''
    R, C = args.rows, args.cols
    assert 1 < R <= 20 and  1 < C <= 20, 'rows and columns must be 1< x <=20'

    grid = Grid(R, C, args) 
    window = grid.setup()
        
    while True:
        event, values = window.Read()
        if event in (None, 'Exit'):
            break

        grid.click(event, values)

    window.Close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='design a floor plan for '
                                                 'egress simulation programs')
    parser.add_argument('rows', metavar='R',  type=int,
                        help='number of rows in the grid. max: 20')
    parser.add_argument('cols', metavar='C', type=int,
                        help='number of cols in the grid. max: 20')
    parser.add_argument('-o', '--output', default='floor.txt', type=str,
                        help='name of file to output plan to')
    global args
    args = parser.parse_args()
    
    main(args)
