import sys, pygame
import pygame.surfarray as surfarray
from math import cos
from math import sin
from math import floor
import numpy as np

# Initialize pygame
pygame.init()

# Define colors
wall_color = (75,233,250)
background_color = (129, 138, 145)
black = 0, 0, 0

# Width and height of the map
width = 400
height = 400
size = (width, height)

# Width and height of textures
# Here we use 32x32 textures, but other sizes can be used
texture_width = 32
texture_height = 32

# Replace zero by a sufficiently small value when division by zero occurs
dbz = 0.0000001

# Define rotational and movement speed
rot_speed = 0.01
mov_speed =  0.01

# Define the world map
# As you can see, the world map is just a two-dimensional Python list
# where zeroes represent empty space, and non-zero integers represent
# different textures
map =  [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 5, 0, 0, 1],
            [1, 0, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 4, 4, 0, 0, 4, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 5, 5, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 5, 5, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1],
            [1, 4, 4, 0, 0, 4, 0, 0, 5, 5, 5, 5, 0, 1, 0, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ]

# Create a screen
screen = pygame.display.set_mode(size)

# Texture loading
# This is done using surfarray.array3d, which converts the images into two-dimensional arrays of RGB colors
# which then can be easily accessed just as any other Python list
bricks = pygame.surfarray.array3d(pygame.image.load('./textures/bricks.png'))
dirt = pygame.surfarray.array3d(pygame.image.load('./textures/dirt.png'))
grass = pygame.surfarray.array3d(pygame.image.load('./textures/grass_block_side.png'))
cobblestone = pygame.surfarray.array3d(pygame.image.load('./textures/cobblestone.png'))
netherbrick = pygame.surfarray.array3d(pygame.image.load('./textures/chiseled_nether_bricks.png'))

# All the textures are put inside an array
# The 0 texture is just a blank placeholder and it is not used
textures = np.asarray([[0,0,0], bricks, dirt, grass, cobblestone, netherbrick], dtype=object)


# This raycasting implementation relies on vector calculations
# The position of the player, its direction, and the camera plane are all vectors 
pos_x, pos_y = 8.0,  5.0 # Position vector
dir_x, dir_y = -1, 1 # Direction vector
plane_x, plane_y = 0, 0.66 # Camera plane vector, it must be perpendicular to the direction vector

# If a key is kept pressed down, the event will keep on being sent repeteadly
pygame.key.set_repeat(1,10) 

# GAME LOOP
while True:
    # Create a surface canvas
    canvas = pygame.Surface( ( width, height ) )
    canvas.fill( background_color ) # The background is created
    canvas_array = pygame.surfarray.array3d(canvas) # Convert the surface canvas into an array for direct pixel manipulation

    # Keystroke event-handling logic
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
        
            # Quit the game by pressing q
            if event.key == pygame.K_q: 
                sys.exit()
            
            # In order for the player to look to the left or right, a standard matrix rotation formula is used
            if event.key == pygame.K_LEFT:
                old_dir_x = dir_x
                dir_x = dir_x * cos(rot_speed) - dir_y  * sin(rot_speed)
                dir_y = old_dir_x * sin(rot_speed) + dir_y * cos(rot_speed)
                old_plane_x = plane_x
                plane_x = plane_x * cos(rot_speed) - plane_y * sin(rot_speed)
                plane_y = old_plane_x * sin(rot_speed) + plane_y * cos(rot_speed)
            if event.key == pygame.K_RIGHT:
                old_dir_x = dir_x
                dir_x = dir_x * cos(-rot_speed)  - dir_y  * sin(-rot_speed)
                dir_y = old_dir_x * sin(-rot_speed) + dir_y * cos(-rot_speed)
                old_plane_x = plane_x
                plane_x = plane_x * cos(-rot_speed) - plane_y * sin(-rot_speed)
                plane_y = old_plane_x * sin(-rot_speed) + plane_y * cos(-rot_speed)

                # In order to move forwards or backwards, a vector sum is applied in order to change the x and y coordinates
                # The position vector is added to the direction vector multiplied by the movement speed
            if event.key == pygame.K_UP:
                if not map[int(pos_x + dir_x * mov_speed)][int(pos_y)]: 
                    pos_x += dir_x *  mov_speed
                if not map[int(pos_x)][int(pos_y + dir_y * mov_speed)]:
                    pos_y += dir_y * mov_speed
            if event.key == pygame.K_DOWN:
                if not map[int(pos_x - dir_x * mov_speed)][int(pos_y)]: 
                    pos_x -= dir_x *  mov_speed
                if not map[int(pos_x)][int(pos_y - dir_y * mov_speed)]:
                    pos_y -= dir_y * mov_speed

    
    # RAYCASTING LOGIC

    # We iterate through every pixel on the screen, from left to right
    for i in range(0, width):
        # From the camera plane x coordinates, we find the direction vector of the ray
        camera_x = 2*i / float(width) - 1
        ray_direction_x = dir_x + plane_x * camera_x
        ray_direction_y = dir_y + plane_y * camera_x

        # Calculate which box of the map we are in
        map_x = int(pos_x)
        map_y = int(pos_y)

        # Each box of the map has a x-side and a y-side
        # It is best to move the ray from one side to another, so that we don't miss any box
        # Here we calculate the length of ray from its current position to the next x or y-side
        side_dist_x = 0
        side_dist_y = 0

        # And here we calculate the length of ray from one x or y-side to next x or y-side
        delta_dist_x = dbz if ray_direction_x == 0 else abs(1/ray_direction_x)
        delta_dist_y = dbz if ray_direction_y == 0 else abs(1/ray_direction_y)

        # This represents the distance from the player to the wall
        perpwall_dist = 0

        # These parameters indicate in which x or y-direction to move each step of the ray (either +1 or -1)
        step_x = 0
        step_y = 0
        
        hit = 0 # Check if a wall was hit
        side =  0 # Check if it was an x-side or a y-side

        # Calculate step and initial sideDist
        if(ray_direction_x < 0):
            step_x = -1
            side_dist_x = (pos_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x
        if(ray_direction_y < 0):
            step_y = -1
            side_dist_y = (pos_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y

        # Perform the ray-steps, until a wall is hit
        while (hit == 0):
            # Basically, the x and y-distances from the current side to the other are updated
            # then the box of the map we are in is updated accordingly by one x or y-step
            # and finally we check if a wall was hit
            if (side_dist_x < side_dist_y):
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1 # If we are closer to a y-side, then update to 1
            # Wall check
            if(map[map_x][map_y]>0): 
                hit = 1
        
        # Calculate the distance between the wall and the player
        if(side == 0):
            perpwall_dist = (side_dist_x - delta_dist_x)
        else:
            perpwall_dist = (side_dist_y - delta_dist_y)

        # From that, calculate height of line to be drawn on screen
        line_height = height / (perpwall_dist + dbz)

        # This calculates the first and the last pixel of the current line
        draw_start = -line_height / 2 + height / 2
        if(draw_start < 0):
            draw_start = 0
        draw_end = line_height / 2 + height / 2
        if(draw_end >= height):
            draw_end = height - 1
        
        # TEXTURING LOGIC

        # Affine texture mapping is applied by finding which coordinate of the wall was hit
        # and the corresponding texture coordinate
        
        # Here we find wall_x ,which is the x wall-coordinte hit by the ray
        wall_x = 0.0
        if(side == 0):
            wall_x = pos_y + perpwall_dist * ray_direction_y 
        else:
            wall_x = pos_x + perpwall_dist * ray_direction_x
        wall_x -= floor(wall_x)

        # From wall_x, it is easy to infer the corresponding x-texture coordinate
        tex_x = int(wall_x * texture_width)
        if(side == 0 and ray_direction_y > 0):
            tex_x = texture_width - tex_x - 1
        if(side == 1 and ray_direction_y < 0):
            tex_x = texture_width - tex_x - 1
        
        # How much to increase the textures coordinate per screen pixel
        step = 1.0 * texture_height / line_height
        # Starting textures coordinate
        tex_pos = (draw_start - height / 2 + line_height / 2) * step

        # RENDERING LOGIC
        if(hit): # Check if a wall was hit
            for y in range(int(draw_start), int(draw_end)): # For each y wall coordinate, calculate the corresponding y texture coordinate
                tex_y = int(tex_pos) & (texture_height - 1)
                # Retrieve the RGB color to draw from the textures array
                # First, from the map box number, get the index of the texture to draw
                # Second, from the x and y texture coordinates, retrieve the exact RGB color to draw
                color = textures[map[map_x][map_y]][tex_x][tex_y]
                if(side == 1):
                    # If it is a side wall, decreases the color brightness
                    # To do so, it removes the last bit in order to divide the RGB value by two, then sets the first bit of every byte to zero
                    # in order to prevent screwing up the colors
                    color = (color >> 1) & 8355711
                tex_pos += step # Increase the step by one pixel
                canvas_array[i][y] = color # Draw the pixel with the right color into the screen
    canvas = pygame.pixelcopy.make_surface(canvas_array)
    screen.blit( canvas, ( 0, 0 ) ) # Blit the canvas
    pygame.display.update() # Refresh the display