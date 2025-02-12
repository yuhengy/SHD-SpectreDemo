
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Rob import Rob as SimuRob
from src.Drawer.AnimationInst import AnimationInst


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


    ## STEP1: Divide into 4 components.
    grid.divideX([fontsize * 2, 1, fontsize * 3], [True, False, True])
    grid.divideY([1, fontsize * 1.5], [False, True])
    tail_grid    = grid.getSubGrid(0, 0)
    entries_grid = grid.getSubGrid(1, 0)
    head_grid    = grid.getSubGrid(2, 0)
    text_grid    = grid.getSubGrid(1, 1)


    ## STEP2: Draw entries.
    entries_grid.divideX([0.5] + [1 for _ in range(numInst+1)])
    for i in range(numInst+1, 0, -1):
      self.entry_grids.append(entries_grid.getSubGrid(i, 0))
    dots_grid = entries_grid.getSubGrid(0, 0)

    self.d.append(draw.Text(
      "......", fontsize,
      dots_grid.x + fontsize, dots_grid.centerY() - fontsize*0.3,
      center=True
    ))
    self.d.append(draw.Line(
      dots_grid.x                    , dots_grid.y,
      dots_grid.x + 3*dots_grid.width, dots_grid.y,
      stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Line(
      dots_grid.x                    , dots_grid.y2(),
      dots_grid.x + 3*dots_grid.width, dots_grid.y2(),
      stroke="black", stroke_width=self.line_width
    ))

    for grid in self.entry_grids[:-1]:
      grid.drawRectangle(d, line_width)


    ## STEP3: Draw Head, Tail, ROB texts.
    self.d.append(draw.Text(
      "Head", fontsize,
      head_grid.centerX(), head_grid.centerY(), center=True
    ))
    self.d.append(draw.Text(
      "Tail", fontsize,
      tail_grid.centerX(), tail_grid.centerY(), center=True
    ))
    self.d.append(draw.Text(
      "ROB", fontsize,
      text_grid.centerX(), text_grid.centerY(), center=True
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
    self.entries[self.head]["animInst"].disappear(self.cycle)
    super().commit_wb(regfileWrite)


  def commit_squash(self, setPc):
    for entry in self.entries[self.head: self.tail]:
      entry["animInst"].disappear(self.cycle)
    super().commit_squash(setPc)





  ## PUBLIC:
  def push(
    self, src_stall, src_data, src_roblink, pc, exe_cmd, wb_enable, wb_addr):
    super().push(
      src_stall, src_data, src_roblink, pc, exe_cmd, wb_enable, wb_addr)

    animInst = AnimationInst(
      self.d, exe_cmd["name"], 0.75*self.fontsize, self.line_width, self.speed,
      self.entry_grids[self.tail-1])
    animInst.appear(self.cycle)
    self.entries[self.tail-1]["animInst"] = animInst


  def collectResultAndForward(self, roblink, result):
    self.entries[roblink]["animInst"].changeColor(self.cycle, "black")
    
    super().collectResultAndForward(roblink, result)

