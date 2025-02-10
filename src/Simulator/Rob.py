
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

    self.printTrace = printTrace


  def push(self, src_stall, src_data, src_roblink,
                 exe_info,
                 wb_enable, wb_addr):
    self.entries.append({
      "status"      : self.Status.STALLED if src_stall else self.Status.READY,
      
      "src_data"    : src_data,
      "src_roblink" : src_roblink,

      "exe_cmd"     : exe_info,
      
      "wb_enable"   : wb_enable,
      "wb_addr"     : wb_addr,
      "wb_data"     : 0,
    })
    self.tail += 1

    if self.printTrace:
      print(f"[ROB] Push entry {self.entries[-1]}.")


  def dispatch(self, aluReq, l1Req):
    for i in range(self.head, self.tail):
      entry = self.entries[i]
      
      if entry["status"]==self.Status.READY:
        exe_cmd = entry["exe_cmd"]
        
        if   exe_cmd["opcode"]=="ALU":
          aluReq(exe_cmd["port"], exe_cmd["latency"], exe_cmd["result"], i)
          entry["status"] = self.Status.DISPATCHED
        
        elif exe_cmd["opcode"]=="LOAD":
          l1Req(entry["src_data"], i)
          entry["status"] = self.Status.DISPATCHED
        
        elif exe_cmd["opcode"]=="NOP":
          l1Req(entry["src_data"], i)
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


  def commit(self, regfileWrite):
    if self.tail==self.head:
      return

    entry = self.entries[self.head]
    
    if entry["status"]== self.Status.FINISHED:
      if entry["wb_enable"]:
        regfileWrite(entry["wb_addr"], entry["wb_data"])
      self.head += 1

      if self.printTrace:
        print(f"[ROB] Commit entry {entry}.")


  def tick(self):
    pass

