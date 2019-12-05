# floorplan

Introduction
---
A PySimpleGUI-based graphical grid that allows users to annotate locations for
four kinds of terrains/members:
  - N (normal/none)
  - F (fire/danger)
  - P (people)
  - W (wall)
  - S (safe)

A square in the grid may be 
    0 or 1 of {N, F}
  AND 
    0 or 1 of {W, P}
If nothing, a square must have at least the 'N' attribute

The program outputs a graph as a pickled dictionary:
```python
graph = {
          (i,j): {'attrs': {'W': 0 or 1, 'N': 0 or 1, 'F': 0 or 1, ...}, 'nbrs': set},
            .
            .
            .
        }
```
    

Usage
---

### First, launch via commandline
```
./floorplan.py [-h] [-o OUTPUT] R C

design a floor plan for egress simulation programs

positional arguments:
  R                     number of rows in the grid. max: 20
  C                     number of cols in the grid. max: 20

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        name of file to output plan to (default: floor.txt)
```

### Once in the GUI
1. Annotate
To annotate a square, click on a square in the grid. Click again to undo.

2. Select mode
To choose the attribute you wish to annotate with using Options > Editing mode.

3. Save to file
Choose File > Save in order to save the layout to txt (default: floor.txt)

4. Load and edit existing file
(NotImplemented)


Example output
---
Here's a 10x10 grid.

![https://i.imgur.com/H9ZKEEE.png](https://i.imgur.com/H9ZKEEE.png)

Below is the output created from this grid.
```
   N;   N;   N;   N;   N;   N;   N;   N;   N;   N
   N;   N;   N;   N;   N;   N;   N;   N;   N;   N
   N;   N;   N;   N;   N;   N;   N;   N;   N;   N
   N; W,N; W,N; W,N; W,N; W,N; W,N; W,N; W,N;   N
   N;   N;   N; P,N; P,F;   F;   F; P,N; W,N;   N
   N; W,N; W,N; P,N; P,F;   F;   F; P,N; W,N;   N
   N;   N; W,N;   N;   F;   F;   F;   N; W,N;   N
   N;   N; W,N; P,N;   N;   N;   N;   N; W,N;   N
   N;   N; W,N;   N; W,N; W,N; W,N; W,N; W,N;   N
   N;   N;   N;   N;   N;   N;   N;   N;   N;   N
```


This program is Free Software
(C) 2019

