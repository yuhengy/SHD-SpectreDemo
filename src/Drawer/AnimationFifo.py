
import drawsvg as draw


class AnimationFifo():
  TAIL_LENGTH = 0.2

  def __init__(self, grid, size, d, line_width, flipVeritically=False):
    self.d          = d
    self.line_width = line_width

    self.entry_grid = []
    self.entry_box  = []
    self.tail_grid = None

    ## STEP1: Divide into grids.
    if flipVeritically:
      grid.divideY([self.TAIL_LENGTH] + [1 for _ in range(size)])
      for i in range(size, 0, -1):
        self.entry_grid.append(grid.getSubGrid(0, i))
      self.tail_grid = grid.getSubGrid(0, 0)
    else:
      grid.divideY([1 for _ in range(size)] + [self.TAIL_LENGTH])
      for i in range(size):
        self.entry_grid.append(grid.getSubGrid(0, i))
      self.tail_grid = grid.getSubGrid(0, size)
      
    ## STEP2: Draw the tail.
    self.d.append(draw.Line(
      self.tail_grid.x, self.tail_grid.y,
      self.tail_grid.x, self.tail_grid.y + self.tail_grid.height,
      stroke="black", stroke_width=line_width
    ))
    self.d.append(draw.Line(
      self.tail_grid.x2(), self.tail_grid.y,
      self.tail_grid.x2(), self.tail_grid.y + self.tail_grid.height,
      stroke="black", stroke_width=line_width
    ))

    ## STEP3: Draw entries.
    for g in self.entry_grid:
      self.entry_box.append(g.drawRectangle(d, line_width))


  def getGrid(self, entryIndex):
    return self.entry_grid[entryIndex]

