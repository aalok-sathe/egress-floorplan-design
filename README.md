# floorplan

Introduction
---
A PySimpleGUI-based graphical grid that allows users to annotate locations for
four kinds of terrains/members:
  - N (normal/none)
  - F (fire/danger)
  - P (people)
  - W (wall)

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

This program is Free Software
(C) 2019, Aalok S.


