import pygame
import time
from os.path import join
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, groups) -> None:
        super().__init__(groups)
        self.images = [
        pygame.image.load(join("images","rakieta1.png")).convert_alpha(),
        pygame.image.load(join("images","rakieta2.png")).convert_alpha(),
        pygame.image.load(join("images","rakieta3.png")).convert_alpha()
        ]
        self.laser_image = pygame.image.load(join("images", "missile.png")).convert_alpha()
        #switcing index of image
        self._img_idx = 0
        self.switch_interval = 0.25
        self.last_switch_time = time.time()
        
        #main attributes of spaceship
        self.image = self.images[self._img_idx]
        self.rect = self.image.get_frect(bottomleft = (WINDOW_WIDTH/2,WINDOW_HEIGHT))
        self.direction = pygame.math.Vector2(1, 0)
        self.speed = 300
        
        #cooldown
        self.can_shoot = True
        self.shoot_time = 0
        self.laser_cooldown = 400
        
        #laser list object -> updates list depending on not out of bounds condition
        self.laser_list = []
        
    def switch_sprite(self) -> None:
        current_time = time.time()
        if current_time - self.last_switch_time > self.switch_interval:
            self._img_idx = (self._img_idx + 1) % len(player.images)
            self.image = self.images[self._img_idx]
            self.last_switch_time = current_time
    
    def shoot_timer(self) -> None:
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > self.laser_cooldown:
                self.can_shoot = True
    
    #self update
    '''Player movement and shooting laser'''
    
    def custom_update(self, delta_time, old_mouse_pos):
        
        pygame.mouse.set_visible(False)
        mouse_pos = pygame.mouse.get_pos()
        if(mouse_pos != old_mouse_pos):
            self.rect.center = (mouse_pos[0], self.rect.center[1])
            old_mouse_pos = mouse_pos
            
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LALT]:
            pygame.mouse.set_visible(True)
            
        self.direction.x =int(keys[pygame.K_d]) - int(keys[pygame.K_a]) 
        self.rect.center += self.direction * self.speed * delta_time
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        
        keys_single = pygame.key.get_just_pressed()
        if (keys_single[pygame.K_SPACE] or pygame.mouse.get_just_pressed()[0]) and self.can_shoot:
            print("shot laser")
            self.shoot_time = pygame.time.get_ticks()
            self.can_shoot = False
            laser_object = Laser(group = (all_sprites, player_laser_sprites),position_vector= self.rect, image = self.laser_image , direction = pygame.math.Vector2(0,-1))
            self.laser_list.append(laser_object)
        self.laser_list = [laser for laser in self.laser_list if not laser.out_of_bounds(WINDOW_HEIGHT, WINDOW_WIDTH)]
        self.shoot_timer()
        return old_mouse_pos
    
    def update(self, delta_time) -> None:
        self.switch_sprite()

class Laser(pygame.sprite.Sprite):
    def __init__(self,group, position_vector, image, direction):
        super().__init__(group)
        
        self.position = position_vector
        self.image = image
        self.rect = self.image.get_frect(center = (position_vector.x+32, position_vector.y+10))
        self.direction = direction
        self.speed = 300
        
    def update(self, delta_time):
        self.rect.center += self.direction * self.speed * delta_time
    
    def out_of_bounds(self, window_height, window_width) -> bool:
        if self.rect.bottom <=0 or self.rect.top >= window_height or self.rect.right <= 0 or self.rect.left >= window_width:
            self.kill()
            return True
        return False
            
         
class Alien(pygame.sprite.Sprite):
   
    def __init__(self, group, image, pos_vector, type = 1, can_shoot = False, can_begin_shoot = False) -> None:
        super().__init__(group)
        
        self.image = image
        self.pos_vector = pos_vector
        self.rect = self.image.get_frect(center = (pos_vector.x, pos_vector.y))
        self.direction = pygame.math.Vector2(1, 0)
        self.speed = 100
        self.left_bound = pos_vector.x - 100  
        self.right_bound = pos_vector.x + 100
        self.type = type
        self.can_begin_shoot = can_begin_shoot
        self.laser_cooldown = random.randint(1000,10000)
        self.can_shoot = can_shoot
        self.shoot_time = 0
        self.laser_list = []
    #moves alien left and right    
    def move_horizontal(self, delta_time):
        if self.rect.left <= self.left_bound:
            self.direction.x = 1
        elif self.rect.right >= self.right_bound:
            self.direction.x = -1
            
        self.rect.center += self.direction * self.speed * delta_time

    #moves alien downwards
    def move_vertically(self):
        self.rect.bottom += 30
        
    def shoot_laser(self):
        
        self.shoot_time = pygame.time.get_ticks()
        if self.type == 1:
            temp_image = pygame.image.load(join("images", "Enemy shoot.png")).convert_alpha()
            
        else:
            temp_image = pygame.image.load(join("images", "Enemy shoot2.png")).convert_alpha()
        laser_position = pygame.Rect(self.rect.x, self.rect.y + 50, self.rect.width, self.rect.height)
        laser_object = Laser(group = alien_laser_sprites, position_vector= laser_position, image = temp_image, direction = pygame.math.Vector2(0,1))
        self.laser_list.append(laser_object)
        self.can_shoot = False
        
    
    def shoot_timer(self) -> None:
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > self.laser_cooldown:
                self.can_shoot = True
                self.laser_cooldown = random.randint(5000, 10000)
    
    def update(self,delta_time):
        self.laser_list = [laser for laser in self.laser_list if not laser.out_of_bounds(WINDOW_HEIGHT, WINDOW_WIDTH)]
        
          
class AlienManager:
    def __init__(self, alien_image,alien_image2, alien_pos, alien_row, alien_column) -> None:
        self.alien_pos = alien_pos
        self.alien_row = alien_row
        self.alien_column = alien_column
        self.alien_image2= alien_image2
        self.alien_list = [[None]*self.alien_column for _ in range(self.alien_row)]
        
        #shoot cooldown
        
        self.shoot_time = 0
        
        #creation of martix with aliens
        for i in range(self.alien_row):
            for j in range (self.alien_column):
                if(i < int(self.alien_row/2)):
                    self.alien_list[i][j] = Alien(alien_sprites, alien_image2, pos_vector = self.alien_pos, type = 2)
                elif(i == self.alien_row-1):
                    self.alien_list[i][j] = Alien(alien_sprites, alien_image, pos_vector = self.alien_pos, can_begin_shoot = True)
                else:
                    self.alien_list[i][j] = Alien(alien_sprites, alien_image, pos_vector = self.alien_pos)
                self.alien_pos.x += 100
            self.alien_pos.x = 90
            self.alien_pos.y += 70
    
    #moves all aliens in the matrix       
    def move_all(self, delta_time):
        for row in self.alien_list:
            for alien in row:
                alien.move_horizontal(delta_time)
                
    def lower_all(self):
        for row in self.alien_list:
            for alien in row:
                alien.move_vertically()

    
    def shoot(self):
         for row in self.alien_list:
            for alien in row:
                if(alien.can_begin_shoot == True and alien.can_shoot):
                    alien.shoot_laser()
                else:
                    alien.shoot_timer()
                   
                    
    
    def update(self, delta_time):
        self.move_all(delta_time= delta_time)
        self.shoot()
        
    def remove_and_start_shoot(self, killed_alien):
        for row_index, column in enumerate(self.alien_list):
            for column_index, alien in enumerate(column):
                if alien == killed_alien:
                    del self.alien_list[row_index][column_index]
                    if row_index > 0:
                        self.alien_list[row_index-1][column_index].can_begin_shoot = True
                    break
                
                
# pygame setup
pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True

all_sprites = pygame.sprite.Group()
player_laser_sprites = pygame.sprite.Group()
alien_sprites = pygame.sprite.Group()
alien_laser_sprites = pygame.sprite.Group()


player = Player(all_sprites)
alien_sprite = pygame.image.load(join("images", "alien.png")).convert_alpha()
alien_sprite2 = pygame.image.load(join("images", "alien2.png")).convert_alpha()
manager = AlienManager( alien_image= alien_sprite, alien_image2 = alien_sprite2 , alien_pos= pygame.math.Vector2(90, 50), alien_row= 5, alien_column= 12)

#custom event -> alien vertical move event
alien_event = pygame.event.custom_type()
pygame.time.set_timer(alien_event, 10000)


#previous mouse pos 
old_mouse_pos = pygame.mouse.get_pos()

#surfaces
background = pygame.image.load(join("images", "space.jpg")).convert()

#Music setup
pygame.mixer.music.load(join("audio" , "02.mp3"))
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.05)

while running:

    delta_time = clock.tick()/1000  # delta time, use for same speed regardless of fps
    # poll for events
        # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == alien_event:
            manager.lower_all()
            
    #check if music playing
    if not pygame.mixer.music.get_busy():
        pygame.music.play()
        pygame.mixer.music.set_volume(0.05)

    #caption name
    pygame.display.set_caption("Space Invaders")
    
    # Game rendering
    
    old_mouse_pos = player.custom_update(delta_time, old_mouse_pos)
    manager.update(delta_time)
    
    #update
    all_sprites.update(delta_time)
    alien_sprites.update(delta_time)
    alien_laser_sprites.update(delta_time)
    
    if(pygame.sprite.spritecollide(player, alien_laser_sprites, True)):
        player.kill()
        running = False
    
    for laser in player_laser_sprites:
        collided_aliens = pygame.sprite.spritecollide(laser, alien_sprites, True)
        if collided_aliens:
            laser.kill()
            for alien in collided_aliens:
                manager.remove_and_start_shoot(alien)
        
            
    
    
    display.fill("white")
    display.blit(background, (0, 0))
    
    
    alien_sprites.draw(display)
    alien_laser_sprites.draw(display)
    all_sprites.draw(display)
    

    # update() the display to put your work on screen
    pygame.display.update()
    
pygame.quit()
