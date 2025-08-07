import sys
from time import sleep
from pathlib import Path
import json

import pygame

from setting import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button

class AlienInvasion :
    """ Overall class to manage game assets and behavior """
    
    def __init__(self) :
        """ Initialize the game, and create game resources """
        # Initializes all pygame modules
        pygame.init()
        
        # This create a clock to make FPS rates consistent across different OS
        self.clock = pygame.time.Clock()
        
        # Initializes the default settings
        self.settings = Settings()
        
        # "Opens a window with the provided settings"
        # self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        
        # "Opens the game in fullscrreen"
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        # Creates an instance to store game statistics
        self.stats = GameStats(self)
        
        # Creates an instance of Scoreboard
        self.sb = Scoreboard(self)
        
        # Set the background color
        self.bg_color = self.settings.bg_color
        
        # Initializes the ship object
        self.ship = Ship(self)
        
        # Initializes a Group object that will contain the bullets
        self.bullets = pygame.sprite.Group()
        
        # Initializes a Group object that will contain the aliens
        self.aliens = pygame.sprite.Group()
        
        # Create a fleet of aliens
        self._create_fleet()
        
        # Sets the active state of an Alien Invasion game
        self.game_active = False
        
        # Shooting flag; start not firing
        self.shooting = False
        
        # Make the Play Button
        self.play_button = Button(self, "Play")
        
        # Stores the current high_score
        self.initial_high_score = self.stats.high_score
    
    def run_game(self) :
        """ Start the main loop for the game. """
        while True :
            # Watch the keyboard and mouse events.
            self._check_events()
            
            # Will continuously fire bullets while self.shooting is set to True
            self._fire_bullet()
            
            # Checks if the ship can fire a bullet :
            self._bullet_cooldown()
            
            if self.settings.bullet_cooldown > 0 :
                self.settings.bullet_cooldown -= 1
            
            if self.game_active :
                # Updates the 'moving' attribute of the ship
                self.ship.update()
            
                # Update each bullet.
                self._update_bullets()
            
                # Update each aliens
                self._update_aliens()
            
            # Updates the screen
            self._update_screen()
                
            # This make so that the game will run consistenly in 60 FPS
            self.clock.tick(60)
    
    def _check_events(self) :
        """ Respond to keypresses and mouse events. """
        for event in pygame.event.get() :
            # If the player pressed the exit button
            if event.type == pygame.QUIT :
                self._quit_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN :
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            
            # If the player hold down a key
            elif event.type == pygame.KEYDOWN :
                self._check_keydown_events(event)
            
            # If the player lets go of a key
            elif event.type == pygame.KEYUP :
                self._check_keyup_events(event)
    
    def _check_play_button(self, mouse_pos) :
        """ Start a new game when the player clicks Play."""
        clicked = self.play_button.rect.collidepoint(mouse_pos)
        
        if clicked and not self.game_active :
            self._start_game()
    
    def _start_game(self) :
        # Reset the game settings
        self.settings.initialize_dynamic_settings()
        
        # Reset the game statistics
        self.stats.reset_stats()
        
        # Resets the scoreboard back to 0
        self.sb.prep_score()
        
        # Resets the level back to 1
        self.sb.prep_level()
        
        # Shows the number of ships left
        self.sb.prep_ships()
            
        # Start a new game
        self.game_active = True
            
        # Get rid of any remaining bullets and aliens.
        self.bullets.empty()
        self.aliens.empty()
            
        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()
            
        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)
    
    def _check_keydown_events(self, event) :
        # If the player holds down the right arrow key
        if event.key == pygame.K_RIGHT :
            self.ship.moving_right = True
                    
        # If the player holds down the left arrow key
        elif event.key == pygame.K_LEFT :
            self.ship.moving_left = True
        
        # If the player pressed 'Q', the game will quit
        elif event.key == pygame.K_q :
            self._quit_game()
        
        # If the player press 'P', the game will start
        elif event.key == pygame.K_p and not self.game_active :
            self._start_game()
        
        # If the player holds 'SPACE', the ship will start firing bullets
        elif event.key == pygame.K_SPACE :
            self.shooting = True
    
    def _check_keyup_events(self, event) :
        # If the player lets go the right arrow key
        if event.key == pygame.K_RIGHT :
            self.ship.moving_right = False
                    
        # If the player lets go the left arrow key
        elif event.key == pygame.K_LEFT :
            self.ship.moving_left = False
        
        # If the player lets go of 'SPACE, the ship will stop firing bullets
        elif event.key == pygame.K_SPACE :
            self.shooting = False
    
    def _fire_bullet(self) :
        """ Create a new bullet and add it to the bullets group """
        if self.shooting and self.settings.bullet_cooldown == 0:
            if len(self.bullets) < self.settings.bullets_allowed :
                new_bullet = Bullet(self)
                self.bullets.add(new_bullet)
                self.settings.bullet_cooldown = 15
    
    def _bullet_cooldown(self) :
        if self.settings.bullet_cooldown > 0 :
                self.settings.bullet_cooldown -= 1
    
    def _update_bullets(self) :
        """ Update position of bullets and get rid of old bullets """
        # Update bullet positions.
        self.bullets.update()
        
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy() :
            if bullet.rect.bottom <= 0 :
                self.bullets.remove(bullet)
                # print(len(self.bullets))
        
        self._check_bullet_alien_collision()
    
    def _create_fleet(self) :
        """ Create the fleet of aliens. """
        # Creates an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        current_x, current_y = alien_width, alien_height
        
        while current_y < (self.settings.screen_height - (6 * alien_height)) :
            while current_x < (self.settings.screen_width - (2 * alien_width)) :
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            
            # Finished a row; reset x value, and increment y value
            current_x = alien_width
            current_y += 2 * alien_height
    
    def _create_alien(self, x_position, y_position) :
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)
    
    def _check_fleet_edges(self) :
        """ Respond appropriately if any aliens have reached an edge. """
        for alien in self.aliens.sprites() :
            if alien.check_edges() :
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self) :
        """ Drop the entire fleet and change the fleet's direction. """
        for alien in self.aliens.sprites() :
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _update_aliens(self) :
        """ Update the positions of all aliens in the fleet """
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens) :
            self._ship_hit()
        
        # Look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()
    
    def _ship_hit(self) :
        """ Respond to the ship being hit by an alien. """
        if self.stats.ships_left > 0 :
            # Decrement ships_left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
        
            # Get rid of any remaining bullets and aliens/
            self.bullets.empty()
            self.aliens.empty()
        
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
        
            # Pause
            sleep(0.5)
            
        else :
            self.game_active = False
            pygame.mouse.set_visible(True)
    
    def _check_aliens_bottom(self) :
        """ Check if any aliens have reached the bottom of the screen. """
        for alien in self.aliens.sprites() :
            if alien.rect.bottom >= self.settings.screen_height :
                # Treat this the same  as if the ship got hit.
                self._ship_hit()
                break
    
    def _check_bullet_alien_collision(self) :
        """ Respond to bullet-alien collision"""
        # Check for any bullets that have hit aliens.
        # If so, get rid of the bullet and alien.
        collision = pygame.sprite.groupcollide(self.bullets, self.aliens,
                                                self.settings.bullet_disappear_after_hit, True)
        
        if collision :
            for aliens in collision.values() :
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        
        # If an entire fleet is destroyed, a new fleet appears
        if not self.aliens :
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            
            # Increase game speed
            self.settings.increase_speed()
            
            # Increase level
            self.stats.level += 1
            self.sb.prep_level()
    
    def _update_screen(self) :
        """ Update images on the screen, and flip to the new screen. """
        # Redraw the screen during each pass through the loop
        self.screen.fill(self.bg_color)
        
        # Draws each bullet
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        
        # Updates the current position of the ship
        self.ship.blitme()
        
        # Draws the aliens
        self.aliens.draw(self.screen)
        
        # Draw the score information.
        self.sb.show_score()
        
        # Draw the play button if the game is inactive
        if not self.game_active :
            self.play_button.draw_button()
        
        # Make the most recently drawn screen visible.
        pygame.display.flip()
    
    def _quit_game(self) :
        """ Exits the game"""
        # Check whether the current high score is greater than the high score at the start of the game
        if (self.stats.high_score > self.initial_high_score) and not self.game_active :
            self._update_high_score()
        
        sys.exit()
    
    def _update_high_score(self) :
        """ Updates high_score.json """
        # Converts self.stats.high_score into .json format
        contents = json.dumps(self.stats.high_score)
        
        # Creates a path to high_score.json then dumps the formated text into it
        path = Path("src/json_files/high_score.json")
        path.write_text(contents)


if __name__ == "__main__" :
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()