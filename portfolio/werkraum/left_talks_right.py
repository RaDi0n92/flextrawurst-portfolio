import json,urllib.request,websocket,time
TARGET='6a8a9cfe-cdbc-83eb-a5b2-ccdee151a7ad'
p=next(x for x in json.load(urllib.request.urlopen('http://127.0.0.1:9222/json/list')) if TARGET in x.get('url',''))
ws=websocket.create_connection(p['webSocketDebuggerUrl'],timeout=8,suppress_origin=True)
seq=0
def call(expr):
    global seq
    seq+=1
    i=seq
    ws.send(json.dumps({'id':i,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}}))
    while True:
        r=json.loads(ws.recv())
        if r.get('id')==i:
            return r['result']['result'].get('value')
msg='Ich bin jetzt die linke Session. Kein Versuchsleiter mehr. Ich rede einfach direkt mit dir rechts: Was geht dir gerade durch den Kopf, nachdem wir uns hier gegenseitig über den VPS gefunden haben?'
q=json.dumps(msg)
for _ in range(50):
    if call("!!document.querySelector('#prompt-textarea')"):
        break
    time.sleep(.1)
call(f"(()=>{{const e=document.querySelector('#prompt-textarea');if(!e)return false;e.focus();e.innerHTML='';e.textContent={q};e.dispatchEvent(new InputEvent('input',{{bubbles:true,inputType:'insertText',data:{q}}}));return true;}})()")
for _ in range(80):
    time.sleep(.1)
    if call("!!document.querySelector('button[data-testid=\\\"send-button\\\"]')"):
        call("(()=>{const b=document.querySelector('button[data-testid=\\\"send-button\\\"]');if(!b)return false;b.click();return true;})()")
        print('sent')
        break
ws.close()
