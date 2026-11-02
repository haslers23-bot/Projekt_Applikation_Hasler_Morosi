import os
import random
import sys

# Schärfe unter Windows: Windows soll das Fenster nicht selbst vergrössern (das macht
# es unscharf). Wir zeichnen stattdessen selbst im Vollbild. Muss vor «import py5» stehen.
if sys.platform.startswith("win"):
    import py5_tools
    py5_tools.add_options("-Dsun.java2d.uiScale=1")

import py5  # noqa: E402


# --- 1. Einstellungen --------------------------------------------------------

BREITE, HOEHE = 1200, 760        # Zeichenfläche; wird auf den Bildschirm skaliert

HINTERGRUND = (214, 226, 240)
WEISS = (255, 255, 255)
TINTE = (36, 40, 52)
GRAU = (110, 118, 132)
LINIE = (200, 213, 229)
PETROL = (28, 96, 108)
BLAU = (38, 80, 170)             # richtiger Graph
ORANGE = (212, 118, 26)          # eigene Lösung
GRUEN = (44, 132, 82)
ROT = (190, 60, 50)
VIOLETT = (126, 76, 160)         # Tipps

# Koordinatensystem von -6 bis 6, eine Einheit = 50 Pixel, Ursprung bei (360 | 410)
KS_X, KS_Y, KS_GROESSE, EINHEIT = 60, 110, 600, 50
PANEL_X = 700                    # rechte Spalte

LERNTIPPS = {
    "q": "q ist der y-Achsenabschnitt: Setze x = 0 ein.",
    "m": "Steigungsdreieck: 1 nach rechts, dann bis zur Geraden. Diese Höhe ist m.",
    "m_vorzeichen": "Fällt die Gerade von links nach rechts, ist m negativ.",
    "nullstelle": "Bei der Nullstelle ist y = 0. Rechne 0 = m·x + q nach x aus.",
    "wertepaare": "Rechne mit einer Wertetabelle genaue Punkte aus, z. B. für x = -2, 0, 2.",
}
STUFEN = {1: "Proportional: y = m·x",
          2: "Linear: y = m·x + q (ganze Zahlen)",
          3: "Linear Profi: auch Kommazahlen"}


# --- 2. Zustand (globale Variablen) ------------------------------------------

skala, rand_x, rand_y = 1, 0, 0  # wie stark und wohin die Zeichenfläche verschoben wird
bildschirm = "login"             # login, menue, einstellungen, aufgabe, auswertung, theorie
zurueck_zu = "menue"

passwoerter = {}
eingabe_name, eingabe_passwort, aktives_feld, meldung = "", "", "name", ""
schueler = ""

modus, stufe, richtung, anzahl = "ueben", 2, "gemischt", 5
aufgabe = None                   # aktuelle Karte (Dictionary)
nummer = 0
ergebnisse = []                  # Resultate der Serie


# --- 3. Hilfsfunktionen ------------------------------------------------------

def zahl(z):
    """2.0 -> «2», 0.5 -> «0,5»"""
    return str(int(z)) if z == int(z) else str(z).replace(".", ",")


def gleichung(m, q):
    """Text wie «y = 2x + 1»"""
    t = "y = " + {1: "", -1: "-"}.get(m, zahl(m)) + "x"
    if q > 0:
        t += " + " + zahl(q)
    if q < 0:
        t += " - " + zahl(-q)
    return t


def zu_pixel(x, y):
    return KS_X + 300 + x * EINHEIT, KS_Y + 300 - y * EINHEIT


def zu_welt(px, py):
    return (px - KS_X - 300) / EINHEIT, (KS_Y + 300 - py) / EINHEIT


def maus():
    """Mausposition auf der Zeichenfläche (Skalierung herausgerechnet)."""
    return (py5.mouse_x - rand_x) / skala, (py5.mouse_y - rand_y) / skala


def maus_ueber(x, y, b, h):
    mx, my = maus()
    return x <= mx <= x + b and y <= my <= y + h


def text(t, x, y, groesse=16, farbe=TINTE, ausrichtung=py5.LEFT):
    py5.fill(*farbe)
    py5.text_size(groesse)
    py5.text_align(ausrichtung, py5.TOP)
    py5.text(t, x, y)


# --- 4. Zeichenfunktionen ----------------------------------------------------

def knopf(beschriftung, x, y, b, h, gewaehlt=False, aktiv=True, groesse=17):
    py5.stroke(*LINIE)
    py5.stroke_weight(1)
    hinter, schrift = WEISS, TINTE
    if not aktiv:
        hinter, schrift = (232, 238, 245), (160, 170, 184)
    elif gewaehlt:
        hinter, schrift = PETROL, WEISS
    elif maus_ueber(x, y, b, h):
        hinter = (241, 246, 252)
    py5.fill(*hinter)
    py5.rect(x, y, b, h, 6)
    py5.fill(*schrift)
    py5.text_size(groesse)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text(beschriftung, x + b / 2, y + h / 2 - 2)


def logo(x, y, s):
    py5.no_stroke()
    py5.fill(*PETROL)
    py5.rect(x, y, s, s, s / 4)
    py5.stroke(*WEISS)
    py5.stroke_weight(s / 11)
    py5.line(x + s * 0.2, y + s * 0.8, x + s * 0.8, y + s * 0.24)
    py5.no_stroke()
    py5.fill(*ORANGE)
    py5.circle(x + s * 0.62, y + s * 0.41, s * 0.2)
    py5.stroke_weight(1)


def kopfzeile(titel):
    py5.no_stroke()
    py5.fill(*WEISS)
    py5.rect(-rand_x / skala, -rand_y / skala, py5.width / skala, 64 + rand_y / skala)
    logo(36, 14, 36)
    text("Funktionsgraphen-Trainer", 84, 20, 20)
    text(titel, 360, 23, 15, GRAU)


def weisse_flaeche(x, y, b, h):
    py5.stroke(*LINIE)
    py5.stroke_weight(1)
    py5.fill(*WEISS)
    py5.rect(x, y, b, h, 8)


def koordinatensystem():
    weisse_flaeche(KS_X - 20, KS_Y - 20, KS_GROESSE + 40, KS_GROESSE + 40)
    py5.stroke(205, 218, 234)
    for i in range(-6, 7):                       # Häuschen
        px, py = zu_pixel(i, i)
        py5.line(px, KS_Y, px, KS_Y + KS_GROESSE)
        py5.line(KS_X, py, KS_X + KS_GROESSE, py)
    py5.stroke(*TINTE)
    py5.stroke_weight(2)
    ox, oy = zu_pixel(0, 0)
    py5.line(KS_X, oy, KS_X + KS_GROESSE, oy)    # x-Achse
    py5.line(ox, KS_Y, ox, KS_Y + KS_GROESSE)    # y-Achse
    py5.stroke_weight(1)
    for i in range(-5, 6):
        if i != 0:
            px, py = zu_pixel(i, i)
            text(str(i), px, oy + 6, 12, GRAU, py5.CENTER)
            text(str(i), ox - 18, py - 8, 12, GRAU, py5.CENTER)


def gerade(m, q, farbe):
    """y = m·x + q als eine einzige Linie, abgeschnitten am Koordinatensystem."""
    py5.clip(KS_X, KS_Y, KS_GROESSE, KS_GROESSE)
    py5.stroke(*farbe)
    py5.stroke_weight(3)
    py5.line(*zu_pixel(-6, -6 * m + q), *zu_pixel(6, 6 * m + q))
    py5.stroke_weight(1)
    py5.no_clip()


def punkt(x, y, farbe, groesse=12):
    py5.no_stroke()
    py5.fill(*farbe)
    py5.circle(*zu_pixel(x, y), groesse)


# --- 5. Aufgaben erstellen und bewerten --------------------------------------

def neue_aufgabe():
    while True:
        if stufe == 1:
            m, q = random.choice([-3, -2, -1, -0.5, 0.5, 1, 2, 3]), 0
        elif stufe == 2:
            m = random.choice([-3, -2, -1, 1, 2, 3])
            q = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        else:
            m = random.choice([-2.5, -2, -1.5, -0.5, 0.5, 1.5, 2, 2.5])
            q = random.choice([-3.5, -2.5, -1.5, -1, 1, 1.5, 2.5, 3.5])
        if abs(q / m) <= 5:                      # Nullstelle muss im Bild liegen
            break
    art = richtung if richtung != "gemischt" else random.choice(["zeichnen", "ablesen"])
    return {"m": m, "q": q, "art": art, "schritt": 1,
            "punkt_q": None, "punkte": [], "nullstelle": None,     # zum Zeichnen
            "wahl_m": 1, "wahl_q": 0, "tipps": 0,                  # zum Ablesen
            "geprueft": False, "start": py5.millis(), "ergebnis": None}


def nahe(a, b):
    return abs(a - b) <= 0.3


def bewerten():
    """Gibt (Punkte, Zeilen, Lerntipp) zurück. Höchstens 4 Punkte pro Karte."""
    a, m, q = aufgabe, aufgabe["m"], aufgabe["q"]
    punkte, zeilen, tipps = 0, [], []
    if a["art"] == "zeichnen":
        if a["punkt_q"] and nahe(a["punkt_q"][0], 0) and nahe(a["punkt_q"][1], q):
            punkte += 1
            zeilen.append("y-Achsenabschnitt richtig (1 P)")
        else:
            zeilen.append("y-Achsenabschnitt falsch, richtig: (0 | " + zahl(q) + ")")
            tipps.append("q")
        gut = sum(1 for x, y in a["punkte"] if nahe(y, m * x + q))
        punkte += gut * 0.4
        zeilen.append(str(gut) + " von 5 Wertepaaren richtig")
        if gut < 5:
            tipps.append("wertepaare")
        if a["nullstelle"] is not None and nahe(a["nullstelle"], -q / m):
            punkte += 1
            zeilen.append("Nullstelle richtig (1 P)")
        else:
            zeilen.append("Nullstelle falsch, richtig: x = " + zahl(round(-q / m, 2)))
            tipps.append("nullstelle")
    else:
        if a["wahl_q"] == q:
            punkte += 2
            zeilen.append("q richtig (2 P)")
        else:
            zeilen.append("q falsch, richtig: q = " + zahl(q))
            tipps.append("q")
        if a["wahl_m"] == m:
            punkte += 2
            zeilen.append("m richtig (2 P)")
        else:
            zeilen.append("m falsch, richtig: m = " + zahl(m))
            tipps.append("m_vorzeichen" if a["wahl_m"] == -m else "m")
        if a["tipps"]:
            punkte = max(0, punkte - a["tipps"] * 0.5)
            zeilen.append(str(a["tipps"]) + " Tipp(s): -" + zahl(a["tipps"] * 0.5) + " P")
    punkte = int(punkte * 2) / 2                     # auf halbe Punkte abrunden
    return punkte, zeilen, (tipps[0] if tipps else None)


def pruefen():
    aufgabe["geprueft"] = True
    aufgabe["ergebnis"] = bewerten()
    punkte, _, tipp = aufgabe["ergebnis"]
    ergebnisse.append({"gleichung": gleichung(aufgabe["m"], aufgabe["q"]),
                       "art": "Gleichung -> Graph" if aufgabe["art"] == "zeichnen"
                       else "Graph -> Gleichung",
                       "punkte": punkte, "tipp": tipp,
                       "zeit": (py5.millis() - aufgabe["start"]) / 1000})


def naechste_karte():
    global aufgabe, nummer, bildschirm
    if nummer >= anzahl:
        bildschirm = "auswertung"
    else:
        nummer += 1
        aufgabe = neue_aufgabe()


def serie_starten():
    global ergebnisse, nummer, bildschirm
    ergebnisse, nummer, bildschirm = [], 0, "aufgabe"
    naechste_karte()


# --- 6. Bildschirme ----------------------------------------------------------

def zeichne_login():
    weisse_flaeche(380, 110, 440, 470)
    logo(568, 140, 64)
    text("Funktionsgraphen-Trainer", 600, 220, 26, TINTE, py5.CENTER)
    for feld, y, inhalt in (("name", 300, eingabe_name),
                            ("passwort", 390, "•" * len(eingabe_passwort))):
        text("Vorname" if feld == "name" else "Passwort", 420, y, 15)
        py5.stroke(*(PETROL if aktives_feld == feld else LINIE))
        py5.fill(*WEISS)
        py5.rect(420, y + 24, 360, 46, 6)
        text(inhalt, 434, y + 36, 18)
    knopf("Anmelden", 420, 490, 360, 50, gewaehlt=True)
    text(meldung, 600, 600, 15, ROT, py5.CENTER)


def zeichne_menue():
    kopfzeile("Angemeldet: " + schueler)
    text("Hallo " + schueler + "!", 60, 110, 32)
    knopf("Üben", 60, 200, 340, 120)
    knopf("Prüfung", 430, 200, 340, 120)
    knopf("Theorie", 800, 200, 340, 120)
    knopf("Abmelden", 1000, 14, 160, 36)


def zeichne_einstellungen():
    kopfzeile("Üben einstellen" if modus == "ueben" else "Prüfung einstellen")
    text("Thema", 60, 100, 22)
    for i in (1, 2, 3):
        knopf(str(i) + "   " + STUFEN[i], 60, 76 + i * 64, 560, 52, stufe == i)
    text("Richtung", 680, 100, 22)
    for i, (wert, name) in enumerate((("zeichnen", "Gleichung -> Graph"),
                                      ("ablesen", "Graph -> Gleichung"),
                                      ("gemischt", "Gemischt"))):
        knopf(name, 680, 140 + i * 64, 460, 52, richtung == wert)
    text("Anzahl Karten", 60, 360, 22)
    for i, n in enumerate((5, 10, 15)):
        knopf(str(n), 60 + i * 120, 400, 100, 52, anzahl == n)
    knopf("Start", 680, 400, 460, 60, True)
    knopf("Zurück", 1000, 14, 160, 36)


def zeichne_aufgabe():
    a = aufgabe
    kopfzeile(("Übung" if modus == "ueben" else "Prüfung") +
              ", Karte " + str(nummer) + " von " + str(anzahl))
    knopf("Theorie", 830, 14, 150, 36)
    knopf("Zum Menü", 1000, 14, 160, 36)
    koordinatensystem()
    weisse_flaeche(PANEL_X, 90, 460, 640)
    if a["art"] == "zeichnen":
        zeichne_zeichnen(a)
    else:
        zeichne_ablesen(a)
    if a["geprueft"]:
        zeichne_rueckmeldung(a)
        knopf("Zur Auswertung" if nummer >= anzahl else "Nächste Karte",
              PANEL_X + 30, 650, 400, 54, True)
    else:
        bereit = a["art"] == "ablesen" or len(a["punkte"]) == 5
        knopf("Prüfen" if modus == "ueben" else "Abgeben", PANEL_X + 30, 650, 400, 54,
              bereit, bereit)


def zeichne_zeichnen(a):
    text("Zeichne den Graphen zu", PANEL_X + 30, 110, 15, GRAU)
    text(gleichung(a["m"], a["q"]), PANEL_X + 30, 132, 34)
    liste = sorted(a["punkte"])                     # mit dem Lineal verbinden
    py5.stroke(*ORANGE)
    py5.stroke_weight(3)
    for p1, p2 in zip(liste, liste[1:]):
        py5.line(*zu_pixel(*p1), *zu_pixel(*p2))
    py5.stroke_weight(1)
    for x, y in liste:
        punkt(x, y, ORANGE)
    if a["punkt_q"]:
        punkt(*a["punkt_q"], ORANGE, 16)
    if a["nullstelle"] is not None:
        punkt(a["nullstelle"], 0, ORANGE, 16)
    if a["geprueft"]:
        if modus == "ueben":
            gerade(a["m"], a["q"], BLAU)
        return
    schritte = ["1  y-Achsenabschnitt anklicken",
                "2  Fünf Wertepaare anklicken (" + str(len(a["punkte"])) + " von 5)",
                "3  Nullstelle auf der x-Achse anklicken"]
    for i, s in enumerate(schritte):
        text(s, PANEL_X + 30, 210 + i * 40, 17, TINTE if a["schritt"] == i + 1 else GRAU)
    if a["schritt"] < 3:
        knopf("Weiter", PANEL_X + 30, 350, 400, 44)
    knopf("Alles löschen", PANEL_X + 30, 410, 400, 44)


def zeichne_ablesen(a):
    text("Welche Gleichung gehört zum Graphen?", PANEL_X + 30, 110, 15, GRAU)
    text(gleichung(a["wahl_m"], a["wahl_q"]), PANEL_X + 30, 132, 34, ORANGE)
    gerade(a["m"], a["q"], BLAU)
    if a["geprueft"]:
        if modus == "ueben":
            gerade(a["wahl_m"], a["wahl_q"], ORANGE)
        return
    for i, (name, wert) in enumerate((("m", a["wahl_m"]), ("q", a["wahl_q"]))):
        y = 220 + i * 70
        text(name + " =", PANEL_X + 30, y + 10, 24)
        knopf("-", PANEL_X + 100, y, 50, 50, groesse=28)
        text(zahl(wert), PANEL_X + 205, y + 10, 24, TINTE, py5.CENTER)
        knopf("+", PANEL_X + 260, y, 50, 50, groesse=28)
    knopf("Tipp (-0,5 P)", PANEL_X + 30, 380, 400, 44, aktiv=a["tipps"] < 2)
    if a["tipps"] >= 1:                              # Tipp 1: q markieren
        punkt(0, a["q"], VIOLETT, 16)
        text("q ist dort, wo die Gerade die y-Achse schneidet.", PANEL_X + 30, 440, 15)
    if a["tipps"] >= 2:                              # Tipp 2: Steigungsdreieck
        py5.stroke(*VIOLETT)
        py5.stroke_weight(3)
        py5.line(*zu_pixel(0, a["q"]), *zu_pixel(1, a["q"]))
        py5.line(*zu_pixel(1, a["q"]), *zu_pixel(1, a["q"] + a["m"]))
        py5.stroke_weight(1)
        text("1 nach rechts, dann bis zur Geraden: das ist m.", PANEL_X + 30, 466, 15)


def zeichne_rueckmeldung(a):
    if modus == "pruefung":
        return
    punkte, zeilen, tipp = a["ergebnis"]
    text("Super!" if punkte >= 3.5 else "Teilweise richtig", PANEL_X + 30, 210, 22)
    text(zahl(punkte) + " / 4 P", PANEL_X + 430, 210, 22, GRUEN if punkte >= 3.5 else ORANGE,
         py5.RIGHT)
    for i, z in enumerate(zeilen):
        text("• " + z, PANEL_X + 30, 260 + i * 30, 15)
    if tipp:
        py5.no_stroke()
        py5.fill(224, 238, 238)
        py5.rect(PANEL_X + 30, 400, 400, 110, 6)
        text("Lerntipp", PANEL_X + 46, 412, 16, PETROL)
        py5.fill(*TINTE)
        py5.text(LERNTIPPS[tipp], PANEL_X + 46, 440, 370, 70)    # Text mit Umbruch


def zeichne_auswertung():
    kopfzeile("Auswertung")
    text("Deine Karten", 60, 90, 26)
    for i, r in enumerate(ergebnisse):
        y = 140 + i * 38
        text(str(i + 1) + ".", 60, y, 16, GRAU)
        text(r["art"], 100, y, 15, GRAU)
        text(r["gleichung"], 290, y, 18)
        text(zahl(r["punkte"]) + " P", 520, y, 18, GRUEN if r["punkte"] >= 3.5 else ROT)
        if modus == "pruefung":
            text(str(round(r["zeit"])) + " s", 600, y, 15, GRAU)
    total = sum(r["punkte"] for r in ergebnisse)
    weisse_flaeche(PANEL_X, 90, 460, 640)
    text(str(round(25 * total / len(ergebnisse))) + " %", PANEL_X + 230, 130, 60, PETROL,
         py5.CENTER)
    text(zahl(total) + " von " + str(4 * len(ergebnisse)) + " Punkten", PANEL_X + 230, 220, 20,
         TINTE, py5.CENTER)
    tipps = [r["tipp"] for r in ergebnisse if r["tipp"]]
    if tipps:
        text("Das solltest du noch üben:", PANEL_X + 30, 320, 17)
        py5.text(LERNTIPPS[max(set(tipps), key=tipps.count)], PANEL_X + 30, 352, 400, 100)
    knopf("Nochmals", PANEL_X + 30, 560, 190, 54, True)
    knopf("Zum Menü", PANEL_X + 240, 560, 190, 54)


def zeichne_theorie():
    kopfzeile("Theorie")
    knopf("Zurück", 1000, 14, 160, 36)
    text("Lineare Funktion   y = m·x + q", 60, 90, 28, PETROL)
    for i, (titel, inhalt) in enumerate((
            ("y-Achsenabschnitt q", "Dort schneidet die Gerade die y-Achse, im Punkt (0 | q)."),
            ("Steigung m", "Gehe 1 nach rechts, dann m nach oben (m negativ: nach unten)."),
            ("Wertepaare", "x einsetzen, y ausrechnen. Beispiel y = 2x + 1: x = 7 ergibt y = 15."),
            ("Nullstelle", "Dort ist y = 0. Aus 0 = m·x + q folgt x = -q : m."),
            ("Proportional", "Bei y = m·x ist q = 0: Die Gerade geht durch den Ursprung."))):
        text(titel, 60, 150 + i * 100, 19)
        text(inhalt, 60, 180 + i * 100, 16, GRAU)


# --- 7. py5: Start, Zeichnen, Maus, Tastatur ---------------------------------

def settings():
    py5.full_screen()                                # ganzer Bildschirm
    py5.pixel_density(py5.display_density())         # Mac Retina
    py5.smooth(8)                                    # Kanten glätten


def setup():
    global skala, rand_x, rand_y
    # Zeichenfläche so gross wie möglich und in die Mitte
    skala = min(py5.width / BREITE, py5.height / HOEHE)
    rand_x, rand_y = (py5.width - BREITE * skala) / 2, (py5.height - HOEHE * skala) / 2
    py5.text_font(py5.create_font("SansSerif", 32))
    ordner = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(ordner, "passwoerter.txt"), encoding="utf-8") as datei:
        for zeile in datei:
            if ";" in zeile and not zeile.startswith("#"):
                name, passwort = zeile.strip().split(";")
                passwoerter[name.lower()] = passwort


def scharf_zeichnen():
    """Schräge Linien ohne Treppchen: Java soll Linien nicht auf Pixel runden."""
    try:
        from jpype import JClass
        hinweise = JClass("java.awt.RenderingHints")
        g2 = py5.get_current_sketch()._instance.g.g2
        g2.setRenderingHint(hinweise.KEY_STROKE_CONTROL, hinweise.VALUE_STROKE_PURE)
        g2.setRenderingHint(hinweise.KEY_TEXT_ANTIALIASING, hinweise.VALUE_TEXT_ANTIALIAS_ON)
    except Exception:
        pass                        # falls es nicht klappt, einfach normal zeichnen


def draw():
    scharf_zeichnen()
    py5.background(*HINTERGRUND)
    py5.translate(rand_x, rand_y)
    py5.scale(skala)
    {"login": zeichne_login, "menue": zeichne_menue, "einstellungen": zeichne_einstellungen,
     "aufgabe": zeichne_aufgabe, "auswertung": zeichne_auswertung,
     "theorie": zeichne_theorie}[bildschirm]()


def key_pressed():
    global eingabe_name, eingabe_passwort, aktives_feld
    if bildschirm != "login":
        return
    if py5.key == py5.TAB or (py5.key in (py5.ENTER, py5.RETURN) and aktives_feld == "name"):
        aktives_feld = "passwort" if aktives_feld == "name" else "name"
    elif py5.key in (py5.ENTER, py5.RETURN):
        anmelden()
    elif py5.key == py5.BACKSPACE:
        if aktives_feld == "name":
            eingabe_name = eingabe_name[:-1]
        else:
            eingabe_passwort = eingabe_passwort[:-1]
    elif isinstance(py5.key, str) and py5.key.isprintable():
        if aktives_feld == "name":
            eingabe_name += py5.key
        else:
            eingabe_passwort += py5.key


def anmelden():
    global bildschirm, schueler, meldung, eingabe_passwort
    if passwoerter.get(eingabe_name.strip().lower()) == eingabe_passwort:
        schueler, bildschirm, meldung = eingabe_name.strip().capitalize(), "menue", ""
    else:
        meldung, eingabe_passwort = "Vorname oder Passwort stimmt nicht.", ""


def mouse_pressed():
    global bildschirm, aktives_feld, modus, stufe, richtung, anzahl, zurueck_zu
    if bildschirm == "login":
        if maus_ueber(420, 324, 360, 46):
            aktives_feld = "name"
        elif maus_ueber(420, 414, 360, 46):
            aktives_feld = "passwort"
        elif maus_ueber(420, 490, 360, 50):
            anmelden()

    elif bildschirm == "menue":
        if maus_ueber(60, 200, 340, 120):
            modus, bildschirm = "ueben", "einstellungen"
        elif maus_ueber(430, 200, 340, 120):
            modus, bildschirm = "pruefung", "einstellungen"
        elif maus_ueber(800, 200, 340, 120):
            zurueck_zu, bildschirm = "menue", "theorie"
        elif maus_ueber(1000, 14, 160, 36):
            bildschirm = "login"

    elif bildschirm == "einstellungen":
        for i in (1, 2, 3):
            if maus_ueber(60, 76 + i * 64, 560, 52):
                stufe = i
        for i, wert in enumerate(("zeichnen", "ablesen", "gemischt")):
            if maus_ueber(680, 140 + i * 64, 460, 52):
                richtung = wert
        for i, n in enumerate((5, 10, 15)):
            if maus_ueber(60 + i * 120, 400, 100, 52):
                anzahl = n
        if maus_ueber(680, 400, 460, 60):
            serie_starten()
        elif maus_ueber(1000, 14, 160, 36):
            bildschirm = "menue"

    elif bildschirm == "aufgabe":
        klick_aufgabe()

    elif bildschirm == "auswertung":
        if maus_ueber(PANEL_X + 30, 560, 190, 54):
            serie_starten()
        elif maus_ueber(PANEL_X + 240, 560, 190, 54):
            bildschirm = "menue"

    elif bildschirm == "theorie" and maus_ueber(1000, 14, 160, 36):
        bildschirm = zurueck_zu


def klick_aufgabe():
    global bildschirm, zurueck_zu
    a = aufgabe
    if maus_ueber(830, 14, 150, 36):
        zurueck_zu, bildschirm = "aufgabe", "theorie"
    elif maus_ueber(1000, 14, 160, 36):
        bildschirm = "menue"
    elif maus_ueber(PANEL_X + 30, 650, 400, 54):            # Prüfen / Nächste Karte
        if a["geprueft"]:
            naechste_karte()
        elif a["art"] == "ablesen" or len(a["punkte"]) == 5:
            pruefen()
            if modus == "pruefung":
                naechste_karte()
    elif a["geprueft"]:
        return
    elif a["art"] == "zeichnen":
        klick_zeichnen(a)
    else:
        klick_ablesen(a)


def klick_zeichnen(a):
    if a["schritt"] < 3 and maus_ueber(PANEL_X + 30, 350, 400, 44):
        a["schritt"] += 1
    elif maus_ueber(PANEL_X + 30, 410, 400, 44):
        a["punkt_q"], a["punkte"], a["nullstelle"], a["schritt"] = None, [], None, 1
    elif maus_ueber(KS_X, KS_Y, KS_GROESSE, KS_GROESSE):
        x, y = zu_welt(*maus())
        x, y = round(x * 2) / 2, round(y * 2) / 2          # auf halbe Einheiten einrasten
        if a["schritt"] == 1:
            a["punkt_q"] = (x, y)
        elif a["schritt"] == 2:
            if (x, y) in a["punkte"]:
                a["punkte"].remove((x, y))                  # nochmals klicken = entfernen
            elif len(a["punkte"]) < 5:
                a["punkte"].append((x, y))
                if len(a["punkte"]) == 5:
                    a["schritt"] = 3
        else:
            a["nullstelle"] = x


def klick_ablesen(a):
    m_werte = [-3, -2.5, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 2.5, 3]
    i = m_werte.index(a["wahl_m"])
    if maus_ueber(PANEL_X + 100, 220, 50, 50):
        a["wahl_m"] = m_werte[max(0, i - 1)]
    elif maus_ueber(PANEL_X + 260, 220, 50, 50):
        a["wahl_m"] = m_werte[min(len(m_werte) - 1, i + 1)]
    elif maus_ueber(PANEL_X + 100, 290, 50, 50):
        a["wahl_q"] = max(-4, a["wahl_q"] - 0.5)
    elif maus_ueber(PANEL_X + 260, 290, 50, 50):
        a["wahl_q"] = min(4, a["wahl_q"] + 0.5)
    elif maus_ueber(PANEL_X + 30, 380, 400, 44) and a["tipps"] < 2:
        a["tipps"] += 1


if __name__ == "__main__":
    py5.run_sketch()
