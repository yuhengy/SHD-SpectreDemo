
def instToStr_noName(inst):

  def destStr():
    if inst["dest"]==0:
      return "__"
    else:
      return f"r{inst['dest']}"
  def srcStr():
    if inst["src"]==7:
      return "rSec"
    else:
      return f"r{inst['src']}"


  if   inst["opcode"]=="ALU":
    return f"{destStr()} <- ALU-{inst['port']}({srcStr()}, lat={inst['latency']})"


  elif inst["opcode"]=="LOAD":
    if "src" in inst:
      return f"{destStr()} <- LOAD({srcStr()})"
    else:
      return f"{destStr()} <- LOAD(0x{inst['srcImm']})"


  elif inst["opcode"]=="BREZ":
    return f"IF ({srcStr()}==0) PC += {inst['offset']}"


  elif inst["opcode"]=="NOP":
    return f"NOP"




def imemToStrList(imem):

  strList = ["" for _ in imem]

  for i, inst in enumerate(imem):
  
    def destStr():
      if inst["dest"]==0:
        return " _"
      else:
        return f"r{inst['dest']}"
    def srcStr():
      if inst["src"]==7:
        return "rSec"
      else:
        return f"r{inst['src']}"


    if   inst["opcode"]=="ALU":
      strList[i] += f"{destStr()} <- ALU-{inst['port']}(r{inst['src']}, lat={inst['latency']}) // {inst['name']}"


    elif inst["opcode"]=="LOAD":
      if "src" in inst:
        strList[i] += f"{destStr()} <- LOAD(r{inst['src']})         // {inst['name']}"
      else:
        strList[i] += f"{destStr()} <- LOAD(0x{inst['srcImm']})        // {inst['name']}"


    elif inst["opcode"]=="BREZ":
      strList[i] += f"IF(r{inst['src']}==0) PC <- PC + {inst['offset']} // {inst['name']}"
      for j in range(i+1, min(i+inst["offset"], len(imem))):
        strList[j] += "  "


    elif inst["opcode"]=="NOP":
      strList[i] += f"NOP                    // {inst['name']}"


  return strList

