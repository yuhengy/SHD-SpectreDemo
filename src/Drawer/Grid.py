
import drawsvg as draw


class Grid():

  def __init__(self, x, y, width, height):
    self.x      = x
    self.y      = y
    self.width  = width
    self.height = height

    self.subGrids_x = [width]
    self.subGrids_y = [height]


  def divide(self, parts, totalLength, useFixedLength=None):
    if useFixedLength==None:
      useFixedLength = [False for _ in range(len(parts))]

    totalFixedLength = 0
    totalRatio       = 0
    for x, useFixed in zip(parts, useFixedLength):
      if useFixed:
        totalFixedLength += x
      else:
        totalRatio       += x

    subGrids = []
    for x, useFixed in zip(parts, useFixedLength):
      if useFixed:
        subGrids.append(x)
      else:
        subGrids.append(x / totalRatio * (totalLength-totalFixedLength))

    # assert sum(subGrids)==totalLength, "Grid is not divided to nothing left."

    return subGrids


  def divideX(self, partsX, useFixedLength=None):
    self.subGrids_x = self.divide(partsX, self.width, useFixedLength)


  def divideY(self, partsY, useFixedLength=None):
    self.subGrids_y = self.divide(partsY, self.height, useFixedLength)


  def centerX(self):
    return self.x + self.width/2


  def centerY(self):
    return self.y + self.height/2


  def x2(self):
    return self.x + self.width


  def y2(self):
    return self.y + self.height


  def drawRectangle(self, d, line_width, color="none"):
    rectangle = draw.Rectangle(
      self.x, self.y, self.width, self.height,
      fill=color, stroke="black", stroke_width=line_width
    )
    d.append(rectangle)
    return rectangle


  def drawText(self, d, text, fontsize):
    text = draw.Text(
      text, fontsize,
      self.centerX(), self.centerY(), center=True
    )
    d.append(text)
    return text


  def getSubGrid(self, x, y):
    return Grid(
      self.x + sum(self.subGrids_x[:x]),
      self.y + sum(self.subGrids_y[:y]),
      self.subGrids_x[x],
      self.subGrids_y[y]
    )


  def getMergedGrid(self, other):
    if   self.x==other.x:
      # assert (self.y+self.height)==other.y or (other.y+other.height)==self.y
      # assert self.width==other.width
      return Grid(
        min(self.x, other.x),
        min(self.y, other.y),
        self.width,
        self.height+other.height
      )
    elif self.y==other.y:
      # assert (self.x+self.width )==other.x or (other.x+other.width )==self.x
      # assert self.height==other.height
      return Grid(
        min(self.x, other.x),
        min(self.y, other.y),
        self.width+other.width,
        self.height
      )


  def getAboveGrid(self, height):
    return Grid(
      self.x,
      self.y - height,
      self.width,
      height
    )


  def getLeftGrid(self, weight):
    return Grid(
      self.x- weight,
      self.y,
      weight,
      self.height
    )

