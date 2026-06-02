import pygame
import random
import math

#Creates a screen and a range surface for translucent viewing
pygame.init()
screen = pygame.display.set_mode((768,768))
rangeSurface = pygame.surface.Surface((768,768))
placementSurface = pygame.surface.Surface((768,768))
path = pygame.image.load("Images/path.png")
path = pygame.transform.scale(path,(768,768))
menu = pygame.image.load("Images/side_menu.png")
menu = pygame.transform.scale(menu,(144,768))

#Create enemy path
gamePath = []
gamePath += [(360,y)for y in range(0,505)]
gamePath += [(x,504)for x in range(360,553)]
gamePath += [(552,y)for y in range(168,103,-1)]
gamePath += [(x,104)for x in range(184,23,-1)]
gamePath += [(24,y)for y in range(104,39,-1)]
gamePath += [(x,40)for x in range(24,91)]
gamePath += [(90,y)for y in range(40,201)]
gamePath += [(x,200)for x in range(90,139)]
gamePath += [(138,y)for y in range(200,256)]

#Create tile system - 16px*16px tiles

tiles = []
for x in range(0,13):
    newList = []
    for y in range(0,16):
        newList.append(pygame.Rect(x*48,y*48,48,48))
    tiles.append(newList)

occupiedTiles = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 [0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
                 [0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0],
                 [0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0],
                 [0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0],
                 [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
                 [0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0],
                 [1,1,1,1,1,1,1,1,1,1,1,0,1,0,0,0],
                 [0,0,0,0,0,0,1,0,0,0,1,0,1,1,1,1],
                 [0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0],
                 [0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0],
                 [0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0],
                 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

class Enemy:
    def __init__(self,x,y,health,speed,imgPath):
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed   
        self.pathIndex = 0
        #Loads basic Attributes for the Enemy class
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
        self.projectiles.append(Projectile(self.x+deltaX,self.y+deltaY,self.x,self.y,self.spawnedProjectileSpeed,angle,self.spawnedProjectileImage,self.rotateProjectileImage,self.projectileDamage,self.projectilePierce,self.range))
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
    def attack(self):
        if currentTime-self.shotTime >= self.atkSpeed:
            self.shoot(random.randint(0,360))



class Cannon(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 3000, 300, 0, False, "Images/cannon_idle.png","Images/cannon_shoot.png",200,"Images/cannon_projectile.png",False,1,5)

class Ballista(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 333, 400, 0, False, "Images/ballista_idle.png", "Images/ballista_shoot.png",500, "Images/ballista_projectile.png", True, 3, 8)

class Projectile:
    def __init__(self,x,y,parentX,parentY,vel,angle,imgPath,toRotate,damage,pierce,range):
        self.x = x
        self.y = y
        self.parentX = parentX
        self.parentY = parentY
        self.velX = vel*math.sin(math.radians(angle))
        self.velY = vel*math.cos(math.radians(angle))
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


tower1 = Cannon(150,150)
rangeSurface.set_alpha(80)
placementSurface.set_alpha(60)

currentTowers = []
currentTowers.append(tower1)
currentEnemies = []

cannonImage = pygame.image.load("Images/cannon_idle.png")
cannonImage = pygame.transform.scale(cannonImage,(48,48))
ballistaImage = pygame.image.load("Images/ballista_idle.png")
ballistaImage = pygame.transform.scale(ballistaImage,(48,48))

def towerShop():
    screen.blit(menu,(624,0))
    screen.blit(cannonImage,(675,50))
    screen.blit(ballistaImage,(676.5,98))

def placeTower(x,y):
    if not occupiedTiles[x][y]:
        if placing == "cannon":
            coords = tiles[x][y].center
            currentTowers.append(Cannon(coords[0],coords[1]))
        elif placing == "ballista":
            coords = tiles[x][y].center
            currentTowers.append(Ballista(coords[0],coords[1]))
        occupiedTiles[x][y] = 1

placing = "none"

clock = pygame.time.Clock()
lastTime = 0
a = 0
while True:
    screen.fill((0,0,0))
    rangeSurface.fill((0,0,0))
    placementSurface.fill((0,0,0))  #Fill surfaces
    screen.blit(path,(0,0))
    
    if placing is not "none":
        for i,tileRow in enumerate(tiles):
            for j,tile in enumerate(tileRow):
                color = (255,255,255)
                if tile.collidepoint(pygame.mouse.get_pos()):
                    color = (0,125,50)
                    if pygame.mouse.get_pressed()[0]:
                        placeTower(i,j)
                if occupiedTiles[i][j]:
                    color = (255,0,0)
                pygame.draw.rect(placementSurface,color,tile)
                pygame.draw.rect(screen,(0,0,0),tile,2)
        if placing == "cannon":
            cannonRect = cannonImage.get_rect(center=pygame.mouse.get_pos())
            placementSurface.blit(cannonImage,cannonRect)
        elif placing == "ballista":
            ballistaRect = ballistaImage.get_rect(center=pygame.mouse.get_pos())
            placementSurface.blit(ballistaImage,ballistaRect)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:  #Check if the towers are being clicked
            for tower in currentTowers:
                tower.checkClick(event.pos)
            if event.pos[0] >= 675 and event.pos[0] <= 723:
                if event.pos[1] >= 50 and event.pos[1] < 98:
                    if placing == "cannon":
                        placing = "none"
                    else:
                        placing = "cannon"
                elif event.pos[1] >= 98 and event.pos[1] <= 146:
                    if placing == "ballista":
                        placing = "none"
                    else:
                        placing = "ballista"
                                

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                placing = "none"
    currentTime = pygame.time.get_ticks()
    
    
    for tower in currentTowers:
        tower.updateAnimation()
        tower.projChecks()
        tower.drawSelf()
        tower.attack()
            
    screen.blit(rangeSurface,(0,0))
    screen.blit(placementSurface,(0,0))
    towerShop()
    pygame.display.update()
    clock.tick(60)
    