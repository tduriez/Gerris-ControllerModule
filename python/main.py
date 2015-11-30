import os
#communicate with another process through named pipe
#one for receive command, the other for send command
sendPath = "/tmp/sendfifo"
recvPath = "/tmp/recvfifo"
wp = open(sendPath, 'r')
rp = open(recvPath, 'w',0)
value = 0
while True:
  query = wp.read(4)
  print "Query function %s" % query
  value = ((value + 1) % 90) + 10
  s = str(value)
  print "Sending %s" % s
  rp.write(s)		
wp.close()
rp.close()
