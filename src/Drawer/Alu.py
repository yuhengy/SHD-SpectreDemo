
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Alu import Alu as SimuAlu


class Alu(SimuAlu):
  def __init__(self, d, bufferSize, grid, fontsize, line_width, speed=1):
    super().__init__()

    self.d          = d
    self.bufferSize = bufferSize
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed

    self.ports_grids = []


    ## STEP1: Divide into 4 components.
    grid.divideY([7, 3])
    grid.divideX([0.5, 9, 0.5])
    grid = grid.getSubGrid(1, 0)
    self.grid = grid

    grid.divideY([bufferSize-0.8, 1, fontsize * 1.5, fontsize * 1.5],
                 [False, False, True, True])
    buffer_grid   = grid.getSubGrid(0, 0).getMergedGrid(grid.getSubGrid(0, 1))
    box_grid      = grid.getSubGrid(0, 1).getMergedGrid(grid.getSubGrid(0, 2)) \
                                         .getMergedGrid(grid.getSubGrid(0, 3))
    textPort_grid = grid.getSubGrid(0, 2)
    textAlu_grid  = grid.getSubGrid(0, 3)


    ## STEP2: Draw 4 buffers and textPort.

    ## STEP2.1: Divide into 4 ports.
    parts = [0.125] + [1, 0.25] * self.NUM_PORTS
    parts[-1] = 0.125
    buffer_grid.divideX(parts)
    for portID in range(self.NUM_PORTS):
      grid = buffer_grid.getSubGrid(1+2*portID, 0)

      ## STEP2.2: Divide into 3 entries.
      grid.divideY([0.2] + [1 for _ in range(bufferSize)])
      port_grids = []
      for i in range(bufferSize, 0, -1):
        port_grids.append(grid.getSubGrid(0, i))
      portTail_grid = grid.getSubGrid(0, 0)
      self.ports_grids.append(port_grids)
      
      ## STEP2.3: Draw the buffer tail.
      self.d.append(draw.Line(
        portTail_grid.x, portTail_grid.y,
        portTail_grid.x, portTail_grid.y+portTail_grid.height*6,
        stroke="black", stroke_width=self.line_width
      ))
      self.d.append(draw.Line(
        portTail_grid.x2(), portTail_grid.y,
        portTail_grid.x2(), portTail_grid.y+portTail_grid.height*6,
        stroke="black", stroke_width=self.line_width
      ))

      ## STEP2.4: Draw the buffer body.
      for g in port_grids[:-1]:
        g.drawRectangle(d, line_width)
      
      ## STEP2.5: Draw the text.
      self.d.append(draw.Text(
        f"Port {portID}", fontsize,
        grid.centerX(), grid.y2()+0.75*fontsize, center=True
      ))


    ## STEP3: Draw ALU box and text.
    self.d.append(draw.Rectangle(
      box_grid.x, box_grid.y, box_grid.width, box_grid.height,
      fill="none", stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Text(
      "ALU", fontsize,
      textAlu_grid.centerX(), textAlu_grid.centerY(), center=True
    ))
    

  def respond_internal(self, portID, head, roblink, result, robResp):
    ## STEP1: Current entry disappear.
    head["animBox"].disappear(self.cycle)


    ## STEP2: Other entries move forward.
    for i, entry in enumerate(self.portFifo[portID]):
      entry["animBox"].moveTo(self.cycle, self.ports_grids[portID][i])


    super().respond_internal(portID, head, roblink, result, robResp)




  ## PUBLIC:
  def sendReq(self, port, latency, result, roblink, animBox):
    super().sendReq(port, latency, result, roblink)
    
    loc = len(self.portFifo[port])
    assert loc <= self.bufferSize, \
           "Buffer for port is full in the visulization, please increase " + \
           "bufferSize argument."

    animBox.moveTo(self.cycle, self.ports_grids[port][loc-1])
    self.portFifo[port][-1]["animBox"] = animBox


  def squash(self):
    for fifo in self.portFifo:
      for entry in fifo:
        entry["animBox"].disappear()

    super().squash()

