# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license


import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
# Added colors for new game elements
BLUE      = (  0,   0, 255)      # Color for second worm
YELLOW    = (255, 255,   0)      # Color for first blinking element
CYAN      = (  0, 255, 255)      # Color for second blinking element
PURPLE    = (128,   0, 128)      # Color for poisonous apples
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        # Capture return values from runGame
        result = runGame()
        if result:
            gameOverReason, baseScore, blinkingItemsEaten = result
            showGameOverScreen(gameOverReason, baseScore, blinkingItemsEaten)
        else:
            showGameOverScreen()


def runGame():
    # Added game time tracking
    gameStartTime = pygame.time.get_ticks()  # Track when game started (in milliseconds)
    gameTime = 0  # Current game time in seconds
    
    # Added score tracking for blinking items 
    blinkingItemsEaten = 0  # Track how many blinking items were eaten (+3 points each)
    
    # Added game over reason tracking
    gameOverReason = None  # 'poison' if lost to poisonous apple, None otherwise
    
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Added second worm system
    secondWormCoords = None  # Will be initialized after 20 seconds
    secondWormDirection = None
    secondWormSpawned = False
    
    # Start the apple in a random place.
    apple = getRandomLocation()
    
    # Added blinking items system
    # First type: appears every 5 seconds, lasts 5 seconds
    blinkingItemsType1 = []  # List of active type 1 blinking items
    lastType1Spawn = 0  # Time when last type 1 item was spawned
    
    # Second type: appears only once, lasts 7 seconds
    blinkingItemType2 = None  # Single type 2 blinking item
    type2Spawned = False  # Track if type 2 has been spawned
    
    # Added poisonous apples system
    poisonousApples = []  # List of active poisonous apples
    numPoisonousApples = random.randint(1, 5)  # Random number between 1 and 5
    poisonSpawnTime = None  # When poisonous apples should spawn (random 10-20 seconds)
    poisonSpawned = False  # Track if poisonous apples have been spawned
    poisonActiveTime = None  # When poisonous apples become inactive (5 seconds after spawn)

    while True: # main game loop
        # Update game time 
        gameTime = (pygame.time.get_ticks() - gameStartTime) / 1000.0  # Convert to seconds
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # Spawn second worm after 20 seconds
        if gameTime >= 20 and not secondWormSpawned:
            # Spawn second worm at a random location (not overlapping with first worm)
            while True:
                secondStartx = random.randint(5, CELLWIDTH - 6)
                secondStarty = random.randint(5, CELLHEIGHT - 6)
                # Check if position overlaps with first worm
                overlap = False
                for coord in wormCoords:
                    if coord['x'] == secondStartx and coord['y'] == secondStarty:
                        overlap = True
                        break
                if not overlap:
                    break
            
            secondWormCoords = [{'x': secondStartx,     'y': secondStarty},
                               {'x': secondStartx - 1, 'y': secondStarty},
                               {'x': secondStartx - 2, 'y': secondStarty}]
            # Random initial direction for second worm
            secondWormDirection = random.choice([UP, DOWN, LEFT, RIGHT])
            secondWormSpawned = True
        
        # Spawn blinking items
        # Type 1: Spawn every 5 seconds each lasts 5 seconds
        if gameTime - lastType1Spawn >= 5.0:
            # Remove expired type 1 items (older than 5 seconds)
            currentTime = pygame.time.get_ticks()
            blinkingItemsType1 = [item for item in blinkingItemsType1 
                                 if (currentTime - item['spawnTime']) / 1000.0 < 5.0]
            
            # Spawn new type 1 item if we have less than 3 total blinking items
            totalBlinkingItems = len(blinkingItemsType1) + (1 if blinkingItemType2 else 0)
            if totalBlinkingItems < 3:
                newItem = getRandomLocation()
                newItem['spawnTime'] = pygame.time.get_ticks()
                newItem['type'] = 1
                blinkingItemsType1.append(newItem)
                lastType1Spawn = gameTime
        
        # Type 2: Spawn only once lasts 7 seconds
        if not type2Spawned and gameTime >= 2.0:  # Spawn after 2 seconds to ensure it appears
            totalBlinkingItems = len(blinkingItemsType1) + (1 if blinkingItemType2 else 0)
            if totalBlinkingItems < 3:
                blinkingItemType2 = getRandomLocation()
                blinkingItemType2['spawnTime'] = pygame.time.get_ticks()
                blinkingItemType2['type'] = 2
                type2Spawned = True
        
        # Remove expired type 2 item (after 7 seconds)
        if blinkingItemType2:
            if (pygame.time.get_ticks() - blinkingItemType2['spawnTime']) / 1000.0 >= 7.0:
                blinkingItemType2 = None
        
        # Spawn poisonous apples
        if not poisonSpawned:
            # Random time between 10 and 20 seconds
            poisonSpawnTime = random.randint(10, 20)
            poisonSpawned = True
        
        if gameTime >= poisonSpawnTime and len(poisonousApples) == 0 and poisonActiveTime is None:
            # Spawn poisonous apples
            for _ in range(numPoisonousApples):
                while True:
                    poisonPos = getRandomLocation()
                    # Check if position overlaps with first worm
                    overlap = False
                    for coord in wormCoords:
                        if coord['x'] == poisonPos['x'] and coord['y'] == poisonPos['y']:
                            overlap = True
                            break
                    # Check if position overlaps with second worm
                    if secondWormCoords:
                        for coord in secondWormCoords:
                            if coord['x'] == poisonPos['x'] and coord['y'] == poisonPos['y']:
                                overlap = True
                                break
                    if not overlap:
                        poisonousApples.append(poisonPos)
                        break
            
            poisonActiveTime = gameTime + 5.0  # Active for 5 seconds
        
        # Remove poisonous apples after 5 seconds
        if poisonActiveTime and gameTime >= poisonActiveTime:
            poisonousApples = []
            poisonActiveTime = None
        
        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        
        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            # Pass game over reason and score
            return (gameOverReason, len(wormCoords) - 3, blinkingItemsEaten) # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                # Pass game over reason and score
                return (gameOverReason, len(wormCoords) - 3, blinkingItemsEaten) # game over

        # Check if worm has eaten a poisonous apple
        poisonEaten = False
        for i, poisonApple in enumerate(poisonousApples):
            if wormCoords[HEAD]['x'] == poisonApple['x'] and wormCoords[HEAD]['y'] == poisonApple['y']:
                # Reduce worm length by 2 segments
                for _ in range(2):
                    if len(wormCoords) > 3:  # Keep minimum length of 3
                        del wormCoords[-1]
                    else:
                        # Worm has no segments left, game over
                        gameOverReason = 'poison'
                        # Pass game over reason and score 
                        return (gameOverReason, len(wormCoords) - 3, blinkingItemsEaten)
                poisonousApples.pop(i)  # Remove eaten poisonous apple
                poisonEaten = True
                break
        
        # Check if worm has eaten blinking items
        # Check type 1 blinking items
        for i, item in enumerate(blinkingItemsType1):
            if wormCoords[HEAD]['x'] == item['x'] and wormCoords[HEAD]['y'] == item['y']:
                blinkingItemsEaten += 1
                blinkingItemsType1.pop(i)
                break
        
        # Check type 2 blinking item
        if blinkingItemType2:
            if wormCoords[HEAD]['x'] == blinkingItemType2['x'] and wormCoords[HEAD]['y'] == blinkingItemType2['y']:
                blinkingItemsEaten += 1
                blinkingItemType2 = None
        
        # Check collision with second worm (after movement
        originalWormGrows = False
        if secondWormCoords:
            # Check if original worm's head touches second worm's body
            for segment in secondWormCoords:
                if wormCoords[HEAD]['x'] == segment['x'] and wormCoords[HEAD]['y'] == segment['y']:
                    # Original worm grows by one segment
                    originalWormGrows = True
                    break
        
        # check if worm has eaten an apple
        appleEaten = False
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation() # set a new apple somewhere
            appleEaten = True
        
        # Remove tail only if not eating apple, not eating poison, and not colliding with second worm
        if not appleEaten and not poisonEaten and not originalWormGrows:
            del wormCoords[-1] # remove worm's tail segment
        
        # Move second worm with random AI 
        if secondWormCoords:
            # Randomly change direction occasionally (30% chance each frame)
            if random.random() < 0.3:
                # Choose a random direction that's not opposite to current
                possibleDirections = [UP, DOWN, LEFT, RIGHT]
                if secondWormDirection == UP:
                    possibleDirections.remove(DOWN)
                elif secondWormDirection == DOWN:
                    possibleDirections.remove(UP)
                elif secondWormDirection == LEFT:
                    possibleDirections.remove(RIGHT)
                elif secondWormDirection == RIGHT:
                    possibleDirections.remove(LEFT)
                secondWormDirection = random.choice(possibleDirections)
            
            # Move second worm
            if secondWormDirection == UP:
                newSecondHead = {'x': secondWormCoords[HEAD]['x'], 'y': secondWormCoords[HEAD]['y'] - 1}
            elif secondWormDirection == DOWN:
                newSecondHead = {'x': secondWormCoords[HEAD]['x'], 'y': secondWormCoords[HEAD]['y'] + 1}
            elif secondWormDirection == LEFT:
                newSecondHead = {'x': secondWormCoords[HEAD]['x'] - 1, 'y': secondWormCoords[HEAD]['y']}
            elif secondWormDirection == RIGHT:
                newSecondHead = {'x': secondWormCoords[HEAD]['x'] + 1, 'y': secondWormCoords[HEAD]['y']}
            
            secondWormCoords.insert(0, newSecondHead)
            
            # Check if second worm hits edge or itself
            if (secondWormCoords[HEAD]['x'] == -1 or secondWormCoords[HEAD]['x'] == CELLWIDTH or 
                secondWormCoords[HEAD]['y'] == -1 or secondWormCoords[HEAD]['y'] == CELLHEIGHT):
                # Second worm dies, remove it
                secondWormCoords = None
            else:
                for wormBody in secondWormCoords[1:]:
                    if wormBody['x'] == secondWormCoords[HEAD]['x'] and wormBody['y'] == secondWormCoords[HEAD]['y']:
                        # Second worm dies, remove it
                        secondWormCoords = None
                        break
                
                if secondWormCoords:
                    # Check if second worm's head touches original worm's body (makes second worm grow)
                    secondWormGrows = False
                    for segment in wormCoords:
                        if secondWormCoords[HEAD]['x'] == segment['x'] and secondWormCoords[HEAD]['y'] == segment['y']:
                            # Second worm grows by one segment
                            secondWormGrows = True
                            break
                    
                    # Check if second worm would eat apple
                    appleEatenBySecond = False
                    if secondWormCoords[HEAD]['x'] == apple['x'] and secondWormCoords[HEAD]['y'] == apple['y']:
                        # Don't remove tail
                        apple = getRandomLocation()
                        appleEatenBySecond = True
                    
                    # Remove tail only if not eating apple and not colliding with original worm
                    if not appleEatenBySecond and not secondWormGrows:
                        if len(secondWormCoords) > 3:  # Keep minimum length
                            del secondWormCoords[-1]
        
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        # Draw second worm
        if secondWormCoords:
            drawSecondWorm(secondWormCoords)
        drawApple(apple)
        # Draw blinking items 
        drawBlinkingItems(blinkingItemsType1, blinkingItemType2, gameTime)
        # Draw poisonous apples
        drawPoisonousApples(poisonousApples)
        # Calculate and draw score with formula
        baseScore = len(wormCoords) - 3
        finalScore = calculateFinalScore(baseScore, blinkingItemsEaten)
        drawScore(finalScore)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


# Added function to calculate final score
def calculateFinalScore(baseScore, blinkingItemsEaten):
    """
    Calculate final score using the formula:
    Final Score = Base Score + (Blinking Items Eaten × 3)
    
    Where:
    - Base Score = Worm length - 3 (starting length)
    - Blinking Items Eaten = Number of blinking items consumed (each worth +3 points)
    
    This formula rewards both growing the worm and collecting blinking items.
    """
    return baseScore + (blinkingItemsEaten * 3)


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


# Modified to accept game over reason and scores
def showGameOverScreen(gameOverReason=None, baseScore=0, blinkingItemsEaten=0):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    
    # Show different message if lost to poison
    if gameOverReason == 'poison':
        gameSurf = gameOverFont.render('You', True, RED)
        overSurf = gameOverFont.render('Lost!', True, RED)
    else:
        gameSurf = gameOverFont.render('Game', True, WHITE)
        overSurf = gameOverFont.render('Over', True, WHITE)
    
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    
    # Display final score
    finalScore = calculateFinalScore(baseScore, blinkingItemsEaten)
    scoreFont = pygame.font.Font('freesansbold.ttf', 36)
    scoreText = f'Final Score: {finalScore}'
    scoreSurf = scoreFont.render(scoreText, True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.midtop = (WINDOWWIDTH / 2, overRect.height + overRect.top + 50)
    DISPLAYSURF.blit(scoreSurf, scoreRect)
    
    # Display score breakdown
    breakdownFont = pygame.font.Font('freesansbold.ttf', 18)
    breakdownText = f'Base Score: {baseScore} + Blinking Items Bonus: {blinkingItemsEaten} × 3 = {finalScore}'
    breakdownSurf = breakdownFont.render(breakdownText, True, DARKGRAY)
    breakdownRect = breakdownSurf.get_rect()
    breakdownRect.midtop = (WINDOWWIDTH / 2, scoreRect.bottom + 20)
    DISPLAYSURF.blit(breakdownSurf, breakdownRect)
    
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


# Added function to draw second worm
def drawSecondWorm(wormCoords):
    """Draw the second worm in blue color to distinguish from the original."""
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, BLUE, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, CYAN, wormInnerSegmentRect)


# Added function to draw blinking items
def drawBlinkingItems(blinkingItemsType1, blinkingItemType2, gameTime):
    """
    Draw blinking items with blinking effect.
    Items blink by toggling visibility based on time.
    """
    # Calculate blink state (blinks every 0.5 seconds)
    blinkState = int(gameTime * 2) % 2 == 0
    
    # Draw type 1 blinking items (yellow)
    for item in blinkingItemsType1:
        if blinkState:  # Only draw when visible
            x = item['x'] * CELLSIZE
            y = item['y'] * CELLSIZE
            itemRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            pygame.draw.rect(DISPLAYSURF, YELLOW, itemRect)
    
    # Draw type 2 blinking item (cyan)
    if blinkingItemType2 and blinkState:  # Only draw when visible
        x = blinkingItemType2['x'] * CELLSIZE
        y = blinkingItemType2['y'] * CELLSIZE
        itemRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, CYAN, itemRect)


# Added function to draw poisonous apples
def drawPoisonousApples(poisonousApples):
    """Draw poisonous apples in purple color."""
    for poisonApple in poisonousApples:
        x = poisonApple['x'] * CELLSIZE
        y = poisonApple['y'] * CELLSIZE
        appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, PURPLE, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()