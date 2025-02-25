
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Rob          import Rob as SimuRob
from src.Simulator.parseProgram import instToStr_noName
from src.Drawer.Color              import Color
from src.Drawer.AnimationInst      import AnimationInst
from src.Drawer.AnimationFifo      import AnimationFifo
from src.Drawer.AnimationTextArray import AnimationTextArray
from src.Drawer.AnimationSquash    import AnimationSquash


class Rob(SimuRob):
  def __init__(self, d, numInst, grid, fontsize, line_width, defense="Baseline",
               speed=1):
    super().__init__(defense)

    self.d          = d
    self.numInst    = numInst
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed

    self.animFifo = None
    self.animTextArray = None
    self.branchNestedLevel = 0
    self.animSquash = None


    ## STEP1: Divide into 4 components.
    grid.divideX([fontsize * 12.5, 1], [True, False])
    instText_grid = grid.getSubGrid(0, 0)
    grid.divideY([fontsize * 1.5, 1], [True, False, True])
    head_grid    = grid.getSubGrid(1, 0)
    entries_grid = grid.getSubGrid(1, 1)


    ## STEP2: Draw entries.
    self.animFifo = AnimationFifo(
      entries_grid, numInst, d, line_width, self.speed)


    ## STEP3: Draw ROB Head texts.
    self.d.append(draw.Text(
      "ROB Head", fontsize,
      head_grid.centerX(), head_grid.centerY(), center=True
    ))


    ## STEP4: Draw program.
    program_grid = self.animFifo.getLeftGrid(fontsize * 12.5)
    self.animTextArray = AnimationTextArray(program_grid, d, fontsize, speed)


    ## STEP5: Draw squash.
    squash_grid = [g1.getMergedGrid(g2)
                   for g1, g2 in zip(self.animTextArray.grid, self.animFifo.grid)]
    self.animSquash = AnimationSquash(
      squash_grid, d, line_width, fontsize, speed)


  def dispatch_alu(self, port, latency, result, i, aluReq):
    animInst = self.entries[i]["animInst"]
    animInst_forDispatch = animInst.fork(self.cycle)
    # animInst.changeColor(self.cycle, Color.DISPATHED_INST)
    self.animFifo.changeColor(self.cycle, i, Color.DISPATHED_INST)
    self.animTextArray.changeColor(self.cycle, i, Color.DISPATHED_INST)
    aluReq(port, latency, result, i, animInst_forDispatch)


  def dispatch_l1(self, addr, i, l1Req, isSpeculative=None):
    animInst = self.entries[i]["animInst"]
    animInst_forDispatch = animInst.fork(self.cycle)
    # animInst.changeColor(self.cycle, Color.DISPATHED_INST)
    self.animFifo.changeColor(self.cycle, i, Color.DISPATHED_INST)
    self.animTextArray.changeColor(self.cycle, i, Color.DISPATHED_INST)
    l1Req(addr, i, animInst_forDispatch, isSpeculative)


  def dispatch_br(self, i):
    super().dispatch_br(i)


  def commit_wb(self, regfileWrite):
    self.animFifo.changeColor(
      self.cycle, self.head, Color.COMMIT)
    self.animTextArray.changeColor(
      self.cycle, self.head, Color.COMMIT)
    super().commit_wb(regfileWrite)


  def commit_squash(self, squash):
    for entry in self.entries[self.head+1: self.tail]:
      animInst = entry["animInst"]
      animInst.changeColor(self.cycle, "black")
    
    self.animFifo.changeColor(self.cycle, self.head, Color.COMMIT)
    self.animTextArray.changeColor(self.cycle, self.head, Color.COMMIT)
    for i in range(self.head+1, self.tail):
      self.animFifo.changeColor(self.cycle, i, Color.SQUASH)
      self.animTextArray.changeColor(self.cycle, i, Color.SQUASH)

    self.branchNestedLevel = 0

    self.animSquash.showBox(self.cycle, self.head, self.tail)

    super().commit_squash(squash)


  def commit_br_noSquash(self):
    self.animFifo.changeColor(self.cycle, self.head, Color.COMMIT)
    self.animTextArray.changeColor(self.cycle, self.head, Color.COMMIT)
    super().commit_br_noSquash()


  def commit_others(self):
    self.animFifo.changeColor(self.cycle, self.head, Color.COMMIT)
    self.animTextArray.changeColor(self.cycle, self.head, Color.COMMIT)
    super().commit_others()





  ## PUBLIC:
  def push(
    self, src_stall, src_data, src_roblink, pc, exe_cmd, wb_enable, wb_addr):
    super().push(
      src_stall, src_data, src_roblink, pc, exe_cmd, wb_enable, wb_addr)

    animInst = AnimationInst(
      self.d, exe_cmd["name"], 0.75*self.fontsize, self.line_width, self.speed,
      self.animFifo.getGrid(self.tail-1))
    animInst.appear(self.cycle)
    self.entries[self.tail-1]["animInst"] = animInst


    ## STEP: Draw program.
    self.animTextArray.appear(
      self.cycle, self.tail-1,
      "\u00A0\u00A0"*self.branchNestedLevel + instToStr_noName(exe_cmd["inst"]))
    if exe_cmd["opcode"]=="BREZ":
      self.branchNestedLevel += 1


  def collectResultAndForward(self, roblink, result):
    animInst = self.entries[roblink]["animInst"]
    animInst.changeColor(self.cycle, "black")
    
    super().collectResultAndForward(roblink, result)

