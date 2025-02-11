
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Processor import Processor as SimuProcessor

from src.Drawer.Grid      import Grid
from src.Drawer.Rob       import Rob
from src.Drawer.Alu       import Alu
from src.Drawer.MemSystem import MemSystem



class Processor(SimuProcessor):

  def __init__(self, imem, l1ValidArray, totalCycle, printTrace=False, \
                     scale=1, xyRatio=16/9, speed=1, bufferSize=3):
    super().__init__(imem, l1ValidArray, totalCycle, printTrace)


    ## STEP1: Scaling factors
    xScale = scale * xyRatio / (16/9)
    yScale = scale
    rScale = min(xScale, yScale)
    fontsize   = 20 * rScale
    line_width =  2 * rScale


    ## STEP2: Draw the whole board.
    grid = Grid(x=0, y=0, width=800 * xScale, height=450 * yScale)

    self.d = draw.Drawing(
      grid.width, grid.height, origin=(grid.x, grid.y),
      animation_config=draw.types.SyncedAnimationConfig(
        duration=totalCycle/speed,
        show_playback_progress=True,
        show_playback_controls=True)
    )


    ## STEP3: Divide the whole board for 4 components.
    
    ## STEP3.1: Remove some margin.
    grid.divideX([fontsize * 0.5, 1, fontsize * 0.5],
                 useFixedLength=[True, False, True])
    grid.divideY([fontsize * 0.5, 1, fontsize],
                 useFixedLength=[True, False, True])
    grid = grid.getSubGrid(1, 1)

    ## STEP3.2: Draw.
    grid.divideY([1, fontsize * 0.5, 4, fontsize * 0.5, fontsize * 2.5],
                 useFixedLength=[False, True, False, True, True])
    rob_grid            = grid.getSubGrid(0, 0)
    cycleIndicator_grid = grid.getSubGrid(0, 4)
    grid.divideX([1, 1])
    alu_grid            = grid.getSubGrid(0, 2)
    memSystem_grid      = grid.getSubGrid(1, 2)


    ## STEP4: Draw the cycle indicator.

    ## STEP4.1: Divide the whole grid into subgrids.
    cycleIndicator_grid.divideX([1, fontsize * 1.5, fontsize * 3],
                                useFixedLength=[False, True, True])
    cycleIndicator_grid.divideY(
      [fontsize * 0.5, fontsize * 0.25, fontsize * 0.75, fontsize * 1],
      useFixedLength=[True, True, True, True])
    cyclePointer_grid = cycleIndicator_grid.getSubGrid(0, 0)
    cycleAxis_grid    = cycleIndicator_grid.getSubGrid(0, 2)
    label_grid        = cycleIndicator_grid.getSubGrid(0, 3)
    arrow_grid        = cycleIndicator_grid.getSubGrid(1, 2)
    text_grid         = cycleIndicator_grid.getSubGrid(2, 2)

    ## STEP4.2: A moving pointer
    pointer = draw.Circle(
      cyclePointer_grid.x,
      cyclePointer_grid.centerY(),
      cyclePointer_grid.height/2,
      fill="black"
    )
    pointer.add_key_frame(               0, cx=cyclePointer_grid.x)
    pointer.add_key_frame(totalCycle/speed, cx=cyclePointer_grid.x2())
    self.d.append(pointer)

    ## STEP4.3: Axis, sticks, and labels.
    self.d.append(draw.Line(
      cycleAxis_grid.x,
      cycleAxis_grid.centerY(),
      arrow_grid.x2(),
      cycleAxis_grid.centerY(),
      stroke="black", stroke_width=line_width
    ))
    for i in range(totalCycle+1):
      x = cycleAxis_grid.x + cycleAxis_grid.width/totalCycle*i
      self.d.append(draw.Line(
        x, cycleAxis_grid.y, x, cycleAxis_grid.y2(),
        stroke="black", stroke_width=line_width
      ))
      self.d.append(draw.Text(
        str(i), fontsize, x, label_grid.centerY(), center=True
      ))

    ## STEP4.4: Arrow
    self.d.append(draw.Lines(
      arrow_grid.x2()      - arrow_grid.width*0.3,
      arrow_grid.centerY() - arrow_grid.width*0.2,
      arrow_grid.x2()                            ,
      arrow_grid.centerY()                       ,
      arrow_grid.x2()      - arrow_grid.width*0.3,
      arrow_grid.centerY() + arrow_grid.width*0.2,
      fill="none", stroke="black", stroke_width=line_width
    ))

    ## STEP4.5: Text
    # text_x = cycleAxis_x2 + text_width/2
    # text_y = cycleAxis_y
    self.d.append(draw.Text(
      "Cycle", fontsize, text_grid.centerX(), text_grid.centerY(), center=True
    ))


    ## STEP5: Draw submodules, i.e., ROB, ALU, and memory system.
    self.rob       = Rob(
      self.d, len(imem), rob_grid, fontsize, line_width, speed)
    self.alu       = Alu(
      self.d, bufferSize, alu_grid, fontsize, line_width, speed)
    self.memSystem = MemSystem(
      l1ValidArray, self.d, bufferSize, memSystem_grid, fontsize, line_width,
      speed)


  def getDraw(self):
    return self.d


  def save(self, name):
    self.d.save_svg(f"{name}.svg")



if __name__ == "__main__":
  processor = Processor(
    imem=[
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 1, "port": 0, "name": "inst0"},
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 1, "port": 0, "name": "inst0"},
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 2, "port": 0, "name": "inst0"},
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 2, "port": 0, "name": "inst0"},
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 4, "port": 0, "name": "inst0"},
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 4, "port": 0, "name": "inst0"},
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 4, "port": 0, "name": "inst0"},
      {"dest": 0, "opcode": "ALU", "src": 0, "latency": 4, "port": 0, "name": "inst0"},
    ],
    l1ValidArray=[False, False, False, False],
    totalCycle=8,
    # scale=1,
    # xyRatio=16/9,
    # speed=1,
    # bufferSize=3,
  )
  processor.simulate()
  processor.getDraw().display_inline()

