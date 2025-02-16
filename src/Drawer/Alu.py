
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Alu import Alu as SimuAlu
from src.Drawer.Color         import Color
from src.Drawer.AnimationFifo import AnimationFifo


class Alu(SimuAlu):
  def __init__(self, d, bufferSize, grid, fontsize, line_width,
               defense="Baseline", speed=1):
    super().__init__(defense)

    self.d          = d
    self.bufferSize = bufferSize
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed

    self.animFifoList = []


    ## STEP1: Divide into 4 components.
    grid.divideY([7, 3])
    grid = grid.getSubGrid(0, 0)
    self.grid = grid

    grid.divideY([fontsize * 1.5, fontsize * 1, 1, bufferSize-0.8],
                 [True, True, False, False])
    textAlu_grid  = grid.getSubGrid(0, 0)
    box_grid      = grid.getSubGrid(0, 0).getMergedGrid(grid.getSubGrid(0, 1)) \
                                         .getMergedGrid(grid.getSubGrid(0, 2))
    buffer_grid   = grid.getSubGrid(0, 2).getMergedGrid(grid.getSubGrid(0, 3))


    ## STEP2: Draw 4 FIFOs and text below each FIFO.
    parts = [0.125] + [1, 0.25] * self.NUM_PORTS
    parts[-1] = 0.125
    buffer_grid.divideX(parts)
    for portID in range(self.NUM_PORTS):
      grid = buffer_grid.getSubGrid(1+2*portID, 0)
      
      self.animFifoList.append(AnimationFifo(
        grid, bufferSize, self.d, self.line_width, self.speed))

      self.d.append(draw.Text(
        f"Port {portID}", fontsize,
        grid.centerX(), grid.y2()+0.75*fontsize, center=True
      ))


    ## STEP3: Draw ALU box and text.
    self.d.append(draw.Rectangle(
      box_grid.x, box_grid.y, box_grid.width, box_grid.height,
      fill="transparent", stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Text(
      "ALU", fontsize,
      textAlu_grid.centerX(), textAlu_grid.centerY(), center=True
    ))
    

  def respond_internal(self, portID, head, roblink, result, robResp):
    ## STEP1: Current entry disappear.
    head["animInst"].disappear(self.cycle)


    ## STEP2: Other entries move forward.
    for i, entry in enumerate(self.portFifo[portID]):
      entry["animInst"].moveTo(self.cycle, self.animFifoList[portID].getGrid(i))


    super().respond_internal(portID, head, roblink, result, robResp)




  ## PUBLIC:
  def sendReq(self, port, latency, result, roblink, animInst):
    super().sendReq(port, latency, result, roblink)

    fifo = self.portFifo[port]
    animFifo = self.animFifoList[port]
    assert len(fifo) <= self.bufferSize, \
           "Buffer for port is full in the visulization, please increase " + \
           "bufferSize argument."

    ## STEP1: Find where the new entry is inserted.
    loc = [i for i, d in enumerate(fifo) if d["roblink"]==roblink][0]

    ## STEP2: Move to this new entry.
    animInst.moveTo(self.cycle, animFifo.getGrid(loc))
    animInst.changeColor(self.cycle, Color.DISPATHED_INST)
    self.portFifo[port][loc]["animInst"] = animInst

    ## STEP3: Adjust other entries, if necessary.
    if self.defense=="GhostMinion":
      for i in range(loc+1, len(fifo)):
        fifo[i]["animInst"].moveTo(self.cycle, animFifo.getGrid(i))


  def squash(self):
    for fifo in self.portFifo:
      for entry in fifo:
        entry["animInst"].disappear(self.cycle)

    super().squash()

