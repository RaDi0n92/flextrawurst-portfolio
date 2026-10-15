"""Baut den Nachbau. Alle Werte gemessen; Herkunft im Kommentar."""
import base64, os, re, urllib.request

B = "/tmp/apimg2"
def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()
def img(name, cls="", alt=""):
    p = os.path.join(B, name)
    if not os.path.exists(p): return ""
    ext = "png" if name.endswith(".png") else "jpeg"
    return f'<img class="{cls}" alt="{alt}" src="data:image/{ext};base64,{b64(p)}">'

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Helvetica Neue",Arial,sans-serif;
  color:rgb(29,29,31);background:#fff;-webkit-font-smoothing:antialiased}
a{text-decoration:none;color:inherit}
.band{height:44px;background:#fff;position:sticky;top:0;z-index:100}
.band nav{max-width:980px;margin:0 auto;padding:0 24px;height:44px;
  display:flex;align-items:center;justify-content:space-between}
.band a{color:rgba(0,0,0,.8);font-size:12px;letter-spacing:-.01em}
.band a:hover{color:#000}
.band .logo{font-size:15px;color:#000}
section{text-align:center;overflow:hidden}
.h1{font-size:56px;font-weight:600;letter-spacing:-.015em;line-height:1.05}
.h2{font-size:40px;font-weight:600;letter-spacing:-.01em;line-height:1.08}
.sub{font-size:21px;font-weight:400;line-height:1.38;margin-top:6px;color:rgb(51,51,54)}
.klein{font-size:17px;font-weight:400;line-height:1.4}
.fuss{font-size:12px;line-height:1.38;color:rgb(51,51,54)}
sup{font-size:11px}
.cta{margin-top:26px;display:flex;gap:14px;justify-content:center;flex-wrap:wrap}
.pille{display:inline-block;font-size:17px;line-height:1.2;padding:11px 21px;border-radius:980px;white-space:nowrap}
.pille.voll{background:rgb(0,113,227);color:#fff}
.pille.hohl{background:transparent;color:rgb(0,113,227);box-shadow:inset 0 0 0 1px rgb(0,113,227)}

/* Hero 44..735 = 692px, max-width 1068px aus dem Inline-Style */
.hero{background:#000;height:692px;color:#f5f5f7;padding-top:52px;position:relative;overflow:hidden}
.hero .h1{color:#f5f5f7}
.hero .sub{color:#f5f5f7;opacity:.9}
.hero .pille{font-size:17px;padding:12px 22px}
.hero .bild{position:absolute;top:64px;left:50%;transform:translateX(-50%);
  width:3008px;max-width:none;margin:0;display:block;z-index:0}
.hero .h1,.hero .sub,.hero .cta{position:relative;z-index:1}

/* 736..1451 = 716px hell */
.promo{background:#fff;height:716px;padding-top:64px;display:flex;flex-direction:column;align-items:center}
.promo .bild{margin-top:28px;width:1068px;max-width:calc(100% - 48px)}

/* 1452..2143 = 692px dunkel, Text unten */
.watch{background:#000;height:692px;overflow:hidden;color:#f5f5f7;display:flex;flex-direction:column;
  align-items:center;justify-content:flex-end;padding-bottom:88px}
.watch .logo{width:415px;max-width:60%;margin-bottom:20px}
.watch .klein{color:#f5f5f7;opacity:.9}

/* 2156..2735 = 580px dunkel, zwei Bilder 1262x580 nebeneinander */
.spalt{height:12px;background:#fff}
.duo{background:#000;color:#f5f5f7;height:580px;overflow:hidden;display:grid;grid-template-columns:1fr 1fr;
  grid-template-rows:278px 278px;gap:24px;padding:0 24px}
.duo .zelle{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px}
.duo .zelle.oben{justify-content:flex-start;padding-top:96px}
.duo .zelle.unten{justify-content:flex-start;padding-top:78px}
.duo .zelle img{width:100%;max-width:583px}

/* 2736..4328 = 1593px: sechs Kacheln im Raster */
.raster{display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:0 24px;background:#fff;margin-bottom:0}
.kachel{height:581px;background:#f5f5f7;display:flex;flex-direction:column;
  align-items:flex-start;justify-content:flex-start;gap:6px;padding:76px 56px;overflow:hidden}
.kachel .cta{justify-content:flex-start;margin-left:-6px}
.kachel .h3{margin-left:-2px}
.kachel.schwarz{background:#000;color:#f5f5f7}
.kachel .logo{height:49px;width:auto}

.kachel .h3{font-size:28px;font-weight:600;letter-spacing:-.01em}
.kachel .klein{max-width:24ch}
.kachel.schwarz .klein{color:#f5f5f7;opacity:.9}

/* Karussell 4342..4454 */
.gallery{background:#fff;height:523px;padding:0;overflow:hidden;position:relative}
.kar{display:flex;gap:13px;align-items:flex-start;overflow:hidden;padding-left:0;height:522px;
  margin-top:0;margin-left:-688px;width:2834px;flex:0 0 2834px}
.karte:not(.haupt){height:522px}

.karte{flex:0 0 930px;height:522px;overflow:hidden;border-radius:8px;overflow:hidden;position:relative;
  display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-end;padding:22px 26px;
  background:#111;color:#fff;text-align:left}
.karte img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}
.karte>*{position:relative;z-index:1}
.karte .fuss-t{display:flex;align-items:center;gap:14px;margin-top:10px}
.karte .cap{font-size:19px;font-weight:400;text-shadow:0 1px 8px rgba(0,0,0,.5)}
.punkte{position:absolute;left:50%;transform:translateX(-50%);top:362px;display:flex;gap:12px;justify-content:center}
.punkt{width:7px;height:7px;border-radius:50%;background:#8e8e93}
.punkt.aktiv{background:#1d1d1f}
.play{position:absolute;right:8px;top:50%;transform:translateY(-50%);width:34px;height:34px;
  border-radius:50%;background:rgba(0,0,0,.08);display:flex;align-items:center;justify-content:center}
.karte .plak{position:absolute;top:20px;left:26px;line-height:0}
.karte .lg{height:24px;width:auto}
.leiste{position:absolute;left:0;right:0;bottom:0;height:124px;background:rgba(0,0,0,.62);
  display:flex;align-items:center;gap:8px;padding:0 49px;z-index:2}
.leiste .sp{margin-right:12px}
.leiste .sp{background:#fff;color:#000;border-radius:980px;padding:8px 17px;
  font-size:17px;font-weight:400;line-height:1.2;white-space:nowrap}
.leiste .genre{color:#fff;font-size:17px;font-weight:600;white-space:nowrap}
.leiste .trenner{color:#fff;opacity:.75;font-size:17px;margin:0 2px}
.leiste .tx{color:#fff;font-size:17px;font-weight:400;line-height:1.2}

.karte .pille{font-size:12px;padding:7px 15px;margin-top:12px;background:rgba(0,0,0,.45);color:#fff;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.55)}

/* Footer ab 4455: 11 Rubriken + Legal aus ac-globalfooter */
footer{background:#f5f5f7;padding:20px 0 34px;color:rgb(51,51,54);font-size:12px}
.foot{max-width:1024px;margin:0 auto;padding:0 24px}
.klapp{display:flex;justify-content:space-between;padding:11px 0;font-size:12px;
  border-bottom:1px solid rgba(0,0,0,.16)}
.klapp .bf{font-size:10px;color:#6e6e73;background:#1d1d1f;color:#f5f5f7;border-radius:4px;
  padding:1px 5px;margin-left:4px}
.kleintext{font-size:11px;line-height:1.45;color:rgb(51,51,54);padding:10px 0 4px;max-width:none}
.foot-block{max-width:980px}
.kleintext p{margin-bottom:14px}
.kleintext a{color:rgb(0,102,204)}
.rubriken{display:flex;border-top:1px solid rgba(0,0,0,.16);border-bottom:1px solid rgba(0,0,0,.16)}
.rub{padding:10px 0;flex:1;border-right:1px solid rgba(0,0,0,.16)}
.rub:last-child{border-right:0}
.rub h4{font-size:12px;font-weight:600;margin-bottom:5px;color:rgb(29,29,31)}
.rub ul{list-style:none}
.rub li{margin:2px 0;line-height:1.3}
.rub li a{color:rgb(0,102,204)}
.legal{font-size:12px;line-height:1.5;padding-top:14px;color:rgb(51,51,54)}
.legal a{color:rgb(0,102,204)}
.legal .trenner{color:rgba(0,0,0,.56);padding:0 6px}
.brands{display:flex;flex-wrap:wrap;gap:14px;padding:14px 0;font-size:12px}
.brands a{color:rgb(0,102,204)}

@media (max-width:776px){.raster,.duo{grid-template-columns:1fr}}
@media (max-width:734px){.hero,.promo,.watch,.duo{height:auto;padding:40px 0}}
"""

NAV = [("Store",0),("Mac",0),("iPad",0),("iPhone",0),("Watch",0),("Vision",0),
       ("AirPods",0),("TV &amp; Home",0),("Entertainment",0),("Zubehör",0),("Support",0)]

RUBRIKEN = [
 ("Einkaufen und mehr", "Store|Mac|iPad|iPhone|Watch|Vision|AirPods|TV &amp; Home|AirTag|Zubehör|Geschenk&shy;karten"),
 ("Apple Wallet", "Apple&nbsp;Pay|Apple&nbsp;Wallet"),
 ("Account", "Deinen Apple Account verwalten|Apple Store Account|iCloud.com"),
 ("Entertainment", "Apple&nbsp;One|Apple&nbsp;TV|Apple&nbsp;Music|Apple&nbsp;Arcade|Apple&nbsp;Fitness+|Apple Podcasts|Apple&nbsp;Books|App&nbsp;Store"),
 ("Apple Store", "Store finden|Genius Bar|Today at Apple|Gruppen&shy;reservierungen|Apple Sommer Camp|Apple Store App|Zertifiziert Refurbished|Apple&nbsp;Trade&nbsp;In|Finanzierung|Bestellstatus|Einkaufshilfe"),
 ("Für Unternehmen", "Apple und Unternehmen|Für Unternehmen einkaufen"),
 ("Für den Bildungsbereich", "Apple und Bildung|Für Hochschulen einkaufen"),
 ("Für das Gesundheitswesen", "Apple und das Gesundheitswesen"),
 ("Für Behörden", "Apple und Behörden"),
 ("Apple Werte", "Barrierefreiheit|Bildung|Nachhaltigkeit|Datenschutz|Innovationen in der Lieferkette"),
 ("Über Apple", "Newsroom|Apple Leadership Team|Stellenangebote|Garantie|Investor:innen|Ethik und Compliance|Events|Jobs schaffen in Europa|Apple Kontakt"),
]

TITEL = ["Mayday","Slow Horses – Ein Fall für Jackson Lamb","Brothers",
         "Dark Matter – Der Zeitenläufer","Ted Lasso","Lucky","Silo","Widow’s Bay","Last Seen"]

def rubrikken_html():
    out = ['<div class="rubriken">']
    for name, items in RUBRIKEN:
        lis = "".join(f'<li><a href="#">{i}</a></li>' for i in items.split("|"))
        out.append(f'<div class="rub"><h4>{name}</h4><ul>{lis}</ul></div>')
    out.append('</div>')
    return "\n".join(out)

def gallery_html():
    titel = ["Mayday","Slow Horses – Ein Fall für Jackson Lamb","Brothers",
             "Dark Matter – Der Zeitenläufer","Ted Lasso","Lucky","Silo",
             "Widow’s Bay","Last Seen"]
    # genre + tagline je karte, woertlich aus der quelle
    txt = {1: ("Action", "Eine Freundschaft. Zu viele Red Flags."),
           2: ("Thriller", "Das chaotische MI5-Team kehrt zur&uuml;ck."),
           3: ("Comedy", "Freunde. Oder doch Familie?"),
           4: ("Science-Fiction", "Unendliche Welten. Nur ein Zuhause."),
           5: ("", "Ted ist zur&uuml;ck &ndash; und herzlicher denn je."),
           6: ("", "Anya Taylor-Joy ist als Trickbetr&uuml;gerin nach einem Raub&uuml;berfall auf der Flucht."),
           7: ("", "Die Wahrheit liegt in der Vergangenheit."),
           8: ("", "Willkommen auf der Insel! Genie&szlig; deinen Aufenthalt. Stell nur nicht zu viele Fragen."),
           9: ("", "Ein Anruf, der alles &auml;ndert")}
    reihenfolge = [9, 1, 2]
    klassen = ["karte", "karte haupt", "karte"]
    teile = []
    for pos, i in enumerate(reihenfolge):
        pb = f"/tmp/tv3/{i}.jpg"
        if not os.path.exists(pb): continue
        g, b_ = txt.get(i, ("", ""))
        leiste = ('<div class="leiste"><span class="sp">Jetzt streamen</span>'
                  + (f'<span class="genre">{g}</span><span class="trenner">&bull;</span>' if g else '')
                  + f'<span class="tx">{b_}</span></div>') if pos > 0 else ''
        
        teile.append(f'<div class="{klassen[pos]}"><img class="bg" alt="{titel[i-1]}" '
                     f'src="data:image/jpeg;base64,{b64(pb)}">{leiste}</div>')
    punkte = '<div class="punkte">' + ''.join(
        '<span class="punkt' + (' aktiv' if k == 0 else '') + '"></span>' for k in range(9)) + '</div>'
    return punkte + '<div class="kar">' + "".join(teile) + '</div>'

HTML = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Nachbau — gemessen von https://www.apple.com/de/</title><style>{CSS}</style></head><body>

<div class="band"><nav>
<a class="logo" href="#">&#63743;</a>
{"".join(f'<a href="#">{t}</a>' for t, _ in NAV)}
<a href="#">&#9906;</a><a href="#">&#9776;</a>
</nav></div>

<!-- 44..735 = 692px -->
<section class="hero">
<h1 class="h1">iPhone 18 Pro</h1>
<p class="sub">Progressiv.</p>
<div class="cta"><a class="pille voll" href="#">Weitere Infos</a><a class="pille hohl" href="#">Kaufen</a></div>
{img("hero_iphone_18_pro__fqe1motd0ymy_large.jpg","bild","iPhone 18 Pro")}
</section>

<!-- 736..1451 = 716px -->
<section class="promo">
<h2 class="h2">iPhone Duo</h2>
<p class="sub">Hallo, hallo.</p>
<p class="klein">Vorbestellen ab 16.10. um 14&nbsp;Uhr</p>
<p class="klein">Erhältlich ab 23.10.</p>
<div class="cta"><a class="pille voll" href="#">Weitere Infos</a><a class="pille hohl" href="#">Preise ansehen</a></div>
</section>

<!-- 1452..2143 = 692px -->
<section class="watch">
<p class="klein">Die präziseste Herzfrequenzmessung in einem Wearable.<sup>1</sup></p>
<div class="cta"><a class="pille voll" href="#">Weitere Infos</a><a class="pille hohl" href="#">Kaufen</a></div>
</section>

<div class="spalt"></div>
<!-- 2156..2735 = 580px -->
<section class="duo">
<div class="zelle oben"><p class="klein">Batteriebestzeit.</p>
<div class="cta"><a class="pille voll" href="#">Weitere Infos</a><a class="pille hohl" href="#">Kaufen</a></div></div>
<div class="zelle"></div>
<div class="zelle"></div>
<div class="zelle unten"><h3 class="h3">AirPods 5</h3>
<p class="klein">Erlebe die Magie der Aktiven<br>Geräuschunterdrückung.</p>
<div class="cta"><a class="pille voll" href="#">Weitere Infos</a><a class="pille hohl" href="#">Kaufen</a></div></div>
</section>

<!-- 2736..4328 = 1593px, drei Reihen zu 520px -->
<div class="raster" style="margin-top:12px">
<div class="kachel"><p class="klein">Gib deinem iPhone noch mehr Power<br>mit zusätzlichem Speicher, Datenschutz<br>und mehr.<sup>2</sup></p>
<div class="cta"><a class="pille voll" href="#">Weitere Infos</a></div>
</div>
<div class="kachel"><h3 class="h3">MacBook Air</h3>
<p class="klein">Jetzt mit der Power des M5.</p>
<div class="cta"><a class="pille voll" href="#">Weitere Infos</a><a class="pille hohl" href="#">Kaufen</a></div>
</div>
<div class="kachel"><h3 class="h3">Uni, geht klar.</h3>
<p class="klein">Beim Kauf eines Mac oder iPad mit<br>Bildungsrabatt erhältst du eine Geschenk&shy;karte<br>im Wert von 80&nbsp;€ bis 120&nbsp;€.<sup>*</sup></p>
<div class="cta"><a class="pille voll" href="#">Zum Store</a></div>
</div>
<div class="kachel"><p class="klein" style="color:rgb(29,29,31);opacity:1">Gib dein iPhone&nbsp;13 oder neuer<br>für eine Gut&shy;schrift in Zahlung.</p>
<div class="cta"><a class="pille voll" href="#">Eintauschwert schätzen lassen</a></div></div>
</div>

<section class="gallery" style="padding-top:0;height:523px;margin-top:-2px">{gallery_html()}</section>
<div style="height:24px">
</div>



<footer>
<div class="foot">
<div class="klapp"><span>iPhone 18 Pro</span><a href="#">Produktinformationsblatt ansehen (PDF)</a></div>
<div class="kleintext">
<p><b>*</b> Qualifizierte Käufer:innen erhalten beim Kauf eines Qualifizierten MacBooks oder iPads
(jewels „Qualifiziertes Produkt“) in einer Qualifizierten Verkaufsstelle vom 13. August 2026 bis
einschließlich zum 22. Oktober 2026 eine Apple Gift Card. Der Wert der Apple Gift Card ist je
nach Qualifiziertem Produkt verschieden. Qualifizierte Käufer:innen erhalten einen Rabatt in Höhe
des Wertes der Apple Gift Card auf den Preis des Qualifizierten Produkts, alle Artikel in ihrem
Einkaufswagen werden ihnen aber berechnet, einschließlich der Apple Gift Card. Es gilt die
Obergrenze von je einer Apple Gift Card pro Qualifiziertem Produkt und Qualifiziertem:r Käufer:in.
Angebot vorbehaltlich Verfügbarkeit. Solange der Vorrat reicht. Einige Zahlungsarten werden im
Rahmen dieses Angebots nicht akzeptiert. Einzelheiten hierzu erhältst du bei <a href="#">Abschluss
der Bestellung</a>. Die vollständigen Allgemeinen Geschäftsbedingungen findest du <a href="#">hier</a>.</p>
<p>1. Basierend auf Daten aus einer von Apple im Juli und August 2026 durchgeführten Studie zur
Genauigkeit der Herzfrequenzmessung bei den meistverkauften Wearables, die im Juni 2026 im
Handel erhältlich waren. Weitere Infos unter <a href="#">apple.com/HRAccuracy</a>.</p>
<p>2. Weitere Infos zu iCloud Features und Systemanforderungen gibt es unter
<a href="#">support.apple.com/de-de/118308</a>. Einige Funktionen erfordern eine WLAN Verbindung.
Bei einigen Services ist der Zugriff auf 10 Geräte beschränkt. Einige Features sind nicht in allen
Ländern oder Regionen verfügbar.</p>
<p>3. Die Eintauschwerte für die Inzahlungnahme variieren abhängig von Zustand, Alter und
Konfiguration deines qualifizierten Eintauschgeräts sowie vom Land oder der Region, in dem bzw.
der dein qualifiziertes Eintauschgerät ursprünglich verkauft wurde. Das Mindestalter für die
Inzahlungnahme gegen eine Gutschrift oder Zahlung beträgt 18 Jahre. Nicht alle Geräte sind für
eine Gutschrift qualifiziert. Weitere Infos zur Inzahlungnahme von qualifizierten Geräten gibt es
beim <a href="#">Apple Partner für die Inzahlungnahme</a>. Möglicherweise gelten Einschränkungen
und Beschränkungen. Auszahlungen basieren darauf, dass das empfangene Gerät der Beschreibung
entspricht, die zum Zeitpunkt der Anfrage abgegeben wurde. Apple behält sich das Recht vor, ein
Gerät aus jeglichem Grund abzulehnen oder die Anzahl von Geräten einzuschränken. Der Wert des
aktuellen Geräts kann beim Kauf eines neuen Apple Geräts angerechnet werden. Dieses Angebot gibt
es möglicherweise nicht in jedem Apple Store. Die Inzahlungnahme von Desktop-Computern ist derzeit
nur online möglich, und einige Stores haben möglicherweise weitere Anforderungen. Du musst
mindestens 18 Jahre alt sein, um die Möglichkeit der Inzahlungnahme gegen Gutschrift per
Banküberweisung nutzen zu können.</p>
</div>
{rubrikken_html()}
<div class="legal">Copyright &copy; 2026 Apple Inc. Alle Rechte vorbehalten.
<span class="trenner">|</span><a href="#">Datenschutzrichtlinie</a><span class="trenner">|</span>
<a href="#">Verwendung von Cookies</a><span class="trenner">|</span>
<a href="#">Nutzungsbedingungen</a><span class="trenner">|</span><a href="#">Verkauf und Rückerstattung</a>
<span class="trenner">|</span><a href="#">Site-Info</a><span class="trenner">|</span><a href="#">Apple Deutschland</a></div>
</div></footer>
</body></html>"""

open("/root/werkraum/_opencode/apple_nachbau_final.html", "w", encoding="utf-8").write(HTML)
print("geschrieben:", os.path.getsize("/root/werkraum/_opencode/apple_nachbau_final.html"), "bytes")