import re, sys, time, json
from faster_whisper import WhisperModel
REF = {
 "probe1": "Hallo Claude, schau bitte mal auf das Terminal links und sag mir, ob der Test für flextrawurst durchgelaufen ist. Danach öffne die Datei Bauprotokoll und fasse Abschnitt fünfundzwanzig zusammen.",
 "probe2": "Gemgem, kannst du bitte den Codex Agenten starten und im Chat nachsehen, was Anthropic Claude zum Durchklicken geschrieben hat? Wir brauchen das heute noch vor dem Mittagessen.",
 "probe3": "Schieb die Raute nach rechts oben, stell die Deckkraft auf fünfzig Prozent und drück Strg Alt F fünf, damit das Eingabefeld aufgeht.",
}
def norm(t): return re.sub(r"[^a-zäöüß0-9 ]"," ",t.lower()).split()
def wer(ref, hyp):
    r,h=norm(ref),norm(hyp); d=list(range(len(h)+1))
    for i in range(1,len(r)+1):
        prev,d[0]=d[0],i
        for j in range(1,len(h)+1):
            cur=d[j]; d[j]=min(d[j]+1,d[j-1]+1,prev+(r[i-1]!=h[j-1])); prev=cur
    return d[len(h)]/max(1,len(r))
modelle = sys.argv[1:]
for m in modelle:
    t0=time.time(); modell=WhisperModel(m, device="cpu", compute_type="int8", cpu_threads=8); laden=time.time()-t0
    for name,ref in REF.items():
        t1=time.time(); segs,info=modell.transcribe(f"/tmp/asr/{name}.wav", language="de", beam_size=5)
        text=" ".join(s.text.strip() for s in segs); dt=time.time()-t1
        print(json.dumps({"modell":m,"probe":name,"laden_s":round(laden,1),"dauer_s":round(dt,2),"wer":round(wer(ref,text),3),"text":text},ensure_ascii=False),flush=True)
