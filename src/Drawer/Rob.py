
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Rob import Rob as SimuRob


class Rob(SimuRob):
  
  def __init__(self, d, numInst, grid, fontsize, line_width, speed=1):
    super().__init__()

    self.d          = d
    self.numInst    = numInst
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed


    ## STEP1: Divide into 4 components.
    grid.divideX([fontsize * 2, 1, fontsize * 3], [True, False, True])
    grid.divideY([1, fontsize * 1.5], [False, True])
    tail_grid    = grid.getSubGrid(0, 0)
    entries_grid = grid.getSubGrid(1, 0)
    head_grid    = grid.getSubGrid(2, 0)
    text_grid    = grid.getSubGrid(1, 1)


    ## STEP2: Draw entries.
    entry_width = entries_grid.width/(numInst+1.5)
    
    self.d.append(draw.Line(
      entries_grid.x,
      entries_grid.y,
      entries_grid.x + 1.5*entry_width,
      entries_grid.y,
      stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Line(
      entries_grid.x,
      entries_grid.y + entries_grid.height,
      entries_grid.x + 1.5*entry_width,
      entries_grid.y + entries_grid.height,
      stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Text(
      "......", fontsize,
      entries_grid.x + fontsize, entries_grid.centerY() - fontsize*0.3,
      center=True
    ))

    for i in range(numInst):
      self.d.append(draw.Rectangle(
        entries_grid.x + entry_width*(i+1.5),
        entries_grid.y,
        entry_width,
        entries_grid.height,
        fill="none", stroke="black", stroke_width=line_width
      ))


    ## STEP3: Draw Head, Tail, ROB texts.
    self.d.append(draw.Text(
      "Head", fontsize,
      head_grid.centerX(), head_grid.centerY(), center=True
    ))
    self.d.append(draw.Text(
      "Tail", fontsize,
      tail_grid.centerX(), tail_grid.centerY(), center=True
    ))
    self.d.append(draw.Text(
      "ROB", fontsize,
      text_grid.centerX(), text_grid.centerY(), center=True
    ))


