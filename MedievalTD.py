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

speed1Image = pygame.image.load("Images/speed_normal.png")
speed1Image = pygame.transform.scale(speed1Image,(48,48))
speed2Image = pygame.image.load("Images/speed_fast.png")
speed2Image = pygame.transform.scale(speed2Image,(48,48))

#Create enemy path
gamePath = []
gamePath += [(360,y)for y in range(0,505)]
gamePath += [(x,504)for x in range(360,553)]
gamePath += [(552,y)for y in range(504,307,-1)]
gamePath += [(x,308)for x in range(552,71,-1)]
gamePath += [(72,y)for y in range(308,119,-1)]
gamePath += [(x,120)for x in range(72,271)]
gamePath += [(270,y)for y in range(120,601)]
gamePath += [(x,600)for x in range(270,415)]
gamePath += [(414,y)for y in range(600,756)]

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
        self.maxHealth = health
        self.speed = speed   
        self.pathIndex = 0
        #Loads basic Attributes for the Enemy class
        self.image = pygame.image.load(imgPath)
        self.image = pygame.transform.scale(self.image,(48,48))

    def drawSelf(self):
        imageRect = self.image.get_rect(center=(self.x,self.y))
        screen.blit(self.image,imageRect)
        pygame.draw.rect(screen,(15,15,15),(imageRect.center[0]-24,imageRect.center[1]-30,48,5))
        pygame.draw.rect(screen,(255,0,0),(imageRect.center[0]-24,imageRect.center[1]-30,self.health/48,5))
    
    def move(self):
        self.pathIndex += 1
        self.x = gamePath[self.pathIndex][0]
        self.y = gamePath[self.pathIndex][1]
        if speed == 2:
            self.pathIndex += 1
            self.x = gamePath[self.pathIndex][0]
            self.y = gamePath[self.pathIndex][1]    

class Tower:
    def __init__(self,x,y,atkSpeed,range,angle,selected,shootImgPathList,spawnedProjectileSpeed,spawnedProjectileImage,rotateProjectileImage,projectilePierce,projectileDamage,animationTime):
        self.x = x
        self.y = y
        self.atkSpeed = atkSpeed
        self.range = range
        self.angle = angle
        self.selected = selected
        self.shootingImages = []
        for imagePath in shootImgPathList:
            image = pygame.image.load(imagePath)
            image = pygame.transform.scale(image,(48,48))
            self.shootingImages.append(image)
        self.projectiles = []
        self.spawnedProjectileSpeed = spawnedProjectileSpeed
        self.spawnedProjectileImage = spawnedProjectileImage
        self.rotateProjectileImage = rotateProjectileImage
        self.projectilePierce = projectilePierce
        self.shootingPhase = 0
        self.projectileDamage = projectileDamage
        self.shotTime = 0
        self.animationTime = animationTime
        self.phaseTime = 0
        self.isCycled = False

    def drawSelf(self):
        newImage = pygame.transform.rotate(self.shootingImages[-self.shootingPhase],self.angle)
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
        self.shootingPhase = len(self.shootingImages) - 1
        self.shotTime = currentTime
        self.phaseTime = currentTime
        self.isCycled = False

    def projChecks(self):
        for i,projectile in enumerate(self.projectiles):
            if projectile.despawnCheck():
                self.projectiles.pop(i)
            projectile.tick()

    def updateAnimation(self):
        if currentTime-self.phaseTime >= self.animationTime/speed and not self.isCycled:
            self.shootingPhase -= 1
            self.phaseTime = currentTime
        if self.shootingPhase < 0:
            self.shootingPhase = 0
            self.phaseTime = currentTime
            self.isCycled = True

    def attack(self):
        if currentTime-self.shotTime >= self.atkSpeed/speed:
            self.shoot(random.randint(0,360))

class Cannon(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 3000, 300, 0, False,["Images/cannon_idle.png","Images/cannon_shoot.png"],200,"Images/cannon_projectile.png",False,1,5,100)

class Ballista(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 300, 400, 0, False,["Images/ballista1.png","Images/ballista2.png","Images/ballista3.png","Images/ballista4.png"],500, "Images/ballista_projectile.png", True, 3, 8, 70)

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
        self.x += speed*self.velX/60
        self.y += speed*self.velY/60

    def despawnCheck(self):
        if ((self.parentX-self.x)**2 + (self.parentY-self.y)**2)**0.5 >= self.range:
            return True
        return False


rangeSurface.set_alpha(80)
placementSurface.set_alpha(60)

enemy1 = Enemy(300,300,100,10,"Images/enemy.png")
enemy1.health = 300

currentTowers = []
currentEnemies = []
currentEnemies.append(enemy1)

cannonImage = pygame.image.load("Images/cannon_idle.png")
cannonImage = pygame.transform.scale(cannonImage,(48,48))
ballistaImage = pygame.image.load("Images/ballista1.png")
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

EnemyMove = pygame.event.custom_type()
pygame.time.set_timer(EnemyMove,20)

clock = pygame.time.Clock()
lastTime = 0
a = 0
speed = 1
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
                for tower in currentTowers:
                    tower.selected = False
            elif event.key == pygame.K_q:
                if placing != "cannon":
                    placing = "cannon"
                else:
                    placing = "none"
            elif event.key == pygame.K_w:
                if placing != "ballista":
                    placing = "ballista"
                else:
                    placing = "none"
            elif event.key == pygame.K_SPACE:
                if speed == 1:
                    speed = 2
                else:
                    speed = 1
        
        elif event.type == EnemyMove:
            for enemy in currentEnemies:
                enemy.move()
    currentTime = pygame.time.get_ticks()
    

    for tower in currentTowers:
        tower.updateAnimation()
        tower.projChecks()
        tower.drawSelf()
        tower.attack()
    
    for enemy in currentEnemies:
        enemy.drawSelf()

    screen.blit(rangeSurface,(0,0))
    screen.blit(placementSurface,(0,0))
    towerShop()
    if speed == 1:
        screen.blit(speed1Image,(672,720))
    else:
        screen.blit(speed2Image,(672,720))
    pygame.display.update()
    clock.tick(60)
    