
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Rob          import Rob as SimuRob
from src.Simulator.parseProgram import instToStr_noName
from src.Drawer.AnimationInst    import AnimationInst
from src.Drawer.AnimationFifo    import AnimationFifo
from src.Drawer.AnimationProgram import AnimationProgram


class Rob(SimuRob):
  def __init__(self, d, numInst, grid, fontsize, line_width,
               speed=1):
    super().__init__()

    self.d          = d
    self.numInst    = numInst
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed

    self.entry_grids = []
    self.animFifo = None
    self.animProgram = None
    self.branchNestedLevel = 0


    ## STEP1: Divide into 4 components.
    grid.divideX([fontsize * 12, 1], [True, False])
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


    ## STEP4: Draw program
    self.animProgram = AnimationProgram(
      self.animFifo.getLeftGrid(fontsize * 12), d, fontsize, speed)


  def dispatch_alu(self, port, latency, result, i, aluReq):
    animInst = self.entries[i]["animInst"]
    animInst_forDispatch = animInst.fork(self.cycle)
    # animInst.changeColor(self.cycle, animInst.COLOR_DISPATHED_INST)
    self.animFifo.changeColor(self.cycle, i, self.animFifo.COLOR_DISPATHED_INST)
    self.animProgram.changeColor(self.cycle, i, self.animProgram.COLOR_DISPATHED_INST)
    aluReq(port, latency, result, i, animInst_forDispatch)


  def dispatch_l1(self, addr, i, l1Req):
    animInst = self.entries[i]["animInst"]
    animInst_forDispatch = animInst.fork(self.cycle)
    # animInst.changeColor(self.cycle, animInst.COLOR_DISPATHED_INST)
    self.animFifo.changeColor(self.cycle, i, self.animFifo.COLOR_DISPATHED_INST)
    self.animProgram.changeColor(self.cycle, i, self.animProgram.COLOR_DISPATHED_INST)
    l1Req(addr, i, animInst_forDispatch)


  def dispatch_br(self, i):
    super().dispatch_br(i)


  def commit_wb(self, regfileWrite):
    self.animFifo.changeColor(
      self.cycle, self.head, self.animFifo.COLOR_COMMIT)
    self.animProgram.changeColor(
      self.cycle, self.head, self.animProgram.COLOR_COMMIT)
    super().commit_wb(regfileWrite)


  def commit_squash(self, squash):
    for entry in self.entries[self.head+1: self.tail]:
      animInst = entry["animInst"]
      animInst.changeColor(self.cycle, "black")
    
    self.animFifo.changeColor(
      self.cycle, self.head, self.animFifo.COLOR_COMMIT)
    self.animProgram.changeColor(
      self.cycle, self.head, self.animProgram.COLOR_COMMIT)
    for i in range(self.head+1, self.tail):
      self.animFifo.changeColor(self.cycle, i, self.animFifo.COLOR_SQUASH)
      self.animProgram.changeColor(self.cycle, i, self.animProgram.COLOR_SQUASH)

    self.branchNestedLevel = 0

    super().commit_squash(squash)


  def commit_others(self):
    self.animFifo.changeColor(
      self.cycle, self.head, self.animFifo.COLOR_COMMIT)
    self.animProgram.changeColor(
      self.cycle, self.head, self.animProgram.COLOR_COMMIT)
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
    self.animProgram.appear(
      self.cycle, self.tail-1,
      "\u00A0\u00A0"*self.branchNestedLevel + instToStr_noName(exe_cmd["inst"]))
    if exe_cmd["opcode"]=="BREZ":
      self.branchNestedLevel += 1


  def collectResultAndForward(self, roblink, result):
    animInst = self.entries[roblink]["animInst"]
    animInst.changeColor(self.cycle, "black")
    
    super().collectResultAndForward(roblink, result)

