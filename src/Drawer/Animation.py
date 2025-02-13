
import drawsvg as draw


class Animation():

  PRE_TIME  = 0.2
  POST_TIME = 0.2

  def __init__(self, speed):
    self.speed = speed


  def startTime(self, cycle):
    return (cycle-1+self.PRE_TIME)/self.speed


  def endTime(self, cycle):
    return (cycle-self.POST_TIME)/self.speed

