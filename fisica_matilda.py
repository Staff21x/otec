#!/usr/bin/env python3
"""
FísicaAventura — Para Matilda 🌟
Física 7mo Básico - Chile
Instalar: pip install pygame
Ejecutar: python fisica_matilda.py
"""
import pygame, sys, math, random
pygame.init()

W, H = 1100, 750
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("⚡ FísicaAventura — Para Matilda ⚡")
clock = pygame.time.Clock()
FPS = 60

# ── COLORS ────────────────────────────────────────────────────────
BG     = (8, 10, 28);   CARD   = (18, 22, 52);  CARD2  = (28, 35, 75)
WHITE  = (255,255,255); YELLOW = (255,215,0);    GOLD   = (255,185,0)
GREEN  = (46,213,115);  DGREEN = (25,140,70);    RED    = (232,65,65)
DRED   = (160,30,30);   BLUE   = (55,130,245);   LBLUE  = (100,195,255)
PURPLE = (155,89,232);  DPURP  = (100,55,180);   PINK   = (255,100,155)
ORANGE = (255,145,55);  CYAN   = (0,215,215);    GRAY   = (90,100,130)
LGRAY  = (160,175,205); TEAL   = (0,185,175);    NAVY   = (15,20,48)
BLACK  = (10,10,20)

# ── FONTS ─────────────────────────────────────────────────────────
def mk_font(sz, bold=False):
    for name in ['Arial','Helvetica','DejaVu Sans']:
        try: return pygame.font.SysFont(name, sz, bold=bold)
        except: pass
    return pygame.font.Font(None, sz)

Fxl = mk_font(68,True); Flg = mk_font(46,True); Fmd = mk_font(32,True)
Fsm = mk_font(24,True); Fbd = mk_font(21);      Fxs = mk_font(17)

def render(text, fnt, color=WHITE, shadow=True):
    if shadow:
        s = fnt.render(text, True, (0,0,0)); return s, fnt.render(text, True, color)
    return None, fnt.render(text, True, color)

def blit_text(surf, text, fnt, x, y, color=WHITE, center=True, shadow=True):
    sh, s = render(text, fnt, color, shadow)
    r = s.get_rect(center=(x,y)) if center else s.get_rect(topleft=(x,y))
    if sh: surf.blit(sh, (r.x+2, r.y+2))
    surf.blit(s, r)
    return r

def wrap_text(surf, text, fnt, x, y, color, max_w, line_h=36, center=True):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        test = cur + w + ' '
        if fnt.size(test)[0] > max_w:
            lines.append(cur.strip()); cur = w + ' '
        else: cur = test
    if cur: lines.append(cur.strip())
    for i, line in enumerate(lines):
        blit_text(surf, line, fnt, x, y + i*line_h, color, center)
    return len(lines) * line_h

# ── ROUNDED RECT ──────────────────────────────────────────────────
def rrect(surf, color, rect, r=16, border=0, bcol=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and bcol: pygame.draw.rect(surf, bcol, rect, border, border_radius=r)

# ── PARTICLES ─────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, col=None):
        self.x, self.y = float(x), float(y)
        a = random.uniform(0, 2*math.pi)
        sp = random.uniform(2, 9)
        self.vx = math.cos(a)*sp; self.vy = math.sin(a)*sp - 3
        self.life = self.max_life = random.randint(40, 80)
        self.sz = random.randint(4, 11)
        self.col = col or random.choice([YELLOW,GREEN,CYAN,PINK,ORANGE,WHITE,LBLUE])
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.25; self.life-=1
    def draw(self, surf):
        a = self.life/self.max_life
        sz = max(1, int(self.sz*a))
        col = tuple(int(c*a) for c in self.col)
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), sz)

particles = []
def burst(x, y, n=40, col=None):
    for _ in range(n): particles.append(Particle(x, y, col))
def upd_particles():
    particles[:] = [p for p in particles if p.life>0]
    for p in particles: p.update()
def draw_particles():
    for p in particles: p.draw(screen)

# ── BACKGROUND ────────────────────────────────────────────────────
bg_stars = [(random.randint(0,W), random.randint(0,H), random.uniform(0.5,1.8)) for _ in range(130)]
def draw_bg():
    screen.fill(BG)
    t = tick*0.025
    for sx,sy,sz in bg_stars:
        b = int(160 + 80*math.sin(t + sx*0.01))
        pygame.draw.circle(screen,(b,b,b),(sx,sy),max(1,int(sz)))

# floating symbols
syms = [{'s':s,'x':random.uniform(0,W),'y':random.uniform(0,H),
          'vx':random.uniform(-0.4,0.4),'vy':random.uniform(-0.4,0.4),
          'a':random.uniform(0,6.28),'col':c}
        for s,c in [('F=ma',LBLUE),('N',YELLOW),('P=mg',GREEN),('→',PINK),
                    ('kg',ORANGE),('a=F/m',CYAN),('⊙',PURPLE),('v',TEAL)]]
def upd_syms():
    for s in syms:
        s['x']=(s['x']+s['vx'])%W; s['y']=(s['y']+s['vy'])%H; s['a']+=0.012
def draw_syms():
    for s in syms:
        surf=Fbd.render(s['s'],True,s['col'])
        surf.set_alpha(int(70+40*math.sin(s['a'])))
        screen.blit(surf,(int(s['x']),int(s['y'])))

# ── BUTTON ────────────────────────────────────────────────────────
class Button:
    def __init__(self, cx, cy, w, h, label, col=BLUE, hcol=None, fnt=Fmd, tcol=WHITE, r=16):
        self.rect = pygame.Rect(cx-w//2, cy-h//2, w, h)
        self.label=label; self.col=col; self.hcol=hcol or tuple(min(255,c+45) for c in col)
        self.fnt=fnt; self.tcol=tcol; self.r=r; self.hov=False
    def update(self, mx, my): self.hov=self.rect.collidepoint(mx,my)
    def draw(self, surf):
        rc=self.rect.inflate(8,6) if self.hov else self.rect
        col=self.hcol if self.hov else self.col
        if self.hov:
            glow=pygame.Surface((rc.w+24,rc.h+24),pygame.SRCALPHA)
            pygame.draw.rect(glow,(*col[:3],50),(12,12,rc.w,rc.h),border_radius=self.r+4)
            surf.blit(glow,(rc.x-12,rc.y-12))
        rrect(surf,col,rc,self.r); rrect(surf,col,rc,self.r,2,tuple(min(255,c+70) for c in col))
        blit_text(surf,self.label,self.fnt,rc.centerx,rc.centery,self.tcol)
    def clicked(self, ev): return ev.type==pygame.MOUSEBUTTONDOWN and self.hov

# ── GAME STATE ────────────────────────────────────────────────────
tick = 0
stars = [0,0,0,0]   # stars per topic

class State:
    def __init__(self):
        self.screen='menu'; self.topic=0; self.phase='learn'; self.slide=0
        self.score=0; self.total=0; self.cur_q=0; self.selected=None
        self.feedback=None; self.fb_timer=0; self.vopts=None
    def goto(self, sc, topic=None, phase='learn', slide=0):
        self.screen=sc; self.phase=phase; self.slide=slide; self.cur_q=0
        self.score=0; self.total=0; self.selected=None
        self.feedback=None; self.fb_timer=0; self.vopts=None
        if topic is not None: self.topic=topic
    def show_feedback(self, correct):
        self.feedback=correct; self.fb_timer=100
        if correct: burst(W//2, 110, 55, GREEN); burst(W//2-80,80,25,YELLOW)
        else: burst(W//2, 110, 30, RED)
    def advance_q(self):
        self.feedback=None; self.cur_q+=1; self.selected=None; self.vopts=None

G = State()

# ── STAR DRAW ─────────────────────────────────────────────────────
def draw_star(surf, cx, cy, sz, col):
    pts=[]
    for j in range(10):
        a=-math.pi/2+j*math.pi/5
        r=sz if j%2==0 else sz//2
        pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
    pygame.draw.polygon(surf,col,pts)

def draw_stars_row(surf, x, y, count, sz=20):
    for i in range(3):
        draw_star(surf,x+i*(sz*2+4),y,sz,GOLD if i<count else GRAY)

# ── FEEDBACK BANNER ───────────────────────────────────────────────
def draw_feedback_banner():
    if G.feedback is None: return
    G.fb_timer-=1
    if G.fb_timer<=0: G.feedback=None; return
    alpha=min(255, G.fb_timer*5)
    msg='¡Correcto! ✓' if G.feedback else '¡Incorrecto! ✗'
    col=GREEN if G.feedback else RED
    s=Flg.render(msg,True,col); s.set_alpha(alpha)
    screen.blit(s,s.get_rect(center=(W//2,115)))

# ══════════════════════════════════════════════════════════════════
#  MENU
# ══════════════════════════════════════════════════════════════════
TOPICS = [
    ('Leyes de Newton','newton',BLUE,(80,140,255),'⚖','Inercia · F=ma · Acción-Reacción',0),
    ('Vectores y Fuerzas','vectors',PURPLE,(190,130,255),'→','Suma y resta de fuerzas',1),
    ('Masa vs Peso','masapeso',TEAL,(0,230,210),'🪨','P = m × g · g = 10 m/s²',2),
    ('Cinemática','cinematica',(180,90,40),(255,160,80),'🚀','Velocidad · Rapidez · Aceleración',3),
]

menu_btns = [Button(300+i%2*520, 370+i//2*210, 460, 175, td[0], td[2], td[3], Fmd)
             for i,td in enumerate(TOPICS)]
back_btn = Button(80, H-38, 140, 46, '← Menú', GRAY, (120,130,160), Fsm)

def draw_menu(mx,my):
    draw_bg(); upd_syms(); draw_syms()
    t=tick*0.04
    blit_text(screen,'⚡ FísicaAventura ⚡',Fxl,W//2,75+int(5*math.sin(t)),YELLOW)
    blit_text(screen,'El juego de física de Matilda 🌟',Fsm,W//2,148,LGRAY)
    blit_text(screen,'Elige un tema para estudiar:',Fbd,W//2,200,LGRAY)

    for i,(td,btn) in enumerate(zip(TOPICS,menu_btns)):
        btn.update(mx,my)
        name,sc,col,hcol,icon,desc,ti=td
        col_r=i%2; col_row=i//2
        bx=60+col_r*540; by=280+col_row*210
        card=pygame.Rect(bx,by,500,190)
        if btn.hov: card=card.inflate(8,6)
        base=tuple(c//4 for c in col)
        rrect(screen,base,card,22); rrect(screen,col,card,22,3,col)
        blit_text(screen,icon,Flg,card.x+70,card.centery,WHITE)
        blit_text(screen,name,Fmd,card.x+145,card.y+48,WHITE,center=False)
        blit_text(screen,desc,Fxs,card.x+145,card.y+90,LGRAY,center=False)
        draw_stars_row(screen,card.x+145,card.y+125,stars[ti],18)
        pb=pygame.Rect(card.right-118,card.centery-22,104,44)
        rrect(screen,hcol if btn.hov else col,pb,12)
        blit_text(screen,'▶ Jugar',Fsm,pb.centerx,pb.centery,WHITE)

    total=sum(stars)
    blit_text(screen,f'⭐ Estrellas totales: {total} / 12',Fsm,W//2,H-38,GOLD)

# ══════════════════════════════════════════════════════════════════
#  QUIZ ENGINE  (shared by Newton, Masa/Peso, Cinemática)
# ══════════════════════════════════════════════════════════════════
OPT_RECTS = [pygame.Rect(55,270+i*105,W-110,88) for i in range(4)]

def draw_quiz(questions, hcol, mx, my):
    qi=G.cur_q
    if qi>=len(questions):
        return 'results'
    q=questions[qi]
    # header
    rrect(screen,tuple(c//2 for c in hcol),(0,0,W,80),0)
    blit_text(screen,f'Quiz  ({qi+1}/{len(questions)})',Fsm,W//2,40,WHITE)
    prog=qi/len(questions)
    pygame.draw.rect(screen,GRAY,(0,80,W,10),border_radius=5)
    pygame.draw.rect(screen,hcol,(0,80,int(W*prog),10),border_radius=5)
    # question card
    qc=pygame.Rect(40,100,W-80,135)
    rrect(screen,CARD,qc,18)
    wrap_text(screen,q['q'],Fbd,qc.centerx,qc.y+28,YELLOW,qc.w-40,38)
    # options
    for i,opt in enumerate(q['opts']):
        r=OPT_RECTS[i]
        if G.feedback is not None:
            if i==q['ans']: col,bc=DGREEN,GREEN
            elif i==G.selected and i!=q['ans']: col,bc=DRED,RED
            else: col,bc=CARD,GRAY
        else:
            col=(30,45,90) if r.collidepoint(mx,my) else CARD
            bc=hcol if r.collidepoint(mx,my) else GRAY
        rrect(screen,col,r,14); rrect(screen,bc,r,14,2,bc)
        pygame.draw.circle(screen,hcol,(r.x+26,r.centery),18)
        blit_text(screen,'ABCD'[i],Fsm,r.x+26,r.centery,WHITE)
        blit_text(screen,opt,Fbd,r.x+58,r.centery,WHITE,center=False)
    # explanation
    if G.feedback is not None:
        ec=pygame.Rect(40,H-108,W-80,65)
        rrect(screen,(20,65,20) if G.feedback else (65,15,15),ec,12)
        wrap_text(screen,q['explain'],Fxs,ec.centerx,ec.y+14,WHITE,ec.w-20,26)
    draw_feedback_banner()
    back_btn.update(mx,my); back_btn.draw(screen)
    return 'quiz'

def handle_quiz_click(questions, ev, mx, my):
    qi=G.cur_q
    if ev.type==pygame.MOUSEBUTTONDOWN:
        if back_btn.hov: G.goto('menu'); return
        if qi<len(questions):
            if G.feedback is None:
                for i,r in enumerate(OPT_RECTS):
                    if r.collidepoint(mx,my):
                        G.selected=i
                        G.total+=1
                        if i==questions[qi]['ans']: G.score+=1; G.show_feedback(True)
                        else: G.show_feedback(False)
                        break
            elif G.fb_timer<65:
                G.advance_q()

def draw_results(topic_idx, mx, my):
    draw_bg(); upd_particles(); draw_particles()
    score=G.score; total=G.total
    pct=score/max(total,1)
    s=3 if pct>=0.9 else 2 if pct>=0.7 else 1 if pct>=0.4 else 0
    stars[topic_idx]=max(stars[topic_idx],s)
    if tick%18==0: burst(random.randint(80,W-80),random.randint(80,350),22)
    col=GREEN if s>=2 else ORANGE if s==1 else RED
    blit_text(screen,'¡Resultados!',Fxl,W//2,90,YELLOW)
    sc=pygame.Rect(W//2-230,165,460,165)
    rrect(screen,CARD,sc,22)
    blit_text(screen,f'{score} / {total}',Fxl,W//2,245,col)
    blit_text(screen,'respuestas correctas',Fsm,W//2,308,LGRAY)
    for i in range(3): draw_star(screen,W//2-56+i*56,410,38,GOLD if i<s else GRAY)
    msgs={0:'¡Sigue practicando! 💪',1:'¡Bien hecho! 😊',2:'¡Muy bien! ⭐',3:'¡PERFECTO! 🎉🌟🎉'}
    blit_text(screen,msgs[s],Fmd,W//2,490,col)
    rb=Button(W//2-165,575,290,56,'🔄 Intentar de nuevo',BLUE,fnt=Fsm)
    mb=Button(W//2+175,575,230,56,'🏠 Menú Principal',TEAL,fnt=Fsm)
    rb.update(mx,my); rb.draw(screen)
    mb.update(mx,my); mb.draw(screen)
    return rb, mb

# ══════════════════════════════════════════════════════════════════
#  TOPIC 1 — NEWTON'S LAWS
# ══════════════════════════════════════════════════════════════════
NEWTON_SLIDES = [
  { 'title':'1ª Ley: LA INERCIA','col':BLUE,
    'theory':['Un objeto en REPOSO permanece en reposo.',
              'Un objeto en MOVIMIENTO sigue moviéndose…',
              '…hasta que una FUERZA EXTERNA actúe sobre él.'],
    'tip':'Si empujas un libro en hielo y lo sueltas, ¡seguiría para siempre sin fricción!',
    'anim':'inercia'},
  { 'title':'2ª Ley: F = m × a','col':GREEN,
    'theory':['Fuerza = Masa × Aceleración',
              'Unidad de Fuerza: Newton (N)',
              '¡Mayor masa → necesitas más fuerza para misma aceleración!'],
    'tip':'a = F / m   →   Si F=20N y m=4kg, entonces a = 5 m/s²',
    'anim':'fma'},
  { 'title':'3ª Ley: ACCIÓN ↔ REACCIÓN','col':ORANGE,
    'theory':['Para cada ACCIÓN hay una REACCIÓN igual y opuesta.',
              'Las fuerzas siempre actúan en PARES.',
              'Si empujas una pared, ¡la pared te empuja a ti!'],
    'tip':'El cohete expulsa gases hacia ABAJO → sube hacia ARRIBA 🚀',
    'anim':'rocket'},
]

NEWTON_QUIZ = [
  {'q':'¿Cuál situación describe la 1ª Ley de Newton (Inercia)?',
   'opts':['Una pelota cae por la gravedad',
           'Un patinador sigue deslizándose tras dejar de empujarse',
           'Un cohete vuela expulsando gases',
           'Levantar una roca pesada requiere más fuerza'],
   'ans':1,'explain':'La inercia: el patinador sigue moviéndose porque no hay fuerza que lo detenga (o hay poca fricción).'},
  {'q':'F = m × a. Si F = 30 N y m = 6 kg, ¿cuál es la aceleración?',
   'opts':['180 m/s²','5 m/s²','24 m/s²','0.2 m/s²'],
   'ans':1,'explain':'a = F / m = 30 N ÷ 6 kg = 5 m/s²'},
  {'q':'¿Cuántos Newtons necesitas para acelerar 8 kg a 4 m/s²?',
   'opts':['2 N','12 N','32 N','48 N'],
   'ans':2,'explain':'F = m × a = 8 kg × 4 m/s² = 32 N'},
  {'q':'Nadas empujando el agua hacia atrás. Según la 3ª Ley, el agua te empuja…',
   'opts':['hacia abajo','hacia atrás','hacia adelante','no te empuja'],
   'ans':2,'explain':'Acción y Reacción: empujas agua atrás → agua te empuja adelante.'},
  {'q':'¿En qué unidad se mide la Fuerza?',
   'opts':['Kilogramos (kg)','Metros/segundo (m/s)','Newtons (N)','Joules (J)'],
   'ans':2,'explain':'La fuerza se mide en Newtons (N), en honor a Isaac Newton.'},
]

n_learn_btns = [Button(W//2+160,H-52,230,50,'Siguiente →',GREEN,fnt=Fsm),
                Button(W//2-180,H-52,220,50,'← Anterior',GRAY,fnt=Fsm)]

def draw_newton_anim(anim, t):
    cx,cy=W//2+30, 420
    if anim=='inercia':
        pygame.draw.line(screen,LGRAY,(cx-270,cy+65),(cx+270,cy+65),3)
        bx=cx-260+(t*1.8)%520
        br=pygame.Rect(bx-38,cy+20,76,45)
        rrect(screen,BLUE,br,10)
        blit_text(screen,'m',Fmd,bx,cy+42,WHITE)
        pygame.draw.line(screen,GREEN,(bx+38,cy+42),(bx+90,cy+42),5)
        pygame.draw.polygon(screen,GREEN,[(bx+90,cy+34),(bx+108,cy+42),(bx+90,cy+50)])
        blit_text(screen,'v →',Fxs,bx+100,cy+22,GREEN)
        blit_text(screen,'sin fricción → sigue para siempre',Fxs,cx-30,cy+105,LGRAY)

    elif anim=='fma':
        pygame.draw.line(screen,LGRAY,(cx-270,cy+65),(cx+270,cy+65),3)
        # small block, big accel
        b1=pygame.Rect(cx-255,cy+20,50,45); rrect(screen,(30,160,60),b1,8)
        blit_text(screen,'2kg',Fxs,b1.centerx,b1.centery,WHITE)
        fl=int(25*math.sin(t*0.06)+70)
        pygame.draw.line(screen,GREEN,(b1.right,b1.centery),(b1.right+fl,b1.centery),5)
        pygame.draw.polygon(screen,GREEN,[(b1.right+fl,b1.centery-8),(b1.right+fl+16,b1.centery),(b1.right+fl,b1.centery+8)])
        blit_text(screen,'F=10N → a=5m/s²',Fxs,b1.right+40,cy+10,GREEN)
        # big block, small accel
        b2=pygame.Rect(cx+30,cy+10,100,55); rrect(screen,(180,50,50),b2,8)
        blit_text(screen,'10kg',Fxs,b2.centerx,b2.centery,WHITE)
        fl2=int(10*math.sin(t*0.06)+28)
        pygame.draw.line(screen,ORANGE,(b2.right,b2.centery),(b2.right+fl2,b2.centery),5)
        pygame.draw.polygon(screen,ORANGE,[(b2.right+fl2,b2.centery-8),(b2.right+fl2+16,b2.centery),(b2.right+fl2,b2.centery+8)])
        blit_text(screen,'F=10N → a=1m/s²',Fxs,b2.right+32,cy+10,ORANGE)
        blit_text(screen,'¡Misma fuerza, diferente aceleración!',Fxs,cx-30,cy+105,LGRAY)

    elif anim=='rocket':
        ry=cy-int(70*math.sin(t*0.045))-30
        pygame.draw.polygon(screen,ORANGE,[(cx,ry-60),(cx-28,ry+35),(cx+28,ry+35)])
        pygame.draw.rect(screen,RED,(cx-28,ry+35,56,50),border_radius=6)
        pygame.draw.rect(screen,LBLUE,(cx-14,ry-10,28,32),border_radius=4)
        for fi in range(6):
            fx=cx-18+fi*7; fh=random.randint(25,55)
            pygame.draw.line(screen,YELLOW,(fx,ry+85),(fx+random.randint(-4,4),ry+85+fh),4)
        pygame.draw.line(screen,RED,(cx+45,ry+60),(cx+45,ry+115),4)
        pygame.draw.polygon(screen,RED,[(cx+37,ry+110),(cx+45,ry+125),(cx+53,ry+110)])
        blit_text(screen,'ACCIÓN (gases↓)',Fxs,cx+120,ry+90,RED)
        pygame.draw.line(screen,GREEN,(cx-45,ry+20),(cx-45,ry-40),4)
        pygame.draw.polygon(screen,GREEN,[(cx-53,ry-35),(cx-45,ry-50),(cx-37,ry-35)])
        blit_text(screen,'REACCIÓN (cohete↑)',Fxs,cx-160,ry-15,GREEN)

def draw_newton_learn(mx, my):
    sl=G.slide; d=NEWTON_SLIDES[sl]; col=d['col']; t=tick
    rrect(screen,tuple(c//3 for c in col),(0,0,W,95),0)
    blit_text(screen,d['title'],Fmd,W//2,48,WHITE)
    # theory card
    tc=pygame.Rect(28,108,508,305)
    rrect(screen,CARD,tc,20); rrect(screen,col,tc,20,3,col)
    blit_text(screen,'📚 Concepto',Fsm,tc.centerx,tc.y+32,col)
    for i,line in enumerate(d['theory']):
        blit_text(screen,line,Fbd,tc.centerx,tc.y+85+i*62,WHITE)
    # tip card
    tip=pygame.Rect(28,425,508,140)
    rrect(screen,CARD2,tip,16)
    blit_text(screen,'💡 Recuerda:',Fxs,tip.x+14,tip.y+18,YELLOW,center=False)
    wrap_text(screen,d['tip'],Fbd,tip.centerx,tip.y+50,LGRAY,tip.w-24,34)
    # animation panel
    ap=pygame.Rect(558,108,514,457)
    rrect(screen,CARD,ap,20)
    blit_text(screen,'🎬 Visualización',Fxs,ap.centerx,ap.y+22,col)
    draw_newton_anim(d['anim'],t)
    # slide dots
    for i in range(3):
        pygame.draw.circle(screen,col if i==sl else GRAY,(W//2-20+i*20,H-53),8)
    # buttons
    nb=n_learn_btns[0]; pb=n_learn_btns[1]
    if sl<2: nb.label='Siguiente →'; nb.col=GREEN; nb.hcol=(80,240,140); nb.tcol=WHITE
    else:    nb.label='¡Al Quiz! 🎯'; nb.col=YELLOW; nb.hcol=GOLD; nb.tcol=BLACK
    nb.update(mx,my); nb.draw(screen)
    if sl>0: pb.update(mx,my); pb.draw(screen)
    back_btn.update(mx,my); back_btn.draw(screen)
    return nb, pb

# ══════════════════════════════════════════════════════════════════
#  TOPIC 2 — VECTORS
# ══════════════════════════════════════════════════════════════════
VEC_PROBLEMS = [
    {'f1':5,'d1':'r','f2':3,'d2':'r','ans':8,'adir':'r'},
    {'f1':7,'d1':'r','f2':3,'d2':'l','ans':4,'adir':'r'},
    {'f1':4,'d1':'l','f2':4,'d2':'r','ans':0,'adir':'eq'},
    {'f1':10,'d1':'r','f2':6,'d2':'l','ans':4,'adir':'r'},
    {'f1':3,'d1':'l','f2':7,'d2':'l','ans':10,'adir':'l'},
    {'f1':8,'d1':'l','f2':5,'d2':'r','ans':3,'adir':'l'},
]

def make_vec_opts(prob):
    f1,f2,ca,cd=prob['f1'],prob['f2'],prob['ans'],prob['adir']
    correct={'v':ca,'d':cd}
    candidates=[correct,
                {'v':f1+f2,'d':'r'},{'v':f1+f2,'d':'l'},
                {'v':abs(f1-f2)+2,'d':'r'},{'v':abs(f1-f2)+2,'d':'l'},
                {'v':ca,'d':'l' if cd=='r' else 'r'},
                {'v':f1,'d':prob['d1']},{'v':f2,'d':prob['d2']}]
    seen=set(); opts=[correct]
    for c in candidates:
        key=(c['v'],c['d'])
        if key not in seen and c!=correct:
            seen.add(key); opts.append(c)
        if len(opts)==4: break
    while len(opts)<4: opts.append({'v':random.randint(1,12),'d':random.choice(['r','l'])})
    opts=opts[:4]; random.shuffle(opts)
    return opts

def opt_label(o):
    if o['v']==0 or o['d']=='eq': return '⊙  FR = 0 N  (Equilibrio)'
    sym='→' if o['d']=='r' else '←'
    return f'{sym}  FR = {o["v"]} N  {sym}'

VOPT_RECTS=[pygame.Rect(55+i%2*545,370+i//2*120,495,95) for i in range(4)]

def draw_vec_problem(prob, opts, mx, my):
    rrect(screen,(50,15,95),(0,0,W,80),0)
    blit_text(screen,f'¡Calcula la Fuerza Resultante!  ({G.cur_q+1}/{len(VEC_PROBLEMS)})',Fsm,W//2,40,WHITE)
    prog=G.cur_q/len(VEC_PROBLEMS)
    pygame.draw.rect(screen,GRAY,(0,80,W,10),border_radius=5)
    pygame.draw.rect(screen,PURPLE,(0,80,int(W*prog),10),border_radius=5)

    pc=pygame.Rect(40,100,W-80,240)
    rrect(screen,CARD,pc,20)
    blit_text(screen,'¿Hacia dónde va el bloque y con cuánta fuerza?',Fsm,W//2,128,YELLOW)

    cx,cy=W//2,240
    # block
    br=pygame.Rect(cx-36,cy-28,72,56); rrect(screen,TEAL,br,10)
    blit_text(screen,'📦',Fmd,cx,cy,WHITE)

    def arrow(ox, oy, mag, direc, col, label):
        px=mag*14
        if direc=='r':
            pygame.draw.line(screen,col,(ox+36,oy),(ox+36+px,oy),6)
            pygame.draw.polygon(screen,col,[(ox+36+px,oy-9),(ox+52+px,oy),(ox+36+px,oy+9)])
            blit_text(screen,label,Fsm,ox+36+px//2,oy-28,col)
        else:
            pygame.draw.line(screen,col,(ox-36,oy),(ox-36-px,oy),6)
            pygame.draw.polygon(screen,col,[(ox-36-px,oy-9),(ox-52-px,oy),(ox-36-px,oy+9)])
            blit_text(screen,label,Fsm,ox-36-px//2,oy-28,col)

    arrow(cx,cy-10,prob['f1'],prob['d1'],GREEN,f'{prob["f1"]}N')
    arrow(cx,cy+14,prob['f2'],prob['d2'],ORANGE,f'{prob["f2"]}N')

    for i,opt in enumerate(opts):
        r=VOPT_RECTS[i]
        is_correct=(opt['v']==prob['ans'] and opt['d']==prob['adir']) or (prob['ans']==0 and opt['v']==0)
        if G.feedback is not None:
            if is_correct: col,bc=DGREEN,GREEN
            elif i==G.selected and not is_correct: col,bc=DRED,RED
            else: col,bc=CARD,GRAY
        else:
            col=(30,20,65) if r.collidepoint(mx,my) else CARD
            bc=PURPLE if r.collidepoint(mx,my) else GRAY
        rrect(screen,col,r,14); rrect(screen,bc,r,14,2,bc)
        blit_text(screen,opt_label(opt),Fmd,r.centerx,r.centery,WHITE)

    if G.feedback is not None:
        f1v,f2v=prob['f1'],prob['f2']
        if prob['d1']==prob['d2']:
            exp=f'Mismo sentido → {f1v}N + {f2v}N = {prob["ans"]}N'
        elif prob['ans']==0:
            exp=f'Fuerzas iguales y opuestas → {f1v}N - {f2v}N = 0  (Equilibrio)'
        else:
            big,sml=max(f1v,f2v),min(f1v,f2v)
            lado='derecha' if prob['adir']=='r' else 'izquierda'
            exp=f'Sentidos opuestos → {big}N - {sml}N = {prob["ans"]}N hacia la {lado}'
        ec=pygame.Rect(40,H-90,W-80,55); rrect(screen,(20,60,20) if G.feedback else (60,15,15),ec,12)
        blit_text(screen,exp,Fxs,ec.centerx,ec.centery,WHITE)

    draw_feedback_banner()
    back_btn.update(mx,my); back_btn.draw(screen)

def draw_vec_learn(mx,my):
    rrect(screen,(55,18,100),(0,0,W,88),0)
    blit_text(screen,'→  Vectores y Fuerza Resultante  ←',Fmd,W//2,44,WHITE)
    cards=[
        ('Mismo sentido → SUMAN',BLUE,'→ 3N  +  → 7N  =  → 10N','3N','r','7N','r',10,'r'),
        ('Sentidos opuestos → RESTAN',ORANGE,'← 3N  +  → 7N  =  → 4N','7N','r','3N','l',4,'r'),
    ]
    for ci,(title,col,formula,la,da,lb,db,res,rd) in enumerate(cards):
        cx=280+ci*555; cy=310
        card=pygame.Rect(cx-250,115,470,390)
        rrect(screen,tuple(c//3 for c in col),card,20)
        rrect(screen,col,card,20,3,col)
        blit_text(screen,title,Fsm,cx,cy-140,col)
        blit_text(screen,formula,Fbd,cx,cy-95,WHITE)
        # mini diagram
        pygame.draw.circle(screen,TEAL,(cx,cy),28)
        blit_text(screen,'📦',Fsm,cx,cy,WHITE)
        def mini_arrow(ox,oy,mag,d,c,lbl):
            px=mag*12
            if d=='r':
                pygame.draw.line(screen,c,(ox+28,oy),(ox+28+px,oy),5)
                pygame.draw.polygon(screen,c,[(ox+28+px,oy-8),(ox+42+px,oy),(ox+28+px,oy+8)])
                blit_text(screen,lbl,Fxs,ox+28+px//2,oy-24,c)
            else:
                pygame.draw.line(screen,c,(ox-28,oy),(ox-28-px,oy),5)
                pygame.draw.polygon(screen,c,[(ox-28-px,oy-8),(ox-42-px,oy),(ox-28-px,oy+8)])
                blit_text(screen,lbl,Fxs,ox-28-px//2,oy-24,c)
        mini_arrow(cx,cy-10,int(la[:-1]),da,GREEN,la)
        mini_arrow(cx,cy+12,int(lb[:-1]),db,RED,lb)
        dir_sym='→' if rd=='r' else '←'
        blit_text(screen,f'FR = {res}N {dir_sym}',Fmd,cx,cy+75,YELLOW)
        blit_text(screen,'El bloque se mueve hacia allá',Fxs,cx,cy+115,LGRAY)

    box=pygame.Rect(W//2-420,525,840,95)
    rrect(screen,(35,35,15),box,16)
    blit_text(screen,'🔑 Si FR = 0 → EQUILIBRIO (el objeto no se mueve)',Fsm,W//2,562,CYAN)
    blit_text(screen,'Las fuerzas son VECTORES: tienen magnitud, dirección y sentido',Fxs,W//2,600,LGRAY)

    nb=Button(W//2,H-45,260,54,'¡A Practicar! 🎮',GREEN,fnt=Fsm)
    nb.update(mx,my); nb.draw(screen)
    back_btn.update(mx,my); back_btn.draw(screen)
    return nb

# ══════════════════════════════════════════════════════════════════
#  TOPIC 3 — MASA vs PESO
# ══════════════════════════════════════════════════════════════════
MASA_SLIDES=[
  {'title':'¿Qué es la MASA?','col':TEAL,
   'lines':['La MASA es la cantidad de materia de un cuerpo.',
            'Se mide en KILOGRAMOS (kg).',
            '¡La masa NO cambia según el planeta!',
            'Una roca de 10 kg tiene 10 kg en la Tierra Y en la Luna.'],
   'note':'Masa = constante sin importar dónde estés 🌍🌕'},
  {'title':'¿Qué es el PESO?','col':ORANGE,
   'lines':['El PESO es una FUERZA gravitacional.',
            'Se mide en NEWTONS (N).',
            'Fórmula: P = m × g',
            'En la Tierra: g ≈ 10 m/s²'],
   'note':'¡El peso SÍ cambia según el planeta!'},
  {'title':'Ejemplo: Roca de 10 kg','col':YELLOW,
   'lines':['Masa = 10 kg  (igual en cualquier planeta)',
            'En la Tierra (g=10): P = 10 × 10 = 100 N',
            'En la Luna (g=1.6): P = 10 × 1.6 = 16 N',
            '¡Misma MASA, diferente PESO!'],
   'note':'Fórmula clave: P = m × g'},
]

MASA_QUIZ=[
  {'q':'¿En qué unidad se mide la MASA?',
   'opts':['Newtons (N)','Kilogramos (kg)','Metros (m)','Joules (J)'],
   'ans':1,'explain':'La masa se mide en KILOGRAMOS (kg). El peso en Newtons (N).'},
  {'q':'Una mochila tiene masa de 5 kg. ¿Cuánto pesa en la Tierra? (g=10 m/s²)',
   'opts':['5 N','2 N','50 N','500 N'],
   'ans':2,'explain':'P = m × g = 5 kg × 10 m/s² = 50 N'},
  {'q':'Un astronauta pesa 800 N en la Tierra. ¿Cuánto es su MASA en la Luna?',
   'opts':['133 kg','80 kg','800 kg','Cambia según el planeta'],
   'ans':1,'explain':'La masa NUNCA cambia: m = P ÷ g = 800 ÷ 10 = 80 kg (igual en la Tierra y la Luna).'},
  {'q':'¿Cuál es la diferencia principal entre MASA y PESO?',
   'opts':['Son lo mismo, solo distinto nombre',
           'La masa cambia según el planeta; el peso no',
           'Masa = cantidad de materia (kg); Peso = fuerza gravitacional (N)',
           'El peso se mide en kg, la masa en N'],
   'ans':2,'explain':'Masa es cantidad de materia (kg). Peso es la fuerza de gravedad sobre esa masa (N).'},
  {'q':'Una piedra pesa 300 N en la Tierra (g=10). ¿Cuál es su masa?',
   'opts':['3000 kg','300 kg','30 kg','3 kg'],
   'ans':2,'explain':'m = P ÷ g = 300 N ÷ 10 m/s² = 30 kg'},
]

masa_nav=[Button(W//2+160,H-50,230,50,'Siguiente →',GREEN,fnt=Fsm),
          Button(W//2-180,H-50,220,50,'← Anterior',GRAY,fnt=Fsm)]

def draw_masa_learn(mx,my):
    sl=G.slide; d=MASA_SLIDES[sl]; col=d['col']
    rrect(screen,tuple(c//3 for c in col),(0,0,W,90),0)
    blit_text(screen,d['title'],Fmd,W//2,45,WHITE)
    # main card
    mc=pygame.Rect(W//2-420,105,840,355)
    rrect(screen,CARD,mc,22); rrect(screen,col,mc,22,3,col)
    for i,line in enumerate(d['lines']):
        c2=YELLOW if i==0 else (GREEN if 'Tierra' in line else CYAN if 'Luna' in line else WHITE)
        blit_text(screen,line,Fsm if i==0 else Fbd,mc.centerx,mc.y+60+i*68,c2)
    # note
    nc=pygame.Rect(W//2-360,472,720,68)
    rrect(screen,(40,40,15),nc,14)
    blit_text(screen,'💡 '+d['note'],Fsm,nc.centerx,nc.centery,YELLOW)

    # visual: planets
    if sl in (0,1):
        planets=[('🌍 Tierra','g=10 m/s²',W//4),('🌕 Luna','g=1.6 m/s²',W*3//4)]
        for pname,gval,px in planets:
            blit_text(screen,pname,Fsm,px,570,WHITE)
            blit_text(screen,gval,Fxs,px,600,LGRAY)
            pygame.draw.circle(screen,(90,70,50),(px,640),38)
            blit_text(screen,'🪨',Fmd,px,640,WHITE)
            if sl==0:
                blit_text(screen,'10 kg',Fbd,px,690,GREEN)
            else:
                v='100 N' if 'Tierra' in pname else '16 N'
                blit_text(screen,v,Fbd,px,690,RED if 'Tierra' in pname else ORANGE)
    else:
        formula=pygame.Rect(W//2-280,555,560,115)
        rrect(screen,(38,38,10),formula,18)
        blit_text(screen,'P = m × g',Flg,W//2,605,YELLOW)
        blit_text(screen,'Peso = Masa × Gravedad',Fsm,W//2,650,LGRAY)

    for i in range(3):
        pygame.draw.circle(screen,col if i==sl else GRAY,(W//2-20+i*20,H-50),8)
    nb=masa_nav[0]; pb=masa_nav[1]
    if sl<2: nb.label='Siguiente →'; nb.col=GREEN; nb.hcol=(80,240,140); nb.tcol=WHITE
    else:    nb.label='¡Al Quiz! 🎯'; nb.col=YELLOW; nb.hcol=GOLD; nb.tcol=BLACK
    nb.update(mx,my); nb.draw(screen)
    if sl>0: pb.update(mx,my); pb.draw(screen)
    back_btn.update(mx,my); back_btn.draw(screen)
    return nb,pb

# ══════════════════════════════════════════════════════════════════
#  TOPIC 4 — CINEMÁTICA
# ══════════════════════════════════════════════════════════════════
CIN_QUIZ=[
  {'q':'¿Cuál es la diferencia entre VELOCIDAD y RAPIDEZ?',
   'opts':['Son exactamente lo mismo',
           'La rapidez incluye dirección; la velocidad no',
           'La velocidad incluye dirección; la rapidez es solo el número con unidad',
           'La rapidez se mide en km y la velocidad en m/s'],
   'ans':2,'explain':'Rapidez: "80 km/h" (solo número). Velocidad: "80 km/h hacia el norte" (número + dirección).'},
  {'q':'¿Cuál es la fórmula para calcular la Aceleración?',
   'opts':['a = m × F','a = F / m','a = m / F','a = F + m'],
   'ans':1,'explain':'De F = m×a, despejando: a = F/m. Unidad: m/s²'},
  {'q':'¿En qué unidad se mide la Aceleración?',
   'opts':['m/s','km/h','m/s²','kg·m/s'],
   'ans':2,'explain':'La aceleración se mide en metros por segundo al cuadrado (m/s²).'},
  {'q':'Un auto va a "90 km/h hacia el sur". ¿Qué magnitud está describiendo?',
   'opts':['Solo la rapidez','La velocidad (incluye dirección)','La aceleración','El peso'],
   'ans':1,'explain':'"90 km/h hacia el sur" incluye magnitud Y dirección → es VELOCIDAD.'},
  {'q':'¿Cuántos Newtons actúan sobre una masa de 6 kg con aceleración 5 m/s²?',
   'opts':['1.2 N','11 N','30 N','65 N'],
   'ans':2,'explain':'F = m × a = 6 kg × 5 m/s² = 30 N'},
]

def draw_cin_learn(mx,my):
    rrect(screen,(55,25,80),(0,0,W,88),0)
    blit_text(screen,'🚀 Conceptos de Cinemática',Fmd,W//2,44,WHITE)
    concepts=[
        ('FUERZA (F)','Newton (N)','F = m × a',BLUE,'💪'),
        ('ACELERACIÓN (a)','m/s²','a = F / m',GREEN,'⚡'),
        ('RAPIDEZ','km/h  o  m/s','Solo el número\n(ej: 80 km/h)',ORANGE,'🏎'),
        ('VELOCIDAD','km/h  o  m/s','Número + dirección\n(ej: 80 km/h Norte)',PURPLE,'🧭'),
    ]
    for i,(name,unit,fml,col,icon) in enumerate(concepts):
        cx=280+(i%2)*555; cy=255+(i//2)*245
        card=pygame.Rect(cx-245,cy-108,462,200)
        rrect(screen,tuple(c//3 for c in col),card,20)
        rrect(screen,col,card,20,3,col)
        blit_text(screen,icon,Flg,card.x+68,card.centery,WHITE)
        blit_text(screen,name,Fsm,card.x+148,card.y+36,col,center=False)
        blit_text(screen,'Unidad: '+unit,Fxs,card.x+148,card.y+72,LGRAY,center=False)
        for j,fl in enumerate(fml.split('\n')):
            blit_text(screen,fl,Fbd,card.x+148,card.y+108+j*34,YELLOW,center=False)
    box=pygame.Rect(W//2-420,635,840,70)
    rrect(screen,(38,18,58),box,14)
    blit_text(screen,'🔑 VELOCIDAD incluye dirección · RAPIDEZ es solo el número · FUERZA en Newtons',Fxs,W//2,670,CYAN)
    nb=Button(W//2,H-35,250,52,'¡Al Quiz! 🎯',YELLOW,(255,210,0),Fsm,BLACK)
    nb.update(mx,my); nb.draw(screen)
    back_btn.update(mx,my); back_btn.draw(screen)
    return nb

# ══════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════════
def main():
    global tick
    running=True
    while running:
        tick+=1
        mx,my=pygame.mouse.get_pos()
        events=pygame.event.get()
        for ev in events:
            if ev.type==pygame.QUIT: running=False
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                if G.screen!='menu': G.goto('menu')

        sc=G.screen

        # ── MENU ───────────────────────────────────────────────
        if sc=='menu':
            draw_menu(mx,my)
            for ev in events:
                for i,(td,btn) in enumerate(zip(TOPICS,menu_btns)):
                    if btn.clicked(ev):
                        G.goto(td[1],topic=td[6])

        # ── NEWTON ─────────────────────────────────────────────
        elif sc=='newton':
            draw_bg()
            if G.phase=='learn':
                nb,pb=draw_newton_learn(mx,my)
                for ev in events:
                    if ev.type==pygame.MOUSEBUTTONDOWN:
                        if back_btn.hov: G.goto('menu')
                        elif nb.hov:
                            if G.slide<2: G.slide+=1
                            else: G.phase='quiz'; G.cur_q=0; G.score=0; G.total=0
                        elif pb.hov and G.slide>0: G.slide-=1
            elif G.phase=='quiz':
                if G.cur_q<len(NEWTON_QUIZ):
                    upd_particles(); draw_particles()
                    draw_quiz(NEWTON_QUIZ,BLUE,mx,my)
                    for ev in events: handle_quiz_click(NEWTON_QUIZ,ev,mx,my)
                else:
                    rb,mb=draw_results(0,mx,my)
                    for ev in events:
                        if ev.type==pygame.MOUSEBUTTONDOWN:
                            if rb.hov: G.goto('newton',0,'quiz')
                            elif mb.hov: G.goto('menu')

        # ── VECTORS ────────────────────────────────────────────
        elif sc=='vectors':
            draw_bg()
            if G.phase=='learn':
                nb=draw_vec_learn(mx,my)
                for ev in events:
                    if ev.type==pygame.MOUSEBUTTONDOWN:
                        if back_btn.hov: G.goto('menu')
                        elif nb.hov: G.phase='quiz'; G.cur_q=0; G.score=0; G.total=0
            elif G.phase=='quiz':
                if G.cur_q<len(VEC_PROBLEMS):
                    upd_particles(); draw_particles()
                    prob=VEC_PROBLEMS[G.cur_q]
                    if G.vopts is None: G.vopts=make_vec_opts(prob)
                    draw_vec_problem(prob,G.vopts,mx,my)
                    for ev in events:
                        if ev.type==pygame.MOUSEBUTTONDOWN:
                            if back_btn.hov: G.goto('menu')
                            elif G.feedback is None:
                                for i,r in enumerate(VOPT_RECTS):
                                    if r.collidepoint(mx,my):
                                        opt=G.vopts[i]
                                        G.selected=i; G.total+=1
                                        ok=(opt['v']==prob['ans'] and opt['d']==prob['adir']) or (prob['ans']==0 and opt['v']==0)
                                        if ok: G.score+=1; G.show_feedback(True)
                                        else: G.show_feedback(False)
                                        break
                            elif G.fb_timer<65:
                                G.advance_q()
                else:
                    rb,mb=draw_results(1,mx,my)
                    for ev in events:
                        if ev.type==pygame.MOUSEBUTTONDOWN:
                            if rb.hov: G.goto('vectors',1,'quiz')
                            elif mb.hov: G.goto('menu')

        # ── MASA/PESO ──────────────────────────────────────────
        elif sc=='masapeso':
            draw_bg()
            if G.phase=='learn':
                nb,pb=draw_masa_learn(mx,my)
                for ev in events:
                    if ev.type==pygame.MOUSEBUTTONDOWN:
                        if back_btn.hov: G.goto('menu')
                        elif nb.hov:
                            if G.slide<2: G.slide+=1
                            else: G.phase='quiz'; G.cur_q=0; G.score=0; G.total=0
                        elif pb.hov and G.slide>0: G.slide-=1
            elif G.phase=='quiz':
                if G.cur_q<len(MASA_QUIZ):
                    upd_particles(); draw_particles()
                    draw_quiz(MASA_QUIZ,TEAL,mx,my)
                    for ev in events: handle_quiz_click(MASA_QUIZ,ev,mx,my)
                else:
                    rb,mb=draw_results(2,mx,my)
                    for ev in events:
                        if ev.type==pygame.MOUSEBUTTONDOWN:
                            if rb.hov: G.goto('masapeso',2,'quiz')
                            elif mb.hov: G.goto('menu')

        # ── CINEMÁTICA ─────────────────────────────────────────
        elif sc=='cinematica':
            draw_bg()
            if G.phase=='learn':
                nb=draw_cin_learn(mx,my)
                for ev in events:
                    if ev.type==pygame.MOUSEBUTTONDOWN:
                        if back_btn.hov: G.goto('menu')
                        elif nb.hov: G.phase='quiz'; G.cur_q=0; G.score=0; G.total=0
            elif G.phase=='quiz':
                if G.cur_q<len(CIN_QUIZ):
                    upd_particles(); draw_particles()
                    draw_quiz(CIN_QUIZ,PURPLE,mx,my)
                    for ev in events: handle_quiz_click(CIN_QUIZ,ev,mx,my)
                else:
                    rb,mb=draw_results(3,mx,my)
                    for ev in events:
                        if ev.type==pygame.MOUSEBUTTONDOWN:
                            if rb.hov: G.goto('cinematica',3,'quiz')
                            elif mb.hov: G.goto('menu')

        upd_particles(); draw_particles()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit(); sys.exit()

if __name__=='__main__':
    main()
