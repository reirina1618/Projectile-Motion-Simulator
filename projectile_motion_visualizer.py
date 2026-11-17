import pygame
import pygame_gui
import math
from pathlib import Path

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500

pygame.init()

win=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Projectile Motion')

crashed=False
clock=pygame.time.Clock()

theme_path = Path(__file__).resolve().parent / "style.json"
font = pygame.font.SysFont("segoeui", 20)

print(theme_path)
print(theme_path.exists())

manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path=str(theme_path))

background=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
background.fill(pygame.Color(180,180,180))

#interactables
launchButton=pygame_gui.elements.UIButton(relative_rect=pygame.Rect(0,-75,200,50),
                                        text='Launch',
                                        manager=manager,anchors={'centerx': 'centerx',
                                                                 'bottom': 'bottom'})

resetButton=pygame_gui.elements.UIButton(relative_rect=pygame.Rect(25,10,100,50),
                                        text='Reset',
                                        manager=manager,anchors={'left': 'left',
                                                                 'top': 'top'})

textInputTheta=pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(50,-75,50,40),
                                              anchors={'left':'left',
                                                        'bottom': 'bottom'},object_id=pygame_gui.core.ObjectID(class_id="@input",
                                                                                               object_id="#input_theta"))
textInputU=pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(50+50+75,-75,50,40),
                                              anchors={'left':'left',
                                                        'bottom': 'bottom'},object_id=pygame_gui.core.ObjectID(class_id="@input",
                                                                                               object_id="#input_u"))
textInputH=pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(50+2*50+2*75,-75,50,40),
                                              anchors={'left':'left',
                                                        'bottom': 'bottom'},object_id=pygame_gui.core.ObjectID(class_id="@input",
                                                                                               object_id="#input_h"))
instructionsButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(-25-100,10,100,50),
                                                  anchors={
                                                      'right':'right',
                                                      'top':'top'},
                                                  text="Instructions",
                                                  manager=manager
)

def drawArrow(win, color, startPoint, endPoint, width=2):
    start = pygame.Vector2(startPoint)
    end = pygame.Vector2(endPoint)

    direction = end - start

    if direction.length() == 0:
        return

    direction = direction.normalize()

    pygame.draw.line(win, color, start, end, width)

    arrowLength = 12
    arrowAngle = math.radians(30)

    left = end + direction.rotate(180 - math.degrees(arrowAngle))*arrowLength
    right = end + direction.rotate(180 + math.degrees(arrowAngle))*arrowLength

    pygame.draw.polygon(win, color, [end, left, right])

class projectile(object):
    def __init__(self,x,y,radius,color,scale):
        self.x=x
        self.y=y
        self.radius=radius
        self.color=color
        self.scale=scale
    def draw(self,win):
        pygame.draw.circle(win, (75,75,75), (self.x,self.y), self.radius)
        pygame.draw.circle(win, self.color, (self.x,self.y), self.radius-1)

    def trajectory(self,x0,y0,u,theta,t):
        angle=theta*(math.pi/180)
        ux=math.cos(angle)*u
        uy=math.sin(angle)*u

        dsx=(ux*t)*self.scale
        dsy=(uy*t+(-4.9*(t**2)))*self.scale

        sx=round(x0+dsx)
        sy=round(y0-dsy)

        return(sx,sy)

    def drawTrajectory(self,win,x0,y0,u,theta):
        points=[]

        angle=theta*math.pi/180
        time=(u*math.sin(angle)+math.sqrt((u**2*math.sin(angle)**2)+4*4.9*(groundY-y0)/(self.scale)))/9.8

        for i in range(101):
            t=time*i/100
            pos=self.trajectory(x0,y0,u,theta,t)
            points.append(pos)

        pygame.draw.aalines(win,(150,150,150),False,points,2)

ball=projectile(20,SCREEN_HEIGHT-20-1-(10*10),20,'white',10)

time=0
elapsedTime=0
u=30
th=45
anglerad=math.radians(th)
shoot=False
resettedX=ball.x
resettedY=ball.y
groundY=resettedY
maxHeight=((groundY-resettedY)/ball.scale)+((u*math.sin(math.radians(th)))**2/19.6)
maxY=groundY-maxHeight*ball.scale
maxX=resettedX+((u*math.cos(math.radians(th))*(u*math.sin(math.radians(th)))/9.8))*ball.scale
time30=(u*math.sin(math.radians(45))+math.sqrt((u**2*math.sin(math.radians(45))**2)+4*4.9*(groundY-resettedY)/(ball.scale)))/9.8
apexTime=0
s30=30*math.cos(math.radians(45))*time30
uMax=(9.8*s30)/(math.cos(anglerad)*math.sqrt(2*(9.8*((groundY-resettedY)/ball.scale)+9.8*s30*math.tan(anglerad))))
v=u*math.sin(anglerad)-9.8*time
passedHighestPoint=False
resetted=True

while not crashed:
    dt=clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed=True
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == launchButton and resetted:
            if not shoot:
                x=ball.x
                y=ball.y
                shoot=True
                passedHighestPoint=False
                resetted=False
        if event.type==pygame_gui.UI_BUTTON_PRESSED and event.ui_element == instructionsButton:
            instructionsWindow = pygame_gui.elements.UIWindow(rect=pygame.Rect(200, 100, 600, 300),
                                                            manager=manager,
                                                            window_display_title="Instructions",
                                                            object_id="#instructionsWindow"
            )
            instructionsText = pygame_gui.elements.UITextBox(
            html_text=f"<b>INPUT RESTRICTIONS</b><br>" \
            f"- θ must be between 0° and 90°<br>"
            f"- Max u (initial speed) for θ = {th} is {round(uMax)} m/s and u must be larger than 0<br>"
            f"- Max h (initial height) must not exceed 33 m<br>"
            f"- Input must always be integers<br>"
            f"<b>CONTROLS</b><br>"
            f"- Press enter to confirm the inputted values<br>"
            f"- Click the reset button before launching again<br>"
            f"<b>NOTE: AIR RESISTANCE IS IGNORED IN THIS SIMULATION</b>",
            relative_rect=pygame.Rect(10, 10, 560, 250),
            manager=manager,
            container=instructionsWindow
            )
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == resetButton and not resetted:
            shoot=False
            ball.x=resettedX
            ball.y=resettedY
            resetted=True
            passedHighestPoint=False
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and resetted:
            if event.ui_object_id=="#input_theta":
                try:
                    th=abs(int(event.text))
                    if th>0 and th%90!=0:
                        th=th%90
                        anglerad=math.radians(th)
                        uMax=(9.8*s30)/(math.cos(anglerad)*math.sqrt(2*(9.8*((groundY-resettedY)/ball.scale)+9.8*s30*math.tan(anglerad))))
                    elif th%90==0 and th%180!=0:
                        th=90
                        anglerad=math.radians(th)
                        uMax=30*math.sin(math.radians(45))
                    elif th%180==0:
                        th=0
                        anglerad=math.radians(th)
                        try:
                            uMax=(9.8*s30)/(math.cos(anglerad)*math.sqrt(2*(9.8*((groundY-resettedY)/ball.scale)+9.8*s30*math.tan(anglerad))))
                        except ZeroDivisionError:
                            uMax=50
                    if u>uMax:
                        u=uMax
                    maxHeight=((groundY-resettedY)/ball.scale)+((u*math.sin(math.radians(th)))**2/19.6)
                    maxY=groundY-maxHeight*ball.scale
                    maxX=resettedX+((u*math.cos(math.radians(th))*(u*math.sin(math.radians(th)))/9.8))*ball.scale
                    v=u*math.sin(anglerad)-9.8*time
                    break
                except ValueError:
                    pass
            if event.ui_object_id == "#input_u":
                try:
                    u=int(event.text)
                    if 0<u<=round(uMax):
                        maxHeight=((groundY-resettedY)/ball.scale)+((u*math.sin(math.radians(th)))**2/19.6)
                        maxY=groundY-maxHeight*ball.scale
                        maxX=resettedX+((u*math.cos(math.radians(th))*(u*math.sin(math.radians(th)))/9.8))*ball.scale
                        v=u*math.sin(anglerad)-9.8*time
                    else:
                        print("Initial velocity (u) must be larger than 0 and smaller than 30 ms^-1")
                        u=uMax
                        maxHeight=((u*math.sin(math.radians(th)))**2/19.6)
                        maxY=groundY-maxHeight*ball.scale
                        maxX=resettedX+((u*math.cos(math.radians(th))*(u*math.sin(math.radians(th)))/9.8))*ball.scale
                        v=u*math.sin(anglerad)-9.8*time
                    break
                except ValueError:
                    pass
            if event.ui_object_id == "#input_h":
                try:
                    ball.y=groundY-abs(int(event.text))*ball.scale
                    if ball.y>2*ball.radius:
                        ball.y=groundY-abs(int(event.text))*ball.scale
                        resettedY=ball.y
                        maxHeight=abs(int(event.text))+((u*math.sin(math.radians(th)))**2/19.6)
                        maxY=groundY-maxHeight*ball.scale
                        maxX=resettedX+((u*math.cos(math.radians(th))*(u*math.sin(math.radians(th)))/9.8))*ball.scale
                        uMax=(9.8*s30)/(math.cos(anglerad)*math.sqrt(2*(9.8*((groundY-resettedY)/ball.scale)+9.8*s30*math.tan(anglerad))))
                        v=u*math.sin(anglerad)-9.8*time
                    else:
                        ball.y=groundY-abs(33)*ball.scale
                        resettedY=ball.y
                        maxHeight=((u*math.sin(math.radians(th)))**2/19.6)
                        maxY=groundY-maxHeight*ball.scale
                        maxX=resettedX+((u*math.cos(math.radians(th))*(u*math.sin(math.radians(th)))/9.8))*ball.scale
                        uMax=(9.8*s30)/(math.cos(anglerad)*math.sqrt(2*(9.8*((groundY-resettedY)/ball.scale)+9.8*s30*math.tan(anglerad))))
                        v=u*math.sin(anglerad)-9.8*time
                    if u>uMax:
                         u=uMax
                    break
                except ValueError:
                    pass
                    

        manager.process_events(event)

    tText=font.render(f"t = {time:.2f} s",True,"black")
    tRect=tText.get_rect(
        topleft=(25,75)
    )

    manager.update(dt)
    win.blit(background,(0,0))
    pygame.draw.rect(win,(210,210,210),pygame.Rect(0,SCREEN_HEIGHT-20-1-(10*10),SCREEN_WIDTH,(u**2/19.6)*ball.scale-(ball.radius-(ball.scale*10))))
    if shoot:
            if ball.y<SCREEN_HEIGHT-ball.radius-(ball.scale*10):
                time+=dt
                prevX=ball.x
                prevY=ball.y
                pos=ball.trajectory(x,y,u,th,time)
                ball.x=pos[0]
                ball.y=pos[1]
                drawArrow(win,(150,150,150),(ball.x,ball.y),(round(ball.x+ball.scale*u*math.cos(math.radians(th))),ball.y),2)
                drawArrow(win,(150,150,150),(ball.x,ball.y),(ball.x,round(ball.y-(ball.scale*(u*math.sin(math.radians(th))-9.8*time)))),2)
                tText=font.render(f"t = {time:.2f} s",True,"black")
                tRect=tText.get_rect(
                    topleft=(25,75)
                )
                v=u*math.sin(anglerad)-9.8*time
                if ball.y>prevY:
                    passedHighestPoint=True
                    apexTime=u*math.sin(anglerad)/9.8
                
            else:
                v=u*math.sin(anglerad)-9.8*time
                shoot=False
                elapsedTime=time
                time=0
                ball.y=SCREEN_HEIGHT-ball.radius-1-(ball.scale*10)
    if not shoot:
        ball.drawTrajectory(win,resettedX,resettedY,u,th)
        if resetted:
            if th<90 and th>0:
                drawArrow(win,(150,150,150),(ball.x,ball.y),(round(ball.x+ball.scale*u*math.cos(math.radians(th))),ball.y),2)
                drawArrow(win,(150,150,150),(ball.x,ball.y),(ball.x,round(ball.y-ball.scale*(u*math.sin(math.radians(th))-9.8*time))),2)
                drawArrow(win,'black',(ball.x,ball.y),(round(ball.x+ball.scale*u*math.cos(math.radians(th))),round(ball.y-(u*ball.scale*math.sin(math.radians(th))))),2)
                arcsize=100*u*math.cos(anglerad)/(30*math.cos(45))
                pygame.draw.arc(win,'black',pygame.Rect(ball.x-arcsize/2,ball.y-arcsize/2,arcsize,arcsize),0,math.radians(th))
            elif th==90:
                drawArrow(win,(150,150,150),(ball.x,ball.y),(ball.x,round(ball.y-(ball.scale*u*math.sin(math.radians(th))))),2)
            elif th==0:
                drawArrow(win,(150,150,150),(ball.x,ball.y),(round(ball.x+ball.scale*u*math.cos(math.radians(th))),ball.y),2)
            thetaText=font.render(f"θ = {th}",True,"black")
            thetaRect=thetaText.get_rect(
                center=(ball.x+100,round(ball.y-(2*ball.scale**2*math.sin(math.radians(th))))+round((5/3)*th+25))
            )
            uValText=font.render(f"u = {u:.0f} m/s",True,"black")
            uValRect=thetaText.get_rect(
                center=(ball.x+100,round(ball.y-(2*ball.scale**2*math.sin(math.radians(th))))+round((5/3)*th+50))
            )
            win.blit(thetaText,thetaRect)
            win.blit(uValText,uValRect)
        else:
            tText=font.render(f"t = {elapsedTime:.2f} s",True,"black")
            tRect=tText.get_rect(
                topleft=(25,75)
            )
    if passedHighestPoint:
        heightText = font.render(f"Max height = {maxHeight:.2f} m\nTime elapsed = {apexTime:.2f}", True, "black")

        height_rect = heightText.get_rect(
            midtop=(maxX, maxY+60)
        )
        if maxX<0+heightText.get_width() or maxY<0+heightText.get_height() or maxY>SCREEN_HEIGHT-20-1-(10*10)-heightText.get_height():
            height_rect = heightText.get_rect(
                        topleft=(25, 250)
                    )
        drawArrow(win,(150,150,150),(resettedX+apexTime*(u*math.cos(anglerad))*ball.scale,groundY),(resettedX+apexTime*(u*math.cos(anglerad))*ball.scale,maxY),2)
        drawArrow(win,(150,150,150),(resettedX+apexTime*(u*math.cos(anglerad))*ball.scale,maxY),(resettedX+apexTime*(u*math.cos(anglerad))*ball.scale,groundY),2)
        win.blit(heightText,height_rect)
    theta=font.render(f"θ =",True,"black")
    thetaRectmain=thetaText.get_rect(
        topleft=(10,SCREEN_HEIGHT-70)
    )
    uText=font.render(f"u =",True,"black")
    uRect=uText.get_rect(
        topleft=(10+50+75,SCREEN_HEIGHT-70)
    )
    hText=font.render(f"h =",True,"black")
    hRect=uText.get_rect(
        topleft=(10+2*(50+75),SCREEN_HEIGHT-70)
    )
    suvatXText=font.render(f"sₓ = {(ball.x-resettedX)/ball.scale:.2f}\nuₓ={u*math.cos(anglerad):.2f}\nvₓ={u*math.cos(anglerad):.2f}",True,"black")
    suvatYText=font.render(f"sᵧ = {(resettedY-ball.y)/ball.scale:.2f}\nuᵧ={u*math.sin(anglerad):.2f}\nvᵧ={v:.2f}",True,"black")
    suvatYRect=suvatYText.get_rect(
            bottomright=(SCREEN_WIDTH-20,SCREEN_HEIGHT-20)
        )
    suvatXRect=suvatXText.get_rect(
                bottomright=(SCREEN_WIDTH-20-25-suvatYText.get_width(),SCREEN_HEIGHT-20)
            )
    ball.draw(win)
    win.blit(theta,thetaRectmain)
    win.blit(uText,uRect)
    win.blit(hText,hRect)
    win.blit(tText,tRect)
    win.blit(suvatXText,suvatXRect)
    win.blit(suvatYText,suvatYRect)
    manager.draw_ui(win)
    pygame.display.update()