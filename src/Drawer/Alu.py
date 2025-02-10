
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Alu import Alu as SimuAlu


class Alu(SimuAlu):
  
  def __init__(self, d, bufferSize, grid, fontsize, line_width, speed=1):
    super().__init__()

    self.d          = d
    self.bufferSize = bufferSize
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed


    ## STEP1: Divide into 4 components.
    grid.divideY([7, 3])
    grid.divideX([0.5, 9, 0.5])
    grid = grid.getSubGrid(1, 0)
    self.grid = grid

    grid.divideY([bufferSize-0.8, 1, fontsize * 1.5, fontsize * 1.5],
                 [False, False, True, True])
    buffer_grid   = grid.getSubGrid(0, 0).getMergedGrid(grid.getSubGrid(0, 1))
    box_grid      = grid.getSubGrid(0, 1).getMergedGrid(grid.getSubGrid(0, 2)) \
                                         .getMergedGrid(grid.getSubGrid(0, 3))
    textPort_grid = grid.getSubGrid(0, 2)
    textAlu_grid  = grid.getSubGrid(0, 3)


    ## STEP2: Draw 4 buffers and textPort.
    parts = [0.125]
    for i in range(self.NUM_PORTS):
      parts += [1, 0.25]
    parts[-1] = 0.125
    buffer_grid.divideX(parts)
    buffers_grid = []
    for i in range(1, 2*self.NUM_PORTS, 2):
      buffers_grid.append(buffer_grid.getSubGrid(i, 0))

    entry_height = buffer_grid.height / (bufferSize + 0.2)

    for portID, grid in enumerate(buffers_grid):
      self.d.append(draw.Line(
        grid.x, grid.y, grid.x, grid.y+entry_height*1.2,
        stroke="black", stroke_width=self.line_width
      ))
      self.d.append(draw.Line(
        grid.x2(), grid.y, grid.x2(), grid.y+entry_height*1.2,
        stroke="black", stroke_width=self.line_width
      ))
      for i in range(bufferSize-1):
        self.d.append(draw.Rectangle(
          grid.x, grid.y+entry_height*(i+1.2), grid.width, entry_height,
          fill="none", stroke="black", stroke_width=self.line_width
        ))
      self.d.append(draw.Text(
        f"Port {portID}", fontsize,
        grid.centerX(), grid.y2()+0.75*fontsize, center=True
      ))


    ## STEP3: Draw ALU box and text.
    self.d.append(draw.Rectangle(
      box_grid.x, box_grid.y, box_grid.width, box_grid.height,
      fill="none", stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Text(
      "ALU", fontsize,
      textAlu_grid.centerX(), textAlu_grid.centerY(), center=True
    ))

