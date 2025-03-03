
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Processor import Processor as SimuProcessor
from src.Drawer.Processor import Processor
from src.Drawer.Grid      import Grid


class drawProcessor():
  def __init__(self, imem, r7, l1ValidArray, defense="Baseline",
               maxCycle=None, scale=1, xyRatio=8/3, speed=0.5):
    self.d         = None
    self.processor = None


    ## STEP1: Scaling factors
    xScale = scale * xyRatio / (8/3)
    yScale = scale
    rScale = min(xScale, yScale)
    fontsize   =  17 * rScale
    line_width = 1.7 * rScale


    ## STEP2: Simulate the processor once to get buffer size.
    simuProcessor = SimuProcessor(imem, r7, l1ValidArray, maxCycle, defense)
    simuProcessor.simulate()
    robSize  = max(5, simuProcessor.rob.statistic_maxInst)
    aluSize  = max(3, simuProcessor.alu.statistic_maxFifoSize)
    mshrSize = max(2, simuProcessor.memSystem.statistic_maxFifoSize)
    if maxCycle==None:
      maxCycle = simuProcessor.cycle - 1


    ## STEP3: Draw the whole board.
    grid = Grid(x=0, y=0, width=800 * xScale, height=300 * yScale)

    self.d = draw.Drawing(
      grid.width, grid.height, origin=(grid.x, grid.y),
      animation_config=draw.types.SyncedAnimationConfig(
        duration=maxCycle/speed,
        show_playback_progress=True,
        show_playback_controls=True)
    )


    ## STEP4: Simulate the processor
    self.processor = Processor(
      imem, r7, l1ValidArray, maxCycle, self.d,
      robSize, aluSize, mshrSize,
      grid, fontsize, line_width, defense, speed)
    self.processor.simulate()


  def printImem(self):
    self.processor.printImem()


  def getDraw(self):
    return self.d


  def save(self, name):
    self.d.save_svg(f"{name}.svg")

