import pygame
from pygame.sprite import Sprite

class Ship(Sprite) :
    """ A class to manage the ship """
    
    def __init__(self, ai_game) :
        """ Initialize the ship and set its starting position. """
        # Implements already-existing code in Sprite
        super().__init__()
        
        # Initializes the screen for the ship as the one in the given instance of a Alien Invasion game
        self.screen = ai_game.screen
        
        # Initializes the settings of the ship as the setting of the current instance of Alien Invasion
        self.setting = ai_game.settings
        
        # Gets the size and edges of the screen so we can position the ship properly.
        self.screen_rect = ai_game.screen.get_rect()
        
        # Load the ship image
        self.image = pygame.image.load("images/ship.bmp")
        
        # Gets a rectangle around the ship image, which helps us know where and how to draw it.
        self.rect = self.image.get_rect()
        
        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom
        
        # Store a float for the ship's exact horizontal position. This because rect.x can only store integer value
        # This line of code will allow x coordinate be incremented by a float value
        self.x = float(self.rect.x)
        
        # Movement flag; start with a ship that's not moving.
        self.moving_right = False
        self.moving_left = False
    
    def center_ship(self) :
        """ Center the ship on the screen. """
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
    
    def update(self) :
        """ Update the ship's position based on the movement flag. """
        # Increment the x attribute as long as the hitbox of the ship is less than the right border of the screen.
        if self.moving_right and (self.rect.right < self.screen_rect.right) :
            self.x += self.setting.ship_speed
            
        # Decrement the x attribute as long as the hitbox of the ship is less than the left border of the screen.
        if self.moving_left and (self.rect.left > self.screen_rect.left):
            self.x -= self.setting.ship_speed
        
        # Updates the position of ship to the value being store in self.x, which be downward casted from float to int
        self.rect.x = self.x
    
    def blitme(self) :
        """ Draw the ship at its current location """
        # Actually places the ship image onto the screen at the position described by its rectangle (rect).
        self.screen.blit(self.image, self.rect)