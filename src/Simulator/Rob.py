
from enum import Enum


class Rob():
  
  class Status(Enum):
    STALLED    = 1
    READY      = 2
    DISPATCHED = 3
    FINISHED   = 4


  def __init__(self, defense="Baseline", printTrace=False):
    self.defense = defense

    self.entries = []
    self.head = 0
    self.tail = 0

    if defense=="InvisiSpec" or defense=="GhostMinion":
      self.isSpeculative         = False
      self.isSpeculative_roblink = None



    self.cycle  = 0
    self.finish = False

    self.statistic_maxInst = 0

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
    
    if self.defense=="InvisiSpec" or self.defense=="GhostMinion":
      self.entries[-1]["isSpeculative"] = self.isSpeculative
      if exe_cmd["opcode"]=="BREZ":
        self.isSpeculative         = True
        self.isSpeculative_roblink = self.tail
    
    self.tail += 1

    if self.printTrace:
      print(f"[ROB] Push entry {self.entries[-1]}.")


  def dispatch_alu(self, port, latency, result, i, aluReq):
    aluReq(port, latency, result, i)


  def dispatch_l1(self, addr, i, l1Req, isSpeculative=None):
    l1Req(addr, i, isSpeculative)


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
          if self.defense=="InvisiSpec" or self.defense=="GhostMinion":
            self.dispatch_l1(addr, i, l1Req, entry["isSpeculative"])
          else:
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

    ## STEP1: Clear renaming table, ALU and L1. Reset PC.
    squash(self.entries[self.head]["squash_pc"])

    ## STEP2: Clear ROB.
    self.head    = self.tail - 1

    if self.defense=="InvisiSpec" or self.defense=="GhostMinion":
      ## STEP3: Clear isSpeculative bit
      self.isSpeculative = False


  def commit_br_noSquash(self):
    if self.defense=="InvisiSpec" or self.defense=="GhostMinion":
      if self.isSpeculative and self.isSpeculative_roblink==self.head:
        self.isSpeculative = False


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
      
      elif entry["exe_cmd"]["opcode"]=="BREZ":
        self.commit_br_noSquash()
      
      else:
        self.commit_others()


      self.head += 1

      if self.printTrace:
        print(f"[ROB] Commit entry {entry}.")


  def tick(self):
    self.cycle += 1
    if self.head==self.tail:
      self.finish = True

    self.statistic_maxInst = len(self.entries)

