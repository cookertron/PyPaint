import os, math, time
from random import randint, uniform

import pygame
from pygame import Rect, Vector2
from pygame.cursors import sizer_x_strings
from pygame.locals import *


class brush:
    radius = 8
    diameter = radius * 2
    pos = None
    previous_pos = None
    background_surface = None

    def __init__(s):
        s.background_surface = pygame.Surface((s.diameter, s.diameter))

    def get_background(s):
        global PDS
        s.previous_pos = Vector2(s.pos)
        s.background_surface.blit(PDS, (0, 0), (s.pos - (s.radius, s.radius), (s.diameter, s.diameter)))

    def put_background(s):
        global PDS
        PDS.blit(s.background_surface, s.previous_pos - (s.radius, s.radius))

    def resize(s, offset):
        s.put_background()
        s.radius += offset
        if s.radius < 1:
            s.radius = 1
        s.diameter = s.radius * 2
        s.background_surface = pygame.Surface((s.diameter, s.diameter))


    def draw(s, color):
        global PDS
        pygame.draw.circle(PDS, color, BRUSH.pos, BRUSH.radius)

class palette:
    def __init__(s, width, background_color=(255, 255, 255)):
        global PDR

        s.rect = Rect(0, 0, width, PDR.h)
        s.background_surface = pygame.Surface(s.rect.size)
        s.palette_surface = pygame.Surface(s.rect.size)
        s.palette_surface.fill(background_color)
        
        palette_image = pygame.image.load("palette.png").convert()
        pallete_size = palette_image.get_rect().size
        ratio = width / pallete_size[0]
        stretch_size = (width, int(pallete_size[1] * ratio))

        s.palette_surface.blit(pygame.transform.scale(palette_image, stretch_size), (0, 0))

        s.color = s.palette_surface.get_at((0, 0))

    def get_color(s, pos):
        if pos.x < s.rect.right:
            s.color = s.palette_surface.get_at((int(pos.x), int(pos.y)))
            return True
        return False

    def show(s):
        global PDS
        s.background_surface.blit(PDS, (0, 0), s.rect)
        PDS.blit(s.palette_surface, (0, 0))
    
    def hide(s):
        global PDS
        PDS.blit(s.background_surface, (0, 0))


class browser:
    class thumbnail_from_file:
        def __init__(s, filename, size):
            s.filename = filename
            s.surface = pygame.transform.smoothscale(pygame.image.load(filename).convert(), size)

    class thumbnail_from_PDS:
        def __init__(s, filename, surface):
            s.filename = filename
            s.surface = surface

    def __init__(s, width, background_color=(255, 255, 255)):
        global PDR

        # create surfaces
        s.background_surface = pygame.Surface((width, PDR.width))
        s.browser_surface = pygame.Surface((width, PDR.width))
        s.browser_surface.fill(background_color)
        s.background_color = background_color

        # calculate the size of the save image thumbnail
        ratio = width / PDR.width
        s.thumbnail_size = (width, int(ratio * PDR.height))

        # how many thumbnails fit into the browser vertically?
        s.visible_thumbnails = PDR.height // s.thumbnail_size[1]

        # saves go in here. create if doesn't exist
        if not os.path.isdir('saves'):
            os.mkdir("saves")

        # grab a list of all the files in the save folder
        save_files =  os.listdir(".\\saves")

        # go through the list of filenames and create thumbnail images
        s.thumbnails = []
        thumbnail_y_pos = 0
        for filename in save_files[::-1]:
            if filename[-3:] == "png" or filename[-3:] == "PNG":
                s.thumbnails.append(s.thumbnail_from_file(".\\saves\\" + filename, s.thumbnail_size))
                if thumbnail_y_pos < s.visible_thumbnails:
                    s.browser_surface.blit(s.thumbnails[-1].surface, (0, thumbnail_y_pos * s.thumbnail_size[1]))
                thumbnail_y_pos += 1

    def show(s):
        global PDS

        s.background_surface.blit(PDS, (0, 0), s.background_surface.get_rect())
        PDS.blit(s.browser_surface, (0, 0))

    def hide(s):
        global PDS

        PDS.blit(s.background_surface, (0, 0))

    def open_image(s, pos):
        if pos.x > s.thumbnail_size[0]:
            return False
        else:
            index = int(pos.y // s.thumbnail_size[1])
            if index < min(s.visible_thumbnails, len(s.thumbnails)):
                print(s.thumbnails[index].filename)
                return pygame.image.load(s.thumbnails[index].filename).convert()
    
    def redraw(s):
        global PDS
        s.browser_surface.fill(s.background_color)
        thumbs_to_blit = min(s.visible_thumbnails, len(s.thumbnails))
        for index in range(thumbs_to_blit):
            s.browser_surface.blit(s.thumbnails[index].surface, (0, index * s.thumbnail_size[1]))

    def save_image(s):
        thumbnail = pygame.transform.smoothscale(PDS, s.thumbnail_size)
        filename = ".\\saves\\image{}.png".format(int(time.time()))
        s.thumbnails.insert(0, s.thumbnail_from_PDS(filename, thumbnail))
        pygame.image.save(PDS, filename)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
PDR = Rect(0, 0, 1280, 800)
PDS = pygame.display.set_mode(PDR.size, FULLSCREEN|SCALED)
PDS.fill(WHITE)

BRUSH = brush()
PALETTE = palette(80, (255, 0, 0))
BROWSER = browser(80)

DRAWING_MODE = 0
PALETTE_OPEN = 1
BROWSER_OPEN = 2

program_state = DRAWING_MODE
changes = False

exit_program = False
while not exit_program:

    BRUSH.pos = Vector2(pygame.mouse.get_pos())
    mb = pygame.mouse.get_pressed()

    # execute code dependant on program state
    if program_state == DRAWING_MODE:
        # handle events for drawing mode
        events = pygame.event.get()
        for event in events:
            
            # key handling
            if event.type == KEYUP:

                # quit program if ESC is pressed
                if event.key == K_ESCAPE:
                    exit_program = True
                    break
                
                if event.key == K_DELETE:
                    PDS.fill(WHITE)
                    BRUSH.get_background()

                # open the palette if the TAB key is pressed
                if event.key == K_TAB:
                    # remove the brush from the display
                    PALETTE.show()
                    program_state = PALETTE_OPEN

                if event.key == K_F1:
                    BROWSER.show()
                    program_state = BROWSER_OPEN

                if event.key == K_F2 and changes == True:
                    BRUSH.put_background()
                    BROWSER.save_image()
                    BROWSER.redraw()
                    BROWSER.show()
                    BRUSH.get_background()
                    changes = False
                    program_state = BROWSER_OPEN

            if event.type == MOUSEWHEEL:
                BRUSH.resize(event.y)

        if program_state != DRAWING_MODE: continue

        # on first run grab the background behind the brush
        BRUSH.get_background()
        BRUSH.draw(PALETTE.color)
        pygame.display.update()
        
        if not mb[0]:
            BRUSH.put_background()
        else:
            changes = True

    if program_state == PALETTE_OPEN:
        # handle events when the palette is open
        events = pygame.event.get()
        for event in events:
            
            # key handling
            if event.type == KEYUP:

                # quit program if ESC is pressed
                if event.key == K_ESCAPE:
                    exit_program = True
                    break

                # Hide the palette if the TAB key is pressed
                if event.key == K_TAB:
                    # remove the brush from the display
                    PALETTE.hide()
                    BRUSH.get_background()
                    program_state = DRAWING_MODE

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not PALETTE.get_color(BRUSH.pos):
                        PALETTE.hide()
                        program_state = DRAWING_MODE

            if event.type == MOUSEWHEEL:
                BRUSH.resize(event.y)

        if program_state != PALETTE_OPEN:
            continue

        # on first run grab the background behind the brush
        BRUSH.get_background()
        BRUSH.draw(PALETTE.color)
        pygame.display.update()
        BRUSH.put_background()

    if program_state == BROWSER_OPEN:
        # handle events when the palette is open
        events = pygame.event.get()
        for event in events:
            
            # key handling
            if event.type == KEYUP:

                # quit program if ESC is pressed
                if event.key == K_ESCAPE:
                    exit_program = True
                    break

                # Hide the browser if the F1 key is pressed
                if event.key == K_F1 or event.key == K_F2:
                    # remove the brush from the display
                    BROWSER.hide()
                    BRUSH.get_background()
                    program_state = DRAWING_MODE

            # if the mouse button is pressed then open the file
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    loaded_image = BROWSER.open_image(BRUSH.pos)
                    if not loaded_image:
                        BROWSER.hide()
                        program_state = DRAWING_MODE
                    else:
                        BRUSH.put_background()
                        BROWSER.hide()
                        PDS.blit(loaded_image, (0, 0))
                        program_state = DRAWING_MODE

            if event.type == MOUSEWHEEL:
                BRUSH.resize(event.y)

        if program_state != BROWSER_OPEN:
            continue

        # on first run grab the background behind the brush
        BRUSH.get_background()
        BRUSH.draw(PALETTE.color)
        pygame.display.update()
        BRUSH.put_background()

pygame.quit()