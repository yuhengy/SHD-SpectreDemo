
import drawsvg as draw


class Animation():

  PRE_TIME  = 0.2
  POST_TIME = 0.2

  COLOR_COMMIT = "#33691E"
  COLOR_SQUASH = "#BDBDBD"
  COLOR_L1VALID = "#A5D6A7"

  COLOR_DISPATHED_INST = "#FB8C00"
  COLOR_MSHR_TO_DROP = "#FFE0B2"


  def __init__(self, speed):
    self.speed = speed


  def startTime(self, cycle):
    return (cycle-1+self.PRE_TIME)/self.speed


  def endTime(self, cycle):
    return (cycle-self.POST_TIME)/self.speed

