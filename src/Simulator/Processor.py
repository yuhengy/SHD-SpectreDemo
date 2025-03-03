
import os, sys
import copy

sys.path.append(os.getcwd())
from src.Simulator.PhysicalRegfile import PhysicalRegfile
from src.Simulator.Rob             import Rob
from src.Simulator.Alu             import Alu
from src.Simulator.MemSystem       import MemSystem
from src.Simulator.decode          import decode
from src.Simulator.parseProgram    import imemToStrList


class Processor():

  def __init__(self, imem, r7, l1ValidArray, maxCycle, defense="Baseline",
               printTrace=False):
    self.pc         = 0
    self.imem       = copy.deepcopy(imem)
    self.regfile    = PhysicalRegfile(r7, printTrace)
    self.rob        = Rob(defense, printTrace)
    self.alu        = Alu(defense, printTrace)
    self.memSystem  = MemSystem(l1ValidArray, defense, printTrace)
    
    self.cycle    = 0
    self.maxCycle = maxCycle

    self.printTrace = printTrace


  def fetch(self):
    if self.pc >= len(self.imem):
      return

    decodedDict = decode(self.imem[self.pc])
    
    src_stall, src_data, src_roblink = self.regfile.read(
      decodedDict["src_used"], decodedDict["src_addr"])
    if decodedDict["wb_enable"]:
      self.regfile.updateRenaming(decodedDict["wb_addr"], self.rob.tail)
    
    self.rob.push(
      src_stall, src_data, src_roblink, self.pc,
      decodedDict["exe_cmd"],
      decodedDict["wb_enable"], decodedDict["wb_addr"])

    self.pc += 1


  def dispatch(self):
    self.rob.dispatch(self.alu.sendReq, self.memSystem.sendReq)


  def executorRespond(self):
    self.alu      .respond(self.rob.collectResultAndForward)
    self.memSystem.respond(self.rob.collectResultAndForward)


  def commit(self):
    def squash(newPc):
      self.regfile  .squash()
      self.alu      .squash()
      self.memSystem.squash()
      self.pc = newPc

    self.rob.commit(self.regfile.write, squash)


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





  ## PUBLIC:
  def printImem(self):
    for inst in imemToStrList(self.imem):
      print(inst)


  def simulate(self):
    if self.maxCycle==None:
      while not self.rob.finish:
        self.tick()
    
    else:
      for _ in range(self.maxCycle+1):
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
      {"opcode": "NOP", "name": "nop"},
    ],
    r7=1,
    l1ValidArray=[False, False, False, False],
    totalCycle=8,
    printTrace=True,
  )
  processor.simulate()

