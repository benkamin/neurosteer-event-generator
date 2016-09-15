import websocket
import thread
import time
import json
import sys
import numpy

data=[]
h1=[]
vals=["c1","c2","c3","e1","e2","e3","h1","h2"]
lastdif=dict()

def on_message(ws, message):
    #print message
    j = json.loads(message)['features']
    #print j['c1']

    #lastval=j['e1']

    #h1.append(lastval)
    
    if len(data)>10:
      for key in data[0].keys():
        def get_value(item):
        	return item[key]
        values = map(get_value,data[-10:])
        #print key
        #print values
        mean=numpy.mean(values)
        std=numpy.std(values)
        dif=(j[key]-mean)/std
        

        #print j[key],'mean:', mean,'std:', std,'dif:',dif
        #print key,dif
        lastdif[key]=dif
      
      s=""
      for key in vals:
        s=s+key+":"+str(lastdif[key])+"; "  
#      print s
  

    else:
	    print ("not ready")   
	    data.append(j)
    
#    str=""
#    for key in vals:
#      str=str+key+":"+str(lastdif[key])+"; "
#    print str

#    for v in j:
#    	sys.stdout.write(v)
#    	sys.stdout.write(':') 
#    	sys.stdout.write(j[v])
#    	sys.stdout.write('	')
#    	val=j[v]

#    	sys.stdout.write(val)
    	
#    sys.stdout.write('\n')
    
    
#    data.append(j)
#    if len(data) > 10:
#        print "ok"
#        print data['h1']
    
    

def on_error(ws, error):
    print (error)

def on_close(ws):
    print ("### closed ###")

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print ("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://cloud.neurosteer.com:8080/v1/features/0006664e5c1a/pull",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
#    ws.on_open = on_open

    ws.run_forever()
