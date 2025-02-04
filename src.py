import drawsvg as draw


## STEP: Keep me default.
CYCLE = 6
ROB_SIZE = 8


class Visual():
  
  CYCLE_PRE = 0.3
  CYCLE_POST = 0.3

  RATIO = 5

  LINE_WIDTH      = 0.3 * RATIO
  LINE_WIDTH_BOLD = 0.6 * RATIO

  DRAW_WIDTH  = 100 * RATIO
  DRAW_HEIGHT = 100 * RATIO

  CYCLE_X = 10 * RATIO
  CYCLE_Y = 80 * RATIO
  CYCLE_LEN = 70 * RATIO
  CYCLE_STICK_LEN = 2 * RATIO
  CYCLE_ARROW_LEN = 2 * RATIO
  CYCLE_FONTSIZE = 5 * RATIO
  CYCLE_RADIUS = 1 * RATIO

  ROB_X = 10 * RATIO
  ROB_Y = 4 * RATIO
  ROB_ENTRY_WIDTH = 8 * RATIO
  ROB_ENTRY_HEIGHT = 16 * RATIO

  INST_RADIUS = 3 * RATIO
  INST_FONTSIZE = 2 * RATIO



  def __init__(self, imem):

    ## STEP1: Initialize the size.
    self.cycle = 0
    self.pc = 0
    self.imem = imem
    self.rob = [{} for _ in range(ROB_SIZE)]
    self.rob_head = 0
    self.rob_tail = 0


    ## STEP2: Initialize the board.
    self.d = draw.Drawing(
    self.DRAW_WIDTH, self.DRAW_HEIGHT, origin=(0, 0),
    animation_config=draw.types.SyncedAnimationConfig(
      duration=CYCLE, show_playback_progress=True, show_playback_controls=True))
    

    ## STEP3: Add structures, e.g., ROB, ALU, etc.
    for i in range(ROB_SIZE):
      self.d.append(draw.Rectangle(
        self.ROB_X + self.ROB_ENTRY_WIDTH * i, self.ROB_Y,
        self.ROB_ENTRY_WIDTH, self.ROB_ENTRY_HEIGHT,
        fill="none", stroke="black", stroke_width=self.LINE_WIDTH_BOLD))


    ## STEP4: Cycle axis.
    arrow = draw.Group(id="arrow")
    arrow.append(draw.Line(0, 0, self.CYCLE_LEN, 0))
    arrow.append(draw.Lines(
      self.CYCLE_LEN, 0,
      self.CYCLE_LEN-self.CYCLE_ARROW_LEN, -self.CYCLE_ARROW_LEN,
      self.CYCLE_LEN-self.CYCLE_ARROW_LEN, self.CYCLE_ARROW_LEN))
    self.d.append(draw.Use(
      arrow, self.CYCLE_X, self.CYCLE_Y, stroke="black", fill="black"))
    for i in range(CYCLE):
      x = self.CYCLE_X + self.CYCLE_LEN/CYCLE * i
      self.d.append(draw.Line(
        x, self.CYCLE_Y-self.CYCLE_STICK_LEN/2,
        x, self.CYCLE_Y+self.CYCLE_STICK_LEN/2,
        stroke="black"))
      self.d.append(draw.Text(
        str(i), self.CYCLE_FONTSIZE, x, self.CYCLE_Y+0.75*self.CYCLE_FONTSIZE,
        center=True))
    self.d.append(draw.Text(
      "Cycle", self.CYCLE_FONTSIZE,
      self.CYCLE_X+self.CYCLE_LEN+1.5*self.CYCLE_FONTSIZE,
      self.CYCLE_Y,
      center=True))
    circle = draw.Circle(
      0, self.CYCLE_Y-self.CYCLE_STICK_LEN-self.CYCLE_RADIUS, self.CYCLE_RADIUS,
      fill="black")
    circle.add_key_frame(0, cx=self.CYCLE_X)
    circle.add_key_frame(CYCLE, cx=self.CYCLE_X+self.CYCLE_LEN)
    self.d.append(circle)


    ## STEP5: Simulate.
    for i in range(CYCLE):
      self.tick()


  def fetch(self):
    self.rob[self.rob_tail]["valid"] = True
    self.rob[self.rob_tail]["pc"] = self.pc
    self.rob_tail += 1

    visual_x = self.ROB_X + self.ROB_ENTRY_WIDTH/2 + \
               self.ROB_ENTRY_WIDTH * (ROB_SIZE - self.rob_tail - 1)
    visual_y = self.ROB_Y + self.ROB_ENTRY_HEIGHT/2
    circle = draw.Circle(
      visual_x, visual_y, self.INST_RADIUS,
      fill="none", stroke_width=self.LINE_WIDTH)
    circle.add_key_frame(self.cycle-1+self.CYCLE_PRE, stroke="none")
    circle.add_key_frame(self.cycle-self.CYCLE_POST, stroke="black")
    self.d.append(circle)
    text = draw.Text(
      "InstX", self.INST_FONTSIZE, visual_x, visual_y, center=True)
    text.add_key_frame(self.cycle-1+self.CYCLE_PRE, fill="none")
    text.add_key_frame(self.cycle-self.CYCLE_POST, fill="black")
    self.d.append(text)
    self.rob[self.rob_tail-1]["visual"] = (circle, text)
  

  def commit(self):
    if self.rob_tail > self.rob_head:
      self.rob[self.rob_head]["valid"] = False
      self.rob_head += 1

      circle, text = self.rob[self.rob_head-1]["visual"]
      circle.add_key_frame(self.cycle-1+self.CYCLE_PRE, stroke="black")
      circle.add_key_frame(self.cycle-self.CYCLE_POST, stroke="none")
      text.add_key_frame(self.cycle-1+self.CYCLE_PRE, fill="black")
      text.add_key_frame(self.cycle-self.CYCLE_POST, fill="none")


  def tick(self):
    self.cycle += 1
    self.commit()
    self.fetch()


  def get_draw(self):
    return self.d


  def save(self, name):
    self.d.save_svg(f"{name}.svg")




if __name__ == "__main__":
  imem = [
    {"dest": 0, "opcode": "ALU", "src": 0, "latency": 4, "port": 0, "name": "inst0"},
  ]

  visual = Visual(imem)
  visual.save("video")
