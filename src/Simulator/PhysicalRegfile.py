
class PhysicalRegfile():
  NUM_REG = 8

  def __init__(self, r7=1, printTrace=False):
    self.architectualRegfile = [0    for _ in range(self.NUM_REG)]
    self.avaliable           = [True for _ in range(self.NUM_REG)]
    self.roblink             = [None for _ in range(self.NUM_REG)]

    self.architectualRegfile[7] = r7

    self.printTrace = printTrace


  def read(self, src_used, src_addr):
    if src_used:
      if self.avaliable[src_addr]:
        return False, self.architectualRegfile[src_addr], None
      else:
        return True, None, self.roblink[src_addr]

    else:
      return False, None, None


  def updateRenaming(self, wb_addr, rob_tail):
    if wb_addr!=0:
      self.avaliable[wb_addr] = False
      self.roblink  [wb_addr] = rob_tail


  def write(self, addr, data, rob_head):
    if self.avaliable[addr]:
      self.architectualRegfile[addr] = data
    
    else:
      if self.roblink[addr]==rob_head:
        self.avaliable          [addr] = True
        self.architectualRegfile[addr] = data


  def squash(self):
    self.avaliable = [True for _ in range(self.NUM_REG)]


  def tick(self):
    pass

