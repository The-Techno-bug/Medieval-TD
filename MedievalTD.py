import pygame
import math
import copy
#Creates a screen and a range surface for translucent viewing
pygame.init()
screen = pygame.display.set_mode((768,768))
rangeSurface = pygame.surface.Surface((768,768))
placementSurface = pygame.surface.Surface((768,768))
path = pygame.image.load("Images/path.png")
path = pygame.transform.scale(path,(768,768))
menu = pygame.image.load("Images/side_menu.png")
menu = pygame.transform.scale(menu,(144,768))

gameFont = pygame.font.SysFont("Akronim",25)

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
    def __init__(self,x,y,health,speed,imgPathList,animationTime):
        self.x = x
        self.y = y
        self.health = health
        self.maxHealth = health
        self.speed = speed
        self.pathIndex = 0
        #Loads basic Attributes for the Enemy class
        self.images = []
        for imagePath in imgPathList:
            image = pygame.image.load(imagePath)
            image = pygame.transform.scale(image,(17*3, 23*3))
            self.images.append(image)
        self.animationTime = animationTime
        self.animationPhase = 0
        self.animationLastTime = 0
        self.damageFlashTime = -100
        self.damageFlashDuration = 100
        self.image = self.images[self.animationPhase]
        self.rect = self.image.get_rect(center=(self.x,self.y))

    def drawSelf(self):
        if currentTime-self.animationLastTime >= self.animationTime/speed:
            self.animationPhase += 1
            if self.animationPhase >= len(self.images):
                self.animationPhase = 0
            self.animationLastTime = currentTime
        self.image = self.images[self.animationPhase]
        self.rect = self.image.get_rect(center=(self.x,self.y))
        if currentTime-self.damageFlashTime < self.damageFlashDuration:
            flashImage = self.image.copy()
            #Mask out transparent pixels so they dont get tinted
            flashMask = pygame.mask.from_surface(self.image)
            flashSurface = flashMask.to_surface(setcolor=(128,0,0,120),unsetcolor=(0,0,0,0))
            flashImage.blit(flashSurface,(0,0),special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(flashImage,self.rect)
        else:
            screen.blit(self.image,self.rect)

    def drawHealthBar(self):
        pygame.draw.rect(screen,(15,15,15),(self.rect.center[0]-20,self.rect.center[1]-30,40,5))
        pygame.draw.rect(screen,(255,0,0),(self.rect.center[0]-20,self.rect.center[1]-30,(self.health/self.maxHealth)*40,5))

    def move(self):
        try:
            if speed == 2:
                iterations = 2*self.speed
            else:
                iterations = self.speed

            for i in range(1,iterations+1):
                self.pathIndex += 1
                self.x = gamePath[self.pathIndex][0]
                self.y = gamePath[self.pathIndex][1]

        except Exception:
            for i,enemy in enumerate(currentEnemies):
                if enemy == self:
                    currentEnemies.pop(i)

    def dealDamage(self,damage):
        self.health -= damage
        self.damageFlashTime = currentTime
        if self.health <= 0:
            self.pathIndex = 5000

    def getVelocity(self):
        if self.pathIndex >= len(gamePath)-1:
            return (0,0)
        nextPathPos = gamePath[self.pathIndex+1]
        return ((nextPathPos[0]-self.x)*self.speed*50,(nextPathPos[1]-self.y)*self.speed*50)

class Barbarian(Enemy):
    def __init__(self,x,y):
        super().__init__(x,y,125,1,["Images/barbarian1.png","Images/barbarian2.png","Images/barbarian3.png","Images/barbarian4.png","Images/barbarian5.png","Images/barbarian6.png"],100)

class Goblin(Enemy):
    def __init__(self,x,y):
        super().__init__(x,y,60,2,["Images/goblin1.png","Images/goblin2.png","Images/goblin3.png","Images/goblin4.png","Images/goblin5.png","Images/goblin6.png"],80)

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
            wasSelected = self.selected
            for tower in currentTowers:
                tower.selected = False
            self.selected = not wasSelected
            return True
        return False

    def findEnemy(self):
        #Grab the enemy furthest in the path
        enemiesByProgress = sorted(currentEnemies,key=lambda enemy: enemy.pathIndex,reverse=True)
        for enemy in enemiesByProgress:
            if ((enemy.x-self.x)**2 + (enemy.y-self.y)**2)**0.5 < self.range:
                aimPoint = self.predictAimPoint(enemy)
                if ((aimPoint[0]-self.x)**2 + (aimPoint[1]-self.y)**2)**0.5 < self.range:
                    angle = math.degrees(math.atan2(aimPoint[0]-self.x,aimPoint[1]-self.y))
                    self.shoot(angle)
                    return

    def predictAimPoint(self,enemy):
        enemyVel = enemy.getVelocity()
        #Vector going from tower to enemy
        relX = enemy.x-self.x
        relY = enemy.y-self.y
        #Use quadratic formula to find travel time to enemy
        a = enemyVel[0]**2+enemyVel[1]**2-self.spawnedProjectileSpeed**2
        b = 2*(relX*enemyVel[0]+relY*enemyVel[1])
        c = relX**2+relY**2
        travelTime = 0
        if abs(a) < 0.01:
            #If a is very close to 0 it is basically linear function
            if b != 0:
                travelTime = -c/b
        else:
            discriminant = b**2-4*a*c
            if discriminant >= 0:
                time1 = (-b+discriminant**0.5)/(2*a)
                time2 = (-b-discriminant**0.5)/(2*a)
                if time1 < 0:
                    travelTime = time2
                elif time2 < 0:
                    travelTime = time1
                else:
                    travelTime = min(time1,time2)
        #The aim point is the enemy's position at the predicted travel time
        return (enemy.x+enemyVel[0]*travelTime,enemy.y+enemyVel[1]*travelTime)


    def shoot(self,angle):
        if currentTime-self.shotTime >= self.atkSpeed/speed:
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
            projectile.checkHits()
            projectile.tick()

    def updateAnimation(self):
        if currentTime-self.phaseTime >= self.animationTime/speed and not self.isCycled:
            self.shootingPhase -= 1
            self.phaseTime = currentTime
        if self.shootingPhase < 0:
            self.shootingPhase = 0
            self.phaseTime = currentTime
            self.isCycled = True


class Cannon(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 3000, 300, 0, False,["Images/cannon_idle.png","Images/cannon_shoot.png"],200,"Images/cannon_projectile.png",False,1,12,100)

    def shoot(self,angle):
        if currentTime-self.shotTime >= self.atkSpeed/speed:
            self.angle = angle + 180
            newAngle = math.radians(angle)
            deltaX = 24*math.sin(newAngle)
            deltaY = 24*math.cos(newAngle)
            self.projectiles.append(SplashProjectile(self.x+deltaX,self.y+deltaY,self.x,self.y,self.spawnedProjectileSpeed,angle,self.spawnedProjectileImage,self.rotateProjectileImage,self.projectileDamage,self.projectilePierce,self.range,80))
            self.shootingPhase = len(self.shootingImages) - 1
            self.shotTime = currentTime
            self.phaseTime = currentTime
            self.isCycled = False

class Ballista(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 300, 400, 0, False,["Images/ballista1.png","Images/ballista2.png","Images/ballista3.png","Images/ballista4.png"],500, "Images/ballista_projectile.png", True, 1, 4, 70)

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
        self.hitEnemies = []
        self.rect = self.image.get_rect(center=(self.x,self.y))

    def drawSelf(self):
        self.rect = self.image.get_rect(center=(self.x,self.y))
        screen.blit(self.image,self.rect)

    def tick(self):
        self.x += speed*self.velX/60
        self.y += speed*self.velY/60

    def despawnCheck(self):
        if ((self.parentX-self.x)**2 + (self.parentY-self.y)**2)**0.5 >= self.range:
            return True
        return False

    def checkHits(self):
        for i,enemy in enumerate(self.hitEnemies):
            if enemy not in currentEnemies:
                self.hitEnemies.pop(i)
        for enemy in currentEnemies:
            dx = (self.rect.centerx-enemy.rect.centerx)
            dy = (self.rect.centery-enemy.rect.centery)
            if (dx**2 + dy**2)**0.5 <= 30:
                self.hitEnemies.append(enemy)
                enemy.dealDamage(self.damage)
                self.pierce -= 1
        if self.pierce <= 0:
            self.x = 5000

class SplashProjectile(Projectile):
    def __init__(self,x,y,parentX,parentY,vel,angle,imgPath,toRotate,damage,pierce,range,splashRadius):
        super().__init__(x,y,parentX,parentY,vel,angle,imgPath,toRotate,damage,pierce,range)
        self.splashRadius = splashRadius
        self.hasSplashed = False

    def splash(self):
        if not self.hasSplashed:
            explosionEffects.append((self.x,self.y,currentTime))
            for enemy in currentEnemies:
                dx = self.x-enemy.x
                dy = self.y-enemy.y
                if (dx**2 + dy**2)**0.5 <= self.splashRadius:
                    enemy.dealDamage(self.damage)
            self.hasSplashed = True

    def despawnCheck(self):
        if ((self.parentX-self.x)**2 + (self.parentY-self.y)**2)**0.5 >= self.range:
            self.splash()
            return True
        return False

    def checkHits(self):
        for enemy in currentEnemies:
            dx = (self.rect.centerx-enemy.rect.centerx)
            dy = (self.rect.centery-enemy.rect.centery)
            if (dx**2 + dy**2)**0.5 <= 30:
                self.splash()
                self.x = 5000
                return



rangeSurface.set_alpha(80)
placementSurface.set_alpha(60)
rangeSurface.set_colorkey((0,0,0))
placementSurface.set_colorkey((0,0,0))

roundNum = 0
rounds = [[(Barbarian,0),(Barbarian,1000),(Goblin,1000),(Barbarian,1000),(Goblin,1000)],
          [(Goblin,0),(Goblin,800),(Barbarian,800),(Goblin,800),(Barbarian,800),(Goblin,800)],
          [(Barbarian,0),(Goblin,700),(Goblin,700),(Barbarian,700),(Goblin,700),(Barbarian,700),(Goblin,700)],
          [copy.deepcopy((Barbarian,250)) for _ in range(50)] + [copy.deepcopy((Goblin,250)) for _ in range(50)]]
roundEnemyIndex = 0
lastSpawnTime = 0
roundActive = False

currentTowers = []
currentEnemies = []
explosionEffects = []

cannonImage = pygame.image.load("Images/cannon_idle.png")
cannonImage = pygame.transform.scale(cannonImage,(48,48))
ballistaImage = pygame.image.load("Images/ballista1.png")
ballistaImage = pygame.transform.scale(ballistaImage,(48,48))
explosionImages = []
for i in range(1,9):
    explosionImage = pygame.image.load(f"Images/explosion{i}.png")
    explosionImage = pygame.transform.scale(explosionImage,(81,81))
    explosionImages.append(explosionImage)

def towerShop():
    roundText = gameFont.render(f"Round {roundNum}",True,(255,255,255))
    screen.blit(menu,(624,0))
    screen.blit(roundText,(648,0))
    screen.blit(cannonImage,(675,50))
    screen.blit(ballistaImage,(676.5,98))

def placeTower(x,y):
    global placing
    if not occupiedTiles[x][y]:
        if placing == "cannon":
            coords = tiles[x][y].center
            currentTowers.append(Cannon(coords[0],coords[1]))
        elif placing == "ballista":
            coords = tiles[x][y].center
            currentTowers.append(Ballista(coords[0],coords[1]))
        occupiedTiles[x][y] = 1
        placing = "none"

def startRound():
    global roundNum,roundEnemyIndex,lastSpawnTime,roundActive
    if roundNum < len(rounds):
        roundNum += 1
        roundEnemyIndex = 0
        lastSpawnTime = currentTime
        roundActive = True

def updateRound():
    global roundEnemyIndex,lastSpawnTime,roundActive
    if not roundActive:
        startRound()
    if roundActive and roundEnemyIndex < len(rounds[roundNum-1]):
        enemyInfo = rounds[roundNum-1][roundEnemyIndex]
        if currentTime-lastSpawnTime >= enemyInfo[1]/speed:
            currentEnemies.append(enemyInfo[0](gamePath[0][0],gamePath[0][1]))
            roundEnemyIndex += 1
            lastSpawnTime = currentTime
    elif roundActive and not currentEnemies:
        roundActive = False

def drawExplosionEffects():
    for i in range(len(explosionEffects)-1,-1,-1):
        effect = explosionEffects[i]
        frame = int((currentTime-effect[2])/75)
        if frame >= len(explosionImages):
            explosionEffects.pop(i)
        else:
            explosionRect = explosionImages[frame].get_rect(center=(effect[0],effect[1]))
            screen.blit(explosionImages[frame],explosionRect)

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

    if placing != "none":
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
        mousePos = pygame.mouse.get_pos()
        if placing == "cannon":
            cannonRect = cannonImage.get_rect(center=mousePos)
            placementSurface.blit(cannonImage,cannonRect)
            pygame.draw.circle(rangeSurface,(255,255,255),mousePos,300)
            pygame.draw.circle(screen,(255,255,255),mousePos,300,2)
        elif placing == "ballista":
            ballistaRect = ballistaImage.get_rect(center=mousePos)
            placementSurface.blit(ballistaImage,ballistaRect)
            pygame.draw.circle(rangeSurface,(255,255,255),mousePos,400)
            pygame.draw.circle(screen,(255,255,255),mousePos,400,2)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:  #Check if the towers are being clicked
            towerClicked = False
            for tower in currentTowers:
                if tower.checkClick(event.pos):
                    towerClicked = True
            if not towerClicked:
                for tower in currentTowers:
                    tower.selected = False
            shopClicked = event.pos[0] >= 675 and event.pos[0] <= 723 and event.pos[1] >= 50 and event.pos[1] <= 146
            if placing != "none" and event.pos[0] >= 624 and not shopClicked:
                placing = "none"
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
            if event.pos[0] >= 672 and event.pos[0] <= 720 and event.pos[1] >= 720 and event.pos[1] <= 768:
                if speed == 1:
                    speed = 2
                else:
                    speed = 1

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
    updateRound()


    for tower in currentTowers:
        tower.updateAnimation()
        tower.projChecks()
        tower.findEnemy()
        tower.drawSelf()

    for enemy in currentEnemies:
        enemy.drawSelf()

    screen.blit(rangeSurface,(0,0))
    screen.blit(placementSurface,(0,0))
    towerShop()
    if speed == 1:
        screen.blit(speed1Image,(672,720))
    else:
        screen.blit(speed2Image,(672,720))
    drawExplosionEffects()
    for enemy in currentEnemies:
        enemy.drawHealthBar()
    pygame.display.update()
    clock.tick(60)
