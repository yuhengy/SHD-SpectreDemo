
import os, sys
sys.path.append(os.getcwd())

from src.PhysicalRegfile import PhysicalRegfile
from src.Rob             import Rob
from src.Alu             import Alu
from src.MemSystem       import MemSystem
from src.decode          import decode


class Processor():

  def __init__(self, imem, l1ValidArray, printTrace=False):
    self.cycle     = 0
    self.pc        = 0
    self.imem      = imem
    self.regfile   = PhysicalRegfile(printTrace)
    self.rob       = Rob(printTrace)
    self.alu       = Alu(printTrace)
    self.memSystem = MemSystem(l1ValidArray, printTrace)

    self.printTrace = printTrace


  def fetch(self):
    decodedDict = decode(self.imem[self.pc])
    
    src_stall, src_data, src_roblink = self.regfile.read(
      decodedDict["src_used"], decodedDict["src_addr"],
      decodedDict["wb_enable"], decodedDict["wb_addr"]
    )
    
    self.rob.push(
      src_stall, src_data, src_roblink,
      decodedDict["exe_cmd"],
      decodedDict["wb_enable"], decodedDict["wb_addr"])

    self.pc += 1


  def dispatch(self):
    self.rob.dispatch(self.alu.sendReq, self.memSystem.sendReq)


  def executorRespond(self):
    self.alu      .respond(self.rob.collectResultAndForward)
    self.memSystem.respond(self.rob.collectResultAndForward)


  def commit(self):
    self.rob.commit(self.regfile.write)


  def tick(self):
    if self.printTrace:
      print(f"======== Cycle {self.cycle} Starts ========")
    
    self.commit()
    self.executorRespond()
    self.dispatch()
    self.fetch()

    self.regfile  .tick()
    self.rob      .tick()
    self.alu      .tick()
    self.memSystem.tick()
    self.cycle += 1
    
    if self.printTrace:
      print()


  def simulate(self, cycle):
    for i in range(cycle):
      self.tick()




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
    printTrace=True
  )
  processor.simulate(8)

