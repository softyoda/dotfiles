#!/usr/bin/env python3
"""Follow ES-DE's native scraper and start the media pass after metadata completes."""
import datetime,json,os,re,subprocess,time,unicodedata,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ES=Path.home()/'ES-DE'
APP=Path.home()/'Applications/ES-DE_x64_9c3c993e2ed359ee249f0377143b8b80.AppImage'
REPORT=ROOT/'esde-scrape-status.json'
OCR='/tmp/esde-ocr';SHOT='/tmp/esde-scrape-monitor.png'
state={'started':datetime.datetime.now().isoformat(),'phase':'metadata','status':'running'}
def run(*args):return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()
def save(**kw):
 state.update(kw);state['updated']=datetime.datetime.now().isoformat()
 tmp=REPORT.with_suffix('.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2));tmp.replace(REPORT)
def window():
 for w in run('xdotool','search','--name','ES-DE').splitlines():
  try:
   pid=run('xdotool','getwindowpid',w)
   if Path('/proc',pid,'comm').read_text().strip()=='es-de':return w
  except Exception:pass
 raise RuntimeError('ES-DE window closed; monitoring stopped')
def read(w):
 run('import','-window',w,SHOT)
 s=run('tesseract',SHOT,'stdout','--tessdata-dir',OCR,'-l','fra')
 return ''.join(c for c in unicodedata.normalize('NFKD',s.upper()) if not unicodedata.combining(c))
def keys(w,*seq):run('xdotool','key','--window',w,'--delay','350',*seq);time.sleep(1)
def expect(w,phrase):
 text=read(w)
 if phrase not in text:raise RuntimeError('Unexpected ES-DE screen: '+text)
def counts():
 n=0
 for p in (ES/'gamelists').glob('*/gamelist.xml'):
  try:n+=sum(bool(g.findtext('desc')) and g.findtext('hidden')!='true' for g in ET.parse(p).getroot().findall('game'))
  except ET.ParseError:pass
 return n
def media_pass(w):
 keys(w,'Return','alt+F4');time.sleep(5)
 p=ES/'settings/es_settings.xml';s=p.read_text()
 # Add only missing media; retain the existing RetroArch artwork links.
 for k in ['Scrape3DBoxes','ScrapeBackCovers','ScrapeCovers','ScrapeFanArt','ScrapeManuals','ScrapeMarquees','ScrapePhysicalMedia','ScrapeScreenshots','ScrapeTitleScreens','ScrapeVideos','MiximageGenerate']:
  s=re.sub('(<bool name="'+k+'" value=")[^"]*',lambda m:m[1]+'true',s)
 p.write_text(s)
 with open(ROOT/'esde-media-console.log','a') as log:
  subprocess.Popen([str(APP),'--no-update-check','--resolution','1280','720'],env=dict(os.environ,SDL_VIDEODRIVER='x11'),stdout=log,stderr=log,start_new_session=True)
 time.sleep(20);w=window()
 keys(w,'Escape');expect(w,'MENU PRINCIPAL')
 keys(w,'Return');expect(w,'SCRAPEUR')
 keys(w,'Down','Down','Return');expect(w,'SCRAPER CES SYSTEMES')
 keys(w,'End','Down','Right','Return','BackSpace');expect(w,'21 SELECTIONNE')
 keys(w,'Insert');save(phase='media',metadata_finished=datetime.datetime.now().isoformat())
 return w
try:
 w=window();last_progress=time.monotonic();last_text=''
 while True:
  s=read(w)
  m=re.search(r'JEU\s+(\d+)\s+SUR\s+(\d+)',s)
  api=re.search(r'APPELS API:\s*(\d+)\s*/\s*(\d+)',s)
  if m:state.update(current_game=int(m[1]),total_games=int(m[2]))
  if api:state.update(api_calls=int(api[1]),api_limit=int(api[2]))
  if s!=last_text:last_progress=time.monotonic();last_text=s
  save(descriptions_saved=counts(),screen=s)
  if 'SCRAPES AVEC SUCCES' in s:
   if state['phase']=='metadata':w=media_pass(w);last_progress=time.monotonic();last_text='';continue
   save(status='complete',finished=datetime.datetime.now().isoformat());break
  if ('ERREUR' in s or 'QUOTA' in s or 'LIMITE' in s) and 'SCRAPING EN COURS' not in s:
   save(status='needs_attention',reason='Service error or quota; left ES-DE open for review');break
  if time.monotonic()-last_progress>600:
   save(status='needs_attention',reason='Screen unchanged for 10 minutes; no automatic retry');break
  time.sleep(30)
except Exception as e:save(status='needs_attention',reason=str(e))
