
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
        "inst"   : inst,
      },
     
      "wb_enable": True,
      "wb_addr"  : inst["dest"],
    }

  elif inst["opcode"]=="LOAD":
    useReg = "src" in inst
    useImm = "srcImm" in inst
    assert useReg ^ useImm, "LOAD use one of src or srcImm."
    return {
      "src_used" : useReg,
      "src_addr" : inst["src"] if useReg else None,
      
      "exe_cmd": {
        "opcode": "LOAD",
        "useImm": useImm,
        "srcImm": inst["srcImm"] if useImm else None,
        "name"  : inst["name"],
        "inst"  : inst,
      },
      
      "wb_enable": True,
      "wb_addr"  : inst["dest"],
    }

  elif inst["opcode"]=="BREZ":
    return {
      "src_used" : True,
      "src_addr" : inst["src"],
      
      "exe_cmd": {
        "opcode"         : "BREZ",
        "predicted_taken": False,
        "offset"         : inst["offset"],
        "name"           : inst["name"],
        "inst"           : inst,
      },
      
      "wb_enable": False,
      "wb_addr"  : None,
    }

  elif inst["opcode"]=="NOP":
    return {
      "src_used" : False,
      "src_addr" : None,
      
      "exe_cmd": {
        "opcode": "NOP",
        "name"  : inst["name"],
        "inst"  : inst,
      },
      
      "wb_enable": False,
      "wb_addr"  : None,
    }

  else:
    assert false, "Unsupported opcode."

