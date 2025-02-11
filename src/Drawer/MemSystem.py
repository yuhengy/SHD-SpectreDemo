
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.MemSystem import MemSystem as SimuMemSystem


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


    ## STEP1: Divide into L1 and main memory.
    grid.divideY([1, fontsize, fontsize * 1.75], [False, True, True])
    grid.divideX([0.5, 9, 0.5])
    l1_grid  = grid.getSubGrid(1, 0)
    mem_grid = grid.getSubGrid(1, 2)


    ## STEP2: Draw L1.

    ## STEP2.1: Divide L1 into MSHR and valid table.
    l1_grid.divideY(
      [fontsize * 0.5, fontsize * 1.75, fontsize * 1.75, 1],
      [True, True, True, False]
    )
    mshr_grid = l1_grid.getSubGrid(0, 3)
    l1_grid.divideX([1, fontsize * 3.5, fontsize * 2.5, fontsize * 2.5,
                     fontsize * 2.5, fontsize * 2.5, 1],
                    [False, True, True, True, True, True, False])
    self.hit_grids = [l1_grid.getSubGrid(2, 0), l1_grid.getSubGrid(3, 0),
                      l1_grid.getSubGrid(4, 0), l1_grid.getSubGrid(5, 0)]
    textAddr_grid  = l1_grid.getSubGrid(1, 1)
    addr_grid      = [l1_grid.getSubGrid(2, 1), l1_grid.getSubGrid(3, 1),
                      l1_grid.getSubGrid(4, 1), l1_grid.getSubGrid(5, 1)]
    textValid_grid = l1_grid.getSubGrid(1, 2)
    valid_grid     = [l1_grid.getSubGrid(2, 2), l1_grid.getSubGrid(3, 2),
                      l1_grid.getSubGrid(4, 2), l1_grid.getSubGrid(5, 2)]
    self.valid_grid = valid_grid

    ## STEP2.2: Draw valid table.
    textAddr_grid .drawText(d, "Addr" , fontsize)
    textValid_grid.drawText(d, "Valid", fontsize)
    for i, grid in enumerate(addr_grid):
      grid.drawText(d, f"0x{i}", fontsize)

    self.valid_text = []
    for i, grid in enumerate(valid_grid):
      self.valid_text.append(
        grid.drawText(d, "1" if l1ValidArray[i] else "0", fontsize))
    
    for grid in [textAddr_grid] + addr_grid + [textValid_grid] + valid_grid:
      grid.drawRectangle(d, line_width)

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

    ## STEP2.3: Draw MSHR buffer.
    self.mshrFifo_grids = []
    buffer_grid.divideY([0.2] + [1 for _ in range(bufferSize)])
    for i in range(bufferSize, 0, -1):
      self.mshrFifo_grids.append(buffer_grid.getSubGrid(0, i))
    mshrFifoTail_grid = buffer_grid.getSubGrid(0, 0)

    self.d.append(draw.Line(
      mshrFifoTail_grid.x, mshrFifoTail_grid.y,
      mshrFifoTail_grid.x, mshrFifoTail_grid.y+mshrFifoTail_grid.height*6,
      stroke="black", stroke_width=self.line_width
    ))
    self.d.append(draw.Line(
      mshrFifoTail_grid.x2(), mshrFifoTail_grid.y,
      mshrFifoTail_grid.x2(), mshrFifoTail_grid.y+mshrFifoTail_grid.height*6,
      stroke="black", stroke_width=self.line_width
    ))
    for g in self.mshrFifo_grids[:-1]:
      g.drawRectangle(d, line_width)

    ## STEP2.4: Draw MSHR box.
    mshrBox_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "MSHR", self.fontsize,
      mshrBox_grid.centerX()+2.25*self.fontsize, mshrBox_grid.centerY(),
      center=True
    ))

    ## STEP2.5: Draw L1 box.
    l1_grid.drawRectangle(d, line_width)
    self.d.append(draw.Text(
      "L1", self.fontsize,
      l1_grid.centerX()+5*self.fontsize, l1_grid.y2()-0.75*self.fontsize,
      center=True
    ))


    ## STEP3: Draw main memory.
    mem_grid.drawRectangle(d, line_width)
    mem_grid.drawText(d, "Main Memory", fontsize)


  def sendReq(self, addr, roblink, circle, text):
    if self.l1ValidArray[addr]:
      self.hitList.append({"addr": addr, "roblink": roblink})
      grid = self.hit_grids[addr]
      self.hitList[-1]["draw"] = (circle, text)

    else:
      existingMiss, entryID = self.findInMshrFifo(addr)
      if existingMiss==None:
        self.mshrFifo.append({
          "addr": addr,
          "latency": self.MISS_LATENCY,
          "roblinkList": [roblink],
        })
        grid = self.mshrFifo_grids[len(self.mshrFifo)-1]
        self.mshrFifo[-1]["draw"] = [(circle, text)]

      else:
        existingMiss["roblinkList"].append(roblink)
        grid = self.mshrFifo_grids[entryID]
        existingMiss["draw"].append((circle, text))


    circle.add_key_frame((
      self.cycle-self.ANIM_POST)/self.speed,
      cx=grid.centerX(), cy=grid.centerY()
    )
    text.add_key_frame(
      (self.cycle-self.ANIM_POST)/self.speed,
      x=grid.centerX(), y=grid.centerY()
    )
  

  def respond_hit(self, entry, robResp):
    circle, text = entry["draw"]
    grid = self.hit_grids[entry["addr"]]
    circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, cx=grid.centerX(), cy=grid.centerY())
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, x=grid.centerX(), y=grid.centerY())
    
    super().respond_hit(entry, robResp)
  

  def respond_miss(self, head, robResp):

    ## STEP1: If there are extra draw (due to squash), remove them.
    for _ in range(len(head["draw"]) - len(head["roblinkList"])):
      circle, text = head["draw"][0]
      
      if self.justSquash:
        circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="black")
        text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
      else:
        circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="orange")
        text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="orange")
      circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="none")
      text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="none")

      head["draw"].pop(0)


    ## STEP2: Returned entry is here at the begining of the cycle.
    grid = self.mshrFifo_grids[0]
    for circle, text in head["draw"]:
      circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, cx=grid.centerX(), cy=grid.centerY())
      text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, x=grid.centerX(), y=grid.centerY())


    ## STEP3: Other entries move forward.
    if len(self.mshrFifo) > 0:
      for i, entry in enumerate(self.mshrFifo):
        grid_old = self.mshrFifo_grids[i+1]
        grid     = self.mshrFifo_grids[i]
        
        for circle, text in entry["draw"]:
          circle.add_key_frame(
            (self.cycle-1+self.ANIM_PRE)/self.speed,
            cx=grid_old.centerX(), cy=grid_old.centerY()
          )
          circle.add_key_frame(
            (self.cycle-self.ANIM_POST)/self.speed,
            cx=grid.centerX(), cy=grid.centerY()
          )
          text.add_key_frame(
            (self.cycle-1+self.ANIM_PRE)/self.speed,
            x=grid_old.centerX(), y=grid_old.centerY()
          )
          text.add_key_frame(
            (self.cycle-self.ANIM_POST)/self.speed,
            x=grid.centerX(), y=grid.centerY()
          )

    ## STEP4: Update the valid arrary.
    text = self.valid_text[head["addr"]]
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="none")
    
    grid = self.valid_grid[head["addr"]]
    text = draw.Text(
      "1", self.fontsize,
      grid.centerX(), grid.centerY(), center=True)
    text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="none")
    text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="black")
    self.d.append(text)
    self.valid_text[head["addr"]] = text

    
    super().respond_miss(head, robResp)


  def squash(self):
    for entry in self.hitList:
      circle, text = entry["draw"]
      
      circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="black")
      circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="none")
      text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
      text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="none")
    
    if len(self.mshrFifo) > 1:
      for entry in self.mshrFifo[1:]:
        for circle, text in entry["draw"]:
          circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="black")
          circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="none")
          text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
          text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="none")
      
      head = self.mshrFifo[0]
      if head["latency"] > 0:
        for circle, text in head["draw"]:
          circle.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, stroke="black")
          circle.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, stroke="orange")
          text.add_key_frame((self.cycle-1+self.ANIM_PRE)/self.speed, fill="black")
          text.add_key_frame((self.cycle-self.ANIM_POST)/self.speed, fill="orange")

    ## TODO: remove this
    self.justSquash = True

    super().squash()
    
