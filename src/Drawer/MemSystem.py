
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.MemSystem import MemSystem as SimuMemSystem
from src.Drawer.Color              import Color
from src.Drawer.AnimationFifo      import AnimationFifo
from src.Drawer.AnimationTable     import AnimationTable
from src.Drawer.AnimationTextArray import AnimationTextArray


class MemSystem(SimuMemSystem):

  ANIM_PRE  = 0.2
  ANIM_POST = 0.2

  def __init__(self, l1ValidArray, d, bufferSize, grid, fontsize, line_width,
               defense="Baseline", speed=1):
    super().__init__(l1ValidArray, defense)

    self.d          = d
    self.bufferSize = bufferSize
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.defense    = defense
    self.speed      = speed

    self.animInst = None

    self.mshrAnimFifo  = None
    self.animTable     = None
    self.animTextArray = None


    ## STEP1: Divide into L1 and main memory.
    grid.divideY([fontsize * 1.75, fontsize, 1], [True, True, False])
    mem_grid = grid.getSubGrid(0, 0)
    l1_grid  = grid.getSubGrid(0, 2)


    ## STEP2: Draw L1.

    ## STEP2.1: Divide L1 into MSHR and valid table.
    l1_grid.divideY([1, fontsize * 3.5,fontsize * 1 ], [False, True, True])
    mshr_grid = l1_grid.getSubGrid(0, 0)
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
        ["transparent"] + [Color.L1VALID if valid else "transparent" \
                    for valid in l1ValidArray],
        ["transparent"] + [Color.L1VALID if valid else "transparent" \
                    for valid in l1ValidArray]
      ],
      line_width, speed)

    ## STEP2.3: Divide MSHR into buffer and box.
    mshr_grid.divideY(
      [fontsize * 0.5, fontsize * 0.5, 1, bufferSize-0.8, fontsize * 0.5],
      [True, True, False, False, True])

    buffer_grid = \
      mshr_grid.getSubGrid(0, 2).getMergedGrid(mshr_grid.getSubGrid(0, 3))
    buffer_grid.divideX([self.fontsize*1.5, 3.5, 6.5], [True, False, False])
    buffer_grid = buffer_grid.getSubGrid(1, 0)
    
    mshrBox_grid = \
      mshr_grid.getSubGrid(0, 1).getMergedGrid(mshr_grid.getSubGrid(0, 2))
    mshrBox_grid.divideX([self.fontsize*0.75, 7, 3], [True, False, False])
    mshrBox_grid = mshrBox_grid.getSubGrid(1, 0)

    ## STEP2.4: Draw MSHR buffer.
    self.mshrAnimFifo = AnimationFifo(
        buffer_grid, bufferSize, d, line_width, speed)
    self.animTextArray = AnimationTextArray(
      self.mshrAnimFifo.getRightGrid(fontsize*0.25), d, fontsize, speed)

    ## STEP2.5: Draw MSHR box.
    mshrBox_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "MSHR", self.fontsize,
      mshrBox_grid.centerX() + self.fontsize*2.75, mshrBox_grid.centerY(),
      center=True
    ))

    ## STEP2.6: Draw L1 box.
    l1_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "L1", self.fontsize,
      l1_grid.centerX()+5*self.fontsize, l1_grid.y+0.75*self.fontsize,
      center=True
    ))


    ## STEP3: Draw main memory.
    mem_grid.drawRectangle(d, line_width)
    mem_grid.drawText(d, "Main Memory", fontsize)




  ## PRIVATE:
  def sendReq_hit(self, addr, roblink):
    super().sendReq_hit(addr, roblink)
    
    self.animInst.moveTo(
      self.cycle,
      self.animTable.getBelowGrid(addr+1))
    self.animInst.changeColor(self.cycle, Color.DISPATHED_INST)
    self.hitList[-1]["animInst"] = self.animInst


  def sendReq_newMshr(self, addr, roblink, isSpeculative):
    super().sendReq_newMshr(addr, roblink, isSpeculative)

    entryID = len(self.mshrFifo)-1
    self.animInst.moveTo(
      self.cycle,
      self.mshrAnimFifo.getGrid(entryID).getRightGrid(self.fontsize*0.75))
    self.animInst.changeColor(self.cycle, Color.DISPATHED_INST)
    self.mshrFifo[-1]["animInstList"] = [self.animInst]
    self.animTextArray.appear(
      self.cycle, entryID, f"0x{addr}", Color.DISPATHED_INST)


  def sendReq_appendMshr(self, addr, roblink, isSpeculative):
    super().sendReq_appendMshr(addr, roblink, isSpeculative)
    
    existingMiss, entryID = self.findInMshrFifo(addr)

    self.animInst.moveTo(
      self.cycle,
      self.mshrAnimFifo.getGrid(entryID).getRightGrid(self.fontsize*0.75))
    self.animInst.changeColor(self.cycle, Color.DISPATHED_INST)
    existingMiss["animInstList"].append(self.animInst)
  

  def respond_hit(self, entry, robResp):
    entry["animInst"].disappear(self.cycle)
    
    super().respond_hit(entry, robResp)
  

  def respond_miss(self, head, robResp):
    ## STEP1: Current entry disappear.
    for animInst in head["animInstList"]:
      animInst.disappear(self.cycle)
    self.animTextArray.disappear(self.cycle, 0)


    ## STEP2: Other entries move forward.
    for i, entry in enumerate(self.mshrFifo):
      for animInst in entry["animInstList"]:
        animInst.moveTo(
          self.cycle,
          self.mshrAnimFifo.getGrid(i).getRightGrid(self.fontsize*0.75))
      self.animTextArray.moveTo(self.cycle, i+1, i)


    ## STEP3: Update the valid arrary.
    def updateValid():
      self.animTable.changeText(self.cycle, 1, head["addr"]+1, "1")
      self.animTable.changeColor(self.cycle, 0, head["addr"]+1, Color.L1VALID)
      self.animTable.changeColor(self.cycle, 1, head["addr"]+1, Color.L1VALID)
    
    if self.defense=="InvisiSpec":
      if not head["isSpeculative"]:
        updateValid()
    else:
      updateValid()

    
    super().respond_miss(head, robResp)




  ## PUBLIC:
  def sendReq(self, addr, roblink, animInst, isSpeculative=None):
    self.animInst = animInst
    super().sendReq(addr, roblink, isSpeculative)


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
          animInst.changeColor(self.cycle, Color.MSHR_TO_DROP)

    super().squash()
    
