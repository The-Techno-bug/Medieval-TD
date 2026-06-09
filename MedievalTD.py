import pygame
import math
import copy
import random
#Creates a screen and a range surface for translucent viewing
pygame.init()
screen = pygame.display.set_mode((768,768))
rangeSurface = pygame.surface.Surface((768,768))
placementSurface = pygame.surface.Surface((768,768))

#Load required images and fonts
path = pygame.image.load("Images/path.png")
path = pygame.transform.scale(path,(768,768))
menu = pygame.image.load("Images/side_menu.png")
menu = pygame.transform.scale(menu,(144,768))

gameFont = pygame.font.Font("Font/BreeSerif-Regular.ttf",25)
smallFont = pygame.font.Font("Font/BreeSerif-Regular.ttf",15)

speed1Image = pygame.image.load("Images/speed_normal.png")
speed1Image = pygame.transform.scale(speed1Image,(48,48))
speed2Image = pygame.image.load("Images/speed_fast.png")
speed2Image = pygame.transform.scale(speed2Image,(48,48))
moneyImage = pygame.image.load("Images/money.png")
moneyImage = pygame.transform.scale(moneyImage,(48,48))
livesImage = pygame.image.load("Images/lives.png")
livesImage = pygame.transform.scale(livesImage,(48,48))

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

#Create tile system - 48px*48px tiles

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
startOccupiedTiles = copy.deepcopy(occupiedTiles)

class Enemy:
    def __init__(self,x,y,health,speed,imgPathList,animationTime,reward):
        #Loads basic Attributes for the Enemy class
        self.x = x
        self.y = y
        self.health = health
        self.maxHealth = health
        self.speed = speed
        self.reward = reward
        self.hasGivenMoney = False
        self.pathIndex = 0
        self.images = []
        #Loads Animation
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
        if currentTime-self.animationLastTime >= self.animationTime/speed:  #Increase animationPhase every few ms, denoted by animationTime
            self.animationPhase += 1
            if self.animationPhase >= len(self.images):  #Prevents an indexError and keeps program within list bounds
                self.animationPhase = 0
            self.animationLastTime = currentTime
        self.image = self.images[self.animationPhase]  #Sets the enemy image to appropriate frame of animation
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

    def drawHealthBar(self):  #Draws Health Bar
        pygame.draw.rect(screen,(15,15,15),(self.rect.center[0]-20,self.rect.center[1]-30,40,5))
        pygame.draw.rect(screen,(255,0,0),(self.rect.center[0]-20,self.rect.center[1]-30,(self.health/self.maxHealth)*40,5))

    def move(self):  #Moves forward on gamePath based on speed 
        try:
            if speed == 2:
                iterations = 2*self.speed
            else:
                iterations = self.speed

            for i in range(1,iterations+1):
                self.pathIndex += 1
                self.x = gamePath[self.pathIndex][0]
                self.y = gamePath[self.pathIndex][1]

        except Exception: #If the enemy reaches the end, subtract their max health from lives
            global lives
            for i,enemy in enumerate(currentEnemies):
                if enemy == self:
                    if self.health > 0:
                        lives -= self.maxHealth
                    currentEnemies.pop(i)

    def dealDamage(self,damage):  #Function to take damage
        global money
        self.health -= damage
        self.damageFlashTime = currentTime
        if self.health <= 0 and not self.hasGivenMoney:  #Givves user money and disappears
            money += self.reward
            self.hasGivenMoney = True
            self.pathIndex = 5000

    def getVelocity(self):   #Returns the current velocity of the enemy 
        if self.pathIndex >= len(gamePath)-1:
            return (0,0)
        nextPathPos = gamePath[self.pathIndex+1]
        return ((nextPathPos[0]-self.x)*self.speed*50,(nextPathPos[1]-self.y)*self.speed*50)

class Barbarian(Enemy):  #Barbarian
    def __init__(self,x,y):
        super().__init__(x,y,125,1,["Images/barbarian1.png","Images/barbarian2.png","Images/barbarian3.png","Images/barbarian4.png","Images/barbarian5.png","Images/barbarian6.png"],100,50)

class Goblin(Enemy):  #Goblin
    def __init__(self,x,y):
        super().__init__(x,y,60,2,["Images/goblin1.png","Images/goblin2.png","Images/goblin3.png","Images/goblin4.png","Images/goblin5.png","Images/goblin6.png"],80,20)

class Tower:
    def __init__(self,x,y,atkSpeed,range,angle,selected,shootImgPathList,spawnedProjectileSpeed,spawnedProjectileImage,rotateProjectileImage,projectilePierce,projectileDamage,animationTime):
        #Loads tower attributes
        self.x = x
        self.y = y
        self.atkSpeed = atkSpeed
        self.range = range
        self.angle = angle
        self.selected = selected
        self.shootingImages = []
        #Loads tower animation
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
        self.isCycled = False #Stops animation when not shooting

    def drawSelf(self):  #Draws itself
        if self.selected:  #If the tower is selected, show range
            pygame.draw.circle(rangeSurface,(255,255,255),(self.x,self.y),self.range)
            pygame.draw.circle(screen,(255,255,255),(self.x,self.y),self.range,2)
        newImage = pygame.transform.rotate(self.shootingImages[-self.shootingPhase],self.angle)
        newRect = newImage.get_rect(center=(self.x,self.y))
        screen.blit(newImage,newRect)
        for projectile in self.projectiles:
            projectile.drawSelf()

    def checkClick(self,mousePos):   #Select and unselect tower
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
                aimPoint = self.predictAimPoint(enemy)  #Predict where enemy will be when the shot lanads and ensure it is inside range
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
            deltaY = 24*math.cos(newAngle)  #Uses a circle of radius 24 from the center to spawn projectiles
            self.projectiles.append(Projectile(self.x+deltaX,self.y+deltaY,self.x,self.y,self.spawnedProjectileSpeed,angle,self.spawnedProjectileImage,self.rotateProjectileImage,self.projectileDamage,self.projectilePierce,self.range))
            self.shootingPhase = len(self.shootingImages) - 1  
            self.shotTime = currentTime
            self.phaseTime = currentTime
            self.isCycled = False  #Allows tower to cycle through animation

    def projChecks(self):  #Handles projectile despawning, velocity, and hits
        for i,projectile in enumerate(self.projectiles):
            if projectile.despawnCheck():
                self.projectiles.pop(i)
            projectile.checkHits()
            projectile.tick()

    def updateAnimation(self):  #Animates Tower
        if currentTime-self.phaseTime >= self.animationTime/speed and not self.isCycled:
            self.shootingPhase -= 1
            self.phaseTime = currentTime
        if self.shootingPhase < 0:
            self.shootingPhase = 0
            self.phaseTime = currentTime
            self.isCycled = True

class Cannon(Tower): #Cannon
    def __init__(self, x, y):
        super().__init__(x, y, 3000, 200, 0, False,["Images/cannon_idle.png","Images/cannon_shoot.png"],200,"Images/cannon_projectile.png",False,1,12,100)

    def shoot(self,angle):   #Since the cannon needs a second class of projectile, we use SplashProjectile
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

class Ballista(Tower): #Ballista
    def __init__(self, x, y):
        super().__init__(x, y, 333, 300, 0, False,["Images/ballista1.png","Images/ballista2.png","Images/ballista3.png","Images/ballista4.png"],500, "Images/ballista_projectile.png", True, 1, 6, 70)

class Catapult(Tower): #Catapult
    def __init__(self, x, y):
        super().__init__(x, y, 2500, 200, 0, False,["Images/catapult1.png","Images/catapult2.png","Images/catapult3.png","Images/catapult4.png","Images/catapult5.png","Images/catapult6.png"],350, "Images/catapult_projectile.png", True, 8, 16, 100)

    def shoot(self,angle):
        if currentTime-self.shotTime >= self.atkSpeed/speed:
            self.angle = angle + 180
            newAngle = math.radians(angle)
            deltaX = 24*math.sin(newAngle)
            deltaY = 24*math.cos(newAngle)
            #Allows projectile to go outside of tower range
            self.projectiles.append(Projectile(self.x+deltaX,self.y+deltaY,self.x,self.y,self.spawnedProjectileSpeed,angle,self.spawnedProjectileImage,self.rotateProjectileImage,self.projectileDamage,self.projectilePierce,self.range,True))
            self.shootingPhase = len(self.shootingImages) - 1
            self.shotTime = currentTime
            self.phaseTime = currentTime
            self.isCycled = False

class Projectile:
    def __init__(self,x,y,parentX,parentY,vel,angle,imgPath,toRotate,damage,pierce,range,persist=False):
        #Projectile Attributes
        self.x = x
        self.y = y
        self.parentX = parentX
        self.parentY = parentY
        self.spawnTime = currentTime
        self.persist = persist
        self.velX = vel*math.sin(math.radians(angle))
        self.velY = vel*math.cos(math.radians(angle))
        self.image = pygame.image.load(imgPath)
        self.image = pygame.transform.scale(self.image,(48,48))
        if toRotate:  #Rotates specific projectiles (arrow) based on angle of release from tower
            self.image = pygame.transform.rotate(self.image,angle+180)
        self.damage = damage
        self.pierce = pierce
        self.range = range
        self.hitEnemies = []
        self.rect = self.image.get_rect(center=(self.x,self.y))

    def drawSelf(self):  #Draw projectile
        self.rect = self.image.get_rect(center=(self.x,self.y))
        screen.blit(self.image,self.rect)

    def tick(self): #Handle movement per frame
        self.x += speed*self.velX/60
        self.y += speed*self.velY/60

    def despawnCheck(self):  #Check if projectile needs to despawn
        if self.persist:
            if currentTime-self.spawnTime >= 5000/speed:
                return True
            return False
        if ((self.parentX-self.x)**2 + (self.parentY-self.y)**2)**0.5 >= self.range:
            return True
        return False

    def checkHits(self): #Check if the projectile has hit an enemy
        for i,enemy in enumerate(self.hitEnemies):
            if enemy not in currentEnemies:
                self.hitEnemies.pop(i)
        for enemy in currentEnemies:
            dx = (self.rect.centerx-enemy.rect.centerx)
            dy = (self.rect.centery-enemy.rect.centery)
            if (dx**2 + dy**2)**0.5 <= 30 and enemy not in self.hitEnemies:
                self.hitEnemies.append(enemy)
                enemy.dealDamage(self.damage)
                self.pierce -= 1
        if self.pierce <= 0:
            self.x = 5000

class SplashProjectile(Projectile): #A type of projectile that explodes
    def __init__(self,x,y,parentX,parentY,vel,angle,imgPath,toRotate,damage,pierce,range,splashRadius):
        super().__init__(x,y,parentX,parentY,vel,angle,imgPath,toRotate,damage,pierce,range)
        self.splashRadius = splashRadius
        self.hasSplashed = False

    def splash(self):  #Damages enemies in a radius
        if not self.hasSplashed:
            explosionEffects.append((self.x,self.y,currentTime))
            for enemy in currentEnemies:
                dx = self.x-enemy.x
                dy = self.y-enemy.y
                if (dx**2 + dy**2)**0.5 <= self.splashRadius:
                    enemy.dealDamage(self.damage)
            self.hasSplashed = True

    def despawnCheck(self):  #Checks if projectile needs to be despawned
        if ((self.parentX-self.x)**2 + (self.parentY-self.y)**2)**0.5 >= self.range:
            self.splash()
            return True
        return False

    def checkHits(self):  #Replaces hit with splash
        for enemy in currentEnemies:
            dx = (self.rect.centerx-enemy.rect.centerx)
            dy = (self.rect.centery-enemy.rect.centery)
            if (dx**2 + dy**2)**0.5 <= 30:
                self.splash()
                self.x = 5000
                return

rangeSurface.set_alpha(80)  #Makes the range and placement surfaces translucent
placementSurface.set_alpha(60)
rangeSurface.set_colorkey((0,0,0))
placementSurface.set_colorkey((0,0,0))

roundNum = 0  #Rounds, money, lives, and tower costs
rounds = [[(Barbarian,0),(Barbarian,2000),(Barbarian,2000),(Barbarian,2000),(Barbarian,2000)],
          [(Goblin,0),(Goblin,600),(Barbarian,600),(Goblin,600),(Barbarian,600),(Goblin,600),(Goblin,600),(Barbarian,600),(Goblin,600),(Barbarian,600)],
          [(Goblin,0),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450),(Goblin,450)]]
roundEnemyIndex = 0
lastSpawnTime = 0
roundActive = False
money = 300
lives = 500
cannonCost = 150
ballistaCost = 300
catapultCost = 300

currentTowers = []
currentEnemies = []
explosionEffects = []

#Image and rectangle loading for shop
cannonImage = pygame.image.load("Images/cannon_idle.png")
cannonImage = pygame.transform.scale(cannonImage,(48,48))
ballistaImage = pygame.image.load("Images/ballista1.png")
ballistaImage = pygame.transform.scale(ballistaImage,(48,48))
catapultImage = pygame.image.load("Images/catapult1.png")
catapultImage = pygame.transform.scale(catapultImage,(48,48))
cannonShopRect = pygame.Rect(675,48,48,48)
ballistaShopRect = pygame.Rect(677,96,48,48)
catapultShopRect = pygame.Rect(675,144,48,48)
startImage = pygame.image.load("Images/start.png")
startImage = pygame.transform.scale(startImage,(256,64))
startHoverImage = pygame.image.load("Images/start_hover.png")
startHoverImage = pygame.transform.scale(startHoverImage,(272,80))


#Creates explosion animation
explosionImages = []
for i in range(1,9):
    explosionImage = pygame.image.load(f"Images/explosion{i}.png")
    explosionImage = pygame.transform.scale(explosionImage,(81,81))
    explosionImages.append(explosionImage)

def tintUnaffordable(image):  #Tints unaffordable towers
    tintedImage = image.copy()
    # dark red tint = image - cyan
    tintedImage.fill((30,128,128),special_flags=pygame.BLEND_RGB_SUB)
    return tintedImage

def getShopImage(image,cost):  #Tints unaffordable towers and doesn't tint affordable ones 
    if money < cost:
        return tintUnaffordable(image)
    return image

def towerShop(): #Displays tower shop
    roundText = gameFont.render(f"Round {roundNum}",True,(0,0,0))
    screen.blit(menu,(624,0))
    screen.blit(roundText,(648,10))
    screen.blit(getShopImage(cannonImage,cannonCost),cannonShopRect)
    screen.blit(getShopImage(ballistaImage,ballistaCost),ballistaShopRect)
    screen.blit(getShopImage(catapultImage,catapultCost),catapultShopRect)

def drawStats():  #Shows Money and Lives
    moneyText = gameFont.render(str(money),True,(0,0,0))
    livesText = gameFont.render(str(lives),True,(0,0,0))
    screen.blit(moneyImage,(8,8))
    screen.blit(moneyText,(60,14))
    screen.blit(livesImage,(128,8))
    screen.blit(livesText,(180,14))

def placeTower(x,y):  #Placement system for towers
    global placing,money
    if not occupiedTiles[x][y]:
        if placing == "cannon" and money >= cannonCost:  #Cannon
            coords = tiles[x][y].center
            currentTowers.append(Cannon(coords[0],coords[1]))
            money -= cannonCost
        elif placing == "ballista" and money >= ballistaCost: #Ballista
            coords = tiles[x][y].center
            currentTowers.append(Ballista(coords[0],coords[1]))
            money -= ballistaCost
        elif placing == "catapult" and money >= catapultCost: #Catapult
            coords = tiles[x][y].center
            currentTowers.append(Catapult(coords[0],coords[1]))
            money -= catapultCost
        else:
            return
        occupiedTiles[x][y] = 1
    placing = "none"

def showCannonTooltip():  #Cannon Tooltip rendering
    mousePos = pygame.mouse.get_pos()
    topleft = (mousePos[0]-144,mousePos[1])
    pygame.draw.rect(placementSurface,(255,255,255),(topleft[0],topleft[1],144,235))
    screen.blit(placementSurface,(0,0))
    pygame.draw.rect(screen,(0,0,0),(topleft[0],topleft[1],144,235),2)
    pygame.draw.rect(screen,(0,0,0),(topleft[0],topleft[1]+50,144,2))
    screen.blit(cannonImage,topleft)
    cannonTowerText = gameFont.render("Cannon",True,(0,0,0))
    cannonTowerTextRect = cannonTowerText.get_rect(center=(topleft[0]+96,topleft[1]+24))
    screen.blit(cannonTowerText,cannonTowerTextRect)
    statsText = ["Cost:             $150","Attack Speed:   1/3s","Damage:          6","Range:          200","Pierce:          1"]
    for i,stat in enumerate(statsText):
        statsTextRender = smallFont.render(stat,True,(0,0,0))
        statsTextRenderRect = statsTextRender.get_rect(center=((topleft[0]+72,topleft[1]+70+i*35)))
        screen.blit(statsTextRender,statsTextRenderRect)

def showBallistaTooltip():  #Ballista Tooltip Rendering
    mousePos = pygame.mouse.get_pos()
    topleft = (mousePos[0]-144,mousePos[1])
    pygame.draw.rect(placementSurface,(255,255,255),(topleft[0],topleft[1],144,235))
    screen.blit(placementSurface,(0,0))
    pygame.draw.rect(screen,(0,0,0),(topleft[0],topleft[1],144,235),2)
    pygame.draw.rect(screen,(0,0,0),(topleft[0],topleft[1]+50,144,2))
    screen.blit(ballistaImage,topleft)
    ballistaTowerText = gameFont.render("Ballista",True,(0,0,0))
    ballistaTowerTextRect = ballistaTowerText.get_rect(center=(topleft[0]+96,topleft[1]+24))
    screen.blit(ballistaTowerText,ballistaTowerTextRect)
    statsText = ["Cost:             $300","Attack Speed:   3/s","Damage:          4","Range:          300","Pierce:          1"]
    for i,stat in enumerate(statsText):
        statsTextRender = smallFont.render(stat,True,(0,0,0))
        statsTextRenderRect = statsTextRender.get_rect(center=((topleft[0]+72,topleft[1]+70+i*35)))
        screen.blit(statsTextRender,statsTextRenderRect)

def showCatapultTooltip():  #Catapult Tooltip Rendering
    mousePos = pygame.mouse.get_pos()
    topleft = (mousePos[0]-144,mousePos[1])
    pygame.draw.rect(placementSurface,(255,255,255),(topleft[0],topleft[1],144,235))
    screen.blit(placementSurface,(0,0))
    pygame.draw.rect(screen,(0,0,0),(topleft[0],topleft[1],144,235),2)
    pygame.draw.rect(screen,(0,0,0),(topleft[0],topleft[1]+50,144,2))
    screen.blit(catapultImage,topleft)
    catapultTowerText = gameFont.render("Catapult",True,(0,0,0))
    catapultTowerTextRect = catapultTowerText.get_rect(center=(topleft[0]+96,topleft[1]+24))
    screen.blit(catapultTowerText,catapultTowerTextRect)
    statsText = ["Cost:             $300","Attack Speed:   1/2.5s","Damage:          12","Range:          200","Pierce:          8"]
    for i,stat in enumerate(statsText):
        statsTextRender = smallFont.render(stat,True,(0,0,0))
        statsTextRenderRect = statsTextRender.get_rect(center=((topleft[0]+72,topleft[1]+70+i*35)))
        screen.blit(statsTextRender,statsTextRenderRect)

def generateRound(roundNumber):
    newRound = []
    enemyCount = 10+roundNumber*5
    delayBase = max(100,700-roundNumber*40)
    goblinChance = min(85,40+roundNumber*7)
    for i in range(0,enemyCount):
        if random.randint(1,100) <= goblinChance:
            enemyType = Goblin
        else:
            enemyType = Barbarian
        if i == 0:
            delay = 0
        else:
            delay = random.randint(max(120,delayBase-120),delayBase+120)
        newRound.append((enemyType,delay))
    return newRound

def startRound():  #Starts next round
    global roundNum,roundEnemyIndex,lastSpawnTime,roundActive
    roundNum += 1
    if roundNum > len(rounds):
        rounds.append(generateRound(roundNum))
    roundEnemyIndex = 0
    lastSpawnTime = currentTime
    roundActive = True
    

def updateRound(): #General function to spawn enemies, change rounds and add money once the round is over
    global roundEnemyIndex,lastSpawnTime,roundActive,money
    if not roundActive:
        startRound()
    if roundActive and roundEnemyIndex < len(rounds[roundNum-1]):
        enemyInfo = rounds[roundNum-1][roundEnemyIndex]
        if currentTime-lastSpawnTime >= enemyInfo[1]/speed:
            currentEnemies.append(enemyInfo[0](gamePath[0][0],gamePath[0][1]))
            roundEnemyIndex += 1
            lastSpawnTime = currentTime
    elif roundActive and not currentEnemies:
        money += 150
        roundActive = False

def drawExplosionEffects():  #Draws explosion
    for i in range(len(explosionEffects)-1,-1,-1):
        effect = explosionEffects[i]
        frame = int((currentTime-effect[2])*speed/75)
        if frame >= len(explosionImages):
            explosionEffects.pop(i)
        else:
            explosionRect = explosionImages[frame].get_rect(center=(effect[0],effect[1]))
            screen.blit(explosionImages[frame],explosionRect)

class MainMenu:
    def __init__(self):
        self.startRect = startImage.get_rect(center=(384,384))

    def drawSelf(self):
        overlay = pygame.Surface((768,768),pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        screen.blit(overlay,(0,0))
        titleText = gameFont.render("Medieval TD",True,(255,255,255))
        titleRect = titleText.get_rect(center=(384,300))
        screen.blit(titleText,titleRect)
        if self.startRect.collidepoint(pygame.mouse.get_pos()):
            hoverRect = startHoverImage.get_rect(center=self.startRect.center)
            screen.blit(startHoverImage,hoverRect)
        else:
            screen.blit(startImage,self.startRect)

    def checkClick(self,mousePos):
        return self.startRect.collidepoint(mousePos)

class LosingScreen(MainMenu):
    def drawSelf(self):
        overlay = pygame.Surface((768,768),pygame.SRCALPHA)
        overlay.fill((0,0,0,170))
        screen.blit(overlay,(0,0))
        titleText = gameFont.render("You Lost",True,(255,255,255))
        titleRect = titleText.get_rect(center=(384,300))
        screen.blit(titleText,titleRect)
        if self.startRect.collidepoint(pygame.mouse.get_pos()):
            hoverRect = startHoverImage.get_rect(center=self.startRect.center)
            screen.blit(startHoverImage,hoverRect)
        else:
            screen.blit(startImage,self.startRect)

def resetGame():
    global roundNum,roundEnemyIndex,lastSpawnTime,roundActive,money,lives,currentTowers,currentEnemies,explosionEffects,occupiedTiles,placing,speed
    roundNum = 0
    roundEnemyIndex = 0
    lastSpawnTime = currentTime
    roundActive = False
    money = 300
    lives = 500
    currentTowers = []
    currentEnemies = []
    explosionEffects = []
    occupiedTiles = copy.deepcopy(startOccupiedTiles)
    placing = "none"
    speed = 1

placing = "none"
state = "start"
mainMenu = MainMenu()
losingScreen = LosingScreen()

EnemyMove = pygame.event.custom_type()  #Creates an event for the enemy to check movement every 20ms
pygame.time.set_timer(EnemyMove,20)

clock = pygame.time.Clock()
lastTime = 0
a = 0
speed = 1
currentTime = pygame.time.get_ticks()
while True:  #Main Loop
    screen.fill((0,0,0))
    rangeSurface.fill((0,0,0))
    placementSurface.fill((0,0,0))  #Fill surfaces
    screen.blit(path,(0,0))
    currentTime = pygame.time.get_ticks()

    if state == "game" and placing != "none":  #Render shadow cannon when in placing mode over your mouse and create tile system. Also highlight occupied squares red
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
        if placing == "cannon": #Render Cannon on mouse
            cannonRect = cannonImage.get_rect(center=mousePos)
            placementSurface.blit(cannonImage,cannonRect)
            pygame.draw.circle(rangeSurface,(255,255,255),mousePos,200)
            pygame.draw.circle(screen,(255,255,255),mousePos,200,2)
        elif placing == "ballista": #Render Ballista on mouse
            ballistaRect = ballistaImage.get_rect(center=mousePos)
            placementSurface.blit(ballistaImage,ballistaRect)
            pygame.draw.circle(rangeSurface,(255,255,255),mousePos,300)
            pygame.draw.circle(screen,(255,255,255),mousePos,300,2)
        elif placing == "catapult": #Render Catapult on mouse
            catapultRect = catapultImage.get_rect(center=mousePos)
            placementSurface.blit(catapultImage,catapultRect)
            pygame.draw.circle(rangeSurface,(255,255,255),mousePos,200)
            pygame.draw.circle(screen,(255,255,255),mousePos,200,2)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:  #Check if the towers are being clicked
            if state == "start" and mainMenu.checkClick(event.pos):
                resetGame()
                state = "game"
            elif state == "lost" and losingScreen.checkClick(event.pos):
                resetGame()
                state = "game"
            elif state == "game":
                towerClicked = False
                for tower in currentTowers:
                    if tower.checkClick(event.pos):
                        towerClicked = True
                if not towerClicked:
                    for tower in currentTowers:
                        tower.selected = False
                shopClicked = cannonShopRect.collidepoint(event.pos) or ballistaShopRect.collidepoint(event.pos) or catapultShopRect.collidepoint(event.pos)
                if placing != "none" and event.pos[0] >= 624 and not shopClicked:
                    placing = "none"
                if cannonShopRect.collidepoint(event.pos):  #Check if the user is trying to buy from the shop
                    if placing == "cannon":
                        placing = "none"
                    else:
                        placing = "cannon"
                elif ballistaShopRect.collidepoint(event.pos):
                    if placing == "ballista":
                        placing = "none"
                    else:
                        placing = "ballista"
                elif catapultShopRect.collidepoint(event.pos):
                    if placing == "catapult":
                        placing = "none"
                    else:
                        placing = "catapult"
                if event.pos[0] >= 672 and event.pos[0] <= 720 and event.pos[1] >= 720 and event.pos[1] <= 768:
                    if speed == 1:
                        speed = 2
                    else:
                        speed = 1

        elif event.type == pygame.KEYDOWN and state == "game":
            if event.key == pygame.K_ESCAPE:  #Unselect all and stop placing
                placing = "none"
                for tower in currentTowers:
                    tower.selected = False
            elif event.key == pygame.K_q:  #Place Cannon
                if placing != "cannon":
                    placing = "cannon"
                else:
                    placing = "none"
            elif event.key == pygame.K_w: #Place Ballista
                if placing != "ballista":
                    placing = "ballista"
                else:
                    placing = "none"
            elif event.key == pygame.K_e:  #Place Catapult
                if placing != "catapult":
                    placing = "catapult"
                else:
                    placing = "none"
            elif event.key == pygame.K_SPACE:  #Increase or decrease speed
                if speed == 1:
                    speed = 2
                else:
                    speed = 1

        elif event.type == EnemyMove and state == "game":  #Move enemies
            for enemy in currentEnemies:
                enemy.move()
    if state == "game":
        updateRound()
        if lives <= 0:
            state = "lost"
            placing = "none"
        for tower in currentTowers:   #Update all towers
            tower.updateAnimation()
            tower.projChecks()
            tower.findEnemy()
            tower.drawSelf()

        for enemy in currentEnemies:  #Draw all enemies
            enemy.drawSelf()

        screen.blit(rangeSurface,(0,0))
        screen.blit(placementSurface,(0,0))
        towerShop()
        if speed == 1:
            screen.blit(speed1Image,(672,720))
        else:
            screen.blit(speed2Image,(672,720))
        mousePos = pygame.mouse.get_pos()
        if placing == "none":   #Show tooltips when not in placing mode
            if cannonShopRect.collidepoint(mousePos):
               showCannonTooltip()
            elif ballistaShopRect.collidepoint(mousePos):
                showBallistaTooltip()
            elif catapultShopRect.collidepoint(mousePos):
                showCatapultTooltip()

        drawExplosionEffects()
        drawStats()
        for enemy in currentEnemies: #Draw enemy health bars and stats
            enemy.drawHealthBar()
    elif state == "start":
        mainMenu.drawSelf()
    elif state == "lost":
        losingScreen.drawSelf()
    pygame.display.update()  #Framerate of 60 fps
    clock.tick(60)
