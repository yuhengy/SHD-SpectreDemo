
def decode(inst):
  if   inst["opcode"]=="ALU":
    return {
      "src_used" : True,
      "src_addr" : inst["src"],
      
      "exe_cmd": {
        "opcode" : "ALU",
        "port"   : inst["port"]   if "port"   in inst else 0,
        "latency": inst["latency"],
        "result" : inst["result"] if "result" in inst else 0,
      },
     
      "wb_enable": True,
      "wb_addr"  : inst["dest"],
    }

  elif inst["opcode"]=="LOAD":
    return {
      "src_used" : True,
      "src_addr" : inst["src"],
      
      "exe_cmd": {
        "opcode": "LOAD",
      },
      
      "wb_enable": True,
      "wb_addr"  : inst["dest"],
    }

  else:
    assert false, "Unsupported opcode."

