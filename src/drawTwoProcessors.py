
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Processor import Processor as SimuProcessor
from src.Drawer.Processor import Processor
from src.Drawer.Grid      import Grid


class drawTwoProcessors():
  def __init__(self, imem, r7Pair, l1ValidArray, defense="Baseline",
               maxCycle=None, scale=1, xyRatio=8/6, speed=0.8):
    self.d          = None
    self.processor0 = None
    self.processor1 = None


    ## STEP1: Scaling factors
    xScale = scale * xyRatio / (8/6)
    yScale = scale
    rScale = min(xScale, yScale)
    fontsize   =  17 * rScale
    line_width = 1.7 * rScale


    ## STEP2: Simulate the processor once to get buffer size.
    simuProcessor0 = SimuProcessor(
      imem, r7Pair[0], l1ValidArray, maxCycle, defense)
    simuProcessor0.simulate()
    robSize  = max(5, simuProcessor0.rob.statistic_maxInst)
    aluSize  = max(3, simuProcessor0.alu.statistic_maxFifoSize)
    mshrSize = max(2, simuProcessor0.memSystem.statistic_maxFifoSize)
    simuProcessor1 = SimuProcessor(
      imem, r7Pair[1], l1ValidArray, maxCycle, defense)
    simuProcessor1.simulate()
    robSize  = max(robSize , simuProcessor1.rob.statistic_maxInst)
    aluSize  = max(aluSize , simuProcessor1.alu.statistic_maxFifoSize)
    mshrSize = max(mshrSize, simuProcessor1.memSystem.statistic_maxFifoSize)
    if maxCycle==None:
      maxCycle = max(simuProcessor0.cycle-1, simuProcessor1.cycle-1)


    ## STEP3: Draw the whole board.
    grid = Grid(x=0, y=0, width=800 * xScale, height=600 * yScale)
    grid.divideY([1, 1])

    self.d = draw.Drawing(
      grid.width, grid.height, origin=(grid.x, grid.y),
      animation_config=draw.types.SyncedAnimationConfig(
        duration=maxCycle/speed,
        show_playback_progress=True,
        show_playback_controls=True)
    )


    ## STEP4: Simulate the processor
    self.processor0 = Processor(
      imem, r7Pair[0], l1ValidArray, maxCycle, self.d, \
      robSize, aluSize, mshrSize,
      grid.getSubGrid(0, 0), fontsize, line_width, defense, speed)
    self.processor0.simulate()
    
    self.processor1 = Processor(
      imem, r7Pair[1], l1ValidArray, maxCycle, self.d, \
      robSize, aluSize, mshrSize,
      grid.getSubGrid(0, 1), fontsize, line_width, defense, speed)
    self.processor1.simulate()


  def printImem(self):
    self.processor0.printImem()


  def getDraw(self):
    return self.d


  def save(self, name):
    self.d.save_svg(f"{name}.svg")

