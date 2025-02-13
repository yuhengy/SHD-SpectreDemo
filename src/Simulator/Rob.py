
from enum import Enum


class Rob():
  
  class Status(Enum):
    STALLED    = 1
    READY      = 2
    DISPATCHED = 3
    FINISHED   = 4


  def __init__(self, printTrace=False):
    self.entries = []
    self.head = 0
    self.tail = 0

    self.cycle = 0

    self.printTrace = printTrace


  def push(self, src_stall, src_data, src_roblink, pc,
                 exe_cmd,
                 wb_enable, wb_addr):
    self.entries.append({
      "status"      : self.Status.STALLED if src_stall else self.Status.READY,
      
      "src_data"    : src_data,
      "src_roblink" : src_roblink,

      "exe_cmd"     : exe_cmd,
      
      "wb_enable"   : wb_enable,
      "wb_addr"     : wb_addr,
      "wb_data"     : 0,

      "pc"          : pc,
      "squash"      : False,
      "squash_pc"   : None,
    })
    self.tail += 1

    if self.printTrace:
      print(f"[ROB] Push entry {self.entries[-1]}.")


  def dispatch_alu(self, port, latency, result, i, aluReq):
    aluReq(port, latency, result, i)


  def dispatch_l1(self, addr, i, l1Req):
    l1Req(addr, i)


  def dispatch_br(self, i):
    entry = self.entries[i]
    exe_cmd = entry["exe_cmd"]

    entry["squash"] = (entry["src_data"]==0) != exe_cmd["predicted_taken"]
    entry["squash_pc"] = entry["pc"] + exe_cmd["offset"]


  def dispatch(self, aluReq, l1Req):
    for i in range(self.head, self.tail):
      entry = self.entries[i]
      
      if entry["status"]==self.Status.READY:
        exe_cmd = entry["exe_cmd"]
        
        if   exe_cmd["opcode"]=="ALU":
          self.dispatch_alu(
            exe_cmd["port"], exe_cmd["latency"], exe_cmd["result"], i, aluReq)
          entry["status"] = self.Status.DISPATCHED
        
        elif exe_cmd["opcode"]=="LOAD":
          addr = exe_cmd["srcImm"] if exe_cmd["useImm"] else entry["src_data"]
          self.dispatch_l1(addr, i, l1Req)
          entry["status"] = self.Status.DISPATCHED
        
        elif exe_cmd["opcode"]=="BREZ":
          self.dispatch_br(i)
          entry["status"] = self.Status.FINISHED
        
        elif exe_cmd["opcode"]=="NOP":
          entry["status"] = self.Status.FINISHED
        
        else:
          assert false, "Unsupported opcode."
        

  def collectResultAndForward(self, roblink, result):
    assert self.head <= roblink and roblink < self.tail, \
           "Infrastructure Error: Wrong roblink for ALU/L1 response."
    
    entry = self.entries[roblink]
    entry["status"]  = self.Status.FINISHED
    entry["wb_data"] = result

    if self.printTrace:
      print(f"[ROB] Entry {roblink} get result {result}.")

    for i in range(self.head, self.tail):
      consumer = self.entries[i]

      if consumer["status"]==self.Status.STALLED and \
         consumer["src_roblink"]==roblink:
        consumer["status"]   = self.Status.READY
        consumer["src_data"] = result
        
        if self.printTrace:
          print(f"[ROB] Forward result {result} to entry {i}.")


  def commit_wb(self, regfileWrite):
    entry = self.entries[self.head]
    regfileWrite(entry["wb_addr"], entry["wb_data"], self.head)


  def commit_squash(self, squash):

    ## STEP2: Clear renaming table, ALU and L1. Reset PC.
    squash(self.entries[self.head]["squash_pc"])

    ## STEP1: Clear ROB.
    self.head    = self.tail - 1


  def commit_others(self):
    pass


  def commit(self, regfileWrite, squash):
    if self.tail==self.head:
      return

    entry = self.entries[self.head]
    
    if entry["status"]== self.Status.FINISHED:
      entry = self.entries[self.head]
      
      if   entry["wb_enable"]:
        self.commit_wb(regfileWrite)
      
      elif entry["squash"]:
        self.commit_squash(squash)
      
      else:
        self.commit_others()


      self.head += 1

      if self.printTrace:
        print(f"[ROB] Commit entry {entry}.")


  def tick(self):
    self.cycle += 1

