
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Drawer.Animation import Animation


class AnimationTextArray(Animation):
  def __init__(self, grid, d, fontsize, speed):
    super().__init__(speed)

    self.grid     = grid
    self.d        = d
    self.fontsize = fontsize

    self.textBox  = [None for _ in grid]
    self.color    = [None for _ in grid]




  ## PUBLIC:
  def appear(self, cycle, i, s, color="black"):
    grid = self.grid[i]
    textBox = draw.Text(
      s, self.fontsize,
      grid.x, grid.centerY(), text_anchor="start", dominant_baseline="middle",
      font_family="monospace", word_spacing=-3, letter_spacing=-1, fill="transparent"
    )
    textBox.add_key_frame(self.startTime(cycle), fill="transparent")
    textBox.add_key_frame(self.endTime(cycle), fill=color)
    self.d.append(textBox)

    self.textBox[i] = textBox
    self.color[i]   = color


  def changeColor(self, cycle, i, color):
    textBox = self.textBox[i]
    
    textBox.add_key_frame(self.startTime(cycle), fill=self.color[i])
    textBox.add_key_frame(self.endTime(cycle), fill=color)

    self.color[i] = color


  def moveTo(self, cycle, fromIdx, toIdx):
    textBox   = self.textBox[fromIdx]
    from_grid = self.grid[fromIdx]
    to_grid   = self.grid[toIdx]
    textBox.add_key_frame(
      self.startTime(cycle), x=from_grid.x, y=from_grid.centerY()
    )
    textBox.add_key_frame(
      self.endTime(cycle), x=to_grid.x, y=to_grid.centerY()
    )
    
    self.textBox[toIdx] = textBox
    self.color  [toIdx] = self.color[fromIdx]


  def rotateToLarger(self, cycle, minIdx, maxIdx):
    if minIdx==maxIdx:
      return

    max_textBox = self.textBox[maxIdx]
    max_color   = self.color[maxIdx]
    from_grid = self.grid[maxIdx]
    to_grid   = self.grid[minIdx]
    max_textBox.add_key_frame(
      self.startTime(cycle), x=from_grid.x, y=from_grid.centerY()
    )
    max_textBox.add_key_frame(
      self.endTime(cycle), x=to_grid.x, y=to_grid.centerY()
    )

    for i in range(minIdx, maxIdx):
      self.moveTo(cycle, i, i+1)
    
    self.textBox[minIdx] = max_textBox
    self.color  [minIdx] = max_color

  

  def disappear(self, cycle, i):
    textBox = self.textBox[i]
    textBox.add_key_frame(self.startTime(cycle), fill=self.color[i])
    textBox.add_key_frame(self.endTime(cycle), fill="transparent")

    self.color[i] = "transparent"
