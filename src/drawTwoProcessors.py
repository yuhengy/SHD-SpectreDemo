
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Drawer.Processor import Processor
from src.Drawer.Grid      import Grid


class drawTwoProcessors():
  def __init__(self, imem, r7, l1ValidArray, totalCycle, \
               scale=1, xyRatio=18/9, speed=1, bufferSize=3):
    self.d          = None
    self.processor0 = None
    self.processor1 = None


    ## STEP1: Scaling factors
    xScale = scale * xyRatio / (18/9)
    yScale = scale
    rScale = min(xScale, yScale)
    fontsize   =  14 * rScale
    line_width = 1.4 * rScale


    ## STEP2: Draw the whole board.
    grid = Grid(x=0, y=0, width=900 * xScale, height=450 * yScale)
    grid.divideX([1, 1])

    self.d = draw.Drawing(
      grid.width, grid.height, origin=(grid.x, grid.y),
      animation_config=draw.types.SyncedAnimationConfig(
        duration=totalCycle/speed,
        show_playback_progress=True,
        show_playback_controls=True)
    )


    ## STEP3: Simulate the processor
    self.processor0 = Processor(
      imem, r7[0], l1ValidArray, totalCycle, \
      self.d, bufferSize, grid.getSubGrid(0, 0), fontsize, line_width, speed)
    self.processor0.simulate()
    
    self.processor1 = Processor(
      imem, r7[1], l1ValidArray, totalCycle, \
      self.d, bufferSize, grid.getSubGrid(1, 0), fontsize, line_width, speed)
    self.processor1.simulate()


  def printImem(self):
    self.processor0.printImem()


  def getDraw(self):
    return self.d


  def save(self, name):
    self.d.save_svg(f"{name}.svg")

