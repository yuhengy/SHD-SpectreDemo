
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Rob import Rob as SimuRob
from src.Drawer.AnimationInst import AnimationInst
from src.Drawer.AnimationFifo import AnimationFifo


class Rob(SimuRob):
  def __init__(self, d, numInst, grid, fontsize, line_width, speed=1):
    super().__init__()

    self.d          = d
    self.numInst    = numInst
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed

    self.entry_grids = []
    self.animFifo = None


    ## STEP1: Divide into 4 components.
    grid.divideY([fontsize * 1.5, 1, fontsize * 1.5], [True, False, True])
    head_grid    = grid.getSubGrid(0, 0)
    entries_grid = grid.getSubGrid(0, 1)
    tail_grid    = grid.getSubGrid(0, 2)


    ## STEP2: Draw entries.
    self.animFifo = AnimationFifo(
      entries_grid, numInst, d, line_width, self.speed)


    ## STEP3: Draw Head, Tail, ROB texts.
    self.d.append(draw.Text(
      "Head", fontsize,
      head_grid.centerX(), head_grid.centerY(), center=True
    ))
    self.d.append(draw.Text(
      "ROB Tail", fontsize,
      tail_grid.centerX(), tail_grid.centerY(), center=True
    ))


  def dispatch_alu(self, port, latency, result, i, aluReq):
    animInst = self.entries[i]["animInst"]
    animInst_forDispatch = animInst.fork(self.cycle)
    animInst.changeColor(self.cycle, "red")
    aluReq(port, latency, result, i, animInst_forDispatch)


  def dispatch_l1(self, addr, i, l1Req):
    animInst = self.entries[i]["animInst"]
    animInst_forDispatch = animInst.fork(self.cycle)
    animInst.changeColor(self.cycle, "red")
    l1Req(addr, i, animInst_forDispatch)


  def dispatch_br(self, i):
    super().dispatch_br(i)
    
    entry = self.entries[i]
    if entry["squash"]:
      entry["animInst"].changeColor(self.cycle, "orange")


  def commit_wb(self, regfileWrite):
    # self.entries[self.head]["animInst"].changeColor(self.cycle, "gray")
    self.animFifo.changeColor(self.cycle, self.head, "green")
    super().commit_wb(regfileWrite)


  def commit_squash(self, squash):
    for entry in self.entries[self.head: self.tail]:
      entry["animInst"].changeColor(self.cycle, "black")
    
    self.animFifo.changeColor(self.cycle, self.head, "green")
    for i in range(self.head+1, self.tail):
      self.animFifo.changeColor(self.cycle, i, "gray")
    super().commit_squash(squash)





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


  def collectResultAndForward(self, roblink, result):
    self.entries[roblink]["animInst"].changeColor(self.cycle, "black")
    
    super().collectResultAndForward(roblink, result)

