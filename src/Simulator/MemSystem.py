
class MemSystem():
  MISS_LATENCY = 3
  READ_ONLY_ARRAY = [0, 0, 0, 0]

  def __init__(self, l1ValidArray, printTrace=False):
    self.l1ValidArray = l1ValidArray
    self.hitList = []
    self.mshrFifo = []
    
    self.cycle = 0

    self.printTrace = printTrace


  def findInMshrFifo(self, addr):
    existingMiss = None
    entryID      = None
    for i, entry in enumerate(self.mshrFifo):
      if entry["addr"]==addr:
        existingMiss = entry
        entryID      = i
    return existingMiss, entryID


  def sendReq(self, addr, roblink):
    if self.l1ValidArray[addr]:
      self.hitList.append({"addr": addr, "roblink": roblink})

      if self.printTrace:
        print(f"[Memory System] Get request and hit: {self.hitList[-1]}.")

    else:
      existingMiss, entryID = self.findInMshrFifo(addr)

      if existingMiss==None:
        self.mshrFifo.append({
          "addr": addr,
          "latency": self.MISS_LATENCY,
          "roblinkList": [roblink],
        })

        if self.printTrace:
          print(f"[Memory System] Get request and miss.",
                f"New MSHR request: {self.mshrFifo[-1]}.")
      
      else:
        existingMiss["roblinkList"].append(roblink)

        if self.printTrace:
          print(f"[Memory System] Get request and miss.",
                f"Append to existing MSHR request: {existingMiss}.")
  

  def respond_hit(self, entry, robResp):
    robResp(entry["roblink"], self.READ_ONLY_ARRAY[entry["addr"]])
  

  def respond_miss(self, head, robResp):
    for roblink in head["roblinkList"]:
      robResp(roblink, self.READ_ONLY_ARRAY[head["addr"]])


  def respond(self, robResp):
    for entry in self.hitList:
      self.respond_hit(entry, robResp)
    self.hitList = []


    if len(self.mshrFifo) > 0:
      head = self.mshrFifo[0]
      
      if head["latency"]==0:
        self.mshrFifo.pop(0)
        self.respond_miss(head, robResp)
        self.l1ValidArray[head["addr"]] = True


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
    
    ## TODO: remove this
    self.justSquash = False

    self.cycle += 1

