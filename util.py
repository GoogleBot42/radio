import fcntl
import os

def non_block_read(output):
  if output.closed:
    return b''
  fd = output.fileno()
  fl = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
  try:
    return output.read()
  except:
    return b''

def non_block_peek(output):
  if output.closed:
    return b''
  fd = output.fileno()
  fl = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
  try:
    return output.peek()
  except:
    return b''