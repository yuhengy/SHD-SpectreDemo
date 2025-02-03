import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from IPython.display import HTML



## STEP: Keep me default.
ROB_SIZE = 8


class Visual():

  LINE_WIDTH = 1
  LINE_WIDTH_BOLD= 2

  ROB_X = 10
  ROB_Y = 80
  ROB_ENTRY_WIDTH = 8
  ROB_ENTRY_HEIGHT = 16

  INST_RADIUS = 3
  INST_FONTSIZE = 6



  def __init__(self, imem):

    ## STEP1: Initialize the size.
    self.fig, self.ax = plt.subplots(figsize=(8, 8), dpi=400)
    self.ax.set_xlim(0, 100)
    self.ax.set_ylim(0, 100)

    ## STEP2: Hide axis and ticks
    self.ax.set_xticks([])
    self.ax.set_yticks([])
    self.ax.set_frame_on(False)

    ## STEP3: Add structures, e.g., ROB, ALU, etc.
    # self.ax.set_title("Out-of-Order Simulation")

    self.pc = 0

    self.imem = imem

    self.rob = [{} for _ in range(ROB_SIZE)]
    self.rob_head = 0
    self.rob_tail = 0
    for i in range(ROB_SIZE):
      self.ax.add_patch(plt.Rectangle(
        (self.ROB_X + self.ROB_ENTRY_WIDTH * i, self.ROB_Y),
        self.ROB_ENTRY_WIDTH, self.ROB_ENTRY_HEIGHT,
        fill=False, edgecolor='black', linewidth=self.LINE_WIDTH_BOLD))

    self.anim = animation.FuncAnimation(self.fig, self.tick, frames=5, interval=1000, repeat=False)


  def fetch(self):
    self.rob[self.rob_tail]["valid"] = True
    self.rob[self.rob_tail]["pc"] = self.pc

    visual_x = self.ROB_X + self.ROB_ENTRY_WIDTH/2 + \
               self.ROB_ENTRY_WIDTH * (ROB_SIZE - self.rob_tail - 1)
    visual_y = self.ROB_Y + self.ROB_ENTRY_HEIGHT/2
    circle = plt.Circle(
      (visual_x, visual_y), self.INST_RADIUS, fill=False, edgecolor='black',
      linewidth=self.LINE_WIDTH)
    self.ax.add_patch(circle)
    text = self.ax.text(
      visual_x, visual_y, "InstX", color="black", ha="center", va="center",
      fontsize=self.INST_FONTSIZE)
    self.rob[self.rob_tail]["visual"] = [circle, text]
    
    self.rob_tail += 1


  def commit(self):
    if self.rob_tail > self.rob_head:
      self.rob[self.rob_head]["valid"] = False
      for item in self.rob[self.rob_head]["visual"]:
        item.remove()
      self.rob_head += 1



  def tick(self, frame):
    self.commit()
    self.fetch()
    self.ax.set_title(f"Cycle {frame+1}")


  def show(self):
    plt.show()


  def save(self, name):
    plt.close(self.fig)
    self.anim.save(name)


if __name__ == "__main__":
  imem = [
    {"dest": 0, "opcode": "ALU", "src": 0, "latency": 4, "port": 0, "name": "inst0"},
  ]

  visual = Visual(imem)
  visual.show()
