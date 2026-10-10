import requests,time
from datetime import datetime
import telebot
from config import *
bot=telebot.TeleBot(TELEGRAM_TOKEN)
last={}
print("bot start")
def get_tickers():
 try:
  r=requests.get(GATE_BASE+"/futures/usdt/tickers",timeout=10)
  data=r.json()
  items=[]
  for t in data:
   c=t.get("contract")
   if not c or not c.endswith("_USDT"): continue
   vol=float(t.get("volume_24h_quote") or t.get("volume_24h_settle") or 0)
   if vol<MIN_VOLUME_24H_USDT: continue
   lastp=float(t.get("last") or 0)
   ch=float(t.get("change_percentage") or 0)
   items.append((c,lastp,ch,vol))
  items.sort(key=lambda x:x[3],reverse=True)
  return items[:40]
 except Exception as e:
  print("tickers err",e)
  return []
def growth15(sym):
 try:
  r=requests.get(GATE_BASE+"/futures/usdt/candlesticks",params={"contract":"mark_"+sym,"interval":"5m","limit":4},timeout=6)
  d=r.json()
  if not isinstance(d,list) or len(d)<4: return 0,0
  old=float(d[0]["c"]); now=float(d[-1]["c"])
  if old==0: return 0,now
  return (now-old)/old, now
 except:
  return 0,0
def imbalance(sym):
 try:
  r=requests.get(GATE_BASE+"/futures/usdt/order_book",params={"contract":sym,"limit":20,"interval":"0"},timeout=5)
  d=r.json()
  b=sum(float(x["s"]) for x in d.get("bids",[]))
  a=sum(float(x["s"]) for x in d.get("asks",[]))
  if b+a==0: return 0
  return (b-a)/(b+a)
 except:
  return 0
def scan():
 print(datetime.now().strftime("%H:%M:%S"),"scan start")
 items=get_tickers()
 print("candidates",len(items))
 found=0
 gif="https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
 for i,(sym,lastp,ch,vol) in enumerate(items):
  g,price=growth15(sym)
  if g<GROWTH_15M_THRESHOLD: continue
  imb=imbalance(sym)
  strong=g>=STRONG_GROWTH_THRESHOLD
  sell=imb<=SELL_PRESSURE_THRESHOLD
  if not (strong or (g>=0.08 and sell)): continue
  if time.time()-last.get(sym,0)<COOLDOWN_SECONDS: continue
  last[sym]=time.time()
  found+=1
  volm=vol/1e6
  p,res,sup1,sup2=levels(sym)
  if not p: p=price
  entry=p
  sl=res if res and res>entry else entry*1.03
  tp1=sup1 if sup1 and sup1<entry else entry*0.97
  tp2=sup2 if sup2 and sup2<tp1 else entry*0.94
  text="\U0001F525 <b>SHORT SIGNAL</b> \U0001F525\n\n\U0001F4B0 <b>"+sym+"</b>\n\U0001F4C8 Growth 15m: <b>+"+str(round(g*100,1))+"%</b>\n\U0001F4B5 Price: <code>"+str(round(p,6))+"</code>\n\U0001F4C9 24h: <b>"+str(ch)+"%</b>\n\U0001F4E6 Volume: <b>"+str(round(volm,1))+"M</b>\n\U0001F4DA Imbalance: <b>"+str(round(imb,2))+"</b>\n\n\U0001F4CD Entry: <code>"+str(round(entry,6))+"</code>\n\U0001F6D1 Stop (resistance): <code>"+str(round(sl,6))+"</code>\n\U0001F3AF TP1 (support): <code>"+str(round(tp1,6))+"</code>\n\U0001F3AF TP2 (support): <code>"+str(round(tp2,6))+"</code>\n\n\u26A0 Possible reversal down\n\U0001F517 <a href=\"https://www.gate.io/futures_trade/"+sym+"\">Open chart</a>"
  try:
   bot.send_animation(CHAT_ID, gif, caption=text, parse_mode="HTML")
   print("sent gif",sym)
  except:
   try:
    bot.send_message(CHAT_ID, text, parse_mode="HTML")
    print("sent text",sym)
   except Exception as e:
    print("tg err",e)
  time.sleep(0.2)
 print(datetime.now().strftime("%H:%M:%S"),"scan done, found",found)
while True:
 try:
  scan()
 except Exception as e:
  print("loop err",e)
 time.sleep(SCAN_INTERVAL)
