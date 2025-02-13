
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Drawer.Animation import Animation


class AnimationTable(Animation):

  def __init__(self, grid, d, fontsize, text, header_width, ncol, nrow,
               color, line_width, speed):
    super().__init__(speed)
    self.d        = d
    self.fontsize = fontsize

    self.grid  = []
    self.box   = []
    self.color = color
    self.text  = []
    self.above_grid = []


    ## STEP1: Divide the table into grids.
    grid.divideX([header_width] + [1 for _ in range(ncol-1)],
                 [True] + [False for _ in range(ncol-1)])
    grid.divideY([1 for _ in range(nrow)])
    for i in range(nrow):
      self.grid.append([grid.getSubGrid(j, i) for j in range(ncol)])


    ## STEP2: Put in text and box for each grid.
    for row_grid, row_color, row_text in zip(self.grid, color, text):
      self.box.append([g.drawRectangle(d, line_width, c) \
                       for g, c in zip(row_grid, row_color)])
      self.text.append([g.drawText(d, t, fontsize) \
                        for g, t in zip(row_grid, row_text)])


    ## STEP3: Create grids that is right above the table.
    for entry_grid in self.grid[0]:
      self.above_grid.append(entry_grid.getAboveGrid(fontsize))




  ## PUBLIC:
  def getAboveGrid(self, colIndex):
    return self.above_grid[colIndex]


  def changeText(self, cycle, rowIndex, colIndex, text):
    text_old = self.text[rowIndex][colIndex]
    text_old.add_key_frame(self.startTime(cycle), fill="black")
    text_old.add_key_frame(self.endTime(cycle), fill="none")

    grid = self.grid[rowIndex][colIndex]
    text_new = draw.Text(
      "1", self.fontsize, grid.centerX(), grid.centerY(), center=True)
    text_new.add_key_frame(self.startTime(cycle), fill="none")
    text_new.add_key_frame(self.endTime(cycle), fill="black")
    self.d.append(text_new)
    self.text[rowIndex][colIndex] = text_new


  def changeColor(self, cycle, rowIndex, colIndex, color):
    box = self.box[rowIndex][colIndex]
    
    box.add_key_frame(
      self.startTime(cycle), fill=self.color[rowIndex][colIndex])
    box.add_key_frame(self.endTime(cycle), fill=color)

    self.color[rowIndex][colIndex] = color

