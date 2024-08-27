from backend import *
from screens import *
import pygame

ANNOUNCE_RANGE = 3
SEEKER_VISION_RADIUS = 3
HIDER_VISION_RADIUS = 2

INFO_BAR = 70
HEIGHT = 500
WIDTH = None
HEIGHT += INFO_BAR
block_edge = None

def setScreen(current_map):
	map_ratio = current_map.num_rows / current_map.num_cols
	WIDTH_ = (HEIGHT - INFO_BAR) / map_ratio
	block_edge_ = (HEIGHT - INFO_BAR) / current_map.num_rows
	return WIDTH_, block_edge_

pygame.init()
screen = pygame.display.init()
timer = pygame.time.Clock()
fps = 15
font = pygame.font.Font('freesansbold.ttf', 27)
counter = 0

def getWallImage(block_edge):
	return pygame.transform.scale(pygame.image.load('Assets/wall_images/ice.png'), (block_edge, block_edge))
def getHiderImages(block_edge):
	hider_images = []
	for i in range(1, 5):
		hider_images.append(pygame.transform.scale(pygame.image.load(f'Assets/hider_images/freefire{i}.png'), (block_edge, block_edge)))
	return hider_images
def getSeekerImages(block_edge):
	seeker_images = []
	for i in range(1, 5):
		seeker_images.append(pygame.transform.scale(pygame.image.load(f'Assets/seeker_images/water{i}.png'), (block_edge, block_edge)))
	return seeker_images
def getObstacleImage(block_edge):
	return pygame.transform.scale(pygame.image.load('Assets/obstacle_images/bush.png'), (block_edge, block_edge))
def getAnnounceImage(block_edge):
	return pygame.transform.scale(pygame.image.load('Assets/announce_images/sparkle.png'), (block_edge, block_edge))

def setImage(block_edge):
	listOfImage = []
	listOfImage.append(getWallImage(block_edge))
	listOfImage.append(getHiderImages(block_edge))
	listOfImage.append(getSeekerImages(block_edge))
	listOfImage.append(getObstacleImage(block_edge))
	listOfImage.append(getAnnounceImage(block_edge))
	return listOfImage

def draw_board(screen, current_map, block_edge, listOfImage, score, move, next_pos, message):
	width, height = pygame.display.get_window_size()

	score_text = font.render("Score: " + str(score), True, "pink")
	screen.blit(score_text, (10, 10))

	move_text = font.render("Moves: " + str(move), True, "pink")
	screen.blit(move_text, (10, 40))

	screen.blit(font.render(message, True, "pink"), (width - 400, 10))
	screen.blit(font.render(str(next_pos), True, "pink"), (width - 250, 40))

	for i in range(current_map.num_rows):
		for j in range(current_map.num_cols):
			top = j * block_edge
			left = INFO_BAR + i * block_edge

			pygame.draw.rect(screen, 'pink', (top, left, block_edge, block_edge), 1)

			if current_map.map_array[i][j] == 1:
				screen.blit(listOfImage[0], (top, left))
			if current_map.map_array[i][j] == 2:
				draw_agent(current_map, i, j, False, block_edge, listOfImage)
			if current_map.map_array[i][j] == 3:
				draw_agent(current_map, i, j, True, block_edge, listOfImage)
			if current_map.map_array[i][j] == 4:
				screen.blit(listOfImage[3], (top, left))
			if current_map.map_array[i][j] == 5:
				screen.blit(listOfImage[4], (top, left))
		
def draw_agent(current_map, i, j, isSeeker, block_edge, listOfImage):
	VISION_RADIUS = 0
	VISION_COLOR = 0
	top =  j * block_edge
	left = INFO_BAR + i * block_edge
	if isSeeker == True:
		screen.blit(listOfImage[2][counter // 5], (top, left))
		VISION_RADIUS = SEEKER_VISION_RADIUS
		VISION_COLOR = (0, 128, 255, 64)
	else:
		screen.blit(listOfImage[1][counter // 5], (top, left))
		VISION_RADIUS = HIDER_VISION_RADIUS
		VISION_COLOR = (255, 128, 0, 64)
	#Draw vision
	agent = Agent((i, j), VISION_RADIUS, (current_map.num_rows, current_map.num_cols), current_map)
	agent.find_agent_valid_vision()
	
	for valid in agent.valid_vision:
		top_ = valid[1] * block_edge
		left_ = INFO_BAR + valid[0] * block_edge
		#Blending transparently
		s = pygame.Surface((block_edge, block_edge), pygame.SRCALPHA)
		s.fill(VISION_COLOR)
		screen.blit(s, (top_, left_))

def traceHider(currentSeeker, hiderPos, level, currentHiderList):
	global counter
	#Search duong di tu Seeker toi vi tri cua Hider khi phat hien
	finalState = a_star(currentSeeker, hiderPos)
	path = trackPath(finalState)
	for i in range(1, len(path)):
		timer.tick(fps)
		if counter < 19:
			counter += 1
		else:
			counter = 0
		currentSeeker.updateSeeker(path[i].currentPosition)
		screen.fill((64, 64, 64))
		draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, hiderPos, "HIDER FOUND! CHASING...")
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return None
		count = 0
		if level >= 3 and count % 2 == 0:
			for currentHider in currentHiderList:
				if currentHider.position == hiderPos:
					currentHider.clear_current_vision()
					currentHider.find_agent_valid_vision()
					seekerPos = seekerPosInVision(currentHider, currentSeeker.map)
					if seekerPos != (-1, -1):
						timer.tick(fps)
						if counter < 19:
							counter += 1
						else:
							counter = 0
						currentHider.Move(currentSeeker.position)
						screen.fill((64, 64, 64))
						draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, hiderPos, "HIDER FOUND! CHASING...")
						pygame.display.flip()
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								return None
						hiderPos = currentHider.position
		count += 1
		#Sau khi bat duoc hider, giam so luong no xuong 1, neu khong con hider thi end game
	if (currentSeeker.position == hiderPos):
		currentSeeker.hiderNum -= 1
		if currentHiderList != None:
			for hider in currentHiderList:
				if hider.position == currentSeeker.position:
					currentHiderList.remove(hider)
					break
		print("1 Hider is caught")   
		screen.fill((64, 64, 64))
		draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, hiderPos, "HIDER CAUGHT! CHECKING.")
		pygame.display.flip()
		pygame.time.wait(1000)

def gamePlay(level, screen, current_map, block_edge, listOfImage):
	global counter
	if level == 1:
		print()
		print("----------------------------------------------------------")
		print("Khoi tao Seeker")
		#Khoi tao seeker
		bound = (current_map.num_rows, current_map.num_cols)
		currentSeeker = Seeker(current_map.seeker_position[0], SEEKER_VISION_RADIUS, bound, current_map)
		#Khoi tao hider
		print("Khoi tao Hider")
		currentHider = Hider(current_map.hider_position[0], HIDER_VISION_RADIUS, bound, current_map)
		#Thuat toan search Hider o day
		seeker_area = getSeekerArea(current_map, currentSeeker)
		while (currentSeeker.hiderNum > 0):
			#Tao ra 1 vi tri ngau nhien, cho Seeker di toi day, (Vi tri nay khong duoc la tuong, obstacles)
			randomPosition = generateNextRandomGoal(current_map, seeker_area)
			seeker_area += 1
			if (seeker_area > 8):
				seeker_area = 1
			print("Random Position Seeker will explore: ", randomPosition)
			print()
			print("----------------------------------------------------------")

			#Search duong di tu Seeker toi vi tri ngau nhien nay
			finalState = a_star(currentSeeker, randomPosition)
			path = trackPath(finalState)

			#Seeker bat dau di chuyen
			for i in range(len(path)):
				timer.tick(fps)
				if counter < 19:
					counter += 1
				else:
					counter = 0

				currentSeeker.updateSeeker(path[i].currentPosition) #cap nhat vi tri cua Seeker sau moi lan di chuyen

				screen.fill((64, 64, 64))
				draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
				pygame.display.flip()
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						return None

				#Neu trong luc di ma Hider nam trong vision cua Seeker thi thay doi lo trinh di
				currentSeeker.clear_current_vision()
				currentSeeker.find_agent_valid_vision()

				if (currentSeeker.moves % 10 == 0 and currentSeeker.moves > 0):
					for i in range(current_map.num_rows):
						for j in range(current_map.num_cols):
							if current_map.map_array[i][j] == 5:
								current_map.map_array[i][j] = 0
					currentHider.announce()
					screen.fill((64, 64, 64))
					draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
					pygame.display.flip()

				hiderPos = hiderPosInVision(currentSeeker, current_map)
				announcePos = announcementPosHeard(currentSeeker)

				if (hiderPos != (-1, -1)):
					print("Hider found at position: ", hiderPos)
					traceHider(currentSeeker, hiderPos, level, None)
					break

				if announcePos != (-1, -1):
					print("Annoucement found at position: ", announcePos)
					tempFinalState = a_star(currentSeeker, announcePos)
					tempPath = trackPath(tempFinalState)
					for i in range(1, len(tempPath)):
						timer.tick(fps)
						if counter < 19:
							counter += 1
						else:
							counter = 0
						currentSeeker.updateSeeker(tempPath[i].currentPosition)
						screen.fill((64, 64, 64))
						draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, announcePos, "ANNOUNCEMENT SPOTTED!!!")
						pygame.display.flip()
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								return None

						currentSeeker.clear_current_vision()
						currentSeeker.find_agent_valid_vision()

						hiderPos = hiderPosInVision(currentSeeker, current_map)
						if (hiderPos != (-1, -1)):
							traceHider(currentSeeker, hiderPos, level, None)
							break
					break
			if (currentSeeker.hiderNum == 0):
				break
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					break
		print("End Game")
		print("Score:", currentSeeker.score)
		print("Total moves:", currentSeeker.moves)
		if (currentSeeker.hiderNum == 0):
			win_screen(font, currentSeeker.score, currentSeeker.moves)
		else:
			lose_screen(font, currentSeeker.score, currentSeeker.moves)
	elif level == 2:
		print("----------------------------------------------------------")
		print("Khoi tao Seeker")
		#Khoi tao seeker
		bound = (current_map.num_rows, current_map.num_cols)
		currentSeeker = Seeker(current_map.seeker_position[0], SEEKER_VISION_RADIUS, bound, current_map)
		#Khoi tao hider
		print("Khoi tao Hider")
		currentHiderList = []
		for i in range(0, len(current_map.hider_position)):
			currentHider = Hider(current_map.hider_position[i], HIDER_VISION_RADIUS, bound, current_map)
			currentHiderList.append(currentHider)
			print(currentHiderList[i].position)
		print("----------------------------------------------------------")
		print("Game Start")

		seeker_area = getSeekerArea(current_map, currentSeeker)
		#Thuat toan search Hider o day
		while (currentSeeker.hiderNum > 0):
			#Tao ra 1 vi tri ngau nhien, cho Seeker di toi day, (Vi tri nay khong duoc la tuong, obstacles)
			randomPosition = generateNextRandomGoal(current_map, seeker_area)
			print("Random Position Seeker will explore: ", randomPosition)
			seeker_area += 1
			if (seeker_area > 8):
				seeker_area = 1

			#Search duong di tu Seeker toi vi tri ngau nhien nay
			finalState = a_star(currentSeeker, randomPosition)
			path = trackPath(finalState)
			#print("PATH TO THIS RANDOM POSITION")

			#in ra cac step can di tu vi tri cua seeker den vi tri ngau nhien nay
			#for i, state in enumerate(path):
			#	print("Step", i, ": explore", state.currentPosition)
		
			#Seeker bat dau di chuyen
			print("Seeker is moving...")
			for i in range(1, len(path)):
				timer.tick(fps)
				if counter < 19:
					counter += 1
				else:
					counter = 0

				currentSeeker.updateSeeker(path[i].currentPosition) #cap nhat vi tri cua Seeker sau moi lan di chuyen

				screen.fill((64, 64, 64))
				draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
				pygame.display.flip()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						return None

				currentSeeker.clear_current_vision()
				currentSeeker.find_agent_valid_vision()
				#printMap(currentSeeker.map.map_array)
			
				#Annoucement 1st time
				if (currentSeeker.moves % 10 == 0 and currentSeeker.moves > 0):
					for i in range(current_map.num_rows):
						for j in range(current_map.num_cols):
							if current_map.map_array[i][j] == 5:
								current_map.map_array[i][j] = 0
					for i in range(0, len(currentHiderList)):
						currentHiderList[i].announce()
					screen.fill((64, 64, 64))
					draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
					pygame.display.flip()
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							return None
					
				#Neu trong luc di ma Hider nam trong vision cua Seeker thi thay doi lo trinh di
			
				hiderPos = hiderPosInVision(currentSeeker, current_map)
				announcePos = announcementPosHeard(currentSeeker)

				if hiderPos != (-1, -1): 
					print("Hider found at position: ", hiderPos)
					traceHider(currentSeeker, hiderPos, level, currentHiderList)
					break

				if announcePos != (-1, -1):
					print("Annoucement found at position: ", announcePos)
					tempFinalState = a_star(currentSeeker, announcePos)
					tempPath = trackPath(tempFinalState)
					#print("Path to ANNOUCEMENT: ")
					#for i, state in enumerate(tempPath):
					#	print("Step", i, ": Go to ", state.currentPosition)
					for i in range(1, len(tempPath)):
						timer.tick(fps)
						if counter < 19:
							counter += 1
						else:
							counter = 0
						currentSeeker.updateSeeker(tempPath[i].currentPosition)
						screen.fill((64, 64, 64))
						draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, announcePos, "ANNOUNCEMENT SPOTTED!!!")
						pygame.display.flip()

						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								return None

						currentSeeker.clear_current_vision()
						currentSeeker.find_agent_valid_vision()
					
						#printMap(currentSeeker.map.map_array)
						#print()
						hiderPos = hiderPosInVision(currentSeeker, current_map)
						if (hiderPos != (-1, -1)):
							traceHider(currentSeeker, hiderPos, level, currentHiderList)
							break
					break
			if (currentSeeker.hiderNum == 0):
				break
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					break
		print(currentSeeker.hiderNum)
		print("End Game")
		print("Score: ", currentSeeker.score)
		print("Total moves: ", currentSeeker.moves)
		if (currentSeeker.hiderNum == 0):
			win_screen(font, currentSeeker.score, currentSeeker.moves)
		else:
			lose_screen(font, currentSeeker.score, currentSeeker.moves)
	elif level == 3:
		print("----------------------------------------------------------")
		print("Khoi tao Seeker")
		#Khoi tao seeker
		bound = (current_map.num_rows, current_map.num_cols)
		currentSeeker = Seeker(current_map.seeker_position[0], SEEKER_VISION_RADIUS, bound, current_map)
		#Khoi tao hider
		print("Khoi tao Hider")
		currentHiderList = []
		for i in range(0, len(current_map.hider_position)):
			currentHider = Hider(current_map.hider_position[i], HIDER_VISION_RADIUS, bound, current_map)
			currentHiderList.append(currentHider)
			print(currentHiderList[i].position)

		print("----------------------------------------------------------")
		print("Game Start")
		#Tim area cua seeker
		seeker_area = getSeekerArea(current_map, currentSeeker)
		#Thuat toan search Hider o day
		while (currentSeeker.hiderNum > 0):
			#Tao ra 1 vi tri ngau nhien, cho Seeker di toi day, (Vi tri nay khong duoc la tuong, obstacles)
			randomPosition = generateNextRandomGoal(current_map, seeker_area)
			print("Random Position Seeker will explore: ", randomPosition)
			seeker_area += 1
			if (seeker_area > 8):
				seeker_area = 1

			#Search duong di tu Seeker toi vi tri ngau nhien nay
			finalState = a_star(currentSeeker, randomPosition)
			path = trackPath(finalState)
			
			#Seeker bat dau di chuyen
			print("Seeker is moving...")
			for i in range(1, len(path)):
				timer.tick(fps)
				if counter < 19:
					counter += 1
				else:
					counter = 0
				currentSeeker.updateSeeker(path[i].currentPosition) #cap nhat vi tri cua Seeker sau moi lan di chuyen
				screen.fill((64, 64, 64))
				draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
				pygame.display.flip()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						return None

				currentSeeker.clear_current_vision()
				currentSeeker.find_agent_valid_vision()

				#Annoucement 1st time
				if (currentSeeker.moves % 10 == 0 and currentSeeker.moves > 0):
					for i in range(current_map.num_rows):
						for j in range(current_map.num_cols):
							if current_map.map_array[i][j] == 5:
								current_map.map_array[i][j] = 0
					for i in range(0, len(currentHiderList)):
						currentHiderList[i].announce()
					screen.fill((64, 64, 64))
					draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
					pygame.display.flip()
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							return None
						
				#Neu trong luc di ma Hider nam trong vision cua Seeker thi thay doi lo trinh di
				
				hiderPos = hiderPosInVision(currentSeeker, current_map)
				announcePos = announcementPosHeard(currentSeeker)

				if (hiderPos != (-1, -1)): 
					print("Hider found at position: ", hiderPos)
					traceHider(currentSeeker, hiderPos, level, currentHiderList)
					break

				if announcePos != (-1, -1):
					print("Annoucement found at position: ", announcePos)
					tempFinalState = a_star(currentSeeker, announcePos)
					tempPath = trackPath(tempFinalState)
					for i in range(1, len(tempPath)):
						timer.tick(fps)
						if counter < 19:
							counter += 1
						else:
							counter = 0
						currentSeeker.updateSeeker(tempPath[i].currentPosition)
						screen.fill((64, 64, 64))
						draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, announcePos, "ANNOUNCEMENT SPOTTED!!!")
						pygame.display.flip()

						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								return None

						currentSeeker.clear_current_vision()
						currentSeeker.find_agent_valid_vision()
						
						hiderPos = hiderPosInVision(currentSeeker, current_map)
						if (hiderPos != (-1, -1)):
							traceHider(currentSeeker, hiderPos, level, currentHiderList)
							break
					break
			if (currentSeeker.hiderNum == 0):
				break 
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					break
		print(currentSeeker.hiderNum)
		print("End Game")
		print("Score: ", currentSeeker.score)
		print("Total moves: ", currentSeeker.moves)
		if (currentSeeker.hiderNum == 0):
			win_screen(font, currentSeeker.score, currentSeeker.moves)
		else:
			lose_screen(font, currentSeeker.score, currentSeeker.moves)
	elif level == 4:
		print("----------------------------------------------------------")
		print("Khoi tao Seeker")
	
		bound = (current_map.num_rows, current_map.num_cols)
		currentSeeker = Seeker(current_map.seeker_position[0], SEEKER_VISION_RADIUS, bound, current_map)
		
		print("Khoi tao Hider")
		currentHiderList = []
		for i in range(0, len(current_map.hider_position)):
			currentHider = Hider(current_map.hider_position[i], HIDER_VISION_RADIUS, bound, current_map)
			currentHiderList.append(currentHider)
			
		print("----------------------------------------------------------")
		print("Hiders is setting up Obstacles")

		#Create obstacles list (their positions on map)
		obstacles_list = []
		for obstacle_pos in current_map.obstacles_position:
				pos = [x for x in obstacle_pos]
				obs = Obstacles(pos[0], pos[1], pos[2], pos[3], current_map.obstacles_position.index(obstacle_pos), current_map)
				obstacles_list.append(obs)

		#Run each hider to the obstacles and set up the obstacles on map
		for i in range(len(currentHiderList)):
			timer.tick(fps)
			if counter < 19:
				counter += 1
			else:
				counter = 0
			#Find path to obstacles for hiders
			tempHiderPos = currentHiderList[i].position
			goalPos = findCellsAroundObstacles(currentHiderList[i], obstacles_list[i])
			print(goalPos)
			finalState = a_star(currentHiderList[i], goalPos)
			path = trackPath(finalState)
			for j in range(1, len(path)):
				timer.tick(5)
				if counter < 19:
					counter += 1
				else:
					counter = 0
				currentHiderList[i].updateHider(path[j].currentPosition)
				screen.fill((64, 64, 64))
				draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, goalPos, "PREPARATION PHRASE.")
				pygame.display.flip()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						return None

			#Set up obstacles on map
			currentHiderList[i].pull(current_map, obstacles_list)
			screen.fill((64, 64, 64))
			draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, (0, 0), "PREPARATION PHRASE.")
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None

			#Find path back to the initial position of hiders
			finalState = a_star(currentHiderList[i], tempHiderPos)
			path = trackPath(finalState)
			for j in range(1, len(path)):
				timer.tick(fps)
				if counter < 19:
					counter += 1
				else:
					counter = 0
				currentHiderList[i].updateHider(path[j].currentPosition)
				screen.fill((64, 64, 64))
				draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, tempHiderPos, "PREPARATION PHRASE.")
				pygame.display.flip()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						return None
		
		print("----------------------------------------------------------")
		print("Game Start")
		printMap(current_map.map_array)
		print()

		seeker_area = getSeekerArea(current_map, currentSeeker)
		
		#Searching algorithm of Seeker to find Hider goes here
		while (currentSeeker.hiderNum > 0 and currentSeeker.moves < 499):
			print("Hider remains:", currentSeeker.hiderNum)
			#Create a random position, Seeker will move to this position, (This position must not be wall, obstacles)
			randomPosition = generateNextRandomGoal(current_map, seeker_area)
			print("Random Position Seeker will explore: ", randomPosition)
			seeker_area += 1
			if (seeker_area > 8):
				seeker_area = 1

			#Search the path from Seeker to this random position
			finalState = a_star(currentSeeker, randomPosition)
			path = trackPath(finalState)
			
			#Seeker starts moving
			print("Seeker is moving...")
			for i in range(1, len(path)):
				timer.tick(fps)
				if counter < 19:
					counter += 1
				else:
					counter = 0
				currentSeeker.updateSeeker(path[i].currentPosition) #cap nhat vi tri cua Seeker sau moi lan di chuyen
				screen.fill((64, 64, 64))
				draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
				pygame.display.flip()
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						return None				

				currentSeeker.clear_current_vision()
				currentSeeker.find_agent_valid_vision()

				#Annoucement
				if (currentSeeker.moves % 10 == 0 and currentSeeker.moves > 0):
					for i in range(current_map.num_rows):
						for j in range(current_map.num_cols):
							if current_map.map_array[i][j] == 5:
								current_map.map_array[i][j] = 0
					for i in range(0, len(currentHiderList)):
						currentHiderList[i].announce()
					screen.fill((64, 64, 64))
					draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, randomPosition, "GO TO RANDOM POSITION.")
					pygame.display.flip()
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							return None
						
				#If Hider is in Seeker's vision, change the path
				hiderPos = hiderPosInVision(currentSeeker, current_map)
				announcePos = announcementPosHeard(currentSeeker)

				if (hiderPos != (-1, -1)): 
					print("Hider found at position: ", hiderPos)
					traceHider(currentSeeker, hiderPos, level, currentHiderList)
					break

				if announcePos != (-1, -1):
					print("Annoucement found at position: ", announcePos)
					tempFinalState = a_star(currentSeeker, announcePos)
					tempPath = trackPath(tempFinalState)
					
					for i in range(1, len(tempPath)):
						timer.tick(fps)
						if counter < 19:
							counter += 1
						else:
							counter = 0
						currentSeeker.updateSeeker(tempPath[i].currentPosition)
						screen.fill((64, 64, 64))
						draw_board(screen, current_map, block_edge, listOfImage, currentSeeker.score, currentSeeker.moves, announcePos, "ANNOUNCEMENT SPOTTED!!!")
						pygame.display.flip()

						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								return None

						currentSeeker.clear_current_vision()
						currentSeeker.find_agent_valid_vision()
						hiderPos = hiderPosInVision(currentSeeker, current_map)
						if (hiderPos != (-1, -1)):
							traceHider(currentSeeker, hiderPos, level, currentHiderList)
							break
					break
			#If all of hiders are caught, End game
			if (currentSeeker.hiderNum < 1):
				break 
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					break
		print("End Game")
		print("Score: ", currentSeeker.score)
		print("Total moves: ", currentSeeker.moves)
		if (currentSeeker.hiderNum == 0):
			win_screen(font, currentSeeker.score, currentSeeker.moves)
		else:
			lose_screen(font, currentSeeker.score, currentSeeker.moves)


level_map = []
running = True
while running:
	timer.tick(fps)
	if counter < 19:
		counter += 1
	else:
		counter = 0

	if len(level_map) == 0:
		pygame.display.quit()
		menu_screen(font, level_map)
		if len(level_map) != 2:
			break
		pygame.display.quit()

	if level_map[0] == 1:
		print()
		print("----------------------------------------------------------")
		print("Khoi tao Map")
		current_map = Map()
		current_map.read_txt_file("Assets/maps/map0.txt")

		WIDTH, block_edge = setScreen(current_map)
		listOfImage = setImage(block_edge)

		screen = pygame.display.set_mode([WIDTH, HEIGHT])
		pygame.display.set_caption("HideAndSeek_Level1_Map0")

		gamePlay(1, screen, current_map, block_edge, listOfImage)
		level_map.clear()
	elif level_map[0] == 2:
		print()
		print("----------------------------------------------------------")
		print("Khoi tao Map")
		#Khoi tao map
		current_map = Map()
		current_map.read_txt_file(f"Assets/maps/map{level_map[1]}.txt")

		WIDTH, block_edge = setScreen(current_map)
		listOfImage = setImage(block_edge)

		screen = pygame.display.set_mode([WIDTH, HEIGHT])
		pygame.display.set_caption(f"HideAndSeek_Level2_Map{level_map[1]}")

		gamePlay(2, screen, current_map, block_edge, listOfImage)
		level_map.clear()
	elif level_map[0] == 3:
		print()
		print("----------------------------------------------------------")
		print("Khoi tao Map")
		#Khoi tao map
		current_map = Map()
		current_map.read_txt_file(f"Assets/maps/map{level_map[1]}.txt")

		WIDTH, block_edge = setScreen(current_map)
		listOfImage = setImage(block_edge)

		screen = pygame.display.set_mode([WIDTH, HEIGHT])
		pygame.display.set_caption(f"HideAndSeek_Level3_Map{level_map[1]}")

		gamePlay(3, screen, current_map, block_edge, listOfImage)
		level_map.clear()
	elif level_map[0] == 4:
		print()
		print("----------------------------------------------------------")
		print("Khoi tao Map")
	
		current_map = Map()
		current_map.read_txt_file(f"Assets/maps/map{level_map[1]}.txt")

		WIDTH, block_edge = setScreen(current_map)
		listOfImage = setImage(block_edge)

		screen = pygame.display.set_mode([WIDTH, HEIGHT])
		pygame.display.set_caption(f"HideAndSeek_Level4_Map{level_map[1]}")

		gamePlay(4, screen, current_map, block_edge, listOfImage)
		level_map.clear()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	pygame.display.flip()
pygame.quit()