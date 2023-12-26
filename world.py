# ---------- library ----------

import sys
from random import *
from typing import Any
import pygame
import time
from collections import deque
from math import * 
from collections import deque
import os
import numpy
import matplotlib.pyplot as plt
from pygame.locals import QUIT,KEYDOWN,K_LEFT,K_RIGHT,K_UP,K_DOWN,Rect,MOUSEBUTTONDOWN,K_SPACE,K_a,K_x,K_z,K_LCTRL,K_RCTRL ,K_d



# ---------- keyword ----------
# velocity : v
# object type : obj_t
# detection : dt
# radius : r
# inclination : I (기울기)
# transition : (변이 정도)
# descendants : (자손 생성을 위한 최소 음식)
# nod : number of descendants = OBJECT_count
# CL : class list
# noj : number of object
# -----------------------------
# -------- result name --------
while 1:
    result_name=input("결과를 저장할 파일 이름을 알려주세요.")
    result_path=f"./result/{result_name}/"
    if os.path.isdir(result_path):
        print("이미 파일이 있습니다. 다른 이름을 알려주세요.")
    else:
        os.mkdir(result_path)
        os.mkdir(f"./graph/object_count/{result_name}")
        break

# -----------------------------
pygame.init()
FPSCLOCK = pygame.time.Clock()
real_width=1600
real_height=1000
width=1000
height=1000
fps=60#100
size=(width,height)
real_size=(real_width,real_height)
SURFACE = pygame.display.set_mode(real_size)
color={
    "black":[0,0,0],
    "white":[255,255,255],
    "red":[255,0,0],
    "blue":[0,0,255],
    "yellow":[255,255,0],
    "green":[0,255,0],
    "gray":[192,192,192],
    "cyan":[0,183,235],
    "purple":[106,13,173],
    "orange":[249,146,69],
    }

#----------- status -----------
FOOD_size=20
OBJECT_velocity=10 
OBJECT_size=30
OBJECT_descendants=[3,2,4,6]
OBJECT_nod=[100,6,3,1]
OBJECT_detection=20
OBJECT_transition=10
FOOD_count=1000#randint(100,200)
OBJECT_count=[5,5,5]#randint(10,30)#randint(600,700)#(100,0)
OBJECT_max_eat_stack=[inf,inf,inf,inf]#0,7,4,2]
start_fc=FOOD_count
start_oc=OBJECT_count
energy_status={"food":500} #value

#----------- setting -----------
DAY=0
start_moving=0
Eat_food=0
daytime=60 #seconds
left_time=time.time()
last_time=0
stop_moving=1
decrease_food=False
decrease_day=0
maintain_day=0
DAM_day=[] # DAM : Decrease And Maintain, 
OBJECT_CL=[]
OBJECT_NAME=["food","level_1","level_2","level_3"]
safety_zone=[[0,0,200,200],[width-200,0,200,200],[0,height-200,200,200]]


def O_division_F_wall():
    pygame.draw.line(SURFACE, color["yellow"], [width+10,0], [width+10,height], 5)
    pygame.draw.rect(SURFACE, color["red"], safety_zone[0],5)
    pygame.draw.rect(SURFACE, color["purple"], safety_zone[1],5)
    pygame.draw.rect(SURFACE, color["blue"], safety_zone[2],5)
    #pygame.draw.line(SURFACE, color["red"], [100-FOOD_size,100-FOOD_size], [width-100+FOOD_size,100-FOOD_size], 5)
    #pygame.draw.line(SURFACE, color["purple"], [100-FOOD_size,100-FOOD_size], [100-FOOD_size,height-100+FOOD_size], 5)
    #pygame.draw.line(SURFACE, color["blue"], [width-100+FOOD_size,100-FOOD_size], [width-100+FOOD_size,height-100+FOOD_size], 5)

def print_n_txt(f,txt):
    print(txt)
    f.write(txt+"\n")

def Cos(angle):
    return cos(radians(angle))

def Sin(angle):
    return sin(radians(angle))

def Atan2(A,B):
    return 180-atan2(A,B)*(180/pi)

def text_draw(text,pos,size):
    font = pygame.font.SysFont("arial", size, True, False)
    text_Title= font.render(str(text), True, color["black"])
    Rect=text_Title.get_rect()
    Rect.centery=pos[1]
    Rect.x=pos[0]
    SURFACE.blit(text_Title, Rect)
    
    
def pos_angle(A,B): # A : object, B : next destination
        
    return Atan2(B[0]-A[0],B[1]-A[1]) #x,y | (future pos)-(present pos)

def distance(A,B):
    return sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2) 

def CCW(posA,posB,posC):
    R=(posA[1]-posB[1])*(posC[0]-posA[0])-(posA[0]-posB[0])*(posC[1]-posA[1])
    if R>0:return 1
    elif R<0:return -1
    else:return 0

class Genetic():
    def __init__(self,start_gene):
        self.gene=start_gene # [OBJECT_velocity,OBJECT_detection]

    def fitness(self,gene):
        V=0
        return V
    
class Graph_Drawing():
    def __init__(self,graph_path):
        self.SURFACE=SURFACE
        self.graph_path=graph_path
        self.lastx=[]
        
    def graph_draw(self,x,y):
        if self.lastx==x:return
        plt.clf()
        for i in range(len(DAM_day)):
            color = 'b' if DAM_day[i]=='m' else 'r'
            plt.plot(x[i:min(len(x),i+2)],y[i:min(len(y),i+2)],color)
        #plt.xlim([0,i*len(x)])
        plt.title(f'Object count')
        #plt.show()
        plt.savefig(self.graph_path)
        self.lastx=x
        
        
    def background_draw(self,x,y):
        try:
            img=pygame.image.load(self.graph_path)
            rect=img.get_rect()
            img=pygame.transform.scale(img,(rect.width/1.1,rect.height/1.1))
            rect=img.get_rect()
            rect.center=(x,y)
            self.SURFACE.blit(img,rect)
        except:
            return
    


class Object(pygame.sprite.Sprite):
    def __init__(self,v,dt,obj_t,obj_size,food_size,energy_value={"food":1},energy=0,make_descendants_max=5,image_name="red_object",start_pos=None):
        pygame.sprite.Sprite.__init__(self)
        self.SURFACE=SURFACE
        
        self.x=0
        self.y=0
        
        # object status
        self.v = v
        self.obj_t=obj_t
        self.obj_size=obj_size
        self.food_size=food_size/2
        self.image_name=image_name
        self.tarcking=False
        
        
        if image_name=="red_object":
            self.num=1
        if image_name=="blue_object":
            self.num=2
        if image_name=="purple_object":
            self.num=3
        
        # 인식 범위가 너무 커지면 태어나자마자 모든 음식을 먹게 되기 때문에 개체가 게을러지고, 수가 증가함 => 최대 인식 범위 설정
        self.dt = max(self.obj_size/2,dt) # r
        self.dt = min(self.dt,int(width/6))
        
        self.font = pygame.font.SysFont("arial", obj_size//3*2, True, False)
        self.energy=energy
        self.energy_value=energy_value
        self.moving_distance=0
        self.make_descendants_max=make_descendants_max
        self.make_descendants=0

        # afterimage food
        self.food_image=pygame.image.load(f"./object/{image_name}.png").convert_alpha()
        self.food_image=pygame.transform.scale(self.food_image,(self.obj_size,self.obj_size))
        self.mask=pygame.mask.from_surface(self.food_image)
        self.rect=self.food_image.get_rect()
        if start_pos==None:
            POS=self.start_pos()
        else:
            POS=start_pos
        self.move(POS)
        self.eat_food=0
        self.last_food=0

        # fake food
        self.food_next_image=pygame.image.load(f"./object/{image_name}.png").convert_alpha()
        self.food_next_image=pygame.transform.scale(self.food_next_image,(1,1))#(self.obj_size/2,self.obj_size/2))
        self.food_next_image.set_alpha(128)
        self.next_rect=self.food_next_image.get_rect()

        # food pos
        self.food_pos=[None,None]

        self.next_pos()
        
    #def energy_calculate(self):
    #    self.energy=self.eat_food*self.energy_value["food"]

    def Eat(self,pos):
        # 실제 좌표 체계와 코딩에서 좌표체계가 다르기 때문에 바꿔줌
        self.y=height-self.y
        pos[1]=height-pos[1]
        
        N_P=[self.move_distance[0]+self.x,self.y+self.move_distance[1]]
          
        
        # 두 개체 접촉    
        #if distance(pos,[self.x,self.y])<=self.obj_size+self.food_size or \
        #    distance(pos,N_P)<=self.obj_size+self.food_size:
        #    return 1
            
        #print("I",I)
        # y = A(x-p)+q -> Ax -pA+q
        # line dot distance => abs(A*(pos[0])-(pos[1])-(self.x)*A+self.y)/sqrt(A**2+1)
        if distance(pos,[self.x,self.y])<=self.dt+self.food_size or \
            distance(pos,N_P)<=self.dt+self.food_size:
            return 1

        if self.move_distance[0]==0:
            line_dot_distance=abs(pos[0]-self.x)
            if line_dot_distance>self.dt:
                return 0


            # dot right angle function => (-1/A)(x-p)+q ->
            
            for extension_x in [-10000,10000]:
                extension_y=pos[1]

                # self.x, self.y, self.x+self.move_distance[0], self.y+self.move_distance[1]
                # pos[0], pos[1], extension_x, extension_y

                #CCW
                A=[self.x, self.y]
                B=N_P
                C=[pos[0], pos[1]]
                D=[extension_x, extension_y]

                if A>B:A,B=B,A
                if C>D:C,D=D,C

                chk=CCW(A,B,C)*CCW(A,B,D)
                chk1=CCW(C,D,A)*CCW(C,D,B)
                ans=(chk<=0 and chk1<=0)
                
                if chk==0 and chk1==0:
                    if A<=D and B>=C:ans=1
                    else:ans=0

                if ans:
                    return 1
                
            return 0

        I=self.move_distance[1]/self.move_distance[0]

        line_dot_distance=abs(I*(pos[0])-(pos[1])-(self.x)*I+self.y)/sqrt(I**2+1)
        if line_dot_distance>self.dt:
            return 0


        # dot right angle function => (-1/A)(x-p)+q ->
        
        for extension_x in [-10000,10000]:
            extension_y=(-1/I)*(extension_x-pos[0])+pos[1]

            # self.x, self.y, self.x+self.move_distance[0], self.y+self.move_distance[1]
            # pos[0], pos[1], extension_x, extension_y

            #CCW
            A=[self.x, self.y]
            B=N_P
            C=[pos[0], pos[1]]
            D=[extension_x, extension_y]

            if A>B:A,B=B,A
            if C>D:C,D=D,C

            chk=CCW(A,B,C)*CCW(A,B,D)
            chk1=CCW(C,D,A)*CCW(C,D,B)
            ans=(chk<=0 and chk1<=0)
            
            if chk==0 and chk1==0:
                if A<=D and B>=C:ans=1
                else:ans=0

            if ans:
                return 1



        """I=self.move_distance[1]/self.move_distance[0]
        #print("I",I)
        # y = A(x-p)+q -> Ax -pA+q
        # line dot distance => abs(A*(pos[0])-(pos[1])-(self.x)*A+self.y)/sqrt(A**2+1)
        if distance(pos,[self.x,self.y])<=self.dt+self.food_size or \
            distance(pos,[self.move_distance[0]+self.x,self.y+self.move_distance[1]])<=self.dt+self.food_size:
            return 1

        line_dot_distance=abs(I*(pos[0])-(pos[1])-(self.x)*I+self.y)/sqrt(I**2+1)
        if line_dot_distance>self.dt:
            return 0


        # dot right angle function => (-1/A)(x-p)+q ->
        
        for extension_x in [-10000,10000]:
            extension_y=(-1/I)*(extension_x-pos[0])+pos[1]

            # self.x, self.y, self.x+self.move_distance[0], self.y+self.move_distance[1]
            # pos[0], pos[1], extension_x, extension_y

            #CCW
            A=[self.x, self.y]
            B=[self.x+self.move_distance[0], self.y+self.move_distance[1]]
            C=[pos[0], pos[1]]
            D=[extension_x, extension_y]

            if A>B:A,B=B,A
            if C>D:C,D=D,C

            chk=CCW(A,B,C)*CCW(A,B,D)
            chk1=CCW(C,D,A)*CCW(C,D,B)
            ans=(chk<=0 and chk1<=0)
            
            if chk==0 and chk1==0:
                if A<=D and B>=C:ans=1
                else:ans=0

            if ans:
                return 1"""

        return 0

    def slow_move(self):
        NEXT=self.destination
            
        if distance([self.x,self.y],NEXT)<=self.v:
            self.move(NEXT)
            #print("####")
            #print("BXCVERFSDFSDF")
            self.next_pos()
        else:
            self.move([self.x+self.move_distance[0],self.y-self.move_distance[1]])
            
        #print("MOVE")
        #print(self.x,self.y)
        #print(self.destination)
        
        

    def next_pos(self,pos=None):
        #safety_zone=[[0,0,200,200],[width-200,0,200,200],[0,height-200,200,200]]
        if pos==None:
            self.tarcking=False
            self.destination=[randint(self.obj_size/2,width-self.obj_size/2),randint(self.obj_size/2,height-self.obj_size/2)]
                
                    
        else:
            self.tarcking=True
            self.destination=pos
            
            
        self.next_rect.center=self.destination
        self.next_move_angle=pos_angle([self.x,self.y],self.destination)
        self.move_distance=[Sin(self.next_move_angle)*self.v,Cos(self.next_move_angle)*self.v]

    def move(self,pos):
        self.moving_distance+=distance((self.x,self.y),pos)
        self.x=pos[0]
        self.y=pos[1]
        self.rect.center=(self.x,self.y)
            

    def draw(self):
        pygame.draw.circle(SURFACE, color["black"], self.rect.center, self.dt,3)
        self.SURFACE.blit(self.food_image,self.rect)
        #self.SURFACE.blit(self.food_next_image,self.next_rect)
        #pygame.draw.line(SURFACE, color["blue"], [self.x,self.y], [self.move_distance[0]+self.x,self.y-self.move_distance[1]], 5)
        text_Title= self.font.render(str(int(self.eat_food)), True, color["black"])
        Rect=text_Title.get_rect()
        Rect.center=self.rect.center     
        self.SURFACE.blit(text_Title, Rect)

    def start_pos(self):
        #self.image_name
        if self.image_name=="red_object": # 왼쪽 위
            return [randint(self.obj_size/2,200-self.obj_size/2),randint(self.obj_size/2,200-self.obj_size/2)]
        elif self.image_name=="purple_object": #오른쪽 위
            return [randint(width-200+self.obj_size/2,width-self.obj_size/2),randint(self.obj_size/2,200-self.obj_size/2)]
        elif self.image_name=="blue_object": # 왼쪽 아래
            return [randint(self.obj_size/2,200-self.obj_size/2),randint(height-200+self.obj_size/2,height-self.obj_size/2)]
            
            
    def using_energy(self):
        #print("distance energy :",max(1,self.v/10) * max(0.1,self.moving_distance/1000))
        use_food=min(self.eat_food,self.moving_distance//self.energy_value["food"])
        self.eat_food-=use_food
        #print("##",max(1,self.v/10) * max(1,self.moving_distance-use_food*self.energy_value["food"]))
        if self.moving_distance-use_food*self.energy_value["food"]<=0 or self.v/10 <=0: return 0
        self.moving_distance=0
        return max(1,self.v/10) * max(1,self.moving_distance-use_food*self.energy_value["food"])
    
    def use_up(self):
        self.energy-=self.using_energy()
    
    def Eat_food(self,energy=0):
        if self.last_food+1<OBJECT_max_eat_stack[self.num]:
            self.eat_food+=1
            self.last_food+=1
            self.energy+=energy/10
            return 1
        return 0
       
#v,dt,obj_t,obj_size,food_size,energy_value={"food":1},energy=0,make_descendants_max=5       
        
class Population(pygame.sprite.Sprite):
    def __init__(self,noj,enable_object_name,object_type="level_1",object_image="green"):
        self.enable_object_name=enable_object_name
        self.OT=object_type
        self.noj=noj
        self.OBJECT_CL=[]
        self.init_noj=noj
        self.record=[]
        self.object_image=object_image
        self.GD=Graph_Drawing(f'./graph/object_count/{result_name}/{self.OT}.png')
        self.txt_path=result_path+f"{self.OT}.txt"
        self.record.append([record_dictionary([OBJECT_velocity]*self.noj),
                            record_dictionary([OBJECT_detection]*self.noj)])
        
        if object_image=="green":
            self.num=0
        if object_image=="red":
            self.num=1
        if object_image=="blue":
            self.num=2
        if object_image=="purple":
            self.num=3
        
        self.OBJECT=[]
        if self.OT=="food":
            self.OBJECT=[
                Food(randint(100,width-100), # random x pos
                     randint(100,height-100), # random y pos
                     FOOD_size) # food size
                for i in range(self.noj)]
        else:
            self.OBJECT=[
                Object(OBJECT_velocity, #velocity
                    OBJECT_detection, # detection 
                    self.OT, # object type
                    OBJECT_size, # object size
                    FOOD_size, # food size
                    energy_status, # energy status
                    energy=0, # init energy
                    make_descendants_max=OBJECT_nod[self.num], # number of making descendants 
                    image_name=f"{object_image}_object")
                for _ in range(self.noj)]
        
            
    def Object_update(self):
        pop_idx=[]
        new_object=[]
        velocity=[]
        detection=[]
        draw_stack=0
        for i in range(self.noj):
            #velocity.append(self.OBJECT[i].v)
            #detection.append(self.OBJECT[i].dt)
            
            if DAY>1:
                #print("before energy",OBJECT[i].energy)
                self.OBJECT[i].use_up()
                #print("after energy :",OBJECT[i].energy)

            self.OBJECT[i].make_descendants=0
            if self.OBJECT[i].energy<0:
                #print("CCC")
                pop_idx.append(i)
            else:
                #print(OBJECT[i].last_food,OBJECT[i].eat_food)
                if self.OBJECT[i].last_food==0 and DAY>1:
                    if self.OBJECT[i].energy<0:
                        #print("!!!")
                        pop_idx.append(i)
                else:
                    descendants_energy=self.OBJECT[i].energy/2
                    while self.OBJECT[i].last_food>=OBJECT_descendants[self.num] and self.OBJECT[i].make_descendants+1<=self.OBJECT[i].make_descendants_max: # /update/ 자손을 낳을 때마다 부모의 에너지를 뺏는 거 구현
                        self.OBJECT[i].make_descendants+=1
                        #self.OBJECT[i].last_food-=OBJECT_descendants
                        
                    if self.OBJECT[i].make_descendants>0:
                        offspring=randint(0,self.OBJECT[i].make_descendants)
                        self.OBJECT[i].last_food-=OBJECT_descendants[self.num]*offspring
                        self.OBJECT[i].energy/=2
                        #print("---------")
                        #print(offspring)
                        for _ in range(offspring):
                            new_object.append([self.OBJECT[i].v,
                                               self.OBJECT[i].dt,
                                               descendants_energy/offspring,
                                               [self.OBJECT[i].x,self.OBJECT[i].y]
                                               ]) # 현재 객체가 가지고 있는 에너지의 반을 뺏김 -> 반만큼을 자손에게 균등 분배
                    #POS=self.OBJECT[i].start_pos()
                    #self.OBJECT[i].move(POS)
                    #self.OBJECT[i].next_pos()
                    #if draw_stack<=100:
                    #    self.OBJECT[i].draw()
                    #draw_stack+=1    
                    
            #self.OBJECT[i].last_food=0
            #self.OBJECT[i].make_descendants=0

        #print(pop_idx)
        #print("pop count",pop_idx)
        #print("object count",len(self.OBJECT))
        for i in range(len(pop_idx)-1,-1,-1):
            self.OBJECT.pop(pop_idx[i])
            self.noj-=1

        for i in range(len(new_object)):
            if len(self.OBJECT)<=1000:
                self.noj+=1
                self.OBJECT.append(Object(new_object[i][0],#randint(max(1,new_object[i][0]-OBJECT_transition*0),new_object[i][0]+OBJECT_transition*0),\
                        new_object[i][1],#randint(max(0,new_object[i][1]-OBJECT_transition*0),new_object[i][1]+OBJECT_transition*0),
                        1,\
                        OBJECT_size,
                        FOOD_size,
                        energy_status,
                        new_object[i][2],make_descendants_max=OBJECT_nod[self.num],image_name=f"{self.object_image}_object",
                        start_pos=new_object[i][3]))
            else:
                break

        shuffle(self.OBJECT)

        #velocity.sort()
        #detection.sort()

        #self.record.append([record_dictionary(velocity),record_dictionary(detection)])
        
    def mkt(self): #make txt
        if self.noj<=1 and DAY>1:
            #print("!!!!")
            f = open(self.txt_path+"","w")
            if self.init_noj<=1 and self.noj==1:
                print_n_txt(f,(str(self.OBJECT[0].v)+' '+str(self.OBJECT[0].dt)))
            print_n_txt(f,"END")
            print_n_txt(f,f"finish day is {DAY}")
            print_n_txt(f,"------------------------")
            print_n_txt(f,f"Object start Velocity : {OBJECT_velocity}")
            print_n_txt(f,f"Object size : {OBJECT_size}")
            print_n_txt(f,f"Object descendants : {OBJECT_descendants[self.num]}")
            print_n_txt(f,f"Object transition : {OBJECT_transition}")
            print_n_txt(f,f"Food size : {FOOD_size}")
            print_n_txt(f,f"Food start count : {start_fc}")
            print_n_txt(f,f"Object start count : {start_oc}")

            print_n_txt(f,"Velocity record")
            for i in range(len(self.record)):
                print_n_txt(f,f"day {i+1} : {self.record[i][0]}")
                
            print_n_txt(f,"")
            print_n_txt(f,"------------------------")
            print_n_txt(f,"")
                
            print_n_txt(f,"Detection record")
            for i in range(len(self.record)):
                print_n_txt(f,f"day {i+1} : {self.record[i][1]}")    
            print_n_txt(f,f"file name is {self.OT}")
            
            return 1
        
        return 0
       
    def draw(self):
        for i in range(min(30,self.noj)):
            self.OBJECT[i].draw()
            
              
            

class Food(pygame.sprite.Sprite):
    def __init__(self,x,y,size):
        pygame.sprite.Sprite.__init__(self)
        self.SURFACE=SURFACE
        self.food_image=pygame.image.load(f"./food/green_food.png").convert_alpha()
        self.food_size=size
        self.food_image=pygame.transform.scale(self.food_image,(self.food_size,self.food_size))
        self.mask=pygame.mask.from_surface(self.food_image)
        self.rect=self.food_image.get_rect()
        self.x=x
        self.y=y
        self.rect.center=(self.x,self.y)
        self.energy=energy_status["food"]

    def move(self,pos):
        self.x=pos[0]
        self.y=pos[1]
        self.rect.center=(self.x,self.y)
    
    def draw(self):
        self.SURFACE.blit(self.food_image,self.rect)
    
  
def eAm_obj(O_A,O_B): # Eat And Move (Population OBJECT_A, Population OBJECT_B)

    for i in range(O_A.noj):
        #MOVE=OBJECT[i].start_pos()
        #OBJECT[i].move(MOVE)
        if stop_moving==0:
            pop_idx=[]
            for g in range(O_B.noj):
                prey=list(O_B.OBJECT[g].rect.center)
                if O_B.num==1 and (safety_zone[0][0]<=prey[0]<=safety_zone[0][0]+safety_zone[0][2]or safety_zone[0][1]<=prey[1]<=safety_zone[0][1]+safety_zone[0][3]):
                    continue
                if O_B.num==2 and (safety_zone[1][0]<=prey[0]<=safety_zone[1][0]+safety_zone[1][2]or safety_zone[1][1]<=prey[1]<=safety_zone[1][1]+safety_zone[1][3]):
                    continue
                if O_B.num==3 and (safety_zone[2][0]<=prey[0]<=safety_zone[2][0]+safety_zone[2][2]or safety_zone[2][1]<=prey[1]<=safety_zone[2][1]+safety_zone[2][3]):
                    continue
                status=O_A.OBJECT[i].Eat(prey)
                O_A.OBJECT[i].y=height-O_A.OBJECT[i].y # 실제 좌표 체계와 코딩에서 좌표체계가 다르기 때문에 바꿔줌 (Eat 에서 바꿈)
                if status==1:
                    eat=O_A.OBJECT[i].Eat_food(O_B.OBJECT[g].energy)
                    if eat:
                        pop_idx.append(g)    
                    
                #if O_A.OBJECT[i].last_food>OBJECT_descendants*OBJECT_nod:
                #    return O_A,O_B
                
            for g in range(len(pop_idx)-1,-1,-1):
                O_B.OBJECT.pop(pop_idx[g])
                O_B.noj-=1
                
            O_A.OBJECT[i].slow_move()
                
            
    return O_A,O_B
    
def record_dictionary(data):
    range_v=10
    statistical_data={10:0}
    for i in range(len(data)):
        while data[i]>range_v:
            range_v+=10
            statistical_data[range_v]=0

        statistical_data[range_v]+=1
    return statistical_data


#----------- gene list -----------
gene=[OBJECT_velocity,OBJECT_detection]

#---------------------------------

"""
    FOOD_size=20
    OBJECT_velocity=10 
    OBJECT_size=30
    OBJECT_descendants=39999
    OBJECT_nod=5
    OBJECT_detection=150
    OBJECT_transition=10
    FOOD_count=randint(500,600)
    OBJECT_count=10#randint(10,30)#randint(600,700)#(100,0)
    start_fc=FOOD_count
    start_oc=OBJECT_count
    energy_status={"food":500} #value

"""


ECOSYSTEM=[Population(FOOD_count,[],"food"),
           Population(OBJECT_count[0],["food"],"level_1","red"),
           Population(OBJECT_count[1],["level_1"],"level_2","blue"),
           Population(OBJECT_count[2],["level_2"],"level_3","purple")]
move=[1,0,0,0]

while 1:
    SURFACE.fill(color["gray"])
    # press start key
    for EVENT in pygame.event.get():
        if EVENT.type==QUIT:pygame.quit();sys.exit()
        if EVENT.type==pygame.KEYDOWN:
            if EVENT.key==pygame.K_SPACE:
                if stop_moving==0:
                    stop_moving=1
                    last_time=time.time()-left_time
                else:
                    stop_moving=0
                    left_time=time.time()
                    
            if EVENT.key==pygame.K_d:
                decrease_food = not decrease_food
                
            if EVENT.key==pygame.K_1:
                move[1]=not move[1]
                
            if EVENT.key==pygame.K_2:
                move[2]=not move[2]
                
            if EVENT.key==pygame.K_3:
                move[3]=not move[3]
                
            if EVENT.key==pygame.K_4:
                for i in range(len(ECOSYSTEM[1].OBJECT)-3):
                    ECOSYSTEM[1].OBJECT.pop(0)
                ECOSYSTEM[1].noj=3
            
                    

    # object count draw
    text_draw(f"Day : {DAY}",(1020,50),30)
    text_draw(f"Object count is : {OBJECT_count}",(1200,50),30)
    text_draw(f"FOOD count is : {FOOD_count}, last food count is {FOOD_count-Eat_food}",(1020,90),30)
    text_draw(f"Decrease food : {decrease_food}",(1020,170),30)
    if DAY>=1:
        text_draw(f"last time : {daytime-(last_time+time.time()-left_time)}",(1020,130),30)
        
    for population in ECOSYSTEM:
        population.GD.background_draw(width+(real_width-width)/2,real_height/2)
        

    # wall
    O_division_F_wall()

    #keys = pygame.key.get_pressed()
    
    if stop_moving==0 and time.time()-left_time>=daytime-last_time:
        start_moving=0

    # --------- start draw ---------
    if start_moving==0 and stop_moving==0:

        DAY+=1
        DAM_day.append("d" if decrease_food else "m")
        if decrease_food and move[0]:
            ECOSYSTEM[0].init_noj-=1
            
        #ECOSYSTEM[0].init_noj=max(ECOSYSTEM[0].init_noj,1)
        #ECOSYSTEM[0].noj=ECOSYSTEM[0].init_noj
        #ECOSYSTEM[0].OBJECT=[Food(randint(100,width-100),randint(100,height-100),FOOD_size)for i in range(ECOSYSTEM[0].noj)]
        
        for population in ECOSYSTEM:
            population.OBJECT_CL.append(population.noj)
            population.GD.graph_draw([Day for Day in range(len(population.OBJECT_CL))],population.OBJECT_CL)
             
        # division wall

        # OBJECT
        #OBJECT=[Object(OBJECT_velocity,OBJECT_detection,1,OBJECT_size,FOOD_size)for i in range(OBJECT_count)]
        """ECOSYSTEM[1].Object_update()
        ECOSYSTEM[2].Object_update()
        ECOSYSTEM[3].Object_update()"""
        
        last_time=0
        left_time=time.time()
        #ECOSYSTEM[0].draw()

        #pygame.display.update()
        """if ECOSYSTEM[1].mkt() and ECOSYSTEM[2].mkt() and ECOSYSTEM[3].mkt():
            sys.exit()"""
        #sys.exit()
        #pygame.time.delay(500)
        start_moving=1

    # --------- draw --------- 
    if stop_moving==0:
        # OBJECT
        if move[1] and move[0]:
            ECOSYSTEM[1],ECOSYSTEM[0]=eAm_obj(ECOSYSTEM[1],ECOSYSTEM[0])
            
        if move[3] and move[2]:
            ECOSYSTEM[3],ECOSYSTEM[2]=eAm_obj(ECOSYSTEM[3],ECOSYSTEM[2])
            #ECOSYSTEM[3],ECOSYSTEM[1]=eAm_obj(ECOSYSTEM[3],ECOSYSTEM[1])
            #ECOSYSTEM[3],ECOSYSTEM[0]=eAm_obj(ECOSYSTEM[3],ECOSYSTEM[0])
            
        if move[2] and move[1]:
            ECOSYSTEM[2],ECOSYSTEM[1]=eAm_obj(ECOSYSTEM[2],ECOSYSTEM[1])
            ECOSYSTEM[2],ECOSYSTEM[0]=eAm_obj(ECOSYSTEM[2],ECOSYSTEM[0])
        
        
        if move[0]:ECOSYSTEM[0].draw()
        if move[1]:ECOSYSTEM[1].draw()
        #if move:
        if move[2]:ECOSYSTEM[2].draw()
        if move[3]:ECOSYSTEM[3].draw()
        
        if move[1]:ECOSYSTEM[1].Object_update()
        if move[3]:ECOSYSTEM[3].Object_update()
        if move[2]:ECOSYSTEM[2].Object_update()
        if move[0] and move[1] and move[2]:
            #print("food energy :",numpy.mean([v.energy for v in ECOSYSTEM[0].OBJECT]))
            #print("level 1 energy :",numpy.mean([v.energy for v in ECOSYSTEM[1].OBJECT]))
            #print("level 2 energy :",numpy.mean([v.energy for v in ECOSYSTEM[2].OBJECT]))
            #print("level 3 energy :",numpy.mean([v.energy for v in ECOSYSTEM[3].OBJECT]))
            print("food count :",len(ECOSYSTEM[0].OBJECT))
            print("level 1 count :",len(ECOSYSTEM[1].OBJECT))
            print("level 2 count :",len(ECOSYSTEM[2].OBJECT))
            if move[3]:
                print("level 3 count :",len(ECOSYSTEM[3].OBJECT))
        #if ECOSYSTEM[1].mkt() and ECOSYSTEM[2].mkt() and ECOSYSTEM[3].mkt():
        #sys.exit()
            
        if move[0]:
            while ECOSYSTEM[0].noj<ECOSYSTEM[0].init_noj:
                ECOSYSTEM[0].noj+=1
                ECOSYSTEM[0].OBJECT.append(Food(randint(100,width-100),randint(100,height-100),FOOD_size))
        
        
        
        #if ECOSYSTEM[0].noj<=0:
        #    start_moving=0

    #start_moving=0
    #FPSCLOCK.tick(fps)

    pygame.display.update()