
class PhysicalRegfile():

  def __init__(self, printTrace=False):
    self.printTrace = printTrace


  def read(self, src_used, src_addr, wb_enable, wb_addr):
    return False, 0, None


  def write(self, addr, data):
    pass


  def tick(self):
    pass

