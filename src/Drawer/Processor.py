
import os, sys
import drawsvg as draw

sys.path.append(os.getcwd())
from src.Simulator.Processor import Processor as SimuProcessor

from src.Drawer.Grid      import Grid
from src.Drawer.Rob       import Rob
from src.Drawer.Alu       import Alu
from src.Drawer.MemSystem import MemSystem


class Processor(SimuProcessor):

  def __init__(self, imem, r7, l1ValidArray, totalCycle, d, \
               robSize, aluSize, mshrSize,
               grid, fontsize, line_width, defense="Baseline", speed=1,
               useLogo=True):
    super().__init__(imem, r7, l1ValidArray, totalCycle, defense, False)


    ## STEP1: Divide the whole board for 4 components.
    
    ## STEP1.1: Remove some margin.
    grid.divideX([fontsize * 0.5, 1, fontsize * 0.5],
                 useFixedLength=[True, False, True])
    grid.divideY([fontsize * 0.5, 1, fontsize],
                 useFixedLength=[True, False, True])
    grid = grid.getSubGrid(1, 1)

    ## STEP1.2: Draw.
    grid.divideX([fontsize*12, 1, 0.5, 8.5],
                 useFixedLength=[True, False, False, False])
    rob_grid            = grid.getSubGrid(0, 0).getMergedGrid(
                          grid.getSubGrid(1, 0))
    
    grid = grid.getSubGrid(3, 0)
    grid.divideY([1, fontsize * 0.5, fontsize * 2.75],
                 useFixedLength=[False, True, True])
    cycleIndicator_grid = grid.getSubGrid(0, 2)

    grid = grid.getSubGrid(0, 0)
    grid.divideX([4, 0.5, 4])
    alu_grid            = grid.getSubGrid(0, 0)
    memSystem_grid      = grid.getSubGrid(2, 0)


    ## STEP2: Draw the cycle indicator.

    ## STEP2.1: Divide the whole grid into subgrids.
    cycleIndicator_grid.divideX([1, fontsize * 1.5, fontsize * 3],
                                useFixedLength=[False, True, True])
    cycleIndicator_grid.divideY(
      [fontsize * 0.25, fontsize * 0.5, fontsize * 0.25,
      fontsize * 0.75, fontsize * 1],
      useFixedLength=[True, True, True, True, True])
    cycleLogo_grid    = cycleIndicator_grid.getSubGrid(0, 0)
    cyclePointer_grid = cycleIndicator_grid.getSubGrid(0, 1)
    cycleAxis_grid    = cycleIndicator_grid.getSubGrid(0, 3)
    label_grid        = cycleIndicator_grid.getSubGrid(0, 4)
    arrow_grid        = cycleIndicator_grid.getSubGrid(1, 3)
    text_grid         = cycleIndicator_grid.getSubGrid(2, 3)

    ## STEP2.2: A moving pointer
    if useLogo:
      pointer = draw.Image(
        cycleLogo_grid.x - cycleLogo_grid.height*4,
        cycleLogo_grid.y,
        cycleLogo_grid.height*8,
        cycleLogo_grid.height*4,
        "logo/matcha-logo-dark-green.svg",
        embed=True,
      )
      pointer.add_key_frame(
                       0, x=cycleLogo_grid.x - cycleLogo_grid.height*4)
      pointer.add_key_frame(
        totalCycle/speed, x=cycleLogo_grid.x2() - cycleLogo_grid.height*4)
    
    else:
      pointer = draw.Circle(
        cyclePointer_grid.x,
        cyclePointer_grid.centerY(),
        cyclePointer_grid.height/2,
        fill="black"
      )
      pointer.add_key_frame(               0, cx=cyclePointer_grid.x)
      pointer.add_key_frame(totalCycle/speed, cx=cyclePointer_grid.x2())
    
    d.append(pointer)

    ## STEP2.3: Axis, sticks, and labels.
    d.append(draw.Line(
      cycleAxis_grid.x,
      cycleAxis_grid.centerY(),
      arrow_grid.x2(),
      cycleAxis_grid.centerY(),
      stroke="black", stroke_width=line_width
    ))
    for i in range(totalCycle+1):
      x = cycleAxis_grid.x + cycleAxis_grid.width/totalCycle*i
      d.append(draw.Line(
        x, cycleAxis_grid.y, x, cycleAxis_grid.y2(),
        stroke="black", stroke_width=line_width
      ))
      d.append(draw.Text(
        str(i), fontsize, x, label_grid.centerY(), center=True
      ))

    ## STEP2.4: Arrow
    d.append(draw.Lines(
      arrow_grid.x2()      - arrow_grid.width*0.3,
      arrow_grid.centerY() - arrow_grid.width*0.2,
      arrow_grid.x2()                            ,
      arrow_grid.centerY()                       ,
      arrow_grid.x2()      - arrow_grid.width*0.3,
      arrow_grid.centerY() + arrow_grid.width*0.2,
      fill="transparent", stroke="black", stroke_width=line_width
    ))

    ## STEP2.5: Text
    # text_x = cycleAxis_x2 + text_width/2
    # text_y = cycleAxis_y
    d.append(draw.Text(
      "Cycle", fontsize, text_grid.centerX(), text_grid.centerY(), center=True
    ))


    ## STEP3: Draw submodules, i.e., ROB, ALU, and memory system.
    self.rob       = Rob(
      d, robSize, rob_grid, fontsize, line_width, defense, speed)
    self.alu       = Alu(
      d, aluSize, alu_grid, fontsize, line_width, defense, speed)
    self.memSystem = MemSystem(
      l1ValidArray, d, mshrSize, memSystem_grid, fontsize, line_width,
      defense, speed)

