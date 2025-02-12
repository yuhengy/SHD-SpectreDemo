
import drawsvg as draw


class AnimationInst():

  PRE_TIME  = 0.2
  POST_TIME = 0.2

  def __init__(self, d, text, r, line_width, speed, grid):
    self.circleBox = draw.Circle(
      grid.centerX(), grid.centerY(), r,
      fill="none", stroke_width=line_width, stroke="none")
    d.append(self.circleBox)
    self.textBox = draw.Text(
      text, 2.5*r / max(2, len(text)),
      grid.centerX(), grid.centerY(), center=True,
      fill="none")
    d.append(self.textBox)

    self.d          = d
    self.text       = text
    self.r          = r
    self.line_width = line_width
    self.speed      = speed

    self.grid  = grid
    self.color = "none"


  ## PRIVATE
  def startTime(self, cycle):
    return (cycle-1+self.PRE_TIME)/self.speed


  def endTime(self, cycle):
    return (cycle-self.POST_TIME)/self.speed


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
    self.changeColor(cycle, "none")

