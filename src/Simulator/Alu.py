
class Alu():
  NUM_PORTS = 3

  def __init__(self, defense="Baseline", printTrace=False):
    self.defense = defense

    self.portFifo = [[] for _ in range(self.NUM_PORTS)]
    
    self.cycle = 0

    self.statistic_maxFifoSize = 0

    self.printTrace = printTrace


  def sendReq(self, port, latency, result, roblink):
    assert port < self.NUM_PORTS, f"ALU only has {self.NUM_PORTS} ports."
    fifo = self.portFifo[port]
    fifo.append({
      "latency": latency,
      "result" : result,
      "roblink": roblink
    })

    if self.defense=="GhostMinion":
      fifo[-1]["resetLatency"] = latency
      self.portFifo[port] = sorted(fifo, key=lambda d: d["roblink"])
      fifo = self.portFifo[port]

      if fifo[0]["roblink"]==roblink and len(fifo) > 1:
        fifo[1]["latency"] = fifo[1]["resetLatency"]

    if self.printTrace:
      print(f"[ALU] Get request {fifo[-1]} at Port {port}.")


  def respond_internal(self, portID, head, roblink, result, robResp):
    robResp(roblink, result)


  def respond(self, robResp):
    for i in range(self.NUM_PORTS):
      fifo = self.portFifo[i]

      if len(fifo) > 0:
        head = fifo[0]
        
        if head["latency"]==0:
          fifo.pop(0)
          self.respond_internal(i, head, head["roblink"], head["result"], robResp)


  def squash(self):
    self.portFifo = [[] for _ in range(self.NUM_PORTS)]


  def tick(self):
    for i in range(self.NUM_PORTS):
      fifo = self.portFifo[i]

      if len(fifo) > 0:
        head = fifo[0]

        assert head["latency"] > 0, "ALU Latency drops below 0"
        head["latency"] = head["latency"] - 1

    self.cycle += 1

    self.statistic_maxFifoSize = max(self.statistic_maxFifoSize,
                                     *[len(fifo) for fifo in self.portFifo])

