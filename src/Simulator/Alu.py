
class Alu():
  NUM_PORTS = 4

  def __init__(self, printTrace=False):
    self.portFifo = [[] for _ in range(self.NUM_PORTS)]
    
    self.cycle = 0

    self.printTrace = printTrace


  def sendReq(self, port, latency, result, roblink):
    assert port < self.NUM_PORTS, f"ALU only has {self.NUM_PORTS} ports."
    self.portFifo[port].append({
      "latency": latency,
      "result" : result,
      "roblink": roblink
    })

    if self.printTrace:
      print(f"[ALU] Get request {self.portFifo[port][-1]} at Port {port}.")


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


  def tick(self):
    for i in range(self.NUM_PORTS):
      fifo = self.portFifo[i]

      if len(fifo) > 0:
        head = fifo[0]

        assert head["latency"] > 0, "ALU Latency drops below 0"
        head["latency"] = head["latency"] - 1

    self.cycle += 1

