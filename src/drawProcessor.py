
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Drawer.Processor import Processor
from src.Drawer.Grid      import Grid


class drawProcessor():
  def __init__(self, imem, r7, l1ValidArray, totalCycle, \
               scale=1, xyRatio=12/9, speed=1, bufferSize=3):
    self.d         = None
    self.processor = None


    ## STEP1: Scaling factors
    xScale = scale * xyRatio / (12/9)
    yScale = scale
    rScale = min(xScale, yScale)
    fontsize   =  18 * rScale
    line_width = 1.8 * rScale


    ## STEP2: Draw the whole board.
    grid = Grid(x=0, y=0, width=600 * xScale, height=450 * yScale)

    self.d = draw.Drawing(
      grid.width, grid.height, origin=(grid.x, grid.y),
      animation_config=draw.types.SyncedAnimationConfig(
        duration=totalCycle/speed,
        show_playback_progress=True,
        show_playback_controls=True)
    )


    ## STEP3: Simulate the processor
    self.processor = Processor(
      imem, r7, l1ValidArray, totalCycle, \
      self.d, bufferSize, grid, fontsize, line_width, speed)
    self.processor.simulate()


  def printImem(self):
    self.processor.printImem()


  def getDraw(self):
    return self.d


  def save(self, name):
    self.d.save_svg(f"{name}.svg")

