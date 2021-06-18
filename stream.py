from util import non_block_read, non_block_peek

class StreamSource(object):
  def getStream(self):
    """ Gets the python stream for reading from """
    pass

class ByteSource(object):
  def peek(self):
    """ Gets the bytes at the head of the queue (if any) without incrementing
    Non-blocking!
    Returns None if no bytes available
    """
    pass
  def read(self):
    """ Gets the bytes at the head of the queue (if any)
    Non-blocking!
    Returns None if no bytes available
    """
    pass

class StreamByteSource(ByteSource):
  def __init__(self, stream):
    self.stream = stream

  def peek(self):
    output = non_block_peek(self.stream)
    if output == None or output == b'':
      return None
    return output

  def read(self):
    output = non_block_read(self.stream)
    if output == None or output == b'':
      return None
    return output

def toByteSource(src):
  if isinstance(src, ByteSource):
    return src
  elif isinstance(src, StreamSource):
    return StreamByteSource(src.getStream())
  elif src is None:
    return None
  else:
    raise Exception("not implemented")