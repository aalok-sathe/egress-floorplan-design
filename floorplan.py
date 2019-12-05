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


#class Grid:
global mode, R, C
mode = 'Walls'

def setup(R, C):
    '''
    makes the initial setup of the floor plan with R rows and C cols
    '''

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

    window = sg.Window('simulation floor layout designer', layout)
    return window


def parsefloor(floor):
    '''
    method that takes a string representation of the grid and constructs a graph
    useful for a simulation
    '''
    grid = []
    for row in floor:
        if not row: continue
        sqs = row.split(';')
        rowattrs = [set(sq.strip().split(',')) for sq in sqs]
        print(rowattrs)
        grid += [rowattrs]


    graph = defaultdict(lambda: {'attrs': dict(), 'nbrs': set()})
    meta = dict(bottleneck=set(), danger=set(), wall=set(), safe=set())

    R, C = len(grid), len(grid[0])
   
    #@lru_cache(maxsize=None)
    def distS(i, j, visited=set()):
        '''
        get the minimum distance from this node to the nearest safe zone
        '''
        print(i, j)
        if (i, j) in visited: 
            print('visited')
            return float('inf')
        if (not 0 <= i < R) or (not 0 <= j < C): return float('inf')

        attrs = graph[(i, j)]['attrs']
        print(i, j, attrs)
        if attrs['S']: return 0 
        if attrs['W']: return float('inf')

        thisvisited = visited.union({(i, j)})

        return 1 + min(
                    distS(i-1, j, thisvisited),
                    distS(i+1, j, thisvisited),
                    distS(i, j-1, thisvisited),
                    distS(i, j+1, thisvisited),
                )
   
    #@lru_cache(maxsize=None)
    def distF(i, j, visited=set()):
        '''
        get the minimum distance from this node to the nearest fire
        '''
        print(i, j)
        if (i, j) in visited: 
            print('visited')
            return float('inf')
        
        if 0 <= i < R and 0 <= j < C:
            pass
        else:
            return float('inf')

        attrs = graph[(i, j)]['attrs']
        print(i, j, attrs)
        if attrs['F']: return 0 
        if attrs['W']: return float('inf')

        thisvisited = visited.union({(i, j)})

        return 1 + min(
                    distF(i-1, j, thisvisited),
                    distF(i+1, j, thisvisited),
                    distF(i, j-1, thisvisited),
                    distF(i, j+1, thisvisited),
                )
 

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
        print('target=', target, 'pos=', pos)
        if graph[pos]['attrs']['W']: return float('inf')
        q = [(pos, 0)]
        visited = set()
        while q:
            print('='*79)
            print(q)
            node, dist = q.pop()
            if node in visited: continue
            visited.add(node)

            node = graph[node]
            if node['attrs']['W']: continue
            if node['attrs'][target]: return dist

            for n in node['nbrs']:
                if n in visited: continue
                q = [(n, dist+1)] + q
            print(q)
            print('='*79)

        return float('inf')
            
    for i in range(R):
        for j in range(C):
            graph[(i,j)]['attrs']['distF'] = bfs('F', (i,j)) 
            graph[(i,j)]['attrs']['distS'] = bfs('S', (i,j))

     

    graph = dict(graph.items())
    pp.pprint(graph)
    return graph



def save(window):
    '''
    saves the current layout to a text file for use by a simulation program
    (or just for your own viewing pleasure)
    '''
    global args
    print('saving to', args.output)
    
    gridstr = ''
    global R, C
    for i in range(R):
        txts = ['{: >4}'.format(window.Element((i,j)).ButtonText) 
                for j in range(C)]
        gridstr += ';'.join(txts) + '\n'

    graph = parsefloor(gridstr.split('\n'))

    with open(args.output+'.pkl', 'wb') as out:
        pickle.dump(graph, file=out)
    with open(args.output, 'w') as out:
        print(gridstr, file=out)


def load(window):
    '''
    loads from floor.txt.pkl
    '''
    with open(args.output+'.pkl', 'rb') as pklf:
        graph = pickle.load(pklf)
    
    for loc, data in graph.items():
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
        square.Update(','.join(reversed(sorted(attrs))), 
                      button_color=('white', color))

def click(window, event, values):
    '''
    handles a click event on a square in a grid
    '''
    global mode, R, C
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
        save(window)
    
    elif event == 'Cancel':
        raise SystemExit
    
    elif event in ['Walls', 'Bottleneck', 'Danger']:
        #global mode
        window.Element('mode').Update('editing mode: {}'.format(event))
        mode = event

    elif event == 'Reset':
        for i in range(1, R-1):
            for j in range(1, C-1):
                square = window.Element((i,j))
                square.Update('N', button_color=('white', 'lightgrey'))

    elif event == 'Open':
        load(window)

    else:
        print('Unknown event:', event)

def main(args):
    '''
    main method: setup board, and handle the event lifecycle
    '''
    global R, C
    R, C = args.rows, args.cols
    assert 1 < R <= 20 and  1 < C <= 20, 'rows and columns must be 1< x <=20'

    window = setup(R, C)
        
    while True:
        event, values = window.Read()
        if event in (None, 'Exit'):
            break

        click(window, event, values)

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
