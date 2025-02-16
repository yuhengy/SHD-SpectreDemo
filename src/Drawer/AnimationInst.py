
import os, sys, math
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Drawer.Animation import Animation


class AnimationInst(Animation):
  def __init__(self, d, text, r, line_width, speed, grid):
    super().__init__(speed)
    
    self.circleBox = draw.Circle(
      grid.centerX(), grid.centerY(), r,
      fill="transparent", stroke_width=line_width, stroke="transparent")
    d.append(self.circleBox)
    self.textBox = draw.Text(
      text, 2.5*r / max(2, len(text)),
      grid.centerX(), grid.centerY(), center=True,
      fill="transparent")
    d.append(self.textBox)

    self.d          = d
    self.text       = text
    self.r          = r
    self.line_width = line_width

    self.grid  = grid
    self.color = "transparent"


  ## PRIVATE:
  def changeColor_internal(self, cycle, color, start, end):
    self.circleBox.add_key_frame(start, stroke=self.color)
    self.circleBox.add_key_frame(end, stroke=color)

    self.textBox.add_key_frame(start, fill=self.color)
    self.textBox.add_key_frame(end, fill=color)

    self.color = color




  ## PUBLIC:
  def fork(self, cycle):
    other = AnimationInst(
      self.d, self.text, self.r, self.line_width, self.speed, self.grid)
    other.changeColor_internal(
      cycle, self.color, self.startTime(cycle)-0.02, self.startTime(cycle)-0.01)
    return other


  def appear(self, cycle, color="black"):
    self.changeColor(cycle, color)


  def moveTo(self, cycle, grid):
    if math.isclose(self.grid.centerX(), grid.centerX()) and \
       math.isclose(self.grid.centerY(), grid.centerY()):
      return

    self.circleBox.add_key_frame(
      self.startTime(cycle), cx=self.grid.centerX(), cy=self.grid.centerY()
    )
    self.circleBox.add_key_frame(
      self.endTime(cycle), cx=grid.centerX(), cy=grid.centerY()
    )
    
    self.textBox.add_key_frame(
      self.startTime(cycle), x=self.grid.centerX(), y=self.grid.centerY()
    )
    self.textBox.add_key_frame(
      self.endTime(cycle), x=grid.centerX(), y=grid.centerY()
    )

    self.grid  = grid


  def changeColor(self, cycle, color):
    self.changeColor_internal(
      cycle, color, self.startTime(cycle), self.endTime(cycle))


  def disappear(self, cycle):
    self.changeColor(cycle, "transparent")

