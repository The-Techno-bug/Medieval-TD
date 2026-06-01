import pygame
import random
import math

#Creates a screen and a range surface for translucent viewing
pygame.init()
screen = pygame.display.set_mode((768,768))
rangeSurface = pygame.surface.Surface((768,768))
path = pygame.image.load("Images/path.png")
path = pygame.transform.scale(path,(768,768))

#Create enemy path

gamePath = []
gamePath += [(120,y)for y in range(0,169)]
gamePath += [(x,168)for x in range(120,184)]
gamePath += [(184,y)for y in range(168,103,-1)]
gamePath += [(x,104)for x in range(184,23,-1)]
gamePath += [(24,y)for y in range(104,39,-1)]
gamePath += [(x,40)for x in range(24,91)]
gamePath += [(90,y)for y in range(40,201)]
gamePath += [(x,200)for x in range(90,139)]
gamePath += [(138,y)for y in range(200,256)]

#Create tile system - 16px*16px tiles

tiles = []
for x in range(0,16):
    newList = []
    for y in range(0,16):
        newList.append(pygame.Rect(x*16,y*16,16,16))
    tiles.append(newList)


class Enemy:
    def __init__(self,x,y,health,speed,imgPath):
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed   #Loads basic Attributes for the Enemy class
        self.image = pygame.image.load(imgPath)

    def drawSelf(self):
        screen.blit(self.image,(self.x,self.y))

class Tower:
    def __init__(self,x,y,atkSpeed,range,angle,selected,imgPath,shootImgPath,spawnedProjectileSpeed,spawnedProjectileImage,rotateProjectileImage,projectilePierce,projectileDamage):
        self.x = x
        self.y = y
        self.atkSpeed = atkSpeed
        self.range = range
        self.angle = angle
        self.selected = selected
        self.image = pygame.image.load(imgPath)
        self.image = pygame.transform.scale(self.image,(48,48))
        self.shootImage = pygame.image.load(shootImgPath)
        self.shootImage = pygame.transform.scale(self.shootImage,(48,48))
        self.projectiles = []
        self.spawnedProjectileSpeed = spawnedProjectileSpeed
        self.spawnedProjectileImage = spawnedProjectileImage
        self.rotateProjectileImage = rotateProjectileImage
        self.projectilePierce = projectilePierce
        self.isShooting = False
        self.lastShotTime = 0
        self.projectileDamage = projectileDamage
        self.shotTime = 0
        self.animationTime = 100

    def drawSelf(self):
        if self.isShooting:
            newImage = pygame.transform.rotate(self.shootImage,self.angle)
        else:
            newImage = pygame.transform.rotate(self.image,self.angle)
        newRect = newImage.get_rect(center=(self.x,self.y))
        screen.blit(newImage,newRect)
        for projectile in self.projectiles:
            projectile.drawSelf()
        if self.selected:
            pygame.draw.circle(rangeSurface,(255,255,255),(self.x,self.y),self.range)
            pygame.draw.circle(screen,(255,255,255),(self.x,self.y),self.range,2)

    def checkClick(self,mousePos):
        towerRect = pygame.Rect(self.x-24,self.y-24,48,48)
        if towerRect.collidepoint(mousePos[0],mousePos[1]):
            self.selected = not self.selected
    
    def shoot(self,angle):
        self.angle = angle + 180
        newAngle = math.radians(angle)
        deltaX = 24*math.sin(newAngle)
        deltaY = 24*math.cos(newAngle)
        self.projectiles.append(Projectile(self.x+deltaX,self.y+deltaY,self.x,self.y,self.spawnedProjectileSpeed,newAngle,self.spawnedProjectileImage,self.rotateProjectileImage,self.projectileDamage,self.projectilePierce,self.range))
        self.isShooting = True
        self.shotTime = currentTime

    def projChecks(self):
        for i,projectile in enumerate(self.projectiles):
            if projectile.despawnCheck():
                self.projectiles.pop(i)
            projectile.tick()

    def updateAnimation(self):
        if currentTime-self.shotTime >= self.animationTime:
            self.isShooting = False

class Cannon(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 200, 0, False, "Images/cannon_idle.png","Images/cannon_shoot.png",200,"Images/cannon_projectile.png",False,1,5)

class Ballista(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 400, 0, False, "Images/ballista_idle.png", "Images/ballista_shoot.png", 500, "Images/cannon_projectile.png", False, 3, 8)

class Projectile:
    def __init__(self,x,y,parentX,parentY,vel,angle,imgPath,toRotate,damage,pierce,range):
        self.x = x
        self.y = y
        self.parentX = parentX
        self.parentY = parentY
        self.velX = vel*math.sin(angle)
        self.velY = vel*math.cos(angle)
        self.image = pygame.image.load(imgPath)
        self.image = pygame.transform.scale(self.image,(48,48))
        if toRotate:
            self.image = pygame.transform.rotate(self.image,angle+180)
        self.damage = damage
        self.pierce = pierce
        self.range = range
    
    def drawSelf(self):
        newRect = self.image.get_rect(center=(self.x,self.y))
        screen.blit(self.image,newRect)

    def tick(self):
        self.x += self.velX/60
        self.y += self.velY/60

    def despawnCheck(self):
        if ((self.parentX-self.x)**2 + (self.parentY-self.y)**2)**0.5 >= self.range:
            return True
        return False


tower1 = Ballista(150,150)
rangeSurface.set_alpha(80)

currentTowers = [tower1]
currentEnemies = []

clock = pygame.time.Clock()
lastTime = 0
a = 0
while True:
    screen.fill((0,0,0))
    rangeSurface.fill((0,0,0))  #Fill surfaces
    screen.blit(path,(0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:  #Check if the towers are being clicked
            for tower in currentTowers:
                tower.checkClick(event.pos)

    
    currentTime = pygame.time.get_ticks()
    if currentTime - lastTime >= 2000:
        a += 30
        a %= 360
        tower1.shoot(a)
        print(a)
        lastTime = currentTime
    
    for tower in currentTowers:
        tower.updateAnimation()
        tower.projChecks()
        tower.drawSelf()
            
    screen.blit(rangeSurface,(0,0))
    pygame.display.update()
    clock.tick(60)
    