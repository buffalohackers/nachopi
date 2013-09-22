import json
import subprocess
import time
import urllib2

vol_args = ['amixer', 'set', 'Master', '0']
old_stream = ''
current_stream = ''
stream_pid = None
owner = 0
masters = {}
addresses = ['http://10.0.0.%s:1337/state' % str(i+1) for i in range(10)]

def update():
    global current_stream, owner, vol_args, masters
    for address in addresses:
        print 'Hitting:', address
        try:
            resp = urllib2.urlopen(address)
            body = json.load(resp)
            print body
            if owner == 0 and body['owner'] != -1:
                print 'SETTING NEW OWNER'
                owner = body['owner']
                masters[address] = owner
                current_stream = body['stream']
                vol_args[3] = '%s%%' % str(body['volume'])
                print 'Updating volume:', vol_args
                p = subprocess.Popen(vol_args)
                p.wait()
                start_stream(current_stream)
            elif body['owner'] == owner:
                print 'HELLO MASTER'
                vol_args[3] = '%s%%' % str(body['volume'])
                print 'Updating volume:', vol_args
                p = subprocess.Popen(vol_args)
                p.wait()
            elif body['owner'] == -1 and address in masters and masters[address] == owner:
                kill_stream()
        except urllib2.URLError:
            continue

def start_stream(current_stream):
    global stream_pid, old_stream
    stream_args = ['mpg321', current_stream]
    if current_stream != '':
        print 'starting new stream:', current_stream
        p = subprocess.Popen(stream_args)
        stream_pid = p
        print 'new stream pid:', stream_pid
        old_stream = current_stream

def kill_stream():
    if stream_pid != None:
        print 'killing', stream_pid
        stream_pid.kill()

while True:
    update()
    print masters
    print owner
    print 'Old stream:', old_stream
    print 'Current stream:', current_stream
    print 'PID:', stream_pid
