import pygame
import random
import math

screen = pygame.display.set_mode((600,600))
rangeSurface = pygame.surface.Surface((600,600))
#Creates a screen and a range surface for translucent viewing

class Enemy:
    def __init__(self,x,y,health,speed,imgPath):
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed   #Loads basic Attributes for the Enemy class
        self.image = pygame.image.load(imgPath)  #

    def drawSelf(self):
        screen.blit(self.image,(self.x,self.y))

class Tower:
    def __init__(self,x,y,atkSpeed,range,angle,selected,imgPath):
        self.x = x
        self.y = y
        self.atkSpeed = atkSpeed
        self.range = range
        self.angle = angle
        self.selected = selected
        self.image = pygame.image.load(imgPath)
    
    def drawSelf(self):
        newImage = pygame.transform.rotate(self.image,self.angle)
        screen.blit(newImage,(self.x,self.y))
        if self.selected:
            pygame.draw.circle(rangeSurface,(255,255,255),(self.x,self.y),self.range)
            pygame.draw.circle(screen,(255,255,255),(self.x,self.y),self.range,2)

class Projectile:
    def __init__(self,x,y,velX,velY,angle,imgPath):
        self.x = x
        self.y = y
        self.velX = velX
        self.velY = velY
        self.angle = angle
        self.image = pygame.image.load(imgPath)
        

tower = Tower(300,300,0,80,0,True,None)
rangeSurface.set_alpha(80)

while True:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    tower.drawSelf()
    screen.blit(rangeSurface,(0,0))
    pygame.display.update()
    