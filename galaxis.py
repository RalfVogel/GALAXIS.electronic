#!/usr/bin/python3

###############################
#  GALAXIS electronic V4.7    #
#  von Daniel Luginbuehl      #
#        (C) 2022             #
# webmaster@ltspiceusers.ch   #
#                             #
#        Serveradresse        #
#    galaxis.game-host.org    #
###############################


from __future__ import print_function
import os, sys, time, configparser, hashlib, subprocess
from time import sleep


# config.ini lesen
config = configparser.ConfigParser()
config.read("config.ini")
nick = config.get("DEFAULT", "nick")
language = config.get("DEFAULT", "language")
HOST_ADDR = config.get("DEFAULT", "hostaddr")
HOST_PORT = int(config.get("DEFAULT", "hostport"))

winexe = 0
if sys.argv[0].endswith("galaxis.exe") == True:
    winexe = 1
if sys.argv[0].endswith("galaxis") == True:
    winexe = 2

install = 0
restarted = False

# Import-Versuche

if winexe == 0:

    def InstallFrage(wert):
        if install > 0:
            if language == "de":
                print("Ich kann versuchen, die fehlenden Pakete automatisch zu installieren.")
                print("q = Abbruch, o = Ok, automatisch installieren")
            else:
                print("I can try to install the missing packages automatically.")
                print("q = Abort, o = Ok, install automatically")
            antwort = input('[q/o]: ')
            if antwort == "q":
                return 2

            try:
                subprocess.check_call([sys.executable, '-m', 'pip', '-V'])
            except:
                print()
                if language == "de":
                    print("python3-pip ist nicht installiert!")
                else:
                    print("python3-pip is not installed!")
                print()
                print("Debian/Ubuntu/Mint:    sudo apt install python3-pip")
                print("CentOS/Red Hat/Fedora: sudo dnf install --assumeyes python3-pip")
                print("MacOS:                 sudo easy_install pip")
                print("Windows:               https://www.geeksforgeeks.org/how-to-install-pip-on-windows/")
                print()

                if language == "de":
                    print("Fenster schliesst in 20 Sekunden.")
                else:
                    print("Window closes in 20 seconds.")

                sleep(20)
                return 2

            if wert-4 > -1:
                wert-=4
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'colorama'])
                print("colorama is installed / ist installiert")

            if wert-2 > -1:
                wert-=2
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PodSixNet'])
                print("PodSixNet is installed / ist installiert")

            if wert-1 > -1:
                wert-=1
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
                print("Pygame is installed / ist installiert")

            return 1
        else:
            return 0

    try:
        import pygame
    except ImportError as e:
        install+=1
        if language == "de":
            print("pygame ist nicht installiert!")
        else:
            print("pygame is not installed!")

    try:
        import PodSixNet
    except ImportError as e:
        install+=2
        if language == "de":
            print("PodSixNet ist nicht installiert!")
        else:
            print("PodSixNet is not installed!")

    try:
        import colorama
    except ImportError as e:
        install+=4
        if language == "de":
            print("colorama ist nicht installiert!")
        else:
            print("colorama is not installed!")

    antwort = InstallFrage(install)
    if antwort == 2:
        sys.exit()
        quit()
    if antwort == 1:
        if language == "de":
            print("Ich starte neu!")
        else:
            print("I'm restarting!")
        time.sleep(2)
        sys.stdout.flush()
        os.system('"' + sys.argv[0] + '"')
        sys.exit()
        quit()
else:
    import pygame
    import PodSixNet
    import colorama

# Importieren der Bibliotheken

import pygame as pg
import random, math, json, threading, socket
from pygame.locals import *
pygame.init()
from pygame import mixer
from sys import stdin, exit
from colorama import Fore
from colorama import Style
colorama.init()
print()

# Zeichensatz initialisieren
pygame.font.init()
font = pygame.font.SysFont(None, 27)
font2 = pygame.font.SysFont(None, 21)

# Pfad zu mp3 und jpg holen

if winexe == 0:
    pfad = os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep
else:
    pfad = "data" + os.sep  # Bei Windows-exe

#### Definitionen ####

# Korrekturfaktor berechnen
def kor(zahl):
    zahl = zahl * MULTIPLIKATOR
    return zahl

# Punkt zeichnen
def element_zeichnen(spalte,reihe,farbe):
    pygame.draw.ellipse(fenster, farbe, [kor(spalte)*4+2*MULTIPLIKATOR, kor(reihe)*4+2*MULTIPLIKATOR,kor(1),kor(1)], 0)

# Wert im Punkt zeichnen
def element_wert(spalte,reihe,wert):
    img = font.render(str(wert), True, SCHWARZ)
    fenster.blit(img, ([kor(spalte)*4+2.25*MULTIPLIKATOR, kor(reihe)*4+2.05*MULTIPLIKATOR]))

# Spielzüge zeichnen
def spielzuge(wert):
    if language == "de":
        stand = "Spielzüge: " + str(wert)
    else:
        stand = "  Moves:      " + str(wert)
    imag = font.render(stand, True, BLAU)
    pygame.draw.rect(fenster, SCHWARZ, [kor(4.53)*4+2.66*MULTIPLIKATOR, kor(5.46)*4+2.17*MULTIPLIKATOR,kor(1.4),kor(1)], 0)
    fenster.blit(imag, ([kor(3.4)*4+2.25*MULTIPLIKATOR, kor(5.5)*4+2.05*MULTIPLIKATOR]))

# Spiel gewonnen
def gewonnen():
    if language == "de":
        imag = font.render("Spiel gewonnen :)", True, ROT)
    else:
        imag = font.render("Won the game :)", True, ROT)
    fenster.blit(imag, ([kor(2.0)*6+2.25*MULTIPLIKATOR, kor(3.5)*4+2.05*MULTIPLIKATOR]))

def gewonnen_offline():
    if language == "de":
        imag = font.render("Spiel gewonnen. ESC zum Verlassen.", True, ROT)
    else:
        imag = font.render("    Won the game. ESC to exit.", True, ROT)
    fenster.blit(imag, ([kor(2.0)*4+2.25*MULTIPLIKATOR, kor(3.5)*4+2.05*MULTIPLIKATOR]))

# Spiel verloren
def verloren(gegner_name):
    if language == "de":
        imag = font.render("Spiel verloren :(", True, ROT)
        fenster.blit(imag, ([kor(2.0)*6+2.25*MULTIPLIKATOR, kor(3.5)*4+2.05*MULTIPLIKATOR]))
        print("Gegner hat gewonnen!!!")
        #time.sleep(6.7)
        info = "Dein Gegner " + gegner_name + " hat gewonnen."
    else:
        imag = font.render("Lost the game :(", True, ROT)
        fenster.blit(imag, ([kor(2.0)*6+2.25*MULTIPLIKATOR, kor(3.5)*4+2.05*MULTIPLIKATOR]))
        print("Opponent won!!!")
        #time.sleep(6.7)
        info = "Your opponent " + gegner_name + " won."
    userinfo(info)
    pygame.display.flip()
    mixer.music.load(pfad + "gewonnen.mp3")
    mixer.music.play()

# Ja/Nein zeichnen
def ja_nein_zeichnen(grund):            # 0 noch eine Runde, 1 auto Update
    if language == "de":
        if grund == 0:
            imag = font.render("Möchtest Du noch eine Runde spielen?", True, ROT)
            fenster.blit(imag, ([kor(9.9), kor(20.05)]))
        else:
            imag = font.render("Neue Version verfügbar. Soll ich automatisch updaten?", True, ROT)
            fenster.blit(imag, ([kor(6.0), kor(20.05)]))
        pygame.draw.ellipse(fenster, GELB, [kor(3)*4+MULTIPLIKATOR, kor(5.5)*4+MULTIPLIKATOR,kor(3),kor(3)], 0)
        pygame.draw.ellipse(fenster, GELB, [kor(5)*4+MULTIPLIKATOR, kor(5.5)*4+MULTIPLIKATOR,kor(3),kor(3)], 0)
        img = font.render(str("Ja"), True, SCHWARZ)
        fenster.blit(img, ([kor(3)*4+2.00*MULTIPLIKATOR, kor(5.5)*4+2.05*MULTIPLIKATOR]))
        img = font.render(str("Nein"), True, SCHWARZ)
        fenster.blit(img, ([kor(5)*4+1.50*MULTIPLIKATOR, kor(5.5)*4+2.05*MULTIPLIKATOR]))
    else:
        if grund == 0:
            imag = font.render("Would you like to play another round?", True, ROT)
            fenster.blit(imag, ([kor(9.9), kor(20.05)]))
        else:
            imag = font.render("New version available. Should I update automatically?", True, ROT)
            fenster.blit(imag, ([kor(6.0), kor(20.05)]))
        pygame.draw.ellipse(fenster, GELB, [kor(3)*4+MULTIPLIKATOR, kor(5.5)*4+MULTIPLIKATOR,kor(3),kor(3)], 0)
        pygame.draw.ellipse(fenster, GELB, [kor(5)*4+MULTIPLIKATOR, kor(5.5)*4+MULTIPLIKATOR,kor(3),kor(3)], 0)
        img = font.render(str("Yes"), True, SCHWARZ)
        fenster.blit(img, ([kor(3)*4+1.75*MULTIPLIKATOR, kor(5.5)*4+2.05*MULTIPLIKATOR]))
        img = font.render(str("No"), True, SCHWARZ)
        fenster.blit(img, ([kor(5)*4+2.00*MULTIPLIKATOR, kor(5.5)*4+2.05*MULTIPLIKATOR]))


# Raumschiff zeichnen
def raumschiff_zeichnen(spalte,reihe,farbe):
    pygame.draw.ellipse(fenster, farbe, [kor(spalte)*4+1.5*MULTIPLIKATOR, kor(reihe)*4+1.5*MULTIPLIKATOR,kor(2),kor(2)], 0)

# Anfrage auswerten > return 5 = Raumschiff gefunden
def ping(spalte, reihe):
    mixer.music.load(pfad + "suchen.mp3")
    mixer.music.play()
    time.sleep(3.6)
    n = 0
    if galaxis[reihe][spalte] == 5:
        if gefunden == 3:
            return 5
        mixer.music.load(pfad + "gefunden.mp3")
        mixer.music.play()
        time.sleep(3.5)
        return 5
    # x-
    x = spalte
    while x > 0:
        x = x - 1
        if galaxis[reihe][x] == 5:
            n = n + 1
            break
    # x+
    x = spalte
    while x < 8:
        x = x + 1
        if galaxis[reihe][x] == 5:
            n = n + 1
            break
    # y-
    y = reihe
    while y > 0:
        y = y - 1
        if galaxis[y][spalte] == 5:
            n = n + 1
            break
    # y+
    y = reihe
    while y < 6:
        y = y + 1
        if galaxis[y][spalte] == 5:
            n = n + 1
            break
    # x- y-
    x = spalte
    y = reihe
    while x > 0 and y > 0:
        x = x - 1
        y = y - 1
        if galaxis[y][x] == 5:
            n = n + 1
            break
    # x+ y+
    x = spalte
    y = reihe
    while x < 8 and y < 6:
        x = x + 1
        y = y + 1
        if galaxis[y][x] == 5:
            n = n + 1
            break
    # x+ y-
    x = spalte
    y = reihe
    while x < 8 and y > 0:
        x = x + 1
        y = y - 1
        if galaxis[y][x] == 5:
            n = n + 1
            break
    # x- y+
    x = spalte
    y = reihe
    while x > 0 and y < 6:
        x = x - 1
        y = y + 1
        if galaxis[y][x] == 5:
            n = n + 1
            break
    if n==1:
        mixer.music.load(pfad + "1beep.mp3")
        mixer.music.play()
        time.sleep(0.8)
    if n==2:
        mixer.music.load(pfad + "2beep.mp3")
        mixer.music.play()
        time.sleep(1.4)
    if n==3:
        mixer.music.load(pfad + "3beep.mp3")
        mixer.music.play()
        time.sleep(2.7)
    if n==4:
        mixer.music.load(pfad + "4beep.mp3")
        mixer.music.play()
        time.sleep(2.7)
    if n==0:
        mixer.music.load(pfad + "0beep.mp3")
        mixer.music.play()
        time.sleep(2.0)
    galaxis[reihe][spalte] = n
    return n

# Mauszeiger-Position berechnen
def fensterposition(x,y):
    x = abs((x - 0.6 * MULTIPLIKATOR)/(4 * MULTIPLIKATOR))
    y = abs((y - 0.6 * MULTIPLIKATOR)/(4 * MULTIPLIKATOR))
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x > 8:
        x = 8
    if y > 6:
        y = 6
    return x, y

def spielfeld_zeichnen():
    # Hintergrundbild holen
    bg = pygame.image.load(pfad + "space5.jpg")

    # Hintergrundfarbe/Bild Fenster
    fenster.fill(SCHWARZ)
    fenster.blit(bg, (0, 0))

    # X Koordinaten zeichnen 1-9
    for x in range(0,9):
        img = font.render(str(x+1), True, WEISS)
        fenster.blit(img, (kor(x)*4+2.3*MULTIPLIKATOR, 12))

    # Y Koordinaten zeichnen A-G
    Ybuchstaben='GFEDCBA'
    for x in range(0,7):
        img = font.render(Ybuchstaben[x], True, WEISS)
        fenster.blit(img, (12, kor(x)*4+2.1*MULTIPLIKATOR))

    # Zeichnen der Punkte im Spielfenster
    for x in range(0,9):
        for y in range(0,7):
            element_zeichnen(x,y,GRAU)

# Offline oder Netzwerk Spiel und/oder Neu gestartet?


class InputBox:

    def __init__(self, x, y, w, h, text=""):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        if language == "de":
            self.beschreibung1 = FONT2.render("Für online Spiel, gib Deinen Nicknamen ein (mind 3 Buchstaben)", True, ROT)
            self.beschreibung2 = FONT2.render("Für offline Spiel, gib ENTER ein", True, ROT)
        else:
            self.beschreibung1 = FONT2.render("For online game, enter your nickname (at least 3 letters)", True, ROT)
            self.beschreibung2 = FONT2.render("For offline play, type ENTER", True, ROT)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                nickname = self.text
                return nickname
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            # Re-render the text.
            self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)

        screen.blit(self.beschreibung1, (25, 5))
        screen.blit(self.beschreibung2, (25, 31))


# genutzte Farben
GELB    = ( 255, 255,   0)
SCHWARZ = (   0,   0,   0)
GRAU    = ( 192, 192, 192)
ROT     = ( 255,   0,   0)
WEISS   = ( 255, 255, 255)
BLAU    = (  51, 255, 255)


try:
    nick = sys.argv[1]
except IndexError:
    pass

nick = nick.replace(" ", "")

if nick == "-":
    if len(nick) < 3:
        pg.init()
        screen = pg.display.set_mode((640, 150))
        if language == "de":
            pygame.display.set_caption("GALAXIS Spielmodus")
        else:
            pygame.display.set_caption("GALAXIS game mode")
        COLOR_INACTIVE = pg.Color('lightskyblue3')
        COLOR_ACTIVE = pg.Color('dodgerblue2')
        FONT = pg.font.Font(None, 32)
        FONT2 = pg.font.Font(None, 27)
        pygame.display.flip()
        clock = pg.time.Clock()
        input_box = InputBox(220, 100, 140, 32)
        done = False

        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done = True
                nickname = input_box.handle_event(event)
                if nickname != "-" and nickname != None:
                    nickname = nickname.replace(" ", "")
                    if len(nickname) > 2:
                        spielmodus = 2
                        done = True
                    else:
                        spielmodus = 1
                        done = True
            input_box.update()
            screen.fill((30, 30, 30))
            input_box.draw(screen)
            pg.display.flip()
            clock.tick(30)
    else:
        nickname = nick
        spielmodus = int(config.get("DEFAULT", "spielmodus"))

else:
    nickname = nick
    if len(nickname) > 2:
        spielmodus = 2
    else:
        spielmodus = 1

# Sound initialisieren
mixer.init()
mixer.music.set_volume(0.7)

# Multiplikator
MULTIPLIKATOR = 20


# Bildschirm Aktualisierungen einstellen
clock = pygame.time.Clock()
pygame.key.set_repeat(10,0)


# Spielfeld Vorgabewerte: 0-4 Rückgabewerte , 5 = Raumschiff , 6 = noch nicht angepeilt
galaxis=[
[6,6,6,6,6,6,6,6,6],
[6,6,6,6,6,6,6,6,6],
[6,6,6,6,6,6,6,6,6],
[6,6,6,6,6,6,6,6,6],
[6,6,6,6,6,6,6,6,6],
[6,6,6,6,6,6,6,6,6],
[6,6,6,6,6,6,6,6,6],
]

# Spielfeld: 1 = wenn bereits angepeilt , 0 = noch nicht angepeilt , 2 = schwarz markiert
angepeilt=[
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0],
]

if spielmodus == 1:

    # Spielfeld erzeugen über Berechnung
    fenster = pygame.display.set_mode((36 * MULTIPLIKATOR, 28 * MULTIPLIKATOR))

    # Titel für Fensterkopf
    if language == "de":
        pygame.display.set_caption("GALAXIS electronic   (ESC zum verlassen)")
    else:
        pygame.display.set_caption("GALAXIS electronic   (ESC to exit)")

    # Raumschiffe zufällig verstecken
    n=0
    while n<4:
        x = random.randint(0, 8)
        y = random.randint(0, 6)
        if galaxis[y][x] == 6:
            galaxis[y][x] = 5
            n=n+1

    spielfeld_zeichnen()

    gefunden = 0
    spielzuege = 0
    alarm = 0
    spielaktiv = True

    # Schleife Hauptprogramm
    while spielaktiv:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                spielaktiv = False
                #print("Spieler hat beendet")
                break


            if event.type == QUIT:
                pygame.quit()
                break
            elif event.type == MOUSEBUTTONDOWN:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]
                xpos, ypos = fensterposition(x,y)
                xpos = int(xpos)
                ypos = int(ypos)
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0] and angepeilt[ypos][xpos]==0:
                    element_zeichnen(xpos,ypos,SCHWARZ)
                    angepeilt[ypos][xpos] = 2
                elif mouse_presses[0] and angepeilt[ypos][xpos]==2:
                    element_zeichnen(xpos,ypos,GRAU)
                    angepeilt[ypos][xpos] = 0
                if mouse_presses[2] and angepeilt[ypos][xpos]==0:
                    spielzuege = spielzuege + 1
                    spielzuge(spielzuege)
                    wert = ping(xpos,ypos)
                    angepeilt[ypos][xpos] = 1
                    if wert==5:
                        raumschiff_zeichnen(xpos,ypos,ROT)
                        gefunden = gefunden + 1
                    else:
                        element_zeichnen(xpos,ypos,GELB)
                        element_wert(xpos,ypos,wert)

        # Fenster aktualisieren
        pygame.display.flip()

        # Refresh-Zeit festlegen
        clock.tick(100)

        if gefunden == 4 and alarm==0:
            alarm = 1
            gewonnen_offline()
            pygame.display.flip()
            #print("Spiel gewonnen mit", spielzuege, "Spielzügen.")
            mixer.music.load(pfad + "gewonnen.mp3")
            mixer.music.play()
            time.sleep(6.7)

    pygame.quit()
    sys.exit()


#### Netzwerk Spiel

from PodSixNet.Connection import connection, ConnectionListener

# Anfrage auswerten

def netping(self, spalte, reihe, gefunden):   # Anfrage auswerten > return 5 = Raumschiff gefunden
    spalte = int(spalte)
    reihe = int(reihe)
    gefunden = int(gefunden)

    n = 0
    if self.galaxis[reihe][spalte] == 5:
        return 5
    # x-
    x = spalte
    while x > 0:
        x = x - 1
        if self.galaxis[reihe][x] == 5:
            n = n + 1
            break
    # x+
    x = spalte
    while x < 8:
        x = x + 1
        if self.galaxis[reihe][x] == 5:
            n = n + 1
            break
    # y-
    y = reihe
    while y > 0:
        y = y - 1
        if self.galaxis[y][spalte] == 5:
            n = n + 1
            break
    # y+
    y = reihe
    while y < 6:
        y = y + 1
        if self.galaxis[y][spalte] == 5:
            n = n + 1
            break
    # x- y-
    x = spalte
    y = reihe
    while x > 0 and y > 0:
        x = x - 1
        y = y - 1
        if self.galaxis[y][x] == 5:
            n = n + 1
            break
    # x+ y+
    x = spalte
    y = reihe
    while x < 8 and y < 6:
        x = x + 1
        y = y + 1
        if self.galaxis[y][x] == 5:
            n = n + 1
            break
    # x+ y-
    x = spalte
    y = reihe
    while x < 8 and y > 0:
        x = x + 1
        y = y - 1
        if self.galaxis[y][x] == 5:
            n = n + 1
            break
    # x- y+
    x = spalte
    y = reihe
    while x > 0 and y < 6:
        x = x - 1
        y = y + 1
        if self.galaxis[y][x] == 5:
            n = n + 1
            break

    return n

def sounds(n):
    if n==1:
        mixer.music.load(pfad + "1beep.mp3")
        mixer.music.play()
        #time.sleep(0.8)
    if n==2:
        mixer.music.load(pfad + "2beep.mp3")
        mixer.music.play()
        #time.sleep(1.4)
    if n==3:
        mixer.music.load(pfad + "3beep.mp3")
        mixer.music.play()
        #time.sleep(2.7)
    if n==4:
        mixer.music.load(pfad + "4beep.mp3")
        mixer.music.play()
        #time.sleep(2.7)
    if n==0:
        mixer.music.load(pfad + "0beep.mp3")
        mixer.music.play()
        #time.sleep(2.0)
    #self.angepeilt[reihe][spalte] = 2

def sound_verraten():
    mixer.music.load(pfad + "verraten.mp3")
    mixer.music.play()
    #time.sleep(6.6)

def sound_suchen():
    mixer.music.load(pfad + "suchen.mp3")
    mixer.music.play()
    #time.sleep(3.4)

def sound_gefunden():
    mixer.music.load(pfad + "gefunden.mp3")
    mixer.music.play()
    #time.sleep(3.5)

def sound_gewonnen():
    mixer.music.load(pfad + "gewonnen.mp3")
    mixer.music.play()

def sound_message():
    mixer.music.load(pfad + "message.mp3")
    mixer.music.play()
    #time.sleep(0.75)

def userinfo(info):
    farbe = BLAU
    string = str(info)
    if string.startswith("Noch 6 Sekunden") or string.startswith("6 seconds left"):
        farbe = ROT
        if language == "en":
            string = "6 seconds left"
    imag = font.render(string, True, farbe)
    pygame.draw.rect(fenster, SCHWARZ, [kor(2.5), kor(29.13),kor(60),kor(1.4)], 0)
    fenster.blit(imag, ([kor(2.6), kor(29.376)]))
    pygame.display.flip()

def md5(file1):
    md5h = hashlib.md5()
    with open(file1, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5h.update(chunk)
    return md5h.hexdigest()

def userinfotext(verfugbar, besetzt):
    farbe = BLAU
    verfugbar = ",".join(verfugbar)
    besetzt = ",".join(besetzt)
    if language == "de":
        verf = font2.render("Verfügbare Spieler: " + verfugbar, True, farbe)
        bese = font2.render("Besetzte Spieler: " + besetzt, True, farbe)
    else:
        verf = font2.render("Available players: " + verfugbar, True, farbe)
        bese = font2.render("Occupied players: " + besetzt, True, farbe)
    if verfugbar != "-":
        pygame.draw.rect(fenster, SCHWARZ, [kor(2.5), kor(30.7),kor(34),kor(1.2)], 0)
        fenster.blit(verf, ([kor(2.6)*1, kor(5.74)*5.4]))
    if besetzt != "-":
        pygame.draw.rect(fenster, SCHWARZ, [kor(2.5), kor(31.822),kor(34),kor(1.2)], 0)
        fenster.blit(bese, ([kor(2.6)*1, kor(5.92)*5.4]))

    pygame.display.flip()


##### Das Spiel

class GalaxisGame(ConnectionListener):

##### Warn-Timer #####

    def timer_starten(self):
        if threading.active_count() < 3 and self.spielaktiv == True:
            self.timer = threading.Timer(54.0, self.timer54)
            self.timer.daemon = True
            self.timer.start()


    def timer_stoppen(self):
        try:
            if self.timer.is_alive() == True:
                self.timer.cancel()
                self.umschalt_warnung = False
        except:
            pass

    def timer54(self):
        self.timer_stoppen()
        self.timer = threading.Timer(6.0, self.timer6)
        self.timer.daemon = True
        if self.timer.is_alive() == False and self.spielaktiv == True:
            self.timer.start()
            # Hier Warnung auf Bildschirm
            self.umschalt_warnung = True
            if language == "de":
                print("noch 6 Sekunden!!!")
            else:
                print("6 seconds left!!!")

    def timer6(self):        # Hier self.turn auf false setzen und an Gegner senden
        self.turn = False
        self.umschalt_warnung = False
        self.ping_remote(0, 0, 8, self.num, self.gameid)

##### Version abfragen

    def Updater(self):
        pygame.quit()
        my_os=sys.platform
        #          my_os=
        #`win32`   for Windows(Win32)
        #'cygwin'  for Windows(cygwin)
        #'darwin'  for macOS
        #'aix'     for AIX
        if my_os == "win32":
            os.system("updater.bat")
        if my_os == "linux":
            os.system(os.getcwd()+"/updater.sh")
        if my_os == "darwin":
            os.system(os.getcwd()+"/updater.sh")
        sys.exit()

    def Network_version(self, data):
        version = data["version"]
        version = int(float(version) * 10)/10
        if version > self.version:
            print(Fore.RED + "Server Version:", version, "/ Client Version:", self.version)
            if language == "de":
                print("Bitte neue Spielversion verwenden." + Style.RESET_ALL)
                print("Download bei")
                print(Fore.BLUE + Style.BRIGHT + "https://www.ltspiceusers.ch/threads/galaxis-electronic-1980-von-ravensburger-python3-spiel.989" + Style.RESET_ALL)
                print("oder")
                print(Fore.BLUE + Style.BRIGHT + "https://github.com/ltspicer/GALAXIS.electronic" + Style.RESET_ALL)
                print("oder")
                print(Fore.BLUE + Style.BRIGHT + "https://ltspicer.itch.io/galaxis-electronic" + Style.RESET_ALL)
                print(" ")
                print("Soll ich automatisch updaten (j/n)?")
            else:
                print("Please use new game version." + Style.RESET_ALL)
                print("Download at")
                print(Fore.BLUE + Style.BRIGHT + "https://www.ltspiceusers.ch/threads/galaxis-electronic-1980-von-ravensburger-python3-spiel.989" + Style.RESET_ALL)
                print("or")
                print(Fore.BLUE + Style.BRIGHT + "https://github.com/ltspicer/GALAXIS.electronic" + Style.RESET_ALL)
                print("or")
                print(Fore.BLUE + Style.BRIGHT + "https://ltspicer.itch.io/galaxis-electronic" + Style.RESET_ALL)
                print(" ")
                print("Should I update automatically (y/n)?")
            connection.Close()
            ja_nein_zeichnen(1)
            antwort_jn = "-"
            while antwort_jn == "-":
                for event in pygame.event.get():
                    pygame.display.flip()
                    if event.type == MOUSEBUTTONDOWN:
                        x = pygame.mouse.get_pos()[0]
                        y = pygame.mouse.get_pos()[1]
                        xpos, ypos = fensterposition(x,y)
                        xpos = int(xpos)
                        ypos = int(ypos)
                        mouse_presses = pygame.mouse.get_pressed()
                        if (mouse_presses[2] or mouse_presses[0]) and xpos == 3 and (ypos == 5 or ypos == 6):
                            antwort_jn = "j"
                            break
                        if (mouse_presses[2] or mouse_presses[0]) and xpos == 5 and (ypos == 5 or ypos == 6):
                            antwort_jn = "n"
                            break
            if antwort_jn == "j":
                self.Updater()
            pygame.quit()
            sys.exit()

        if winexe == 0:
            checksumme = md5("galaxis.py")
        if winexe == 1:
            checksumme = md5("galaxis.exe")
        if winexe == 2:
            checksumme = md5("galaxis")
        self.Send({"action": "checksumme", "summe": checksumme, "gameid": self.gameid, "userid": self.userid})


##### Diverses für PodSixNet

    def Network_checksum(self, data):
        status=data["status"]
        if status == False:
            if language == "de":
                print(Fore.RED + "Der Quellcode wurde verändert. Bitte aktuelle Version runterladen!" + Style.RESET_ALL)
                print("Download bei")
                print(Fore.BLUE + Style.BRIGHT + "https://www.ltspiceusers.ch/threads/galaxis-electronic-1980-von-ravensburger-python3-spiel.989" + Style.RESET_ALL)
                print("oder")
                print(Fore.BLUE + Style.BRIGHT + "https://github.com/ltspicer/GALAXIS.electronic" + Style.RESET_ALL)
                print("oder")
                print(Fore.BLUE + Style.BRIGHT + "https://ltspicer.itch.io/galaxis-electronic" + Style.RESET_ALL)
                print(" ")
                print("Soll ich sie automatisch holen (j/n)?")
            else:
                print(Fore.RED + "The source code was modified manually. Please download current version!" + Style.RESET_ALL)
                print("Download at")
                print(Fore.BLUE + Style.BRIGHT + "https://www.ltspiceusers.ch/threads/galaxis-electronic-1980-von-ravensburger-python3-spiel.989" + Style.RESET_ALL)
                print("or")
                print(Fore.BLUE + Style.BRIGHT + "https://github.com/ltspicer/GALAXIS.electronic" + Style.RESET_ALL)
                print("or")
                print(Fore.BLUE + Style.BRIGHT + "https://ltspicer.itch.io/galaxis-electronic" + Style.RESET_ALL)
                print(" ")
                print("Should I fetch them automatically (y/n)?")
            connection.Close()
            ja_nein_zeichnen(1)
            antwort_jn = "-"
            while antwort_jn == "-":
                for event in pygame.event.get():
                    pygame.display.flip()
                    if event.type == MOUSEBUTTONDOWN:
                        x = pygame.mouse.get_pos()[0]
                        y = pygame.mouse.get_pos()[1]
                        xpos, ypos = fensterposition(x,y)
                        xpos = int(xpos)
                        ypos = int(ypos)
                        mouse_presses = pygame.mouse.get_pressed()
                        if (mouse_presses[2] or mouse_presses[0]) and xpos == 3 and (ypos == 5 or ypos == 6):
                            antwort_jn = "j"
                            break
                        if (mouse_presses[2] or mouse_presses[0]) and xpos == 5 and (ypos == 5 or ypos == 6):
                            antwort_jn = "n"
                            break
            if antwort_jn == "j":
                self.Updater()
            pygame.quit()
            sys.exit()

    def Network_close(self, data):
        if language == "de":
            info = "Dein Gegner ist aus dem Netzwerk verschwunden. Bitte neu starten."
        else:
            info = "Your opponent has disappeared from the network. Please restart."
        userinfo(info)
        self.timer_stoppen()
        time.sleep(1)
#        exit()
        self.spielaktiv = False
        self.spiel_fertig = False

    def Network_players(self, data):
        string = [p for p in data['players'] if p != self.mein_name and p != "-"]
        if self.old_string != string:
            userinfotext(string, "-")
            if language == "de":
                print("Verfügbare Spieler: " + Fore.BLUE + Style.BRIGHT + ", ".join(string if len(string) > 0 else ["keine"])  + Style.RESET_ALL)
            else:
                print("Available players: " + Fore.BLUE + Style.BRIGHT + ", ".join(string if len(string) > 0 else ["none"])  + Style.RESET_ALL)
            self.old_string = string
            if self.running == False:
                sound_message()

    def Network_busyplayers(self, data):
        string = [p for p in data['players'] if p != "-"]
        if self.old_string2 != string:
            userinfotext("-", string)
            if language == "de":
                print("Besetzte Spieler: " + Fore.BLUE + Style.BRIGHT + ", ".join(string if len(string) > 0 else ["keine"])  + Style.RESET_ALL)
            else:
                print("Occupied players: " + Fore.BLUE + Style.BRIGHT + ", ".join(string if len(string) > 0 else ["none"])  + Style.RESET_ALL)
            self.old_string2 = string
            if self.running == False:
                sound_message()

    def Network_message(self, data):
        print(Fore.BLUE + Style.BRIGHT + data['who'] + ": " + data['message']  + Style.RESET_ALL)
        pygame.display.flip()
        if self.running == False:
            sound_message()
        if data["message"].startswith("Dein gewählter Gegner ist noch nicht bereit!") and data["who"] == self.mein_name:
            self.gegner_verbunden = False

    def Network_error(self, data):
        print('Fehler/error:', data['error'][1])
        connection.Close()

    def Network_connected(self, data):
        if language == "de":
            print("Du bist nun mit dem Server verbunden")
        else:
            print("You are now connected to the server")
        print()
    
    def Network_disconnected(self, data):
        if language == "de":
            print(Fore.RED + 'Sorry. Server nicht verbunden.' + Style.RESET_ALL)
            exit()
        else:
            print(Fore.RED + 'Sorry server not connected.' + Style.RESET_ALL)
            exit()

    def Network_num_gameid(self, data):
        #print("type data:", type(data))
        users = data["users"]
        self.num=data["player"]
        self.gameid=data["gameid"]
        self.userid=data["userid"]
        self.gegner=data["nickgegner"]
        self.gegner_bereit = data["bereit"]
        if self.mein_name == "robot" or self.mein_name == "roboteasy":
            if language == "de":
                print(Fore.RED + "Dieser Nickname ist nicht erlaubt!" + Style.RESET_ALL)
            else:
                print(Fore.RED + "This nickname is not allowed!" + Style.RESET_ALL)
            time.sleep(8)
            pygame.display.quit()
            pygame.quit()
            sys.exit()
            quit()

        if len(list(filter(lambda x: self.mein_name in x, users))) > 0 and users != "-" and self.restarted == False:
            if language == "de":
                print(Fore.RED + "Dein gewählter Nickname ist bereits vergeben!" + Style.RESET_ALL)
                self.mein_name = self.mein_name + str(self.userid)
                print(Fore.RED + "Dein neuer Nickname ist", self.mein_name + Style.RESET_ALL)
            else:
                print(Fore.RED + "Your chosen nickname is already taken!" + Style.RESET_ALL)
                self.mein_name = self.mein_name + str(self.userid)
                print(Fore.RED + "Your new nickname is", self.mein_name + Style.RESET_ALL)

        restarted = False
        if self.gegner_bereit == True and self.spielerbereit == True:
            self.spielaktiv = True
            self.running = True
        if self.num == 0:
            self.turn = True
        else:
            self.turn = False
        if self.gegner_bereit == True:
            print("Gameid:", self.gameid, ", Userid:", self.userid)
            if language == "de":
                print("Spieler 0 beginnt. Du bist Spieler", self.num)
            else:
                print("Player 0 begins. You are player", self.num)

        connection.Send({"action": "nickname", "nickname": self.mein_name, "num": self.num, "gameid": self.gameid, "userid": self.userid})

    def Network_startgame(self, data):
        anzahl_spieler=data["players"]
        gameid=data["gameid"]
        bereit=data["bereit"]
        num=data["num"]
        gegnerbereit = False

#        if language == "de":
#            print("Anzahl Spieler empfangen:", anzahl_spieler, "| Spieler:", num, "| Bereit?", bereit, "| Gegner bereit?", gegnerbereit, "| Spieler bereit?", self.spielerbereit)
#        else:
#            print("Number of players received:", anzahl_spieler, "| Player:", num, "| Ready?", bereit, "| Opponent ready?", gegnerbereit, "| Player ready?", self.spielerbereit)

        if anzahl_spieler == 2 and gameid == self.gameid and self.spielerbereit == True:
            self.spielaktiv = True
            self.running = True
            if self.num != 0:
                self.turn = False
                self.ping_remote(0, 0, 8, self.num, self.gameid)   # Sag dem Gegner, dass er am Zug ist.
            if language == "de":
                print("Mein Name:", self.mein_name, "Gegner:", self.gegner)
            else:
                print("My name:", self.mein_name, "Opponent:", self.gegner)

##### Spielbezogene Funktionen

    def raumschiff_loeschen(self):
        spielfeld_zeichnen()
        for ypos in range(7):
            for xpos in range(9):
                if self.galaxis[ypos][xpos] == 5:
                    raumschiff_zeichnen(xpos,ypos,WEISS)

    def wer_ist_am_zug(self):
        if self.turn==True:
            if language == "de":
                info = self.mein_name + ", Du bist am Zug. Dein Gegner: " + str(self.gegner)
            else:
                info = self.mein_name + ", It's your turn. Your opponent: " + str(self.gegner)
        else:
            if language == "de":
                info = self.mein_name + ", dein Gegner " + str(self.gegner) + " ist am Zug"
            else:
                info = self.mein_name + ", it's your opponent's turn (" + str(self.gegner) + ")"

        userinfo(info)

        if self.turn == True and self.spielzuege > 0:
            self.timer_starten()

    def mein_name_retour(self):
        return self.mein_name

    def ping_remote(self, xpos, ypos, wert, num, gameid):
        if self.galaxis[ypos][xpos] == 5:
            self.verraten = True
            raumschiff_zeichnen(xpos,ypos,SCHWARZ)
        else:
            self.verraten = False
        self.Send({"action": "antwort", "xpos": xpos, "ypos": ypos, "verraten": self.verraten, "num": num, "gameid": gameid, "gefunden": self.gefunden, "wert": wert})

    def Network_antwort(self, data):
        xpos = data["xpos"]
        ypos = data["ypos"]
        verraten = data["verraten"]
        num = data["num"]
        wert = data["wert"]
        gefunden = data["gefunden"]
        gameid = data["gameid"]

        if num != self.num and wert == 8:  #### Gegner sagt, dass Du am Zug bist
            self.turn = True
            return

        if num != self.num and wert == 7:  #### Gegner sagt, unternimm nichts
            return

        if num != self.num and wert == 6:  #### Anfrage von Gegner
            gesehn = netping(self, xpos, ypos, gefunden)
            
            self.angepeilt[ypos][xpos] = 1
            if galaxis[ypos][xpos] == 6:
                element_zeichnen(xpos,ypos,SCHWARZ)
                self.turn = True
            if gesehn == 5:
                gefunden+=1
                self.turn = False
                raumschiff_zeichnen(xpos,ypos,SCHWARZ)  # Raumschiff aus galaxis Array löschen

            if gesehn < 5 and verraten == False:
                sounds(gesehn)
                self.turn = True
                #time.sleep(1)

            if gesehn == 5 and verraten == False:
                sound_gefunden()
                self.turn = False

            if gesehn == 5 and gefunden == 4:   # Gegner hat gewonnen!!!
                self.alarm = 1
                self.antwort = 10
                self.empfangen = True
                self.spiel_fertig = True
                self.timer_stoppen()
                verloren(self.gegner)

            if verraten == True:
                self.gefunden+=1
                raumschiff_zeichnen(xpos,ypos,ROT)
                self.angepeilt[ypos][xpos] = 1
                if gefunden < 4 and self.gefunden == 4:
                    self.alarm = 1
                    self.antwort = 9
                    self.empfangen = True
                    self.timer_stoppen()
                    gewonnen()
                    sound_gewonnen()
                    self.spiel_fertig = True
                    if language == "de":
                        info = "Du hast gegen " + str(self.gegner) + " gewonnen."
                    else:
                        info = "You won against " + str(self.gegner) + "."
                    userinfo(info)
                    #time.sleep(5)
                    gesehn = 10

                elif gefunden == 4:   # Gegner hat gewonnen!!!
                    self.alarm = 1
                    self.antwort = 10
                    self.empfangen = True
                    self.spiel_fertig = True
                    self.timer_stoppen()
                    verloren(self.gegner)
                else:
                    time.sleep(0.2)
                    sound_verraten()

            self.ping_remote(xpos, ypos, gesehn, self.num, gameid) # Antwort an Gegner senden

        else:  #### Antwort von Gegner
            self.xpos = xpos
            self.ypos = ypos
            self.turn = False
            if wert == 10:
                self.timer_stoppen()
                verloren(self.gegner)
            if wert == 5:
                self.gefunden+=1
                self.turn = True
            if wert == 5 and self.gefunden == 4:   # Du hast gewonnen!!!
                self.timer_stoppen()
                if language == "de":
                    print("Du hast gewonnen!!!")
                else:
                    print("You won!!!")
                self.spiel_fertig = True
            self.antwort = wert
            self.empfangen = True

    def __init__(self, mein_name):
        self.mein_name = mein_name
        self.restarted = False

        # Spielfeld Vorgabewerte: 0-4 Rückgabewerte , 5 = Raumschiff , 6 = noch nicht angepeilt
        self.galaxis=[
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        ]

        # Spielfeld: 1 = wenn bereits angepeilt , 0 = noch nicht angepeilt , 2 = schwarz markiert
        self.angepeilt=[
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        ]

        self.players = []
        self.xpos = []
        self.ypos = []
        self.verraten = False
        self.wert = 6
        self.gefunden = 0
        self.antwort = 0
        self.spielerbereit = False
        self.gegner = "---"
        self.version = 4.7
        self.spielaktiv = False
        self.old_string = ""
        self.old_string2 = ""
        self.spiel_fertig = False


        #initialize pygame clock
        self.clock=pygame.time.Clock()


        #self.initSound()
        self.turn = False
        self.running=False

        try:
            self.Connect((HOST_ADDR, HOST_PORT))

        except:
            print("Serververbindung fehlgeschlagen! / Server connection failed!")
            time.sleep(5)
            sys.exit()
        print("Galaxis Client Version", self.version, "gestartet / started")

    def Neustart(self):
        self.restarted = True
        # Spielfeld Vorgabewerte: 0-4 Rückgabewerte , 5 = Raumschiff , 6 = noch nicht angepeilt
        self.galaxis=[
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        [6,6,6,6,6,6,6,6,6],
        ]

        # Spielfeld: 1 = wenn bereits angepeilt , 0 = noch nicht angepeilt , 2 = schwarz markiert
        self.angepeilt=[
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        ]

        self.players = []
        self.xpos = []
        self.ypos = []
        self.verraten = False
        self.wert = 6
        self.gefunden = 0
        self.antwort = 0
        self.spielerbereit = False
        self.gegner = "---"
        self.spielaktiv = False
        self.old_string = ""
        self.old_string2 = ""
        self.spiel_fertig = False

        #initialize pygame clock
        self.clock=pygame.time.Clock()

        #self.initSound()
        self.turn = False
        self.running=False

        try:
            self.Connect((HOST_ADDR, HOST_PORT))

        except:
            print("Serververbindung fehlgeschlagen! / Server connection failed!")
            time.sleep(5)
            sys.exit()

    def Warten(self):       # 2 Sekunden warten, dabei "Gegner verbunden" Status abfragen
        i = 0
        while True:
            self.Pump()
            connection.Pump()
            time.sleep(0.01)
            i+=1
            if i == 200:
                return self.gegner_verbunden

##### Game Hauptschleife
    def Galaxis(self):
        self.spielzuege = 0
        self.alarm = 0
        self.umschalt_warnung = False
        self.timer_stoppen()
        i = 0
        while not self.running:
            self.Pump()
            connection.Pump()
            sleep(1.5)
            i+=1
            if i == 40:
                i = 0
                self.ping_remote(0, 0, 7, self.num, self.gameid)   # Sag dem Gegner, dass er nichts machen soll. Timeout verhindern
            pygame.display.flip()
        sound_gefunden()
        while self.spielaktiv:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.spielaktiv = False
                    if language == "de":
                        print("Spieler hat beendet")
                    else:
                        print("Player has finished")
                    self.spiel_fertig = True
                    return self.spielaktiv

                if event.type == QUIT:
                    pygame.quit()
                    self.spielaktiv = False
                    self.spiel_fertig = True
                    return self.spielaktiv
                elif event.type == MOUSEBUTTONDOWN:
                    x = pygame.mouse.get_pos()[0]
                    y = pygame.mouse.get_pos()[1]
                    xpos, ypos = fensterposition(x,y)
                    xpos = int(xpos)
                    ypos = int(ypos)
                    mouse_presses = pygame.mouse.get_pressed()
                    if mouse_presses[0] and self.angepeilt[ypos][xpos]==0:
                        element_zeichnen(xpos,ypos,SCHWARZ)
                        self.angepeilt[ypos][xpos] = 2
                    elif mouse_presses[0] and self.angepeilt[ypos][xpos]==2:
                        element_zeichnen(xpos,ypos,GRAU)
                        self.angepeilt[ypos][xpos] = 0
                    if mouse_presses[2] and self.angepeilt[ypos][xpos]==0 and self.turn == True:
                        self.timer_stoppen()
                        self.spielzuege+=1
                        self.angepeilt[ypos][xpos] = 1
                        sound_suchen()
                        time.sleep(3.4)
                        self.empfangen = False
                        self.ping_remote(xpos,ypos, 6, self.num, self.gameid)
                        self.timer_stoppen()
                        while self.empfangen == False:
                            self.Pump()
                            connection.Pump()
                            sleep(0.01)
                        if self.antwort==10:
                            self.alarm = 1
                            self.timer_stoppen()
                            verloren(self.gegner)
                            self.spiel_fertig = True

                        if self.antwort==5:
                            raumschiff_zeichnen(xpos,ypos,ROT)
                            self.turn = True
                            time.sleep(0.2)
                            sound_gefunden()
                        elif self.antwort < 5:
                            element_zeichnen(xpos,ypos,GELB)
                            element_wert(xpos,ypos,self.antwort)
                            self.turn = False
                            time.sleep(0.2)
                            sounds(self.antwort)
                        else:
                            raumschiff_zeichnen(xpos,ypos,SCHWARZ)

                        if self.antwort==9:
                            self.gefunden = 4
                            self.antwort = 5
                            self.alarm = 0
                            self.timer_stoppen()
                            gewonnen()
                            self.spiel_fertig = True
                            if language == "de":
                                info = "Du hast gegen " + str(self.gegner) + " gewonnen."
                            else:
                                info = "You won against " + str(self.gegner) + "."
                            sound_gewonnen()
                            userinfo(info)

                        if self.verraten == True:
                            time.sleep(3.7)
                            sound_verraten()
                        #time.sleep(4.9)
                
            self.Pump()
            connection.Pump()
            sleep(0.01)

            # Fenster aktualisieren
            pygame.display.flip()

            # Refresh-Zeit festlegen
            clock.tick(100)

            if self.gefunden == 4 and self.alarm==0:
                self.alarm = 1
                gewonnen()
                self.timer_stoppen()
                self.spiel_fertig = True
                if language == "de":
                    info = "Du hast gegen " + str(self.gegner) + " gewonnen."
                else:
                    info = "You won against " + str(self.gegner) + "."
                userinfo(info)
                pygame.display.flip()
                mixer.music.load(pfad + "gewonnen.mp3")
                mixer.music.play()
                #time.sleep(6.7)

            # Ausgabe, wer am Zug ist
            elif self.spielaktiv == True:
                if self.umschalt_warnung == False:
                    self.wer_ist_am_zug()
                else:
                    if language == "de":
                        info = "Noch 6 Sekunden, dann ist "+self.gegner+" am Zug!"
                    else:
                        info = "6 seconds left, then it's "+self.gegner+"'s turn!"
                    userinfo(info)

            if self.spiel_fertig == True:
                self.spielaktiv = False

        return self.spiel_fertig

##### Der Terminal/Chat Thread

    def InputLoop(self):
        while 1:
            input = stdin.readline().rstrip("\n")
            if input.startswith("gegner=") or input.startswith("opponent="):
                print("Eingabe nicht erlaubt!")
                print("Input not allowed!")
            else:
                connection.Send({"action": "message", "message": input, "gameid": self.gameid, "user": self.mein_name})
                self.Pump()
                connection.Pump()
                sleep(0.1)


##### Raumschiffe verstecken

    def Verstecken(self, info):
        self.spielerbereit = False
        anzahl_versteckt = 0
        i = 0
        verfugbar, besetzt = "-", "-"
        userinfotext(verfugbar, besetzt)
        while anzahl_versteckt < 4:
            i+=1
            if i == 7000:
                i = 0
                self.ping_remote(0, 0, 7, self.num, self.gameid)   # Sag dem Gegner, dass er nichts machen soll. Timeout verhindern
                connection.Pump()
                self.Pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if language == "de":
                        print("Spieler hat beendet")
                    else:
                        print("Player has finished")
                    return False
                if event.type == QUIT:
                    return False
                elif event.type == MOUSEBUTTONDOWN:
                    x = pygame.mouse.get_pos()[0]
                    y = pygame.mouse.get_pos()[1]
                    xpos, ypos = fensterposition(x,y)
                    xpos = int(xpos)
                    ypos = int(ypos)
                    mouse_presses = pygame.mouse.get_pressed()
                    if mouse_presses[2] and self.galaxis[ypos][xpos]==6:
                        raumschiff_zeichnen(xpos,ypos,WEISS)
                        self.galaxis[ypos][xpos] = 5
                        anzahl_versteckt+=1

                    elif mouse_presses[2] or mouse_presses[0] and self.galaxis[ypos][xpos]==5:
                        self.galaxis[ypos][xpos] = 6
                        self.raumschiff_loeschen()
                        userinfo(info)
                        userinfotext(verfugbar, besetzt)
                        anzahl_versteckt-=1
                connection.Pump()
                self.Pump()

            # Fenster aktualisieren
            pygame.display.flip()

            # Refresh-Zeit festlegen
            clock.tick(100)

        if language == "de":
            info = self.mein_name+", warte auf Gegner"
        else:
            info = self.mein_name+", wait for opponent"
        userinfo(info)
        userinfotext(verfugbar, besetzt)
        self.spielerbereit = True

        return True

    def GegnerWaehlen(self):
        self.gegner_verbunden = True
        self.Send({"action": "spieler_bereit", "num": self.num, "gameid": self.gameid, "userid": self.userid, "bereit": self.spielerbereit})
        if language == "de":
            text = "Wähle einen Gegner:"
        else:
            text = "Choose an opponent:"
        text = font2.render(text, True, (255, 0, 0))
        pygame.draw.rect(fenster, SCHWARZ, [kor(17.5), kor(29.25),kor(30),kor(1.2)], 0)
        fenster.blit(text, ([kor(17.6), kor(29.5)]))
        pygame.draw.rect(fenster, SCHWARZ, [kor(25.4), kor(29.25),kor(30),kor(1.4)], 0)
        pygame.draw.rect(fenster, BLAU, [kor(25.5), kor(29.25),kor(10.3),kor(1.2)], 1)
        pygame.display.flip()
        while True:
            text = ""
            pg.key.set_repeat()
            while len(text) < 3:
                run = True
                while run:
                    clock.tick(60)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                            text = ""
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                return False, False
                            if event.key == pygame.K_RETURN:
                                run = False
                            elif event.key == pygame.K_BACKSPACE:
                                text =  text[:-1]
                            else:
                                text += event.unicode[:1]
                            text_surf = font.render(text, True, (255, 0, 0))
                            pygame.draw.rect(fenster, SCHWARZ, [kor(25.6), kor(29.35),kor(10.1),kor(1)], 0)
                            fenster.blit(text_surf, ([kor(25.6), kor(29.376)]))
                        connection.Pump()
                        self.Pump()
                        pygame.display.flip()
                        if self.running == True:
                            return False, True
            pygame.draw.rect(fenster, SCHWARZ, [kor(17.5), kor(29.25),kor(30),kor(1.2)], 0)
            pygame.draw.rect(fenster, SCHWARZ, [kor(25.4), kor(29.25),kor(30),kor(1.4)], 0)
            return "gegner=" + text, True


##### Chat Thread starten

    def Chat(self):
        input_thread = threading.Thread(target=self.InputLoop, name="input_thread")
        input_thread.daemon = True
        input_thread.start()
        self.input_thread = input_thread
        return self.input_thread


##### Grundsätzliche Aufrufe

galax=GalaxisGame(nickname) # __init__ wird hier aufgerufen

# Chat starten
input_thread = galax.Chat()


while True:

    if restarted == True:
        galax.Neustart()

    # Spielfeld erzeugen über Berechnung
    fenster = pygame.display.set_mode((36 * MULTIPLIKATOR, 33 * MULTIPLIKATOR))

    # Titel für Fensterkopf
    if language == "de":
        pygame.display.set_caption("GALAXIS electronic   (ESC zum verlassen)")
    else:
        pygame.display.set_caption("GALAXIS electronic   (ESC to exit)")

    spielfeld_zeichnen()

    connection.Pump()
    galax.Pump()

    mein_name = str(galax.mein_name_retour())

    # Raumschiffe verstecken

    if language == "de":
        print("Wenn Du fertig versteckt hast, wähle einen Gegner aus.")
        print("ESC im Spielfenster zum verlassen.")
        print("Gib hier Deine Chat-Nachrichten ein. Absenden mit ENTER")
        info = mein_name + ", verstecke Deine Raumschiffe (rechte Maustaste)"
    else:
        print("When you have finished hiding, choose an opponent.")
        print("ESC in game window to exit.")
        print("Enter your chat messages here. Submit with ENTER")
        info = mein_name + ", hide your spaceships (right mouse button)"
    userinfo(info)

    if galax.Verstecken(info) == False:
        pygame.quit()
        sys.exit()

    erfolg = False                                                          # Info:
    gegner_verbunden = True                                                 # - False   False = Abgebrochen
    while gegner_verbunden:                                                 # - False   True  = Von anderem Spieler aufgerufen
        while erfolg == False:                                              # - !=False True  = selber Gegner ausgewählt
            gegner, erfolg = galax.GegnerWaehlen()
            if erfolg == False:                                             # False   False = Gegnerwahl abgebrochen:
                if language == "de":
                    print(Fore.RED + "Spiel abgebrochen" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Game aborted" + Style.RESET_ALL)
                gegner_verbunden = False
                break
            if gegner == False and erfolg == True:                          # False   True  = Von anderem Spieler aufgerufen
                break
            if gegner != False and erfolg == True:                          # !=False True  = selber Gegner ausgewählt
                connection.Send({"action": "message", "message": gegner, "gameid": -1, "user": mein_name})
            erfolg = galax.Warten()

        if gegner_verbunden == True:
            spiel_fertig = galax.Galaxis()                                  #### Spiel starten
            if spiel_fertig == False:                                       # Wenn Spiel abgebrochen:
                if language == "de":
                    print(Fore.RED + "Spiel abgebrochen" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Game aborted" + Style.RESET_ALL)
                gegner_verbunden = False
            if spiel_fertig == True:                                        # Wenn Spiel fertig:
                gegner_verbunden = False

    #### Spiel neu starten?
    ja_nein_zeichnen(0)

    # Fenster aktualisieren
    pygame.display.flip()

    # Refresh-Zeit festlegen
    clock.tick(100)

    antwort_jn = "-"
    while antwort_jn == "-":
        for event in pygame.event.get():
            pygame.display.flip()
            if event.type == MOUSEBUTTONDOWN:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]
                xpos, ypos = fensterposition(x,y)
                xpos = int(xpos)
                ypos = int(ypos)
                mouse_presses = pygame.mouse.get_pressed()
                if (mouse_presses[2] or mouse_presses[0]) and xpos == 3 and (ypos == 5 or ypos == 6):
                    antwort_jn = "j"
                    break
                if (mouse_presses[2] or mouse_presses[0]) and xpos == 5 and (ypos == 5 or ypos == 6):
                    antwort_jn = "n"
                    break
    if antwort_jn == "j":
        restarted = True
    else:
        break

connection.Send({"action": "UserSchliessen"})
time.sleep(1)
connection.Close()
pygame.quit()
sys.exit()
