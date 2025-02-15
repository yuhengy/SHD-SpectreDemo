
import copy


class MemSystem():
  MISS_LATENCY = 3
  READ_ONLY_ARRAY = [0, 0, 0, 0]

  def __init__(self, l1ValidArray, defense="Baseline", printTrace=False):
    self.l1ValidArray = copy.copy(l1ValidArray)
    self.defense = defense
    
    self.hitList = []
    self.mshrFifo = []
    
    self.cycle = 0

    self.statistic_maxFifoSize = 0

    self.printTrace = printTrace




  ## PRIVATE:
  def findInMshrFifo(self, addr):
    existingMiss = None
    entryID      = None
    for i, entry in enumerate(self.mshrFifo):
      if entry["addr"]==addr:
        existingMiss = entry
        entryID      = i
    return existingMiss, entryID


  def sendReq_hit(self, addr, roblink):
    self.hitList.append({"addr": addr, "roblink": roblink})

    if self.printTrace:
      print(f"[Memory System] Get request and hit: {self.hitList[-1]}.")


  def sendReq_newMshr(self, addr, roblink, isSpeculative):
    self.mshrFifo.append({
      "addr": addr,
      "latency": self.MISS_LATENCY,
      "roblinkList": [roblink],
    })

    if self.defense=="InvisiSpec":
      self.mshrFifo[-1]["isSpeculative"] = isSpeculative

    if self.printTrace:
      print(f"[Memory System] Get request and miss.",
            f"New MSHR request: {self.mshrFifo[-1]}.")


  def sendReq_appendMshr(self, addr, roblink, isSpeculative):
    existingMiss, _ = self.findInMshrFifo(addr)
    existingMiss["roblinkList"].append(roblink)

    if self.defense=="InvisiSpec":
      existingMiss["isSpeculative"] = existingMiss["isSpeculative"] and \
                                      isSpeculative

    if self.printTrace:
      print(f"[Memory System] Get request and miss.",
            f"Append to existing MSHR request: {existingMiss}.")


  

  def respond_hit(self, entry, robResp):
    robResp(entry["roblink"], self.READ_ONLY_ARRAY[entry["addr"]])
  

  def respond_miss(self, head, robResp):
    for roblink in head["roblinkList"]:
      robResp(roblink, self.READ_ONLY_ARRAY[head["addr"]])

    if self.defense=="InvisiSpec":
      if not head["isSpeculative"]:
        self.l1ValidArray[head["addr"]] = True
    else:
      self.l1ValidArray[head["addr"]] = True




  ## PUBLIC:
  def sendReq(self, addr, roblink, isSpeculative=None):
    if self.l1ValidArray[addr]:
      self.sendReq_hit(addr, roblink)

    else:
      existingMiss, _ = self.findInMshrFifo(addr)

      if existingMiss==None:
        self.sendReq_newMshr(addr, roblink, isSpeculative)
      
      else:
        self.sendReq_appendMshr(addr, roblink, isSpeculative)


  def respond(self, robResp):
    for entry in self.hitList:
      self.respond_hit(entry, robResp)
    self.hitList = []


    if len(self.mshrFifo) > 0:
      head = self.mshrFifo[0]
      
      if head["latency"]==0:
        self.mshrFifo.pop(0)
        self.respond_miss(head, robResp)


  def squash(self):
    self.hitList = []
    if len(self.mshrFifo) > 0:
      head = self.mshrFifo[0]
      head["roblinkList"] = []
      self.mshrFifo = [head]


  def tick(self):
    if len(self.mshrFifo) > 0:
      head = self.mshrFifo[0]

      assert head["latency"] > 0, "MSHR Latency drops below 0"
      head["latency"] = head["latency"] - 1

    self.cycle += 1

    self.statistic_maxFifoSize = max(self.statistic_maxFifoSize,
                                     len(self.mshrFifo))

