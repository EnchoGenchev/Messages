import subprocess
import time

#start the server
server = subprocess.Popen(["python", "servers/server.py"])

#give the server a moment to start up
time.sleep(1)

#start two clients
client1 = subprocess.Popen(["python", "clients/client.py"])
client2 = subprocess.Popen(["python", "clients/client.py"])

try:
    server.wait()
except KeyboardInterrupt:
    pass

#terminate if interrupted
client1.terminate()
client2.terminate()
server.terminate()
