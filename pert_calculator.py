import pandas as pd
import pygame
import math

#- INIZIALIZZAZIONE PYGAME -
pygame.init()
screen = pygame.display.set_mode((1500,800))
pygame.display.set_caption("PERT")

# - COSTANTI -
BLACK = (0,0,0)
WHITE = (255,255,255)
YELLOW = (255,255,0)
RED = (255,0,0)
GREEN = (0,255,0)
ORANGE = (255,70,0)
PINK = (255,0,255)
BLUE = (0,55,255)
GRAY = (107,107,107)
LIGHT_BLUE = (130,236,255)
FONT = pygame.font.Font(None, 25) #adattare la grandezza a piacimento
END_ARROW = pygame.image.load("arrow.png") # ! ! ! MODIFICARE PERCORSO FILE ! ! !
END_ARROW = pygame.transform.scale(END_ARROW, (14, 10))
LENGHT, HEIGHT = END_ARROW.get_size()

# - CLASSI -
class Nodo:
    lista_nodi = []
    nodi_iniziali = []
    nodi_finali = []
    criticalPath = ["", 0] #lista contenete il percorso di nodi e la durata totale
    istanze = {} #dizionario {"nome":"istanza",...}

    #VARIABILI X PYGAME
    nodi_con_coordinate = [] #contiene i nodi con le coordinate già calcolate
    nodi_in_wait = [] # contiene ogni nodo che al momento non può essere disegnato
    y_successiva = 70 #serve per tenere traccia del prossimo spazio disponibile
    x_max = 0 #nodo più distante
    y_end = 0 #altezza del nodo END
    x_generale = 0 #servono per il movimento
    y_generale = 0 # ^ ^ ^

    def __init__(self, nome, durata, predecessori):
        self.nome = nome
        self.durata = durata
        self.predecessori = predecessori
        self.successori = [] #la riempio più tardi
        self.alap = 0
        self.asap = 0

        self.x = 0 #servono per pygame
        self.y = 0

        Nodo.lista_nodi.append(self)
        if not self.predecessori: #se non ha predecessori
            Nodo.nodi_iniziali.append(self)
        Nodo.istanze[nome] = self

    def __str__(self):
        return str(self.nome)+"("+str(self.durata)+")["+str(self.asap)+"]{"+str(self.alap)+"}"
    
    def cambio_predecessori(): #prima la lista predecessori era piena di nomi, ora di istanze
        for nodo in Nodo.lista_nodi:
            nodo.predecessori = [Nodo.istanze[p] for p in nodo.predecessori]

    def assegnazione_successori():
        for nod in Nodo.lista_nodi: #aggiungo un nodo come predecessore a tutti i suoi successori
            for predecessore in nod.predecessori:
                predecessore.successori.append(nod)
        
        for nod in Nodo.lista_nodi:
            if not nod.successori:#tutti i nodi senza successori sono i finali
                Nodo.nodi_finali.append(nod)
    
    def start():
        Nodo.cambio_predecessori()
        Nodo.assegnazione_successori()

        #richiamo una alla volta le tre funzioni
        for nod in Nodo.nodi_iniziali:
            nod.calcolo_criticalPath(["", 0])
        
        for nod in Nodo.nodi_iniziali:
            nod.calcolo_asap()
        
        for nod in Nodo.nodi_finali:
            nod.calcolo_alap()

        Nodo.stampa()

        #PYGAME
        for nod in Nodo.nodi_iniziali: #inizio disegnando i nodi inziali
            if not nod in Nodo.nodi_con_coordinate:
                nod.calcolo_coordinate(550, Nodo.y_successiva)
        
        while Nodo.nodi_in_wait: #finché ci sono nodi in waiting
            lista = Nodo.nodi_in_wait[::] #[::] importantissimo!
            for nod in lista:
                nod.calcolo_coordinate_wait()

        for n,nodo in enumerate(Nodo.nodi_finali):
            Nodo.y_end += nodo.y
        Nodo.y_end /= n+1 #faccio la media delle y di tutti i nodi finali


    def calcolo_criticalPath(self, percorso_critico):
        #percorso_critico = ["nome1-nome2-...", durataTot]
        percorso_critico[0] += self.nome
        percorso_critico[1] += self.durata
        
        if self.successori: #se ha dei successori aggiunge "-"
            percorso_critico[0] += "-"
            for successore in self.successori: #inoltro la funzione a tutti i successori
                successore.calcolo_criticalPath(percorso_critico[::])
                #è importantissimo aggiungere [::]
                #perché altrimenti python non crea una nuova lista uguale a percorso_critico, ma aggiunge
                #solamente un indirizzo di collegamento allo stesso spazio di memoria
        
        else: #se non ha successori siamo all'end
            if percorso_critico[1] > Nodo.criticalPath[1]:
                Nodo.criticalPath = percorso_critico #se è il più lungo aggiorna il criticalPath
    
    def calcolo_asap(self):
        if self in Nodo.nodi_iniziali:
            asap = self.durata #i nodi iniziali hanno asap = durata
        else:
            #si prende l'asap più grande tra tutti quelli dei predecessori e si somma alla propria durata
            asap = self.durata + max([nodo.asap for nodo in self.predecessori])
        self.asap = asap #aggiorno il valore

        for successore in self.successori: #inoltro la funzione a tutti i successori
            successore.calcolo_asap()

    def calcolo_alap(self):
        if self in Nodo.nodi_finali:
            alap = Nodo.criticalPath[1] #i nodi finali hanno asap = durata percorso critico
        else:
            #si prende la differenza più piccola tra l'alap dei successori e la loro durata
            alap = min([(nodo.alap - nodo.durata) for nodo in self.successori])
        self.alap = alap #aggiorno il valore
        
        for predecessore in self.predecessori: #inoltro la funzione a tutti i predecessori
            predecessore.calcolo_alap()

    def stampa():
        print(F"CRITICAL PATH: {Nodo.criticalPath[0]}({Nodo.criticalPath[1]})")

        for nod in Nodo.lista_nodi:
            print(str(nod.nome) + "(" + str(nod.durata) + ")[" + str(nod.asap) + "]{" + str(nod.alap) + "}")

    def calcolo_coordinate(self, x, y):
        if y >= Nodo.y_successiva:
            Nodo.y_successiva = y + 110
        if x > Nodo.x_max:
            Nodo.x_max = x

        self.x = x
        self.y = y
        cond = self.controllo_sovrapposizione()
        while cond:
            cond = self.controllo_sovrapposizione()

        Nodo.nodi_con_coordinate.append(self)

        for nod in self.successori:
            if not (nod in Nodo.nodi_con_coordinate):
                if len(nod.predecessori) == 1: #se ha solo un predecessore
                    nod.calcolo_coordinate(x+250, y)
                        
                else: #se ha piu di un predecessore devo fare dei controlli
                    cond = True
                    for n in nod.predecessori: #controllo che tutti i predecessori siano stati già calcolati
                        cond = cond and (n in Nodo.nodi_con_coordinate)
                            
                    if cond: #se tutti i predecessori sono già stati calcolati
                        #calcolo le due y agli estremi
                        y_min, y_max = min(i.y for i in nod.predecessori), max(i.y for i in nod.predecessori)
                        if (y_max - y_min) < 200: #se non c'è spazio sposto tutti i nodi più in basso
                            y = y_min + 100
                            sposta(y, 200-(y_max - y_min))
                        else: #se c'è spazio calcolo la media
                            y = (y_max + y_min)/2
                        x = max(i.x for i in nod.predecessori) + 250
                        nod.calcolo_coordinate(x, y)
                    else: #non tutti i predecessori sono ancora stati disegnati, quindi lo metto in waiting
                        if not (nod in Nodo.nodi_in_wait):
                            Nodo.nodi_in_wait.append(nod)

    def calcolo_coordinate_wait(self):
        cond = True
        for nod in self.predecessori: #controllo che tutti i predecessori siano stati già calcolati
            cond = cond and (nod in Nodo.nodi_con_coordinate)
                            
        if cond: #se tutti i predecessori sono già stati calcolati
            Nodo.nodi_in_wait.remove(self)
            #calcolo le due y agli estremi
            y_min, y_max = min(i.y for i in self.predecessori), max(i.y for i in self.predecessori)
            if (y_max - y_min) < 200: #se non c'è spazio sposto tutti i nodi più in basso
                y = y_min + 100
                sposta(y, 200-(y_max - y_min))
            else: #se c'è spazio calcolo la media
                y = (y_max + y_min)/2
            x = max(i.x for i in self.predecessori) + 250
            self.calcolo_coordinate(x, y)

    def controllo_sovrapposizione(self, change = False): #controllo che per ogni successore dei suoi predecessori non ci sia una sovrapposizione
        for genitore in self.predecessori:
            for fratello in genitore.successori:
                if fratello.nome != self.nome:
                    dist = ((self.x-fratello.x)**2 + (self.y-fratello.y)**2)**(0.5) #pitagora per calcolare la distanza
                    if dist < 100: #se si sovrappongono ne sposto uno in su e uno in giù
                        self.y += (110-dist)/2
                        fratello.y -= (110-dist)/2
                        change = True
        return change

# - FUNZIONI -
def creazione_nodi_da_excel(): #funzionante se le tre colonne nell'excel sono rispettivamente: nome nodo - durata - predecessori(separati da una ",")
    df = pd.read_excel("prova ex.xlsx") # ! ! ! CAMBIARE IL NOME/PERCORSO DEL FILE ! ! !
    df = df.fillna(-1) #sostituisce tutti i nan (cella excel vuota = nan)
    lista = df.values.tolist()
    for nod in lista: #lista è una lista di liste [["nome", durata, "pred1,pred2,pred3"],[...]]
        nome, durata, predecessori = nod
        if predecessori == -1 or predecessori == "-": #se la cella predecessori era vuota/segnata con "-"
            predecessori = []
        else:
            predecessori = predecessori.split(",")
        Nodo(nome.upper(), durata, [nodo.upper() for nodo in predecessori]) #upper() per evitare errori di denominazione
        
def creazione_nodi_manuale():
    stringa = "A:1:-B:7:A-C:3:-D:4:C-E:2:D,A-F:5:E,B-G:4:-H:2:F,G-I:3:-L:7:-M:2:L-N:1:M,I,H" # stringa = nome:durata:pred1,pred2,pred3-nome2:durata2:pre1,pre2,pre3
    for nodo in stringa.split("-"): #nodo = nome:durata:pred1,pred2,pred3
        nome, durata, predecessori = nodo.split(":")
        predecessori = predecessori.split(",")
        if not predecessori[0]: #se nel csv non si mettono predecessori
            predecessori = []
        Nodo(nome, int(durata), predecessori)

def aggiorna():
    pygame.display.update() #aggiorna il display di pygame
    pygame.time.Clock().tick(100) #determina gli FPS
    screen.fill(WHITE)

def chiudi_gioco():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() #restituisce un errore su shell
                    
def sposta(y_riferimento, spostamento):
    for nod in Nodo.nodi_con_coordinate:
        if nod.y >= y_riferimento:
            nod.y += spostamento
            
        if nod.y >= Nodo.y_successiva:
            Nodo.y_successiva = nod.y + 110      

def disegna_cerchi():
    #nodo START
    pygame.draw.circle(screen, BLACK, (60+Nodo.x_generale, (Nodo.y_successiva-110)/2+Nodo.y_generale), 70)
    text = FONT.render("START", True, WHITE)
    text_rect = text.get_rect(center=(60+Nodo.x_generale, (Nodo.y_successiva-110)/2+Nodo.y_generale))
    screen.blit(text, text_rect)

    #nodi centrali
    for nod in Nodo.lista_nodi:
        color = RED if nod.nome in Nodo.criticalPath[0] else LIGHT_BLUE #è rosso se fa parte del C.P.
        pygame.draw.circle(screen, color, (nod.x+Nodo.x_generale, nod.y+Nodo.y_generale), 50)

        text = FONT.render(str(nod), True, BLACK) #scrive la funzione __str__ sul cerchio
        text_rect = text.get_rect(center=(nod.x+Nodo.x_generale, nod.y+Nodo.y_generale))
        screen.blit(text, text_rect)

    #nodo END
    pygame.draw.circle(screen, BLACK, (Nodo.x_max+400+Nodo.x_generale, Nodo.y_end+Nodo.y_generale), 70)
    text = FONT.render("END", True, WHITE)
    text_rect = text.get_rect(center=(Nodo.x_max+400+Nodo.x_generale, Nodo.y_end+Nodo.y_generale))
    screen.blit(text, text_rect)

def disegna_freccie():
    for nod in Nodo.lista_nodi:
        x1, y1 = nod.x+Nodo.x_generale, nod.y+Nodo.y_generale

        color, width = (RED,4) if nod.nome in Nodo.criticalPath[0] else (BLACK,1) #è rosso se fa parte del C.P.
        if nod in Nodo.nodi_finali: #va collegato a END
            Q = (Nodo.x_max+400+Nodo.x_generale,Nodo.y_end+Nodo.y_generale)
            L = pygame.draw.line(screen, color, (x1,y1), Q, width)
            disegna_punta_freccia((x1, y1), Q, 70)
        elif nod in Nodo.nodi_iniziali: #va collegato a START
            Q = (60+Nodo.x_generale, (Nodo.y_successiva-110)/2+Nodo.y_generale)
            L = pygame.draw.line(screen, color, (x1,y1), Q, width)
            disegna_punta_freccia(Q, (x1, y1), 50)
            
        for succ in nod.successori: #per fare una freccia devo prima creare una linea che collega nod con succ
            x2, y2 = succ.x+Nodo.x_generale, succ.y+Nodo.y_generale
            color, width = (RED,4) if (nod.nome in Nodo.criticalPath[0] and succ.nome in Nodo.criticalPath[0]) else (BLACK, 1)
            L = pygame.draw.line(screen, color, (x1,y1), (x2,y2), width)
                
            disegna_punta_freccia((x1, y1), (x2, y2), 50)

def disegna_punta_freccia(c1, c2, r):
    x1, y1 = c1
    x2, y2 = c2
    d = ((x2-x1)**2+(y2-y1)**2)**(0.5)
    Px = x1 + (x2-x1)*(1 - (r+7)/d)
    if y1<y2:
        Py = y1 + (y2 - y1)*(1 - (r+7)/d)
    else:
        Py = y1 - (y1 - y2)*(1 - (r+7)/d)
    Px -= LENGHT // 2 #serve per centrare il png
    Py -= HEIGHT // 2                           #-arcsin(cateto opposto/ipotenusa)*360/2pi
    freccia = pygame.transform.rotate(END_ARROW, -(math.asin((y2-y1)/d))*180/3.1418) #calcolo dell'angolazione
    screen.blit(freccia, (Px, Py))

def movimento(): #i due attributi di classe vanno ad influire in tutti gli elementi
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        Nodo.y_generale += 10
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        Nodo.y_generale -= 10
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        Nodo.x_generale += 10
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        Nodo.x_generale -= 10

def stampa_coordinate():
    print("-------")
    for nod in Nodo.lista_nodi:
        print(nod.nome, nod.x, nod.y)

# - PROGRAMMA PRINCIPALE -
creazione_nodi_manuale() #sostituire a mano se si vuol utilizzare l'altra funzione (manuale)
Nodo.start()

while True:
    aggiorna()
    disegna_freccie()
    disegna_cerchi()
    movimento()
    chiudi_gioco()