
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Drawer.Animation import Animation
from src.Drawer.Color     import Color


class AnimationSquash(Animation):
  MARGIN_X       = 0.5
  MARGIN_Y_ABOVE = 0.75
  MARGIN_Y_BELOW = 0.25


  def __init__(self, grid, d, line_width, fontsize, speed):
    super().__init__(speed)

    self.grid       = grid
    self.d          = d
    self.line_width = line_width
    self.fontsize   = fontsize




  ## PUBLIC:
  def showBox(self, cycle, first, last):
    first_grid = self.grid[first]
    
    rectangle = draw.Rectangle(
      first_grid.x - self.fontsize*self.MARGIN_X,
      first_grid.y - self.fontsize*self.MARGIN_Y_ABOVE,
      first_grid.width + self.fontsize*self.MARGIN_X*2,
      first_grid.height*(last-first) \
        + self.fontsize*(self.MARGIN_Y_ABOVE+self.MARGIN_Y_BELOW),
      fill="transparent", stroke="transparent", stroke_width=self.line_width*2
    )
    rectangle.add_key_frame(self.startTime(cycle), stroke="transparent")
    rectangle.add_key_frame(self.endTime(cycle), stroke=Color.DISPATHED_INST)
    rectangle.add_key_frame(self.startTime(cycle+1), stroke=Color.DISPATHED_INST)
    rectangle.add_key_frame(self.endTime(cycle+1), stroke="transparent")
    self.d.append(rectangle)

    text = draw.Text(
      "Squash!", self.fontsize,
      first_grid.centerX(), first_grid.y, center=True,
      fill="transparent")
    text.add_key_frame(self.startTime(cycle), fill="transparent")
    text.add_key_frame(self.endTime(cycle), fill=Color.DISPATHED_INST)
    text.add_key_frame(self.startTime(cycle+1), fill=Color.DISPATHED_INST)
    text.add_key_frame(self.endTime(cycle+1), fill="transparent")
    self.d.append(text)

