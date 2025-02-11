
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Rob import Rob as SimuRob


class Rob(SimuRob):

  ANIM_PRE  = 0.2
  ANIM_POST = 0.2
  
  def __init__(self, d, numInst, grid, fontsize, line_width, speed=1):
    super().__init__()

    self.d          = d
    self.numInst    = numInst
    self.grid       = grid
    self.fontsize   = fontsize
    self.line_width = line_width
    self.speed      = speed


    ## STEP1: Divide into 4 components.
    grid.divideX([fontsize * 2, 1, fontsize * 3], [True, False, True])
    grid.divideY([1, fontsize * 1.5], [False, True])
    tail_grid    = grid.getSubGrid(0, 0)
    entries_grid = grid.getSubGrid(1, 0)
    head_grid    = grid.getSubGrid(2, 0)
    text_grid    = grid.getSubGrid(1, 1)


    ## STEP2: Draw entries.
    entries_grid.divideX([0.5] + [1 for _ in range(numInst+1)])
    self.entry_grids = []
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


  def push(
    self, src_stall, src_data, src_roblink, exe_cmd, wb_enable, wb_addr):
    super().push(src_stall, src_data, src_roblink, exe_cmd, wb_enable, wb_addr)

    if self.tail >= len(self.entry_grids):
      return

    entry      = self.entries    [self.tail-1]
    entry_grid = self.entry_grids[self.tail-1]
    
    circle = draw.Circle(
      entry_grid.centerX(), entry_grid.centerY(), 0.75*self.fontsize,
      fill="none", stroke_width=self.line_width)
    circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="none")
    circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="black")
    self.d.append(circle)

    text = draw.Text(
      exe_cmd["name"], self.fontsize * 2 / max(2, len(exe_cmd["name"])),
      entry_grid.centerX(), entry_grid.centerY(), center=True)
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="none")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="black")
    self.d.append(text)

    entry["draw"] = (circle, text)
    
    circle = draw.Circle(
      entry_grid.centerX(), entry_grid.centerY(), 0.75*self.fontsize,
      fill="none", stroke_width=self.line_width)
    circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="none")
    circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="black")
    self.d.append(circle)

    text = draw.Text(
      exe_cmd["name"], self.fontsize * 2 / max(2, len(exe_cmd["name"])),
      entry_grid.centerX(), entry_grid.centerY(), center=True)
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="none")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="black")
    self.d.append(text)

    entry["draw_dispatched"] = (circle, text)


  def dispatch_draw(self, i):
    entry      = self.entries    [i]
    entry_grid = self.entry_grids[i]
    exe_cmd    = entry["exe_cmd"]
    if "draw" not in entry:
      return


    circle, text = entry["draw"]
    circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="black")
    circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="red")
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="red")


    circle, text = entry["draw_dispatched"]
    circle.add_key_frame(
      (self.cycle-1+self.ANIM_PRE)/self.speed,
      cx=entry_grid.centerX(), cy=entry_grid.centerY()
    )
    text.add_key_frame(
      (self.cycle-1+self.ANIM_PRE)/self.speed,
      x=entry_grid.centerX(), y=entry_grid.centerY()
    )

    return circle, text


  def dispatch_alu(self, port, latency, result, i, aluReq):
    circle, text = self.dispatch_draw(i)
    aluReq(port, latency, result, i, circle, text)


  def dispatch_l1(self, src_data, i, l1Req):
    circle, text = self.dispatch_draw(i)
    l1Req(src_data, i, circle, text)
        

  def collectResultAndForward(self, roblink, result):
    entry      = self.entries    [roblink]
    entry_grid = self.entry_grids[roblink]


    circle, text = entry["draw"]
    circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="red")
    circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="black")
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="red")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="black")


    circle, text = entry["draw_dispatched"]
    circle.add_key_frame(
      (self.cycle-self.ANIM_POST)/self.speed,
      cx=entry_grid.centerX(), cy=entry_grid.centerY()
    )
    text.add_key_frame(
      (self.cycle-self.ANIM_POST)/self.speed,
      x=entry_grid.centerX(), y=entry_grid.centerY()
    )
    

    super().collectResultAndForward(roblink, result)


  def commit_internal(self, regfileWrite):
    entry      = self.entries    [self.head]
    entry_grid = self.entry_grids[self.head]


    circle, text = entry["draw"]
    circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="black")
    circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="none")
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="none")


    circle, text = entry["draw_dispatched"]
    circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="black")
    circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="none")
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="none")


    super().commit_internal(regfileWrite)

