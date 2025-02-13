
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.MemSystem import MemSystem as SimuMemSystem
from src.Drawer.AnimationFifo  import AnimationFifo
from src.Drawer.AnimationTable import AnimationTable


class MemSystem(SimuMemSystem):

  ANIM_PRE  = 0.2
  ANIM_POST = 0.2

  def __init__(self, l1ValidArray, d, bufferSize, grid, fontsize, line_width,
               speed=1):
    super().__init__(l1ValidArray)

    self.d          = d
    self.bufferSize = bufferSize
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed

    self.mshrAnimFifo = None
    self.animTable    = None


    ## STEP1: Divide into L1 and main memory.
    grid.divideY([1, fontsize, fontsize * 1.75], [False, True, True])
    l1_grid  = grid.getSubGrid(0, 0)
    mem_grid = grid.getSubGrid(0, 2)


    ## STEP2: Draw L1.

    ## STEP2.1: Divide L1 into MSHR and valid table.
    l1_grid.divideY([fontsize * 1, fontsize * 3.5, 1], [True, True, False])
    mshr_grid = l1_grid.getSubGrid(0, 2)
    l1_grid.divideX([1, fontsize * (3.5 + 2.5*4), 1], [False, True, False])
    table_grid = l1_grid.getSubGrid(1, 1)

    ## STEP2.2: Draw valid table.
    ncol = len(l1ValidArray) + 1
    self.animTable = AnimationTable(
      table_grid, d, fontsize,
      [
        ["Addr"] + [f"0x{i}" for i in range(ncol-1)],
        ["Valid"] + ["1" if valid else "0" for valid in l1ValidArray]
      ],
      fontsize*3.5, ncol, 2,
      [
        ["none"] + [AnimationTable.COLOR_L1VALID if valid else "none" \
                    for valid in l1ValidArray],
        ["none"] + [AnimationTable.COLOR_L1VALID if valid else "none" \
                    for valid in l1ValidArray]
      ],
      line_width, speed)

    ## STEP2.3: Divide MSHR into buffer and box.
    mshr_grid.divideY(
      [fontsize * 0.5, bufferSize-0.8, 1, fontsize * 0.5, fontsize * 0.5],
      [True, False, False, True, True])

    buffer_grid = \
      mshr_grid.getSubGrid(0, 1).getMergedGrid(mshr_grid.getSubGrid(0, 2))
    buffer_grid.divideX([1.5, 2.25, 6.25])
    buffer_grid = buffer_grid.getSubGrid(1, 0)
    
    mshrBox_grid = \
      mshr_grid.getSubGrid(0, 2).getMergedGrid(mshr_grid.getSubGrid(0, 3))
    mshrBox_grid.divideX([1, 5.5, 3.5])
    mshrBox_grid = mshrBox_grid.getSubGrid(1, 0)

    ## STEP2.4: Draw MSHR buffer.
    self.mshrAnimFifo = AnimationFifo(
        buffer_grid, bufferSize, self.d, self.line_width, self.speed,
        flipVeritically=True)

    ## STEP2.5: Draw MSHR box.
    mshrBox_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "MSHR", self.fontsize,
      mshrBox_grid.centerX()+2.25*self.fontsize, mshrBox_grid.centerY(),
      center=True
    ))

    ## STEP2.6: Draw L1 box.
    l1_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "L1", self.fontsize,
      l1_grid.centerX()+5*self.fontsize, l1_grid.y2()-0.75*self.fontsize,
      center=True
    ))


    ## STEP3: Draw main memory.
    mem_grid.drawRectangle(d, line_width)
    mem_grid.drawText(d, "Main Memory", fontsize)
  

  def respond_hit(self, entry, robResp):
    entry["animInst"].disappear(self.cycle)
    
    super().respond_hit(entry, robResp)
  

  def respond_miss(self, head, robResp):
    ## STEP1: Current entry disappear.
    for animInst in head["animInstList"]:
      animInst.disappear(self.cycle)


    ## STEP2: Other entries move forward.
    for i, entry in enumerate(self.mshrFifo):
      for animInst in entry["animInstList"]:
        animInst.moveTo(self.cycle, self.mshrAnimFifo.getGrid(i))


    ## STEP3: Update the valid arrary.
    self.animTable.changeText(self.cycle, 1, head["addr"]+1, "1")
    self.animTable.changeColor(self.cycle, 0, head["addr"]+1, "green")
    self.animTable.changeColor(self.cycle, 1, head["addr"]+1, "green")

    
    super().respond_miss(head, robResp)




  ## PUBLIC:
  def sendReq(self, addr, roblink, animInst):
    if self.l1ValidArray[addr]:
      self.hitList.append({"addr": addr, "roblink": roblink})
      animInst.moveTo(self.cycle, self.animTable.getAboveGrid(addr+1))
      animInst.changeColor(self.cycle, "red")
      self.hitList[-1]["animInst"] = animInst

    else:
      existingMiss, entryID = self.findInMshrFifo(addr)
      if existingMiss==None:
        self.mshrFifo.append({
          "addr": addr,
          "latency": self.MISS_LATENCY,
          "roblinkList": [roblink],
        })
        animInst.moveTo(
          self.cycle, self.mshrAnimFifo.getGrid(len(self.mshrFifo)-1))
        animInst.changeColor(self.cycle, "red")
        self.mshrFifo[-1]["animInstList"] = [animInst]

      else:
        existingMiss["roblinkList"].append(roblink)
        animInst.moveTo(self.cycle, self.mshrAnimFifo.getGrid(entryID))
        animInst.changeColor(self.cycle, "red")
        existingMiss["animInstList"].append(animInst)


  def squash(self):
    for entry in self.hitList:
      entry["animInst"].disappear(self.cycle)
    
    for entry in self.mshrFifo[1:]:
      for animInst in entry["animInstList"]:
        animInst.disappear(self.cycle)
      
    if len(self.mshrFifo) > 0:
      head = self.mshrFifo[0]
      if head["latency"] > 0:
        for animInst in head["animInstList"]:
          animInst.changeColor(self.cycle, "orange")

    super().squash()
    
