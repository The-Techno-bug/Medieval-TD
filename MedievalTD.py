import pygame
import random
import math

#Creates a screen and a range surface for translucent viewing
pygame.init()
screen = pygame.display.set_mode((768,768))
rangeSurface = pygame.surface.Surface((768,768))

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
        screen.blit(newImage,(self.x,self.y))
        for projectile in self.projectiles:
            projectile.drawSelf()
        if self.selected:
            pygame.draw.circle(rangeSurface,(255,255,255),(self.x+8,self.y+8),self.range)
            pygame.draw.circle(screen,(255,255,255),(self.x+8,self.y+8),self.range,2)

    def checkClick(self,mousePos):
        towerRect = pygame.Rect(self.x,self.y,8,8)
        if towerRect.collidepoint(mousePos[0],mousePos[1]):
            self.selected = not self.selected
    
    def shoot(self,angle):
        self.angle = angle
        newAngle = math.radians(angle)
        deltaX = 16*math.cos(newAngle)
        deltaY = 16*math.sin(newAngle)
        self.projectiles.append(Projectile(self.x+deltaX,self.y+deltaY,self.spawnedProjectileSpeed,newAngle,self.spawnedProjectileImage,self.rotateProjectileImage,self.projectileDamage,self.projectilePierce))
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
    def __init__(self, x, y, angle):
        super().__init__(x, y, 30, 50, angle, False, "Images/cannon_idle.png","Images/cannon_shoot.png",200,"Images/cannon_projectile.png",False,1,5)

class Projectile:
    def __init__(self,x,y,vel,angle,imgPath,toRotate,damage,pierce):
        self.x = x
        self.y = y
        self.velX = vel*math.sin(angle)
        self.velY = vel*math.cos(angle)
        self.image = pygame.image.load(imgPath)
        self.image = pygame.transform.scale(self.image,(48,48))
        if toRotate:
            self.image = pygame.transform.rotate(self.image,angle+180)
    
    def drawSelf(self):
        screen.blit(self.image,(self.x,self.y))

    def tick(self):
        self.x += self.velX/60
        self.y += self.velY/60

    def despawnCheck(self):
        if self.x > 300 or self.x < -50 or self.y > 300 or self.y < -50:
            return True
        return False


tower1 = Cannon(100,100,30)
rangeSurface.set_alpha(80)

currentTowers = [tower1]
currentEnemies = []

clock = pygame.time.Clock()
lastTime = 0
while True:
    screen.fill((0,0,0))
    rangeSurface.fill((0,0,0))  #Fill surfaces
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:  #Check if the towers are being clicked
            for tower in currentTowers:
                tower.checkClick(event.pos)

    
    currentTime = pygame.time.get_ticks()
    if currentTime - lastTime >= 2000:
        tower1.shoot(random.randint(0,360))
        lastTime = currentTime
    
    for tower in currentTowers:
        tower.updateAnimation()
        tower.projChecks()
        tower.drawSelf()
            
    screen.blit(rangeSurface,(0,0))
    pygame.display.update()
    clock.tick(60)
    