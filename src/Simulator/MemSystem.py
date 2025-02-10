
class MemSystem():
  MISS_LATENCY = 4
  READ_ONLY_ARRAY = [0, 0, 0, 0]

  def __init__(self, l1ValidArray, printTrace=False):
    self.l1ValidArray = l1ValidArray
    self.hitList = []
    self.mshrFifo = []

    self.printTrace = printTrace


  def sendReq(self, addr, roblink):
    if self.l1ValidArray[addr]:
      self.hitList.append({"addr": addr, "roblink": roblink})

      if self.printTrace:
        print(f"[Memory System] Get request and hit: {self.hitList[-1]}.")

    else:
      existingMiss = list(filter(
        lambda entry: entry["addr"]==addr,
        self.mshrFifo
      ))

      if   len(existingMiss)==0:
        self.mshrFifo.append({
          "addr": addr,
          "latency": self.MISS_LATENCY,
          "roblinkList": [roblink],
        })

        if self.printTrace:
          print(f"[Memory System] Get request and miss.",
                f"New MSHR request: {self.mshrFifo[-1]}.")
      
      elif len(existingMiss)==1:
        existingMiss[0]["roblinkList"].append(roblink)

        if self.printTrace:
          print(f"[Memory System] Get request and miss.",
                f"Append to existing MSHR request: {existingMiss[0]}.")
      
      else:
        assert False, "Duplicated entries in the mshrFifo."


  def respond(self, robResp):
    for entry in self.hitList:
      robResp(entry["roblink"], self.READ_ONLY_ARRAY[entry["addr"]])
    self.hitList = []


    if len(self.mshrFifo) > 0:
      head = self.mshrFifo[0]
      
      if head["latency"]==0:
        self.mshrFifo.pop(0)
        for roblink in head["roblinkList"]:
          robResp(roblink, self.READ_ONLY_ARRAY[head["addr"]])


  def tick(self):
    if len(self.mshrFifo) > 0:
      head = self.mshrFifo[0]

      assert head["latency"] > 0, "MSHR Latency drops below 0"
      head["latency"] = head["latency"] - 1

