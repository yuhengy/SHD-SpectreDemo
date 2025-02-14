
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Drawer.Animation import Animation


class AnimationProgram(Animation):
  def __init__(self, grid, d, fontsize, speed):
    super().__init__(speed)

    self.grid     = grid
    self.d        = d
    self.fontsize = fontsize

    self.textBox  = [None for _ in grid]
    self.color    = [None for _ in grid]




  ## PUBLIC:
  def appear(self, cycle, i, s):
    grid = self.grid[i]
    textBox = draw.Text(
      s, self.fontsize,
      grid.x, grid.centerY(), text_anchor="start", dominant_baseline="middle",
      font_family="monospace", word_spacing=-3, letter_spacing=-1, fill="transparent"
    )
    textBox.add_key_frame(self.startTime(cycle), fill="transparent")
    textBox.add_key_frame(self.endTime(cycle), fill="black")
    self.d.append(textBox)

    self.textBox[i] = textBox
    self.color[i]   = "black"


  def changeColor(self, cycle, i, color):
    textBox = self.textBox[i]
    
    textBox.add_key_frame(self.startTime(cycle), fill=self.color[i])
    textBox.add_key_frame(self.endTime(cycle), fill=color)

    self.color[i] = color

