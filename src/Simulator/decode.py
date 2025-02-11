
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
        "name"   : inst["name"],
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
        "name"   : inst["name"],
      },
      
      "wb_enable": True,
      "wb_addr"  : inst["dest"],
    }

  elif inst["opcode"]=="NOP":
    return {
      "src_used" : False,
      "src_addr" : None,
      
      "exe_cmd": {
        "opcode": "NOP",
        "name"   : inst["name"],
      },
      
      "wb_enable": False,
      "wb_addr"  : None,
    }

  else:
    assert false, "Unsupported opcode."

