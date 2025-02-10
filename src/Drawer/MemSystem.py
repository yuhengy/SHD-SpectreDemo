
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.MemSystem import MemSystem as SimuMemSystem


class MemSystem(SimuMemSystem):
  
  def __init__(self, l1ValidArray, d, bufferSize, grid, fontsize, line_width,
               speed=1):
    super().__init__(l1ValidArray)

    self.d          = d
    self.bufferSize = bufferSize
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed


    ## STEP1: Divide into L1 and main memory.
    grid.divideY([1, fontsize, fontsize * 1.75], [False, True, True])
    grid.divideX([0.5, 9, 0.5])
    l1_grid  = grid.getSubGrid(1, 0)
    mem_grid = grid.getSubGrid(1, 2)


    ## STEP2: Draw L1.

    ## STEP2.1: Divide L1 into MSHR and valid table.
    l1_grid.divideY(
      [fontsize * 0.5, fontsize * 1.75, fontsize * 1.75, 1],
      [True, True, True, False]
    )
    mshr_grid = l1_grid.getSubGrid(0, 3)
    l1_grid.divideX([1, fontsize * 3.5, fontsize * 2.5, fontsize * 2.5,
                     fontsize * 2.5, fontsize * 2.5, 1],
                    [False, True, True, True, True, True, False])
    textAddr_grid  = l1_grid.getSubGrid(1, 1)
    addr_grid      = [l1_grid.getSubGrid(2, 1), l1_grid.getSubGrid(3, 1),
                      l1_grid.getSubGrid(4, 1), l1_grid.getSubGrid(5, 1)]
    textValid_grid = l1_grid.getSubGrid(1, 2)
    valid_grid     = [l1_grid.getSubGrid(2, 2), l1_grid.getSubGrid(3, 2),
                      l1_grid.getSubGrid(4, 2), l1_grid.getSubGrid(5, 2)]

    ## STEP2.2: Draw valid table.
    textAddr_grid .drawText(d, "Addr" , fontsize)
    textValid_grid.drawText(d, "Valid", fontsize)
    for i, grid in enumerate(addr_grid):
      grid.drawText(d, f"0x{i}", fontsize)
    for i, grid in enumerate(valid_grid):
      grid.drawText(d, "1" if l1ValidArray[i] else "0", fontsize)
    
    for grid in [textAddr_grid] + addr_grid + [textValid_grid] + valid_grid:
      grid.drawRectangle(d, line_width)

    ## STEP2.3: Divide MSHR into buffer and box.
    mshr_grid.divideY(
      [fontsize * 0.5, bufferSize-0.8, 1, fontsize * 0.5, fontsize * 0.5],
      [True, False, False, True, True])

    buffer_grid = \
      mshr_grid.getSubGrid(0, 1).getMergedGrid(mshr_grid.getSubGrid(0, 2))
    buffer_grid.divideX([1.5, 2.25, 6.25])
    buffer_grid = buffer_grid.getSubGrid(1, 0)
    
    mshrBox_grid = \
      mshr_grid.getSubGrid(0, 2).getMergedGrid(mshr_grid.getSubGrid(0, 3))
    mshrBox_grid.divideX([1, 5.5, 3.5])
    mshrBox_grid = mshrBox_grid.getSubGrid(1, 0)

    ## STEP2.3: Draw MSHR buffer.
    entry_height = buffer_grid.height / (bufferSize + 0.2)
    self.d.append(draw.Line(
      buffer_grid.x, buffer_grid.y,
      buffer_grid.x, buffer_grid.y+entry_height*1.2,
      stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Line(
      buffer_grid.x2(), buffer_grid.y,
      buffer_grid.x2(), buffer_grid.y+entry_height*1.2,
      stroke="black", stroke_width=self.line_width
    ))
    for i in range(bufferSize-1):
      self.d.append(draw.Rectangle(
        buffer_grid.x, buffer_grid.y+entry_height*(i+1.2),
        buffer_grid.width, entry_height,
        fill="none", stroke="black", stroke_width=self.line_width
      ))

    ## STEP2.4: Draw MSHR box.
    mshrBox_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "MSHR", self.fontsize,
      mshrBox_grid.centerX()+2.25*self.fontsize, mshrBox_grid.centerY(),
      center=True
    ))

    ## STEP2.5: Draw L1 box.
    l1_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "L1", self.fontsize,
      l1_grid.centerX()+5*self.fontsize, l1_grid.y2()-0.75*self.fontsize,
      center=True
    ))


    ## STEP3: Draw main memory.
    mem_grid.drawRectangle(d, line_width)
    mem_grid.drawText(d, "Main Memory", fontsize)

