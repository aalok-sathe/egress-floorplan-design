#!/usr/bin/env python3

'''
This program is Free Software
(C) 2019, Aalok S.

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
                             ['Walls', 'People', 'Danger'], ]],      
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
    #layout += [bottomrow]

    window = sg.Window('simulation floor layout designer', layout)
    return window


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
    with open(args.output, 'w') as out:
        print(gridstr, file=out)

def click(window, event, values):
    '''
    handles a click event on a square in a grid
    '''
    print('clicked:', event, values)
    
     
    if type(event) is tuple:
        i, j = event
        if i == 0 or i == R-1 or j == 0 or j == C-1:
            print('Cannot alter safe zone! (Tried editing {})'.format((i,j)))
            return
        square = window.Element(event)
        attrs = set(square.ButtonText.split(','))

        global mode
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

        elif mode == 'People':
            if 'W' in attrs:
                print('Can\'t place a human in a wall!')
                return
            elif 'P' in attrs:
                attrs.remove('P')
                color = 'red' if 'F' in attrs else 'lightgrey'
            else:
                attrs.add('P')
                color = 'lightblue' if 'F' not in attrs else 'yellow'

        elif mode == 'Danger':
            if 'F' in attrs:
                attrs.add('N')
                attrs.remove('F')
                color = 'grey' if 'W' in attrs else 'lightgrey'
            else:
                attrs.difference_update({'P', 'N'})
                attrs.add('F')
                color = 'orange' if 'W' in attrs else 'red'

        square.Update(','.join(reversed(sorted(attrs))), 
                      button_color=('white', color))

    elif event == 'Save':
        save(window)
    
    elif event == 'Cancel':
        raise SystemExit
    
    elif event in ['Walls', 'People', 'Danger']:
        global mode
        mode = event

    elif event in ['Reset']:
        global R, C
        for i in range(1, R-1):
            for j in range(1, C-1):
                square = window.Element((i,j))
                square.Update('N', button_color=('white', 'lightgrey'))

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
