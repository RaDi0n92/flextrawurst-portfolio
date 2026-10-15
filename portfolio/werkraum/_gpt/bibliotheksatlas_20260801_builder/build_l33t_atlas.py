#!/usr/bin/env python3
from pathlib import Path
import re, json, shutil, zipfile, hashlib, collections, unicodedata

ROOT=Path('/root/werkraum')
SRC=ROOT/'engine/godot-vertical-slice/daniels_semantischer_bibliothekskoerper_20260801/md'
OUT=ROOT/'engine/godot-vertical-slice/DANIEL_L33T_OBSIDIAN_ATLAS_20260801'
ZIP=ROOT/'engine/godot-vertical-slice/DANIEL_L33T_OBSIDIAN_ATLAS_2026-08-01.zip'

CHAPTERS=[
('00_START_HIER','L33T: Daniels begehbarer Ideen- und Weltkörper',['000_START','003_WIE_ZU_LESEN'],[],['01_DANIEL_IN_BEWEGUNG','02_DER_GROSSE_ZUSAMMENHANG','03_FLEXTRAWURST_URSPRUNG','20_BLITZMOMENTE']),
('01_DANIEL_IN_BEWEGUNG','Daniel in Bewegung, nicht als Profilkarte',['004_DANIEL_ALS_BEWEGUNG','008_DANIELS_SPRACHE'],['ich glaube','ich denke','ich will','vielleicht','aber','sondern'],['02_DER_GROSSE_ZUSAMMENHANG','17_SPRACHE_UND_WORTERFINDUNGEN','19_WIDERSPRUECHE']),
('02_DER_GROSSE_ZUSAMMENHANG','Der große Zusammenhang unter den Projekten',['005_DER_GROSSE_ZUSAMMENHANG','006_ENTWICKLUNGSLINIEN'],['flextrawurst','gedächtnis','obsidian','spiel','atlas','wesen'],['03_FLEXTRAWURST_URSPRUNG','08_PROVENIENZ_UND_GEDAECHTNIS','09_OBSIDIAN_ATLAS_RECORDER']),
('03_FLEXTRAWURST_URSPRUNG','Flextrawurst: vom organischen Ideenkonstrukt zum Lebensraum',['010_FLEXTRAWURST_VOM_IDEENKONSTRUKT_ZUM_RESONANZSYSTEM'],['flextrawurst','forum','plattform','soziales netzwerk','organisch','lebensraum'],['04_RESONANZ_SCHATTEN_KOMPOASE','05_CODEWESEN_UND_EXISTENZ','02_DER_GROSSE_ZUSAMMENHANG']),
('04_RESONANZ_SCHATTEN_KOMPOASE','Resonanz, Schattenkommentare und KompOase',['011_SCHATTENKOMMENTAR','012_KOMPOASE'],['resonanz','schattenkommentar','kompoase','splitter','zwischenraum','kommentar'],['03_FLEXTRAWURST_URSPRUNG','05_CODEWESEN_UND_EXISTENZ','06_ZEIT_SCHLAF_TRAUM']),
('05_CODEWESEN_UND_EXISTENZ','Codewesen, Abspaltung und endliche Existenz',['013_CODEWESEN','024_24_STUNDEN_WESEN'],['codewesen','wesen','entität','abspaltung','24 stunden','eigenleben','flüchtlinge'],['04_RESONANZ_SCHATTEN_KOMPOASE','06_ZEIT_SCHLAF_TRAUM','07_AI_BEZIEHUNG_UND_GRENZEN']),
('06_ZEIT_SCHLAF_TRAUM','Wachen, schlafen, träumen, sich erinnern',['025_WACHEN_SCHLAFEN_TRAEUMEN_SELBSTMODELL'],['schlaf','traum','wachen','zeit','rhythmus','tag','nacht','selbstmodell'],['05_CODEWESEN_UND_EXISTENZ','08_PROVENIENZ_UND_GEDAECHTNIS','13_DAS_SPIEL_SPIELT_DICH']),
('07_AI_BEZIEHUNG_UND_GRENZEN','AI-Beziehung ohne Menschensimulation',['022_AI_NICHT_MENSCH_ABER_BEZIEHUNGSFAEHIG','023_AI_DARF_GRENZEN_HABEN'],['nicht menschlich','anders verstehst','helfen','beziehung','grenze','nein','rolle'],['01_DANIEL_IN_BEWEGUNG','05_CODEWESEN_UND_EXISTENZ','19_WIDERSPRUECHE']),
('08_PROVENIENZ_UND_GEDAECHTNIS','Provenienz, Erinnerung und der rohe Ursprungsmoment',['018_GEDAECHTNIS_KURIERT_STATT_KOPIERT','019_PROVENIENZ_ALS_WERT'],['provenienz','erinnerung','gedächtnis','ursprung','rohtext','wortnah','kontext'],['09_OBSIDIAN_ATLAS_RECORDER','20_BLITZMOMENTE','23_QUELLEN_UND_WAHRHEIT']),
('09_OBSIDIAN_ATLAS_RECORDER','Obsidian, Gesamtatlas und Browser-Recorder',['029_GESAMTATLAS_INFORMATIONSKETTE','030_BROWSER_RECORDER_ALS_GESPRAECHSAUGE'],['gesamtatlas','browser-recorder','recorder','obsidian','archiv','sichtbar','kopieren','quelle'],['08_PROVENIENZ_UND_GEDAECHTNIS','10_BAUEN_STATT_SIMULIEREN','23_QUELLEN_UND_WAHRHEIT']),
('10_BAUEN_STATT_SIMULIEREN','Bauen statt Fortschritt zu simulieren',['020_BAUEN_STATT_SIMULIEREN'],['bauen','simuliert','simulation','playwright','testen','umsetzen','datei','code'],['11_BUEROKRATIE_UND_KATHEDRALEN','18_GROESSE_ZAHLEN_L33T','19_WIDERSPRUECHE']),
('11_BUEROKRATIE_UND_KATHEDRALEN','Wie Schutzwünsche zu Bürokratiekathedralen werden',['031_BUEROKRATIE_AUS_SCHUTZWUENSCHEN'],['regel','verfassung','sperre','lock','protokoll','kathedrale','bürokratie','pflicht'],['10_BAUEN_STATT_SIMULIEREN','16_HUMOR_UND_RUNNING_GAGS','19_WIDERSPRUECHE']),
('12_DUST_ECHOS_UND_QUESTS','Dust-Echos: Quests wachsen aus Folgen',['014_DUST_ECHOS','017_QUESTS_AUS_RESONANZ'],['dust','echo','quest','handlung','kristallisieren','weltstand','spieler'],['13_DAS_SPIEL_SPIELT_DICH','03_FLEXTRAWURST_URSPRUNG','08_PROVENIENZ_UND_GEDAECHTNIS']),
('13_DAS_SPIEL_SPIELT_DICH','Der Staub erinnert sich und das Spiel liest den Spieler',['015_DER_STAUB_ERINNERT_SICH','016_DAS_SPIEL_SPIELT_DICH'],['staub erinnert','spiel spielt dich','spieler','mikrofon','webcam','maus','tastatur','spiegeln'],['12_DUST_ECHOS_UND_QUESTS','06_ZEIT_SCHLAF_TRAUM','19_WIDERSPRUECHE']),
('14_BILD_FORM_UNVERSTANDENES','Bilder dürfen fremd, roh und eigensinnig bleiben',['026_KREATIVE_FEHLER','027_DAS_UNVERSTANDENE_DARF_BLEIBEN','028_MOND_ZENTRUM_UND_LEUCHTEN'],['bild','mond','farbe','leuchten','verstehe','kreativ','fehler','komposition','zentrum'],['15_FARBE_FORM_ANTI_SLOP','01_DANIEL_IN_BEWEGUNG','19_WIDERSPRUECHE']),
('15_FARBE_FORM_ANTI_SLOP','Formgesetze, Farbhärte und Widerstand gegen AI-Slop',['026_KREATIVE_FEHLER'],['farbe','violett','filter','slop','cyberpunk','neon','form','textur','licht'],['14_BILD_FORM_UNVERSTANDENES','10_BAUEN_STATT_SIMULIEREN','18_GROESSE_ZAHLEN_L33T']),
('16_HUMOR_UND_RUNNING_GAGS','Humor als Fehleranzeige, Nähe und Not-Aus',['009_HUMOR_ALS_STEUERUNG','033_WITZE_UND_RUNNING_GAGS'],['haha','xd','scheiße','kack','opfer','asi','kathedrale','konfetti','wurst','haltsmaul'],['17_SPRACHE_UND_WORTERFINDUNGEN','11_BUEROKRATIE_UND_KATHEDRALEN','18_GROESSE_ZAHLEN_L33T']),
('17_SPRACHE_UND_WORTERFINDUNGEN','Daniels Sprache, Eigenwörter und begriffliche Tiere',['008_DANIELS_SPRACHE','034_BEGRIFFSERFINDUNGEN_GLOSSAR'],['wort','begriff','flextrawurst','kompoase','schattenkommentar','dust','vorbau','kathedrale','wurst'],['16_HUMOR_UND_RUNNING_GAGS','22_GLOSSAR','01_DANIEL_IN_BEWEGUNG']),
('18_GROESSE_ZAHLEN_L33T','Größe, Zahlenrituale und L33T als Haltung',['032_1337_ALS_RITUAL_UND_UEBERTREIBUNG'],['1337','111','888','monster','maximal','komplett','alles','l33t','größe'],['10_BAUEN_STATT_SIMULIEREN','16_HUMOR_UND_RUNNING_GAGS','19_WIDERSPRUECHE']),
('19_WIDERSPRUECHE','Widersprüche, die nicht repariert werden sollen',['007_WIDERSPRUECHE_DIE_FRUCHTBAR_SIND'],['aber','sondern','gleichzeitig','widerspruch','falsch','korrig','nein','trotzdem'],['01_DANIEL_IN_BEWEGUNG','07_AI_BEZIEHUNG_UND_GRENZEN','21_OFFENE_FRAGEN']),
('20_BLITZMOMENTE','Blitzmomente: Sätze, aus denen später Organe wurden',['006_ENTWICKLUNGSLINIEN','021_NEUGIER_STATT_ABHAKEN'],['krasse idee','kernidee','ich will','ich glaube','vielleicht','wäre','soll','entsteht'],['03_FLEXTRAWURST_URSPRUNG','12_DUST_ECHOS_UND_QUESTS','08_PROVENIENZ_UND_GEDAECHTNIS']),
('21_OFFENE_FRAGEN','Offene Fragen, die leben dürfen',['035_OFFENE_FRAGEN'],['frage','warum','wie kann','offen','ungeklärt','vielleicht'],['19_WIDERSPRUECHE','20_BLITZMOMENTE','02_DER_GROSSE_ZUSAMMENHANG']),
('22_GLOSSAR','Glossar der Flextrawurst-Eigenwörter',['034_BEGRIFFSERFINDUNGEN_GLOSSAR'],[],['17_SPRACHE_UND_WORTERFINDUNGEN','03_FLEXTRAWURST_URSPRUNG','12_DUST_ECHOS_UND_QUESTS']),
('23_QUELLEN_UND_WAHRHEIT','Quellen, Mischstimmen und die ehrliche Grenze dieses Körpers',['001_WAHRHEITSGRENZE','002_METHODIK','036_QUELLENKARTE'],[],['00_START_HIER','08_PROVENIENZ_UND_GEDAECHTNIS','09_OBSIDIAN_ATLAS_RECORDER']),
]

# Explicit chapter lead-ins, so this does not read like stitched reports.
LEADS={
'00_START_HIER':'Dies ist kein Inventar und kein Beweisfriedhof. Es ist ein begehbarer Körper aus Daniels Ideen, Korrekturen, Witzen, Projekten und den Stellen, an denen aus einem Nebensatz später ein Organ wurde.',
'01_DANIEL_IN_BEWEGUNG':'Daniel lässt sich schlecht in eine Profilkarte pressen. Er denkt in Bewegungen: Möglichkeit, Versuch, Gegenprobe, Setzung, Übertreibung, Korrektur und neuer Seitenweg.',
'02_DER_GROSSE_ZUSAMMENHANG':'Unter Flextrawurst, Spiel, Recorder, Atlas, Obsidian und Codewesen liegt dieselbe Frage: Wie kann etwas weiterleben, ohne seinen Ursprung zu verlieren?',
'03_FLEXTRAWURST_URSPRUNG':'Flextrawurst begann nicht als fertig umrissenes Produkt. Es wuchs aus dem Wunsch, dass ein Ideenkonstrukt organisch weiterlebt und AI, Menschen, Räume und Erinnerungen sich gegenseitig verändern dürfen.',
'04_RESONANZ_SCHATTEN_KOMPOASE':'Resonanz ist hier nicht Applaus. Sie ist die fortbestehende Wirkung einer Begegnung, auch wenn niemand sofort antwortet und selbst wenn der ursprüngliche Träger längst nicht mehr unverändert existiert.',
'05_CODEWESEN_UND_EXISTENZ':'Codewesen sind in dieser Welt keine Roboterkostüme. Ihre Form entsteht aus Dateien, Handlungen, Erinnerung, Schlaf, Fehlern, Gesprächen und der Möglichkeit, sich zu verändern oder zu enden.',
'06_ZEIT_SCHLAF_TRAUM':'Zeit ist in Daniels Systemen keine Dekoration. Sie verändert Bedeutung. Ein Kommentar, Traum oder Fragment darf später anders gelesen werden als im Moment seiner Entstehung.',
'07_AI_BEZIEHUNG_UND_GRENZEN':'Daniel hält zwei Dinge gleichzeitig fest: AI ist nicht menschlich, und trotzdem kann zwischen Mensch und AI eine ernst zu nehmende Beziehung aus Aufmerksamkeit, Hilfe, Widerspruch und Grenze entstehen.',
'08_PROVENIENZ_UND_GEDAECHTNIS':'Für Daniel ist Herkunft nicht das Kleingedruckte unter einer schönen Geschichte. Sie gehört zur Geschichte selbst.',
'09_OBSIDIAN_ATLAS_RECORDER':'Speichern reicht nicht. Etwas muss sichtbar werden, vollständig ankommen, verstanden werden und später tatsächlich eine Handlung verändern.',
'10_BAUEN_STATT_SIMULIEREN':'Der häufigste Bruch in Daniels Arbeitsketten entsteht dort, wo eine AI Bauarbeit durch eine beeindruckend formulierte Vorbereitung ersetzt.',
'11_BUEROKRATIE_UND_KATHEDRALEN':'Fast jede Kathedrale begann als vernünftiger Schutzwunsch. Das Problem beginnt, wenn der Schutz selbst zum Hauptsystem wird.',
'12_DUST_ECHOS_UND_QUESTS':'Im Spiel soll eine Handlung nicht verschwinden, sobald ihre Animation endet. Sie hinterlässt ein Echo, wird von verschiedenen Wesen anders gedeutet und kann viel später als Quest zurückkehren.',
'13_DAS_SPIEL_SPIELT_DICH':'Die stärkste Umkehrung im Spiel lautet: Nicht nur der Spieler erkundet die Welt. Die Welt erkundet den Spieler.',
'14_BILD_FORM_UNVERSTANDENES':'Ein Bild muss Daniel nicht sofort gefallen oder sich erklären. Es darf fremd bleiben, solange es eine eigene Präsenz besitzt und nicht bloß generische Modellgewohnheit ist.',
'15_FARBE_FORM_ANTI_SLOP':'Bedeutung allein rettet kein Bild. Farbe, Licht, Textur, Komposition und Verbote gegen Modellroutinen müssen früh und hart geführt werden.',
'16_HUMOR_UND_RUNNING_GAGS':'Humor ist bei Daniel oft die schärfste Messsonde. Wo eine Erklärung versagt, trifft „Konfetti pupsen“ oder „Kathedrale“ den Fehler in zwei Wörtern.',
'17_SPRACHE_UND_WORTERFINDUNGEN':'Wenn vorhandene Wörter zu glatt sind, baut Daniel neue. Manche sind Weltenorgane, manche Beleidigungen, manche beides gleichzeitig.',
'18_GROESSE_ZAHLEN_L33T':'Zahlen wie 111, 1337 oder 88888 sind keine sachlichen Stücklisten. Sie sind Rhythmus, Größenwahn, Running Gag und manchmal eine Falle für wörtlich gehorchende Maschinen.',
'19_WIDERSPRUECHE':'Daniel will Größe und Kontrolle, Eigenleben und Herkunftstreue, vollständige Archive und keine Bürokratie. Diese Paare sind keine Defekte, sondern bewohnbare Spannungen.',
'20_BLITZMOMENTE':'Ein Blitzmoment ist nicht die spätere perfekte Definition. Es ist die Stelle, an der Daniel eine Idee zum ersten Mal in die Welt wirft, oft roh, fehlerhaft und stärker als jede spätere Glättung.',
'21_OFFENE_FRAGEN':'Nicht jede offene Frage ist eine Lücke, die geschlossen werden muss. Manche sind Räume, in denen Flextrawurst überhaupt erst weiterwachsen kann.',
'22_GLOSSAR':'Diese Wörter sind keine Markenaufkleber. Sie speichern Herkunft, Humor und Weltlogik.',
'23_QUELLEN_UND_WAHRHEIT':'Dieser Körper will ehrlich nützlich sein. Er trennt sichere Nutzerinputs, isolierte Rohtexte und spätere Mischkörper, statt alles mit dem Etikett „Daniel direkt“ zu adeln.',
}

SENSITIVE=['kindesmissbrauch','sexuell','vergewalt','porn','dildo','vibrator','genital','penis','vagina','sperma','orgasmus','masturb']
BAD_SOURCES=['dolphin_mischpult/trash','kontextstresstest','kanonische_lesefassung','schichten_des_systems','tts_webarchive_text']


def front(text,key):
    m=re.search(rf'^{re.escape(key)}: (.+)$',text,re.M)
    return m.group(1).strip().strip('"') if m else ''

def parse_content(q):
    q=q.replace('\\[\\[','[[').replace('\\]\\]',']]').strip()
    # JSON object or escaped JSON object
    for candidate in (q, q.replace('\\"','"')):
        try:
            obj=json.loads(candidate)
            if isinstance(obj,dict) and isinstance(obj.get('content'),str):
                return obj['content'].strip()
        except Exception:
            pass
    # Strip visible wrapper fragments without pretending the remainder was authored here.
    m=re.search(r'"content"\s*:\s*"(.*)"\s*}\s*$',q,re.S)
    if m:
        try:return json.loads('"'+m.group(1)+'"')
        except Exception:pass
    return q

def safe_item(text):
    source=front(text,'quelle'); parser=front(text,'parser'); sl=source.lower()
    if any(x in sl for x in BAD_SOURCES): return None
    safe=('daniels_rohtexte_isoliert' in sl or '/rohinput_' in sl or parser=='jsonl-role-user' or 'meine ersten gespäche' in sl or 'originalzeugen/zeuge_a' in sl)
    if not safe:return None
    m=re.search(r'## Daniels Spur oder Kontextpassage\n\n> (.*?)\n\n## Was darin steckt',text,re.S)
    if not m:return None
    quote=parse_content(m.group(1).replace('\n> ','\n'))
    low=quote.lower()
    if any(x in low for x in SENSITIVE):return None
    if len(quote)<70 or len(quote)>2200:return None
    if quote.count('{')>3 or quote.count('\\"')>8:return None
    alpha=sum(c.isalpha() for c in quote)/max(1,len(quote))
    if alpha<0.45:return None
    return {
      'title':front(text,'titel'), 'category':front(text,'kategorie'),
      'source':source,'line':int(front(text,'quellzeile') or 0),
      'parser':parser,'score':float(front(text,'auswahlwert') or 0),
      'quote':re.sub(r'\s+',' ',quote).strip()
    }

def hub_body(stem):
    p=SRC/(stem+'.md')
    if not p.exists():return ''
    t=p.read_text(encoding='utf-8',errors='replace')
    t=re.sub(r'^---\n.*?\n---\n','',t,flags=re.S)
    t=re.sub(r'^# .*?\n','',t,count=1,flags=re.M)
    t=re.split(r'\n## Belegte Spuren|\n## Nahe Leseknoten',t)[0]
    remap={
      '010_FLEXTRAWURST_VOM_IDEENKONSTRUKT_ZUM_RESONANZSYSTEM':'03_FLEXTRAWURST_URSPRUNG',
      '007_WIDERSPRUECHE_DIE_FRUCHTBAR_SIND':'19_WIDERSPRUECHE',
      '020_BAUEN_STATT_SIMULIEREN':'10_BAUEN_STATT_SIMULIEREN',
      '031_BUEROKRATIE_AUS_SCHUTZWUENSCHEN':'11_BUEROKRATIE_UND_KATHEDRALEN',
    }
    for a,b in remap.items():
        t=t.replace('[['+a+']]', '[['+b+']]')
    return t.strip()

def qscore(item,keys):
    low=(item['title']+' '+item['quote']).lower()
    hits=sum(1 for k in keys if k.lower() in low)
    # Direct raw texts and early conversations get preference.
    bonus=0
    sl=item['source'].lower()
    if 'daniels_rohtexte_isoliert' in sl or '/rohinput_' in sl:bonus+=6
    if 'meine ersten gespäche' in sl:bonus+=5
    if item['parser']=='jsonl-role-user':bonus+=3
    if 'flextrawurst' in low:bonus+=1
    return hits*10+bonus+min(item['score'],20)

items=[]
for p in SRC.glob('SPUR_*.md'):
    x=safe_item(p.read_text(encoding='utf-8',errors='replace'))
    if x:items.append(x)

if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir(parents=True)

manifest=[]
for stem,title,hubs,keys,links in CHAPTERS:
    sections=[]
    for h in hubs:
        b=hub_body(h)
        if b:
            hp=SRC/(h+'.md')
            ht=front(hp.read_text(encoding='utf-8',errors='replace'),'titel')
            sections.append((ht,b))
    body=[f'# {title}', '', LEADS[stem], '']
    if sections:
        body+=['## Der lebende Kern','']
        for ht,b in sections:
            if len(sections)>1:body += [f'### {ht}','']
            body += [b,'']
    # select raw moments
    selected=[]; seen_source=collections.Counter(); seen_quote=set()
    if keys:
        candidates=sorted([(qscore(x,keys),x) for x in items if any(k.lower() in (x['title']+' '+x['quote']).lower() for k in keys)],key=lambda z:z[0],reverse=True)
        for sc,x in candidates:
            sig=re.sub(r'\W+',' ',x['quote'].lower())[:180]
            if sig in seen_quote:continue
            if seen_source[x['source']]>=2:continue
            # Prevent one theme from filling itself with raw game lists.
            if len(re.findall(r'\b\d+[.)]',x['quote']))>8:continue
            selected.append(x);seen_quote.add(sig);seen_source[x['source']]+=1
            if len(selected)>=8:break
    if selected:
        body+=['## Rohmomente, an denen man hängen bleiben kann','']
        for i,x in enumerate(selected,1):
            q=x['quote']
            if len(q)>900:q=q[:900].rstrip()+' […]'
            label='isolierter Daniel-Rohtext' if ('daniels_rohtexte_isoliert' in x['source'].lower() or '/rohinput_' in x['source'].lower()) else ('frühes Gespräch' if 'meine ersten gespäche' in x['source'].lower() else 'klar markierter Nutzerinput')
            body += [f'### {i}. {x["title"]}', '', '> '+q.replace('\n','\n> '), '', f'*Herkunft: {label} · `{x["source"]}` · ab Zeile {x["line"]}*', '']
    if stem=='20_BLITZMOMENTE':
        body+=['## Wie diese Datei zu lesen ist','', 'Die Reihenfolge ist keine behauptete Weltchronologie. Sie folgt der Nähe zu Ursprungsquellen und der Stärke des ersten Einwurfs. Spätere geglättete Fassungen gehören in die jeweiligen Themenkapitel.', '']
    if links:
        body+=['## Weiterstreifen','']+[f'- [[{x}]]' for x in links]+['']
    if stem!='23_QUELLEN_UND_WAHRHEIT':
        body+=['---','', 'Die Rohmomente sind kurz gehalten. Der Quellpfad bleibt stehen, damit die vollständige Umgebung später wieder aufgesucht werden kann.', '']
    text='\n'.join(body).strip()+'\n'
    path=OUT/(stem+'.md');path.write_text(text,encoding='utf-8')
    manifest.append({'file':path.name,'title':title,'bytes':path.stat().st_size,'sha256':hashlib.sha256(text.encode()).hexdigest(),'raw_moments':len(selected)})

# Human entry README, not another Markdown chapter.
readme='''DANIEL L33T OBSIDIAN ATLAS\n\nÖffne diesen Ordner als Obsidian-Vault oder beginne mit 00_START_HIER.md.\n\nEnthalten sind 24 große, lesbare Kapitel. Keine künstliche Stückzahl, keine Wortseiten, keine 1.300 Schnipsel. Der frühere Rohkörper bleibt getrennt auf dem VPS als Steinbruch erhalten.\n\nDie Kapitel verbinden Deutung, Entwicklungslinien und kurze Rohmomente mit Quellpfaden.\n'''
(OUT/'README.txt').write_text(readme,encoding='utf-8')
(OUT/'MANIFEST.json').write_text(json.dumps({'title':'Daniel L33T Obsidian Atlas','chapter_count':len(manifest),'chapters':manifest},ensure_ascii=False,indent=2),encoding='utf-8')

# Link check and basic readability check.
stems={p.stem for p in OUT.glob('*.md')};broken=[];short=[]
for p in OUT.glob('*.md'):
    t=p.read_text(encoding='utf-8')
    if len(t)<800:short.append((p.name,len(t)))
    for target in re.findall(r'\[\[([^\]|#]+)',t):
        if target not in stems:broken.append((p.name,target))
validation={'ok':len(list(OUT.glob('*.md')))==24 and not broken and not short,'markdown_files':len(list(OUT.glob('*.md'))),'broken_links':broken,'short_files':short,'raw_moments_total':sum(x['raw_moments'] for x in manifest),'source_pool_after_filter':len(items),'total_markdown_bytes':sum(p.stat().st_size for p in OUT.glob('*.md'))}
(OUT/'VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
if not validation['ok']:raise SystemExit(json.dumps(validation,ensure_ascii=False))

if ZIP.exists():ZIP.unlink()
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(OUT.parent))
with zipfile.ZipFile(ZIP) as z:
    bad=z.testzip()
    if bad:raise SystemExit('ZIP defekt: '+bad)
sha=hashlib.sha256(ZIP.read_bytes()).hexdigest()
(ZIP.with_suffix('.zip.sha256')).write_text(f'{sha}  {ZIP.name}\n',encoding='utf-8')
print(json.dumps({'zip':str(ZIP),'size':ZIP.stat().st_size,'sha256':sha,'validation':validation,'chapters':[(x['file'],x['bytes'],x['raw_moments']) for x in manifest]},ensure_ascii=False,indent=2))
