from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import random
import time


WIN_W = 1920
WIN_H = 1080
VIEW_ANGLE = 85.0
FIELD_WIDTH = 820
FIELD_DEPTH = 480
OBSTACLE_HEIGHT = 90 
AVATAR_SCALE = 42
FLOAT_HEIGHT = 28
SCREEN_RATIO = WIN_W / WIN_H


SHOT_RADIUS = 7.0
SHOT_SPEED = 24.0
WEAPON_MODES = {
    'BASIC': 0,
    'ICE': 1,
    'FIRE': 2,
    'BACKWARDS': 3,
    'SLUGGISH': 4,
    'CHAOS': 5
}
SHOT_PALETTE = {
    0: (0.8, 0.8, 0.8),
    1: (0.1, 0.6, 0.9),
    2: (0.9, 0.3, 0.2),
    3: (0.2, 0.9, 0.7),
    4: (0.95, 0.7, 0.1),
    5: (0.85, 0.1, 0.85)
}


MAX_THREATS = 6
THREAT_SCALE = 32
THREAT_VELOCITY = 0.18
SPAWN_OFFSET = 110
THREAT_APPENDAGES = 4
COMBAT_RANGE = 45
STRIKE_DELAY = 550


BOOST_TYPES = ['VITALITY', 'MUNITIONS', 'FURY', 'STASIS']
BOOST_HUES = {
    'VITALITY': (0.95, 0.1, 0.1),
    'MUNITIONS': (0.95, 0.65, 0.15),
    'FURY': (0.15, 0.85, 0.4),
    'STASIS': (0.15, 0.95, 0.95)
}
BOOST_SCALE = 22
BOOST_LIFETIME = 5500


ICE_EFFECT = 5500
FIRE_EFFECT = 2200
BLAST_RANGE = 110
REWIND_EFFECT = 1800
TRACK_INTERVAL = 90
POSITION_MEMORY = 25
SLUG_EFFECT = 8500
CHAOS_EFFECT = 6500


KILL_VALUE = 12
STREAK_BONUS = 1.8
TIME_SCORE = 2
STREAK_TIME = 1800


PHASE2_START = 1200
SHIFTER_INIT = 1
SHIFTER_HITS = 3
SHIFTER_DAMAGE = 6
SHIFTER_COOLDOWN = 450
SHIFTER_GROWTH = 1


PHASE3_START = 2400
COLOSSUS_SIZE = 85
COLOSSUS_PACE = 0.07
COLOSSUS_STAMINA = 6
MAX_COLOSSUS = 2
COLOSSUS_FATAL = True
BABY_SIZE = COLOSSUS_SIZE * 0.55
BABY_LIFE = 3
BABY_PACE = COLOSSUS_PACE * 1.15

SUCCESS_TARGET = 3500
mission_accomplished = False


MAX_VISIBLE_THREATS = 6
MAX_VISIBLE_BOOSTS = 7
boost_generation = True
next_boost_time = 0
BOOST_FREQUENCY = 5500


GUARD_TIME = 5500
GUARD_DELAY = 16000
guard_up = False
last_guard_time = 0
GUARD_SPAN = AVATAR_SCALE + 35

PULSE_DELAY = 5500
PULSE_RANGE = 320
PULSE_STRENGTH = 55
PULSE_PARALYSIS = 1200
last_pulse_time = 0

view_point = [-310.0, 10.0, 310.0]
avatar_location = [10, -10, FLOAT_HEIGHT]
avatar_orientation = 15
game_points = 0
streak_count = 0
streak_clock = 0
last_time_score = 0
shots_fired = []
active_weapon = 0
RUSH_VELOCITY = 130.0
rushing = False
last_rush_time = 0
RUSH_COOLDOWN = 5500
hostiles = []
avatar_vitality = 120
simulation_paused = False


CLIP_SIZE = 28
STOCK_SIZE = 110
current_clip = CLIP_SIZE
ammo_stock = STOCK_SIZE
refilling = False
refill_start = 0
REFILL_DURATION = 2800
perspective_mode = False

boost_items = []
fury_active = False
fury_end = 0
stasis_active = False
stasis_end = 0


next_hostile_id = 1000
_boost_tracker = set()


shifter_active = False
shifter_target = SHIFTER_INIT
shifters_eliminated = 0
last_shifter_strike = 0


admin_mode = False
divine_active = False
divine_target = 0
simulation_ended = False

override_active = False
divine_active = False
limitless_ammo = False
perception_mode = False
immortality_active = False
PERCEPTION_AVATAR_SPEED = 22
PERCEPTION_THREAT_SLOW = 0.25

CHAOS_KILL_DELAY = 550
DRIVE_DURATION = 11000
DRIVE_COOLDOWN = 32000
DRIVE_VELOCITY = 16.0
drive_mode = False
last_drive_time = 0

def reset_simulation():
    
    global simulation_ended, simulation_paused, avatar_vitality, game_points
    global shots_fired, hostiles, boost_items, streak_count, streak_clock
    global shifter_active, shifters_eliminated, shifter_target
    global boost_generation, next_boost_time, next_hostile_id
    global current_clip, ammo_stock, refilling, refill_start, mission_accomplished
    global avatar_location, avatar_orientation, view_point, last_rush_time
    global last_guard_time, last_pulse_time, drive_mode, last_drive_time

    drive_mode = False
    last_drive_time = 0

    simulation_ended = False
    simulation_paused = False
    mission_accomplished = False

    avatar_vitality = 120
    game_points = 0
    shots_fired = []
    boost_items = []
    hostiles = []
    streak_count = 0
    streak_clock = 0

    shifter_active = False
    shifters_eliminated = 0
    shifter_target = SHIFTER_INIT

    boost_generation = True
    next_boost_time = int(time.time() * 1000) + random.randint(1800, 5200)

    current_clip = CLIP_SIZE
    ammo_stock = STOCK_SIZE
    refilling = False
    refill_start = 0

def divine_fire():
   
    global shots_fired, current_clip, refilling, ammo_stock, avatar_orientation
    global divine_active, divine_target, active_weapon

    if not divine_active or simulation_paused or refilling or current_clip <= 0 or not hostiles:
        return

    if active_weapon == 0:
        ax, ay, az = avatar_location
        
        
        distances = []
        for h in hostiles:
            dist = ((h[0]-ax)**2 + (h[1]-ay)**2) ** 0.5
            distances.append((dist, h))
        
        if distances:
            target = min(distances, key=lambda x: x[0])[1]
            dx = target[0] - ax
            dy = target[1] - ay
            angle = math.atan2(dy, dx)
            avatar_orientation = math.degrees(angle)
            
            barrel_x = ax + math.cos(angle) * 24.0
            barrel_y = ay + math.sin(angle) * 24.0
            barrel_z = az + 56.0
            
            if len(shots_fired) < 3 or (shots_fired and shots_fired[-1][4] > 3):
                shots_fired.append([
                    barrel_x,
                    barrel_y,
                    barrel_z,
                    avatar_orientation,
                    0,
                    active_weapon
                ])
                if not divine_active:
                    current_clip -= 1
                    if current_clip == 0 and not refilling and ammo_stock > 0:
                        refilling = True
                        refill_start = int(time.time() * 1000)
    
    else:
       
        active_special_shots = sum(1 for s in shots_fired if s[5] == active_weapon)
        if active_special_shots < 2:
            ax, ay, az = avatar_location
            
            if len(hostiles) > 0:
                if divine_target >= len(hostiles):
                    divine_target = 0
                
                
                targets = [h for h in hostiles if h != hostiles[divine_target]]
                if targets:
                    target = random.choice(targets)
                    divine_target = (divine_target + 1) % len(hostiles)
                    
                    dx = target[0] - ax
                    dy = target[1] - ay
                    angle = math.atan2(dy, dx)
                    avatar_orientation = math.degrees(angle)
                    
                    barrel_x = ax + math.cos(angle) * 24.0
                    barrel_y = ay + math.sin(angle) * 24.0
                    barrel_z = az + 56.0
                    
                    shots_fired.append([
                        barrel_x,
                        barrel_y,
                        barrel_z,
                        avatar_orientation,
                        0,
                        active_weapon
                    ])
                    
                    if not divine_active:
                        current_clip -= 1
                        if current_clip == 0 and not refilling and ammo_stock > 0:
                            refilling = True
                            refill_start = int(time.time() * 1000)

def render_drive_mode():
    
    glPushMatrix()
    try:
        glTranslatef(avatar_location[0], avatar_location[1], avatar_location[2])
        glRotatef(avatar_orientation, 0, 0, 1)
        
        
        glColor3f(0.95, 0.95, 0.95)
        glPushMatrix()
        glScalef(0.9, 0.7, 0.5)
        gluCylinder(gluNewQuadric(), AVATAR_SCALE * 0.9, AVATAR_SCALE * 0.9, AVATAR_SCALE, 10, 2)
        glPopMatrix()
        
        glColor3f(0.08, 0.08, 0.08)
        for wx in [-0.65, 0.65]:
            for wz in [-0.4, 0.4]:
                glPushMatrix()
                glTranslatef(wx * AVATAR_SCALE, wz * AVATAR_SCALE, -AVATAR_SCALE * 0.25)
                gluSphere(gluNewQuadric(), AVATAR_SCALE * 0.25, 10, 10)
                glPopMatrix()

        glColor3f(0.7, 0.15, 0.15)
        glPushMatrix()
        glTranslatef(-AVATAR_SCALE * 0.4, 0, AVATAR_SCALE * 0.45)
        glScalef(0.6, 0.6, 0.4)
        gluCylinder(gluNewQuadric(), AVATAR_SCALE * 0.7, AVATAR_SCALE * 0.5, AVATAR_SCALE, 10, 2)
        glPopMatrix()
        
        glColor3f(0.1, 0.95, 0.95)
        glPushMatrix()
        glTranslatef(0, 0, -AVATAR_SCALE * 0.35)
        glScalef(AVATAR_SCALE * 1.6, AVATAR_SCALE * 1.1, 0.12)
        glutSolidCube(1)
        glPopMatrix()
    finally:
        glPopMatrix()

def render_avatar():
    
    if perspective_mode:
        return
    if drive_mode:
        render_drive_mode()
    else:
        glPushMatrix()
        try:
            glTranslatef(avatar_location[0], avatar_location[1], avatar_location[2])
            glRotatef(avatar_orientation, 0, 0, 1)
            
           
            glColor3f(0.35, 0.35, 0.4)
            glPushMatrix()
            glTranslatef(0, 0, 35)
            gluCylinder(gluNewQuadric(), 22, 18, 45, 10, 3)
            glColor3f(0.1, 0.8, 1.0)
            glTranslatef(0, 0, 22)
            gluCylinder(gluNewQuadric(), 19, 18, 18, 10, 2)
            glPopMatrix()
            
            
            glPushMatrix()
            glTranslatef(0, 0, 80)
            glColor3f(0.35, 0.35, 0.4)
            gluCylinder(gluNewQuadric(), 9, 9, 6, 10, 2)
            glColor3f(0.95, 0.95, 1.0)
            gluSphere(gluNewQuadric(), 14, 10, 10)
            glColor3f(0.1, 0.8, 1.0)
            glPushMatrix()
            glTranslatef(10, 6, 3)
            gluSphere(gluNewQuadric(), 4, 6, 6)
            glTranslatef(0, -12, 0)
            gluSphere(gluNewQuadric(), 4, 6, 6)
            glPopMatrix()
            glColor3f(0.2, 0.7, 1.0)
            glTranslatef(7, 0, 0)
            gluCylinder(gluNewQuadric(), 14, 12, 10, 10, 2)
            glPopMatrix()
            
            
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(0, side * 22, 55)
                glColor3f(0.1, 0.8, 1.0)
                gluSphere(gluNewQuadric(), 9, 8, 8)
                glColor3f(0.35, 0.35, 0.4)
                if side == 1:
                    glRotatef(20, 1, 0, 0)
                else:
                    glRotatef(15, 1, 0, 0)
                gluCylinder(gluNewQuadric(), 7, 6, 22, 8, 2)
                glTranslatef(0, 0, 22)
                glColor3f(0.1, 0.8, 1.0)
                gluSphere(gluNewQuadric(), 7, 8, 8)
                if side == 1:
                    
                    glColor3f(0.25, 0.25, 0.25)
                    glRotatef(95, 0, 1, 0)
                    glRotatef(-15, 0, 0, 1)
                    gluCylinder(gluNewQuadric(), 3.5, 3.5, 28, 10, 2)
                    glColor3f(0.4, 0.4, 0.4)
                    glTranslatef(0, 0, 28)
                    gluCylinder(gluNewQuadric(), 2.2, 1.8, 18, 10, 2)
                    glColor3f(0.5, 0.5, 0.5)
                    glTranslatef(0, 5, -18)
                    gluCylinder(gluNewQuadric(), 1.2, 1.2, 9, 6, 2)
                glPopMatrix()
            
            
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(0, side * 12, 35)
                glColor3f(0.85, 0.55, 0.25)
                gluSphere(gluNewQuadric(), 9, 8, 8)
                glColor3f(0.35, 0.35, 0.4)
                gluCylinder(gluNewQuadric(), 9, 7, 22, 8, 2)
                glTranslatef(0, 0, 22)
                glColor3f(0.85, 0.55, 0.25)
                gluSphere(gluNewQuadric(), 7, 8, 8)
                glTranslatef(0, 0, 18)
                glColor3f(0.2, 0.2, 0.2)
                gluCylinder(gluNewQuadric(), 6, 8, 6, 8, 2)
                gluSphere(gluNewQuadric(), 8, 8, 8)
                glPopMatrix()
        finally:
            glPopMatrix()

def render_hostiles():
    
    current_time = int(time.time() * 1000)
    for hostile in hostiles:
        glPushMatrix()
        try:
            glTranslatef(hostile[0], hostile[1], hostile[2])
            iced = hostile[4] > current_time
            blazing = hostile[5] > current_time
            sluggish = hostile[9] > current_time
            chaotic = hostile[10] > current_time
            is_shifter = (len(hostile) > 12 and hostile[12] == 10)
            is_colossus = (len(hostile) > 12 and hostile[12] == 20)

            if is_colossus:
                is_infant = hostile[12] == 30
                scale_factor = 0.55 if is_infant else 1.0
                
                glPushMatrix()
                glTranslatef(0, 0, 0)
                glColor3f(0.12, 0.12, 0.12)
                glScalef(2.0 * scale_factor, 2.0 * scale_factor, 1.8 * scale_factor)

                
                glPushMatrix()
                glTranslatef(0, 0, 45)
                gluCylinder(gluNewQuadric(), 35, 32, 70, 14, 3)
                glPopMatrix()
                
                glPushMatrix()
                glTranslatef(0, 0, 125)
                glColor3f(0.18, 0.18, 0.18)
                gluSphere(gluNewQuadric(), 32, 14, 14)
                glPopMatrix()
                
               
                for side in [-1, 1]:
                    glPushMatrix()
                    glTranslatef(0, side * 40, 70)
                    glColor3f(0.15, 0.15, 0.15)
                    gluSphere(gluNewQuadric(), 22, 10, 10)
                    glRotatef(20 if side == 1 else -20, 1, 0, 0)
                    gluCylinder(gluNewQuadric(), 18, 16, 60, 10, 2)
                    glPopMatrix()
                
              
                remaining_hits = hostile[13] if len(hostile) > 13 else COLOSSUS_STAMINA
                glow_level = max(0.3, min(1.0, remaining_hits / COLOSSUS_STAMINA))
                glPushMatrix()
                glTranslatef(15, 0, 125)
                glColor3f(1.0, 0.7 * glow_level, 0.3 * glow_level)
                gluSphere(gluNewQuadric(), 8, 10, 10)
                glPopMatrix()
                glPopMatrix()
                return

            if sluggish:
                glColor3f(0.95, 0.8, 0.1)
                for i in range(3):
                    glPushMatrix()
                    glRotatef(current_time * (0.08 if i == 0 else -0.12), 0, 0, 1)
                    glScalef(1.3, 1.3, 1.1)
                    gluSphere(gluNewQuadric(), THREAT_SCALE + 2, 10, 10)
                    glPopMatrix()
            
            if iced:
                glColor3f(0.6, 0.85, 1.0)
                gluSphere(gluNewQuadric(), THREAT_SCALE + 3, 10, 10)
            
            if blazing:
                glColor3f(0.9, 0.3, 0.2)
                for _ in range(8):
                    glPushMatrix()
                    rand_x = random.uniform(-10, 10)
                    rand_y = random.uniform(-10, 10)
                    rand_h = random.uniform(0, 35)
                    glTranslatef(rand_x, rand_y, rand_h)
                    glColor3f(0.25, 0.25, 0.25)
                    gluSphere(gluNewQuadric(), 5, 6, 6)
                    glPopMatrix()

           
            if chaotic:
                base_hue = (0.9, 0.2, 0.9)
            elif is_shifter:
                base_hue = (0.35, 0.15, 0.6)
            elif blazing:
                base_hue = (0.9, 0.35, 0.25)
            elif iced:
                base_hue = (0.4, 0.7, 1.0)
            else:
                base_hue = (0.5, 0.6, 0.65)

            glColor3f(*base_hue)
           
            glPushMatrix()
            glTranslatef(0, 0, 35)
            gluCylinder(gluNewQuadric(), 18, 14, 35, 10, 3)
            glColor3f(base_hue[0] * 1.3, base_hue[1] * 1.3, base_hue[2] * 1.3)
            glTranslatef(0, 0, 18)
            gluCylinder(gluNewQuadric(), 15, 16, 12, 10, 2)
            glPopMatrix()
            
            glPushMatrix()
            glTranslatef(0, 0, 70)
            glColor3f(*base_hue)
            gluCylinder(gluNewQuadric(), 6, 6, 6, 8, 2)
            glColor3f(base_hue[0] * 0.9, base_hue[1] * 0.9, base_hue[2] * 0.9)
            glTranslatef(0, 0, 6)
            glScalef(1, 1, 1.3)
            gluSphere(gluNewQuadric(), 12, 10, 10)
            glColor3f(base_hue[0] * 0.7, base_hue[1] * 0.7, base_hue[2] * 0.7)
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(10*side, 0, 3)
                glRotatef(50*side, 0, 0, 1)
                glScalef(0.6, 0.25, 1)
                gluSphere(gluNewQuadric(), 10, 6, 6)
                glPopMatrix()
            glColor3f(1.0, 0.25, 0.1)
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(5*side, 4, 3)
                gluSphere(gluNewQuadric(), 3, 6, 6)
                glPopMatrix()
            glColor3f(base_hue[0] * 0.7, base_hue[1] * 0.7, base_hue[2] * 0.7)
            glTranslatef(0, 7, 0)
            glRotatef(50, 1, 0, 0)
            gluCylinder(gluNewQuadric(), 3, 0, 8, 10, 2)
            glPopMatrix()
            
           
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(0, side * 18, 55)
                glColor3f(*base_hue)
                gluSphere(gluNewQuadric(), 7, 8, 8)
                glRotatef(25 if side == 1 else -25, 1, 0, 0)
                gluCylinder(gluNewQuadric(), 5, 4, 18, 8, 2)
                glTranslatef(0, 0, 18)
                gluSphere(gluNewQuadric(), 5, 8, 8)
                glRotatef(25 if side == 1 else -15, 1, 0, 0)
                gluCylinder(gluNewQuadric(), 4, 3, 18, 8, 2)
                glTranslatef(0, 0, 18)
                glColor3f(base_hue[0] * 0.9, base_hue[1] * 0.9, base_hue[2] * 0.9)
                gluSphere(gluNewQuadric(), 4, 8, 8)
                if side == 1:
                    # DIFFERENT WEAPON DESIGN
                    glColor3f(0.45, 0.45, 0.45)
                    glRotatef(-55, 1, 0, 0)
                    gluCylinder(gluNewQuadric(), 2, 1, 15, 6, 2)
                    glColor3f(0.35, 0.25, 0.15)
                    glTranslatef(0, 0, -8)
                    gluCylinder(gluNewQuadric(), 2.5, 2.5, 8, 8, 2)
                else:
                    # DIFFERENT TOOL DESIGN
                    glColor3f(0.7, 0.5, 0.3)
                    glTranslatef(0, -4, 0)
                    glRotatef(-95, 1, 0, 0)
                    gluSphere(gluNewQuadric(), 10, 8, 8)
                    glColor3f(0.45, 0.35, 0.2)
                    glTranslatef(0, 0, 10)
                    gluCylinder(gluNewQuadric(), 10, 8, 3, 10, 2)
                glPopMatrix()
            
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(0, side * 10, 35)
                glColor3f(*base_hue)
                gluSphere(gluNewQuadric(), 7, 8, 8)
                gluCylinder(gluNewQuadric(), 6, 5, 18, 8, 2)
                glTranslatef(0, 0, 18)
                gluSphere(gluNewQuadric(), 5, 8, 8)
                glRotatef(20, 1, 0, 0)
                gluCylinder(gluNewQuadric(), 5, 4, 14, 8, 2)
                glTranslatef(0, 0, 14)
                glColor3f(base_hue[0] * 0.8, base_hue[1] * 0.8, base_hue[2] * 0.8)
                glScalef(1, 1.6, 1)
                gluSphere(gluNewQuadric(), 5, 8, 8)
                glPopMatrix()
        finally:
            glPopMatrix()

def render_weapon_fpp():
   
    glPushMatrix()
    try:
        ax, ay, az = avatar_location
        ang = math.radians(avatar_orientation)
        
        
        glTranslatef(
            ax + math.cos(ang) * 26 - math.sin(ang) * 16,
            ay + math.sin(ang) * 26 + math.cos(ang) * 16,
            az + 55
        )
        
        glRotatef(avatar_orientation, 0, 0, 1)
        glRotatef(-8, 1, 0, 0)
        
        glColor3f(0.25, 0.25, 0.3)
        gluCylinder(gluNewQuadric(), 3.5, 3.5, 28, 10, 2)
        
        glColor3f(0.85, 0.55, 0.25)
        glTranslatef(0, 0, 28)
        gluCylinder(gluNewQuadric(), 2.2, 1.7, 18, 10, 2)
        
        glColor3f(0.1, 0.8, 1.0)
        glTranslatef(0, 5, -18)
        gluCylinder(gluNewQuadric(), 1.2, 1.2, 10, 6, 2)
    finally:
        glPopMatrix()

def render_pulse_wave(radius, progression):
    
    glColor3f(0.75, 0.5, 0.25)
    
    segments = 10
    width = 22
    
    glBegin(GL_QUADS)
    for i in range(segments):
        angle1 = i * (360.0 / segments)
        angle2 = (i + 1) * (360.0 / segments)
        
        rad1 = math.radians(angle1)
        rad2 = math.radians(angle2)
        
        x1_in = math.cos(rad1) * (radius - width)
        y1_in = math.sin(rad1) * (radius - width)
        x2_in = math.cos(rad2) * (radius - width)
        y2_in = math.sin(rad2) * (radius - width)
        
        x1_out = math.cos(rad1) * radius
        y1_out = math.sin(rad1) * radius
        x2_out = math.cos(rad2) * radius
        y2_out = math.sin(rad2) * radius

        glVertex3f(x1_in, y1_in, 0)
        glVertex3f(x1_out, y1_out, 0)
        glVertex3f(x2_out, y2_out, 0)
        glVertex3f(x2_in, y2_in, 0)
    glEnd()
    
   
    glColor3f(0.85, 0.6, 0.3)
    glBegin(GL_QUADS)
    particle_size = 35
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        
        px = math.cos(rad) * radius
        py = math.sin(rad) * radius
        
        glVertex3f(px - particle_size, py - particle_size, 0)
        glVertex3f(px + particle_size, py - particle_size, 0)
        glVertex3f(px + particle_size, py + particle_size, 0)
        glVertex3f(px - particle_size, py + particle_size, 0)
    glEnd()

def render_targeting():
   
    target_size = 12
    offset_x = -50
    offset_y = 5
    center_x = WIN_W / 2 + offset_x
    center_y = WIN_H / 2 + offset_y

    glColor3f(0.1, 0.8, 1.0)

    glPointSize(9.0)
    glBegin(GL_POINTS)
    glVertex3f(center_x, center_y, 0)
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        glVertex3f(center_x + math.cos(rad) * target_size, 
                   center_y + math.sin(rad) * target_size, 0)
    glEnd()

    box_size = 5
    glBegin(GL_QUADS)
    # Top-left
    glVertex3f(center_x - target_size - box_size, center_y + target_size - box_size, 0)
    glVertex3f(center_x - target_size + box_size, center_y + target_size - box_size, 0)
    glVertex3f(center_x - target_size + box_size, center_y + target_size + box_size, 0)
    glVertex3f(center_x - target_size - box_size, center_y + target_size + box_size, 0)
    # Top-right
    glVertex3f(center_x + target_size - box_size, center_y + target_size - box_size, 0)
    glVertex3f(center_x + target_size + box_size, center_y + target_size - box_size, 0)
    glVertex3f(center_x + target_size + box_size, center_y + target_size + box_size, 0)
    glVertex3f(center_x + target_size - box_size, center_y + target_size + box_size, 0)
    # Bottom-left
    glVertex3f(center_x - target_size - box_size, center_y - target_size - box_size, 0)
    glVertex3f(center_x - target_size + box_size, center_y - target_size - box_size, 0)
    glVertex3f(center_x - target_size + box_size, center_y - target_size + box_size, 0)
    glVertex3f(center_x - target_size - box_size, center_y - target_size + box_size, 0)
    # Bottom-right
    glVertex3f(center_x + target_size - box_size, center_y - target_size - box_size, 0)
    glVertex3f(center_x + target_size + box_size, center_y - target_size - box_size, 0)
    glVertex3f(center_x + target_size + box_size, center_y - target_size + box_size, 0)
    glVertex3f(center_x + target_size - box_size, center_y - target_size + box_size, 0)
    glEnd()

def render_shield_bubble(radius, divisions=50, layers=26):
    
    half_layers = max(1, layers // 2)
    shield_thickness = 5.0
    
    for i in range(half_layers):
        theta = (i / half_layers) * (math.pi / 2.0)
        inner_rad = radius - shield_thickness
        outer_rad = radius
        
        glBegin(GL_QUADS)
        for j in range(divisions):
            phi1 = (j / divisions) * (2.0 * math.pi)
            phi2 = ((j + 1) / divisions) * (2.0 * math.pi)
            
            x1 = inner_rad * math.sin(theta) * math.cos(phi1)
            y1 = inner_rad * math.sin(theta) * math.sin(phi1)
            z1 = inner_rad * math.cos(theta)
            
            x2 = inner_rad * math.sin(theta) * math.cos(phi2)
            y2 = inner_rad * math.sin(theta) * math.sin(phi2)
            z2 = inner_rad * math.cos(theta)
            
            x3 = outer_rad * math.sin(theta) * math.cos(phi2)
            y3 = outer_rad * math.sin(theta) * math.sin(phi2)
            z3 = outer_rad * math.cos(theta)
            
            x4 = outer_rad * math.sin(theta) * math.cos(phi1)
            y4 = outer_rad * math.sin(theta) * math.sin(phi1)
            z4 = outer_rad * math.cos(theta)
            
            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y2, z2)
            glVertex3f(x3, y3, z3)
            glVertex3f(x4, y4, z4)
        glEnd()

def render_environment():
    
    glBegin(GL_QUADS)
    
    glColor3f(0.18, 0.22, 0.25)
    glVertex3f(-FIELD_WIDTH, -FIELD_DEPTH, 0)
    glVertex3f(-FIELD_WIDTH, FIELD_DEPTH, 0)
    glColor3f(0.22, 0.26, 0.3)
    glVertex3f(FIELD_WIDTH, FIELD_DEPTH, 0)
    glVertex3f(FIELD_WIDTH, -FIELD_DEPTH, 0)
    glEnd()

    line_width = 0.6
    glColor3f(0.1, 0.95, 0.95)
    
    
    glBegin(GL_QUADS)
    for x in range(-FIELD_WIDTH, FIELD_WIDTH + 80, 80):
        glVertex3f(x - line_width, -FIELD_DEPTH, 0.15)
        glVertex3f(x + line_width, -FIELD_DEPTH, 0.15)
        glVertex3f(x + line_width, FIELD_DEPTH, 0.15)
        glVertex3f(x - line_width, FIELD_DEPTH, 0.15)

    for z in range(-FIELD_DEPTH, FIELD_DEPTH + 80, 80):
        glVertex3f(-FIELD_WIDTH, z - line_width, 0.15)
        glVertex3f(FIELD_WIDTH, z - line_width, 0.15)
        glVertex3f(FIELD_WIDTH, z + line_width, 0.15)
        glVertex3f(-FIELD_WIDTH, z + line_width, 0.15)
    glEnd()

    
    glBegin(GL_QUADS)
    wall_hue = (0.22, 0.28, 0.32)
    glColor3f(*wall_hue)
    
    glVertex3f(-FIELD_WIDTH, FIELD_DEPTH, 0)
    glVertex3f(FIELD_WIDTH, FIELD_DEPTH, 0)
    glColor3f(0.12, 0.18, 0.24)
    glVertex3f(FIELD_WIDTH, FIELD_DEPTH, OBSTACLE_HEIGHT)
    glVertex3f(-FIELD_WIDTH, FIELD_DEPTH, OBSTACLE_HEIGHT)
    
    glColor3f(*wall_hue)
    glVertex3f(-FIELD_WIDTH, -FIELD_DEPTH, 0)
    glVertex3f(FIELD_WIDTH, -FIELD_DEPTH, 0)
    glColor3f(0.12, 0.18, 0.24)
    glVertex3f(FIELD_WIDTH, -FIELD_DEPTH, OBSTACLE_HEIGHT)
    glVertex3f(-FIELD_WIDTH, -FIELD_DEPTH, OBSTACLE_HEIGHT)
    
    glColor3f(*wall_hue)
    glVertex3f(FIELD_WIDTH, -FIELD_DEPTH, 0)
    glVertex3f(FIELD_WIDTH, FIELD_DEPTH, 0)
    glColor3f(0.12, 0.18, 0.24)
    glVertex3f(FIELD_WIDTH, FIELD_DEPTH, OBSTACLE_HEIGHT)
    glVertex3f(FIELD_WIDTH, -FIELD_DEPTH, OBSTACLE_HEIGHT)
    
    glColor3f(*wall_hue)
    glVertex3f(-FIELD_WIDTH, -FIELD_DEPTH, 0)
    glVertex3f(-FIELD_WIDTH, FIELD_DEPTH, 0)
    glColor3f(0.12, 0.18, 0.24)
    glVertex3f(-FIELD_WIDTH, FIELD_DEPTH, OBSTACLE_HEIGHT)
    glVertex3f(-FIELD_WIDTH, -FIELD_DEPTH, OBSTACLE_HEIGHT)
    glEnd()

def setup_view():
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(VIEW_ANGLE, SCREEN_RATIO, 0.15, 1600.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if perspective_mode:
        ax, ay, az = avatar_location
        eye_height = 78
        ang_rad = math.radians(avatar_orientation)
        cam_x = ax - math.sin(ang_rad) * 12 + math.cos(ang_rad) * 14
        cam_y = ay + math.cos(ang_rad) * 12 + math.sin(ang_rad) * 14
        cam_z = az + eye_height - 10
        look_x = ax + math.cos(ang_rad) * 110
        look_y = ay + math.sin(ang_rad) * 110
        look_z = az + eye_height - 10
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        vx, vy, vz = view_point
        gluLookAt(vx, vy, vz, 0.0, 0.0, 0.0, 0, 0, 1)

def process_input(key, x, y):
    
    global avatar_location, avatar_orientation, active_weapon
    global rushing, last_rush_time, simulation_paused, perspective_mode
    global refilling, refill_start, current_clip, ammo_stock
    global guard_up, last_guard_time, last_pulse_time
    global override_active, divine_active, limitless_ammo, perception_mode
    global simulation_ended, immortality_active, avatar_vitality, drive_mode, last_drive_time
    
    
    if simulation_ended and key == b'y':
        reset_simulation()
        return

    
    if key == b'c':
        override_active = not override_active
        if not override_active:
            divine_active = False
            limitless_ammo = False
            perception_mode = False
        return
    
    
    if override_active:
        
        if key == b'g':
            divine_active = not divine_active
            return
        
        elif key == b'i':
            limitless_ammo = not limitless_ammo
            if limitless_ammo:
                refilling = False
                current_clip = CLIP_SIZE
            return
        
        elif key == b'm':
            perception_mode = not perception_mode
            return
        
        elif key == b'h':
            immortality_active = not immortality_active
            if immortality_active:
                avatar_vitality = 120
            return

   
    if key == b'v':
        perspective_mode = not perspective_mode
        return
    
   
    if key == b' ':
        simulation_paused = not simulation_paused
        return
    
   
    if key == b'r' and not refilling and current_clip < CLIP_SIZE and ammo_stock > 0:
        refilling = True
        refill_start = int(time.time() * 1000)
        return

  
    if key == b'q':
        current_time = int(time.time() * 1000)
        if divine_active or current_time - last_guard_time >= GUARD_DELAY:
            guard_up = True
            last_guard_time = current_time
    
  
    if key == b'x':
        current_time = int(time.time() * 1000)
        if divine_active or current_time - last_pulse_time >= PULSE_DELAY:
            activate_pulse()
            last_pulse_time = current_time

    if not simulation_paused:
        nx = avatar_location[0]
        ny = avatar_location[1]
        move_speed = DRIVE_VELOCITY if drive_mode else (12 * (PERCEPTION_AVATAR_SPEED if perception_mode else 1))
        
       
        if key == b'e':
            current_time = int(time.time() * 1000)
            if divine_active or current_time - last_rush_time >= RUSH_COOLDOWN:
                ang = math.radians(avatar_orientation)
                nx = avatar_location[0] + math.cos(ang) * RUSH_VELOCITY
                ny = avatar_location[1] + math.sin(ang) * RUSH_VELOCITY
                rushing = True
                last_rush_time = current_time
        
       
        elif key == b'w':
            ang = math.radians(avatar_orientation)
            nx = avatar_location[0] + math.cos(ang) * move_speed
            ny = avatar_location[1] + math.sin(ang) * move_speed
        elif key == b's':
            nx -= math.cos(math.radians(avatar_orientation)) * 12
            ny -= math.sin(math.radians(avatar_orientation)) * 12
        elif key == b'a':
            avatar_orientation = (avatar_orientation + 6) % 360
        elif key == b'd':
            avatar_orientation = (avatar_orientation - 6) % 360
        
       
        elif key == b'z':
            current_time = int(time.time() * 1000)
            if drive_mode:
                drive_mode = False
            elif divine_active or current_time - last_drive_time >= DRIVE_COOLDOWN:
                drive_mode = True
                last_drive_time = current_time

        
        if abs(nx) < FIELD_WIDTH - 60 and abs(ny) < FIELD_DEPTH - 60:
            avatar_location[0] = nx
            avatar_location[1] = ny

      
        if key == b'1':
            active_weapon = WEAPON_MODES['BASIC']
        elif key == b'2':
            active_weapon = WEAPON_MODES['ICE']
        elif key == b'3':
            active_weapon = WEAPON_MODES['FIRE']
        elif key == b'4':
            active_weapon = WEAPON_MODES['BACKWARDS']
        elif key == b'5':
            active_weapon = WEAPON_MODES['SLUGGISH']
        elif key == b'6':
            active_weapon = WEAPON_MODES['CHAOS']

def process_special_keys(key, x, y):
    
    global view_point
    vx, vy, vz = view_point
    if key == GLUT_KEY_UP:
        vz += 7.0
    elif key == GLUT_KEY_DOWN:
        vz -= 7.0
    elif key == GLUT_KEY_LEFT:
        vy += 7.0
    elif key == GLUT_KEY_RIGHT:
        vy -= 7.0
    view_point = [vx, vy, vz]

def render_shots():
    
    for shot in shots_fired:
        glPushMatrix()
        try:
            glTranslatef(shot[0], shot[1], shot[2])
            hue = SHOT_PALETTE[shot[5]]
            if fury_active:
                glColor3f(1.0, 0.6, 0.2)
            else:
                glColor3f(*hue)
            gluSphere(gluNewQuadric(), SHOT_RADIUS/2.2, 10, 10)
        finally:
            glPopMatrix()

def update_shots():
    
    if not simulation_paused:
        global shots_fired
        new_shots = []
        for shot in shots_fired:
            angle = math.radians(shot[3])
            
            shot[0] += math.cos(angle) * SHOT_SPEED * 0.95
            shot[1] += math.sin(angle) * SHOT_SPEED * 0.95
            shot[4] += 1
            if (abs(shot[0]) < FIELD_WIDTH and
                abs(shot[1]) < FIELD_DEPTH and
                shot[4] < 65):
                new_shots.append(shot)
        shots_fired = new_shots

def process_mouse(button, state, x, y):
    
    global shots_fired, current_clip, refilling, refill_start, ammo_stock
    
    if not simulation_paused and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if limitless_ammo or current_clip > 0:
            if not refilling or limitless_ammo:
                angle = math.radians(avatar_orientation)
                barrel_x = avatar_location[0] + math.cos(angle) * 24.0
                barrel_y = avatar_location[1] + math.sin(angle) * 24.0
                barrel_z = avatar_location[2] + 56.0
                shots_fired.append([
                    barrel_x,
                    barrel_y,
                    barrel_z,
                    avatar_orientation,
                    0,
                    active_weapon
                ])
                if not (override_active and limitless_ammo):
                    current_clip -= 1
                    if current_clip == 0 and ammo_stock > 0:
                        refilling = True
                        refill_start = int(time.time() * 1000)

def spawn_shifter():
    
    global next_hostile_id
    current_time = int(time.time() * 1000)
    side = random.choice(['top', 'right', 'bottom', 'left'])
    margin = SPAWN_OFFSET
    
    
    if side == 'top':
        x = random.uniform(-FIELD_WIDTH + margin, FIELD_WIDTH - margin)
        y = FIELD_DEPTH - margin
    elif side == 'right':
        x = FIELD_WIDTH - margin
        y = random.uniform(-FIELD_DEPTH + margin, FIELD_DEPTH - margin)
    elif side == 'bottom':
        x = random.uniform(-FIELD_WIDTH + margin, FIELD_WIDTH - margin)
        y = -FIELD_DEPTH + margin
    else:
        x = -FIELD_WIDTH + margin
        y = random.uniform(-FIELD_DEPTH + margin, FIELD_DEPTH - margin)
    
    hid = next_hostile_id
    next_hostile_id += 1
    base = [
        x, y, FLOAT_HEIGHT,
        120,
        0,
        0,
        [],
        0,
        current_time,
        0,
        0,
        hid
    ]
    base.append(10) 
    base.append(SHIFTER_HITS)
    return base

def spawn_threat():
    
    global next_hostile_id
    current_time = int(time.time() * 1000)
   
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(SPAWN_OFFSET, min(FIELD_WIDTH, FIELD_DEPTH) * 0.8)
    
    x = math.cos(angle) * distance
    y = math.sin(angle) * distance
    
    hid = next_hostile_id
    next_hostile_id += 1
    return [x, y, FLOAT_HEIGHT, 120, 0, 0, [], 0, current_time, 0, 0, hid]

def spawn_boost_item(x, y, z, hostile_id=None):
    
    global _boost_tracker
    if hostile_id is not None:
        if hostile_id in _boost_tracker:
            return
        _boost_tracker.add(hostile_id)
    btype = random.choice(BOOST_TYPES)
    boost_items.append([x, y, z, btype, int(time.time() * 1000)])

def generate_random_boost():
    
    global boost_items
    
    if len(boost_items) >= MAX_VISIBLE_BOOSTS:
        return

    margin = 90
    
    for _ in range(25):
       
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(margin, min(FIELD_WIDTH, FIELD_DEPTH) - margin)
        
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        z = FLOAT_HEIGHT
        
        
        if ((x - avatar_location[0])**2 + (y - avatar_location[1])**2) ** 0.5 < AVATAR_SCALE * 3.5:
            continue
            
        too_near = False
        for b in boost_items:
            if ((x - b[0])**2 + (y - b[1])**2) ** 0.5 < BOOST_SCALE * 2.5:
                too_near = True
                break
        
        if not too_near:
            btype = random.choice(BOOST_TYPES)
            boost_items.append([x, y, z, btype, int(time.time() * 1000)])
            break

def render_boost_items():
   
    for boost in boost_items:
        glPushMatrix()
        try:
            glTranslatef(boost[0], boost[1], boost[2])
            
            current_time = int(time.time() * 1000)
            glRotatef((current_time % 4000) * 0.09, 1, 1, 0)
            
            pulse = (math.sin(current_time * 0.0025) + 1) * 0.25 + 0.5
            glColor3f(
                BOOST_HUES[boost[3]][0] * pulse,
                BOOST_HUES[boost[3]][1] * pulse,
                BOOST_HUES[boost[3]][2] * pulse
            )
            
            glutSolidCube(BOOST_SCALE)
        finally:
            glPopMatrix()

def update_boost_items():
   
    global avatar_vitality, current_clip, ammo_stock, fury_active
    global fury_end, stasis_active, stasis_end, next_boost_time
    global THREAT_VELOCITY, boost_generation
    
    current_time = int(time.time() * 1000)

    if current_time >= next_boost_time:
        generate_random_boost()
        next_boost_time = current_time + BOOST_FREQUENCY

    active_boosts = []
    for boost in boost_items:
        dx = avatar_location[0] - boost[0]
        dy = avatar_location[1] - boost[1]
        dz = avatar_location[2] - boost[2]
        distance = (dx*dx + dy*dy + dz*dz) ** 0.5
        
        if distance < AVATAR_SCALE + BOOST_SCALE/2:
            if boost[3] == 'VITALITY':
                avatar_vitality = min(120, avatar_vitality + 25)
            elif boost[3] == 'MUNITIONS':
                ammo_gain = min(12, STOCK_SIZE - ammo_stock)
                ammo_stock += ammo_gain
            elif boost[3] == 'FURY':
                fury_active = True
                fury_end = current_time + BOOST_LIFETIME
            elif boost[3] == 'STASIS':
                stasis_active = True
                stasis_end = current_time + BOOST_LIFETIME
                THREAT_VELOCITY = 0.04
        else:
            active_boosts.append(boost)
    
    boost_items[:] = active_boosts
    
    if fury_active and current_time > fury_end:
        fury_active = False
    if stasis_active and current_time > stasis_end:
        stasis_active = False
        THREAT_VELOCITY = 0.18

def remove_hostile(hostile, replace=True):
   
    global shifters_eliminated, shifter_target, boost_generation
    if hostile in hostiles:
        boost_generation = False
        is_shifter = (len(hostile) > 12 and hostile[12] == 10)
        is_colossus = (len(hostile) > 12 and hostile[12] == 20)
        is_infant = (len(hostile) > 12 and hostile[12] == 30)
        
        if is_colossus and not is_infant:
            old_x, old_y = hostile[0], hostile[1]
            hostiles.remove(hostile)
            
            for _ in range(3):
                infant = spawn_colossus(is_infant=True)
                infant[0] = old_x + random.uniform(-25, 25)
                infant[1] = old_y + random.uniform(-25, 25)
                hostiles.append(infant)
            return True
        
        hostiles.remove(hostile)
        if replace and not (is_colossus or is_infant):
            if len(hostiles) < MAX_VISIBLE_THREATS:
                hostiles.append(spawn_threat())
        if is_shifter:
            shifters_eliminated += 1
            shifter_target = min(shifter_target + SHIFTER_GROWTH, MAX_VISIBLE_THREATS)
        return True
    return False

def track_hostile_movement(hostile, current_time):
  
    if hostile[7] > current_time:
        return
    if current_time - hostile[8] >= TRACK_INTERVAL:
        if len(hostile[6]) >= POSITION_MEMORY:
            hostile[6].pop(0)
        hostile[6].append((hostile[0], hostile[1]))
        hostile[8] = current_time

def update_hostiles():
    
    global avatar_vitality, hostiles, shots_fired, game_points, streak_count, streak_clock
    global guard_up, simulation_paused, simulation_ended, last_time_score, mission_accomplished
    
    if simulation_paused:
        return

    current_time = int(time.time() * 1000)
    active_hostiles = []

    if game_points >= SUCCESS_TARGET and not mission_accomplished:
        mission_accomplished = True
        simulation_paused = True
        simulation_ended = True

    if avatar_vitality <= 0 and not simulation_ended:
        simulation_ended = True
        simulation_paused = True

    if current_time - last_time_score >= 900:
        game_points += TIME_SCORE
        last_time_score = current_time

    for hostile in hostiles:
        track_hostile_movement(hostile, current_time)

    if streak_count > 0 and current_time - streak_clock > STREAK_TIME:
        streak_count = 0

    if guard_up and current_time - last_guard_time >= GUARD_TIME:
        guard_up = False

    for hostile in hostiles[:]:
        if hostile[5] > 0 and current_time >= hostile[5]:
            exp_x, exp_y, exp_z = hostile[0], hostile[1], hostile[2]
            removed = 0
            if remove_hostile(hostile, replace=False):
                removed += 1
            for other in hostiles[:]:
                dx = other[0] - exp_x
                dy = other[1] - exp_y
                dist = (dx*dx + dy*dy) ** 0.5
                if dist < BLAST_RANGE:
                    if remove_hostile(other, replace=False):
                        removed += 1
            for _ in range(removed):
                hostiles.append(spawn_threat())
            streak_count += removed
            streak_clock = current_time
            game_points += int(KILL_VALUE * removed * (STREAK_BONUS if streak_count > 1 else 1))
            continue

        if hostile[10] > 0 and current_time >= hostile[10]:
            if remove_hostile(hostile, replace=True):
                streak_count += 1
                streak_clock = current_time
                game_points += int(KILL_VALUE * (STREAK_BONUS if streak_count > 1 else 1))
            continue

    for hostile in hostiles[:]:
        keep_hostile = True
        iced = hostile[4] > current_time
        blazing = hostile[5] > current_time
        rewinding = hostile[7] > current_time
        sluggish = hostile[9] > current_time
        chaotic = hostile[10] > current_time
        is_shifter = (len(hostile) > 12 and hostile[12] == 10)
        is_colossus = (len(hostile) > 12 and hostile[12] == 20)
        is_infant = (len(hostile) > 12 and hostile[12] == 30)

        speed_factor = 0.45 if sluggish else 1.0
        base_pace = COLOSSUS_PACE if is_colossus else THREAT_VELOCITY
        if perception_mode:
            speed_factor *= PERCEPTION_THREAT_SLOW

        if not iced:
            if rewinding and len(hostile[6]) > 0:
                time_left = hostile[7] - current_time
                progress = time_left / REWIND_EFFECT
                history_idx = int(len(hostile[6]) * (1 - progress))
                if 0 <= history_idx < len(hostile[6]):
                    hostile[0], hostile[1] = hostile[6][history_idx]
            elif blazing:
                nearest_dist = float('inf')
                target_x, target_y = hostile[0], hostile[1]
                for other in hostiles:
                    if other is hostile:
                        continue
                    dx = other[0] - hostile[0]
                    dy = other[1] - hostile[1]
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist < nearest_dist:
                        nearest_dist = dist
                        target_x, target_y = other[0], other[1]
                if nearest_dist != float('inf'):
                    dx = target_x - hostile[0]
                    dy = target_y - hostile[1]
                    distance = (dx*dx + dy*dy) ** 0.5
                    if distance > 0:
                        hostile[0] += (dx / distance) * base_pace * 2.2 * speed_factor
                        hostile[1] += (dy / distance) * base_pace * 2.2 * speed_factor
            elif chaotic:
                current_time = int(time.time() * 1000)
                nearest_dist = float('inf')
                target = None
                
                if current_time - hostile[11] >= CHAOS_KILL_DELAY:
                    for other in hostiles:
                        if other is hostile or other not in hostiles:
                            continue
                        if len(other) > 12 and other[12] == 10:
                            continue
                        dx = other[0] - hostile[0]
                        dy = other[1] - hostile[1]
                        dist = (dx*dx + dy*dy) ** 0.5
                        if dist < nearest_dist:
                            nearest_dist = dist
                            target = other

                if target is not None and target in hostiles:
                    dx = target[0] - hostile[0]
                    dy = target[1] - hostile[1]
                    distance = (dx*dx + dy*dy) ** 0.5
                    if distance > 0:
                        hostile[0] += (dx/distance) * base_pace * 2.2 * speed_factor
                        hostile[1] += (dy/distance) * base_pace * 2.2 * speed_factor
                    
                    if distance <= COMBAT_RANGE and current_time - hostile[11] >= CHAOS_KILL_DELAY:
                        if remove_hostile(target, replace=True):
                            streak_count += 1
                            streak_clock = current_time
                            game_points += int(KILL_VALUE * (STREAK_BONUS if streak_count > 1 else 1))
                            hostile[11] = current_time
            else:
                dx = avatar_location[0] - hostile[0]
                dy = avatar_location[1] - hostile[1]
                distance = (dx*dx + dy*dy) ** 0.5

                if guard_up:
                    safe_dist = GUARD_SPAN + ((COLOSSUS_SIZE if is_colossus else THREAT_SCALE) * 0.7)
                    if distance < safe_dist and distance > 0:
                        ang = math.atan2(hostile[1] - avatar_location[1], hostile[0] - avatar_location[0])
                        target_x = avatar_location[0] + math.cos(ang) * safe_dist
                        target_y = avatar_location[1] + math.sin(ang) * safe_dist
                        
                        push = 0.65
                        hostile[0] += (target_x - hostile[0]) * push
                        hostile[1] += (target_y - hostile[1]) * push
                        
                        hostile[0] = max(min(hostile[0], FIELD_WIDTH - 60), -FIELD_WIDTH + 60)
                        hostile[1] = max(min(hostile[1], FIELD_DEPTH - 60), -FIELD_DEPTH + 60)
                        
                        continue

                if distance <= COMBAT_RANGE:
                    if drive_mode:
                        if remove_hostile(hostile, replace=True):
                            streak_count += 1
                            streak_clock = current_time
                            game_points += int(KILL_VALUE * (STREAK_BONUS if streak_count > 1 else 1))
                        continue
                    elif not (override_active and immortality_active):
                        if is_colossus:
                            avatar_vitality = 0
                        elif is_shifter:
                            avatar_vitality = max(0, avatar_vitality - SHIFTER_DAMAGE)
                        else:
                            avatar_vitality = max(0, avatar_vitality - 2)
                        if is_colossus:
                            continue
                        if remove_hostile(hostile, replace=True):
                            pass
                        continue

                if distance > 0:
                    hostile[0] += (dx / distance) * base_pace * speed_factor
                    hostile[1] += (dy / distance) * base_pace * speed_factor
        
        for shot in shots_fired[:]:
            if detect_collision(hostile, shot):
                if is_shifter:
                    if len(hostile) > 13:
                        hostile[13] -= 1
                    else:
                        hostile.append(SHIFTER_HITS - 1)
                    if shot in shots_fired:
                        shots_fired.remove(shot)
                    if hostile[13] > 0:
                        keep_hostile = True
                        break
                
                if shot[5] == WEAPON_MODES['SLUGGISH']:
                    hostile[9] = current_time + SLUG_EFFECT
                elif shot[5] == WEAPON_MODES['BACKWARDS']:
                    if len(hostile[6]) > 0:
                        hostile[7] = current_time + REWIND_EFFECT
                elif shot[5] == WEAPON_MODES['ICE']:
                    hostile[4] = current_time + ICE_EFFECT
                elif shot[5] == WEAPON_MODES['FIRE']:
                    if hostile[5] == 0:
                        hostile[5] = current_time + FIRE_EFFECT
                    if shot in shots_fired:
                        shots_fired.remove(shot)
                    break
                elif shot[5] == WEAPON_MODES['CHAOS']:
                    if hostile[10] == 0:
                        hostile[10] = current_time + CHAOS_EFFECT
                    if shot in shots_fired:
                        shots_fired.remove(shot)
                    break
                elif shot[5] == WEAPON_MODES['BASIC']:
                    global next_hostile_id
                    
                    if is_colossus and not is_infant:
                        if len(hostile) <= 13:
                            hostile[13] = COLOSSUS_STAMINA
                        hostile[13] -= 1
                        
                        if shot in shots_fired:
                            shots_fired.remove(shot)
                            
                        game_points += 6
                        streak_count += 1
                        streak_clock = current_time
                        
                        if hostile[13] <= 0:
                            hx, hy = hostile[0], hostile[1]
                            hostiles.remove(hostile)
                            
                            for _ in range(3):
                                infant = [
                                    hx + random.uniform(-25, 25),
                                    hy + random.uniform(-25, 25),
                                    FLOAT_HEIGHT,
                                    120,
                                    0,
                                    0,
                                    [],
                                    0,
                                    current_time,
                                    0,
                                    0,
                                    next_hostile_id,
                                    30,
                                    BABY_LIFE
                                ]
                                next_hostile_id += 1
                                hostiles.append(infant)
                            
                            keep_hostile = False
                            break
                        keep_hostile = True
                    elif is_infant:
                        hostile[13] -= 1
                        if shot in shots_fired:
                            shots_fired.remove(shot)
                        if hostile[13] <= 0:
                            hostiles.remove(hostile)
                            game_points += 12
                            keep_hostile = False
                        else:
                            keep_hostile = True
                    else:
                        streak_count += 1
                        streak_clock = current_time
                        game_points += int(KILL_VALUE * (STREAK_BONUS if streak_count > 1 else 1))
                        remove_hostile(hostile, replace=True)
                        if shot in shots_fired:
                            shots_fired.remove(shot)
                        keep_hostile = False
                        break

                if shot in shots_fired:
                    shots_fired.remove(shot)
                break

        if keep_hostile and hostile in hostiles:
            hostile[0] = max(min(hostile[0], FIELD_WIDTH - 60), -FIELD_WIDTH + 60)
            hostile[1] = max(min(hostile[1], FIELD_DEPTH - 60), -FIELD_DEPTH + 60)
            active_hostiles.append(hostile)

    hostiles[:] = active_hostiles

def detect_collision(hostile, shot):
  
    dx = shot[0] - hostile[0]
    dy = shot[1] - hostile[1]
    distance = (dx*dx + dy*dy) ** 0.5
    is_colossus = (len(hostile) > 12 and hostile[12] == 20)
    radius = COLOSSUS_SIZE if is_colossus else THREAT_SCALE
    return distance <= radius * 0.9

def spawn_colossus(is_infant=False):
   
    global next_hostile_id
    current_time = int(time.time() * 1000)
    
    # DIFFERENT SPAWN ALGORITHM
    angle = random.uniform(0, 2 * math.pi)
    max_distance = min(FIELD_WIDTH, FIELD_DEPTH) - SPAWN_OFFSET
    distance = random.uniform(max_distance * 0.7, max_distance)
    
    x = math.cos(angle) * distance
    y = math.sin(angle) * distance

    hid = next_hostile_id
    next_hostile_id += 1

    base = [x, y, FLOAT_HEIGHT, 120, 0, 0, [], 0, current_time, 0, 0, hid]
    base.append(30 if is_infant else 20)
    base.append(BABY_LIFE if is_infant else COLOSSUS_STAMINA)
    return base

def manage_threats():
   
    global shifter_active, shifter_target
    if not simulation_paused:
        
        total = len(hostiles)
        normal_threats = sum(1 for h in hostiles if not (len(h) > 12 and (h[12] == 10 or h[12] == 20 or h[12] == 30)))
        shifter_count = sum(1 for h in hostiles if len(h) > 12 and h[12] == 10)
        colossus_count = sum(1 for h in hostiles if len(h) > 12 and h[12] == 20)
        infant_count = sum(1 for h in hostiles if len(h) > 12 and h[12] == 30)

        if game_points >= PHASE2_START:
            shifter_active = True

        if game_points >= PHASE3_START:
            available = MAX_VISIBLE_THREATS - infant_count
            
            while colossus_count < MAX_COLOSSUS and total < available:
                hostiles.append(spawn_colossus())
                colossus_count += 1
                total += 1

        available = MAX_VISIBLE_THREATS - (colossus_count + infant_count)
        while normal_threats < MAX_THREATS and total < available:
            hostiles.append(spawn_threat())
            normal_threats += 1
            total += 1

        if shifter_active:
            available = MAX_VISIBLE_THREATS - (total + infant_count)
            needed = max(0, shifter_target - shifter_count)
            to_create = min(needed, available)
            for _ in range(to_create):
                hostiles.append(spawn_shifter())
                total += 1

def activate_pulse():
    
    current_time = int(time.time() * 1000)
    for hostile in hostiles:
        dx = hostile[0] - avatar_location[0]
        dy = hostile[1] - avatar_location[1]
        distance = (dx*dx + dy*dy) ** 0.5
        if distance <= PULSE_RANGE:
            if distance > 0:
                push_x = (dx/distance) * PULSE_STRENGTH
                push_y = (dy/distance) * PULSE_STRENGTH
                new_x = hostile[0] + push_x
                new_y = hostile[1] + push_y
                hostile[0] = max(min(new_x, FIELD_WIDTH - 60), -FIELD_WIDTH + 60)
                hostile[1] = max(min(new_y, FIELD_DEPTH - 60), -FIELD_DEPTH + 60)
                hostile[4] = current_time + PULSE_PARALYSIS

def render_display():
    
    divine_fire()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_view()
    glEnable(GL_DEPTH_TEST)

    render_environment()
    render_avatar()
    render_shots()
    render_boost_items()

    if not simulation_paused:
        manage_threats()
        update_hostiles()
        update_shots()
        update_boost_items()

    render_hostiles()

    if guard_up:
        current_time = int(time.time() * 1000)
        glPushMatrix()
        try:
            glTranslatef(avatar_location[0], avatar_location[1], avatar_location[2] + 50)
            bubble_radius = max(GUARD_SPAN * 1.6, AVATAR_SCALE * 2.4)
            
            glColor3f(0.1, 0.8, 0.8)
            glRotatef((current_time % 3800) * 0.04, 0, 0, 1)
            render_shield_bubble(bubble_radius, divisions=36, layers=20)
            
            glColor3f(0.1, 0.6, 0.7)
            glRotatef(35, 0, 0, 1)
            render_shield_bubble(bubble_radius * 1.03, divisions=28, layers=16)
        finally:
            glPopMatrix()
    
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    
    weapon_labels = ['Standard', 'Ice', 'Fire', 'Rewind', 'Slow', 'Chaos']
    hue = SHOT_PALETTE[active_weapon]
    glColor3f(*hue)
    glRasterPos2f(15, WIN_H - 35)
    text = f"Weapon: {weapon_labels[active_weapon]}"
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    global refilling, current_clip, ammo_stock, refill_start
    if refilling:
        current_time = int(time.time() * 1000)
        refill_progress = (current_time - refill_start) / REFILL_DURATION
        if refill_progress >= 1.0:
            refilling = False
            if ammo_stock > 0:
                needed = CLIP_SIZE - current_clip
                reload_amount = min(needed, ammo_stock)
                current_clip += reload_amount
                ammo_stock -= reload_amount

    glColor3f(0.1, 0.8, 0.8)
    glRasterPos2f(15, WIN_H - 65)
    text = f"Ammo: {current_clip}/{CLIP_SIZE} | Stock: {ammo_stock}"
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    if refilling:
        glColor3f(0.25, 0.25, 0.25)
        glBegin(GL_QUADS)
        glVertex3f(15, WIN_H - 95, 0)
        glVertex3f(215, WIN_H - 95, 0)
        glVertex3f(215, WIN_H - 75, 0)
        glVertex3f(15, WIN_H - 75, 0)
        glEnd()
        glColor3f(0.85, 0.55, 0.25)
        glBegin(GL_QUADS)
        glVertex3f(15, WIN_H - 95, 0)
        glVertex3f(15 + 200 * min(refill_progress, 1.0), WIN_H - 95, 0)
        glVertex3f(15 + 200 * min(refill_progress, 1.0), WIN_H - 75, 0)
        glVertex3f(15, WIN_H - 75, 0)
        glEnd()
        glColor3f(0.1, 0.8, 0.8)
        glRasterPos2f(225, WIN_H - 90)
        text = "RELOADING..." if ammo_stock > 0 else "OUT OF AMMO!"
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    
    glColor3f(0.25, 0.25, 0.25)
    glBegin(GL_QUADS)
    glVertex3f(15, WIN_H - 155, 0)
    glVertex3f(215, WIN_H - 155, 0)
    glVertex3f(215, WIN_H - 135, 0)
    glVertex3f(15, WIN_H - 135, 0)
    glEnd()
    health_percent = avatar_vitality / 120.0
    if health_percent > 0.6:
        glColor3f(0.1, 0.8, 0.1)
    elif health_percent > 0.3:
        glColor3f(0.8, 0.8, 0.1)
    else:
        glColor3f(0.8, 0.1, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(15, WIN_H - 155, 0)
    glVertex3f(15 + 200 * health_percent, WIN_H - 155, 0)
    glVertex3f(15 + 200 * health_percent, WIN_H - 135, 0)
    glVertex3f(15, WIN_H - 135, 0)
    glEnd()
    glColor3f(0.1, 0.8, 0.8)
    glRasterPos2f(225, WIN_H - 150)
    text = f"Health: {avatar_vitality}/120"
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    if rushing:
        glColor3f(0.1, 0.8, 1.0)
        glPushMatrix()
        try:
            glTranslatef(avatar_location[0], avatar_location[1], avatar_location[2])
            glRotatef(avatar_orientation, 0, 0, 1)
            
            line_width = 2.5
            glBegin(GL_QUADS)
            for i in range(-3, 4):
                x1 = -25 + i*6
                y1 = -35
                x2 = -45 + i*6
                y2 = -55
                
                dx = x2 - x1
                dy = y2 - y1
                length = (dx*dx + dy*dy) ** 0.5
                nx = -dy/length * line_width
                ny = dx/length * line_width
                
                glVertex3f(x1 + nx, y1 + ny, 0)
                glVertex3f(x1 - nx, y1 - ny, 0)
                glVertex3f(x2 - nx, y2 - ny, 0)
                glVertex3f(x2 + nx, y2 + ny, 0)
            glEnd()
        finally:
            glPopMatrix()

    current_time = int(time.time() * 1000)
    time_since_rush = current_time - last_rush_time

    if divine_active:
        glColor3f(0.1, 0.8, 0.1)
        glRasterPos2f(15, WIN_H - 125)
        text = "Rush Ready! (E)"
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    else:
        if time_since_rush < RUSH_COOLDOWN:
            glColor3f(0.85, 0.55, 0.25)
            glRasterPos2f(15, WIN_H - 125)
            cooldown_left = (RUSH_COOLDOWN - time_since_rush) / 1000
            text = f"Rush Cooldown: {cooldown_left:.1f}s"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        else:
            glColor3f(0.1, 0.8, 0.1)
            glRasterPos2f(15, WIN_H - 125)
            text = "Ready to Rush! (E)"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    
    glColor3f(0.85, 0.55, 0.25)
    glRasterPos2f(WIN_W - 320, WIN_H - 35)
    phase_text = "PHASE 1: SCATTERERS ACTIVE"
    if game_points >= PHASE3_START:
        phase_text = "PHASE 3: COLOSSUS APPEARS"
    elif game_points >= PHASE2_START:
        phase_text = "PHASE 2: SHIFTERS ENGAGED"
    for ch in phase_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    glColor3f(0.1, 0.8, 0.8)
    glRasterPos2f(WIN_W - 220, WIN_H - 65)
    score_text = f"Points: {game_points}"
    for ch in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    if streak_count > 1:
        glColor3f(0.85, 0.55, 0.25)
        glRasterPos2f(WIN_W - 220, WIN_H - 95)
        streak_text = f"Streak: x{streak_count}"
        for ch in streak_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        streak_left = 1.0 - (current_time - streak_clock) / STREAK_TIME
        if streak_left > 0:
            glBegin(GL_QUADS)
            glVertex3f(WIN_W - 220, WIN_H - 105, 0)
            glVertex3f(WIN_W - 220 + (110 * streak_left), WIN_H - 105, 0)
            glVertex3f(WIN_W - 220 + (110 * streak_left), WIN_H - 100, 0)
            glVertex3f(WIN_W - 220, WIN_H - 100, 0)
            glEnd()

    if simulation_ended:
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(WIN_W, 0, 0)
        glVertex3f(WIN_W, WIN_H, 0)
        glVertex3f(0, WIN_H, 0)
        glEnd()

        if mission_accomplished:
            glColor3f(0.1, 0.8, 0.1)
            title = "MISSION COMPLETE!"
            tx = WIN_W / 2 - (len(title) * 13)
            ty = WIN_H / 2 + 45
            glRasterPos2f(tx, ty)
            for ch in title:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        else:
            glColor3f(0.8, 0.1, 0.1)
            title = "SIMULATION TERMINATED"
            tx = WIN_W / 2 - (len(title) * 13)
            ty = WIN_H / 2 + 45
            glRasterPos2f(tx, ty)
            for ch in title:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        glColor3f(0.1, 0.8, 0.8)
        score_text = f"Final Score: {game_points}"
        sx = WIN_W / 2 - (len(score_text) * 9)
        sy = WIN_H / 2
        glRasterPos2f(sx, sy)
        for ch in score_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        hint = "Press Y to Restart"
        hx = WIN_W / 2 - (len(hint) * 8)
        hy = WIN_H / 2 - 45
        glRasterPos2f(hx, hy)
        for ch in hint:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        glEnable(GL_DEPTH_TEST)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glutSwapBuffers()
        return

    if simulation_paused:
        glDisable(GL_DEPTH_TEST)
        glColor3f(0, 0, 0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(WIN_W, 0, 0)
        glVertex3f(WIN_W, WIN_H, 0)
        glVertex3f(0, WIN_H, 0)
        glEnd()
        glColor3f(0.1, 0.8, 0.8)
        text = "SIMULATION PAUSED"
        text_width = len(text) * 16
        x = (WIN_W - text_width) / 2
        y = WIN_H / 2 + 25
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        text = "Press R to Resume"
        text_width = len(text) * 11
        x = (WIN_W - text_width) / 2
        y = WIN_H / 2 - 25
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        glEnable(GL_DEPTH_TEST)

    current_time = int(time.time() * 1000)
    time_since_guard = current_time - last_guard_time

    if divine_active:
        glColor3f(0.1, 0.8, 0.8)
        glRasterPos2f(15, WIN_H - 185)
        text = "Shield Ready! (Q)"
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    else:
        if time_since_guard < GUARD_DELAY:
            glColor3f(0.1, 0.8, 0.8)
            glRasterPos2f(15, WIN_H - 185)
            cooldown_left = (GUARD_DELAY - time_since_guard) / 1000
            text = f"Shield Cooldown: {cooldown_left:.1f}s"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        else:
            glColor3f(0.1, 0.8, 0.8)
            glRasterPos2f(15, WIN_H - 185)
            text = "Shield Ready! (Q)"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    time_since_pulse = current_time - last_pulse_time

    if time_since_pulse < 1200:
        glPushMatrix()
        try:
            glTranslatef(avatar_location[0], avatar_location[1], avatar_location[2])
            progress = time_since_pulse / 250.0
            radius = PULSE_RANGE * progress
            render_pulse_wave(radius, progress)
        finally:
            glPopMatrix()

    if divine_active:
        glColor3f(0.85, 0.55, 0.25)
        glRasterPos2f(15, WIN_H - 240)
        text = "Pulse Ready! (X)"
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    else:
        if time_since_pulse < PULSE_DELAY:
            glColor3f(0.85, 0.55, 0.25)
            glRasterPos2f(15, WIN_H - 240)
            cooldown_left = (PULSE_DELAY - time_since_pulse) / 1000
            text = f"Pulse Cooldown: {cooldown_left:.1f}s"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        else:
            glColor3f(0.85, 0.55, 0.25)
            glRasterPos2f(15, WIN_H - 240)
            text = "Pulse Ready! (X)"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    global drive_mode, last_drive_time
    time_since_drive = current_time - last_drive_time
    
    if drive_mode:
        if current_time - last_drive_time >= DRIVE_DURATION:
            drive_mode = False
        else:
            glColor3f(0.9, 0.15, 0.15)
            glRasterPos2f(15, WIN_H - 275)
            time_left = (DRIVE_DURATION - (current_time - last_drive_time)) / 1000
            text = f"Drive Mode: {time_left:.1f}s (Z)"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    elif divine_active:
        glColor3f(0.9, 0.15, 0.15)
        glRasterPos2f(15, WIN_H - 275)
        text = "Drive Mode Ready! (Z)"
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    else:
        if time_since_drive < DRIVE_COOLDOWN:
            glColor3f(0.9, 0.15, 0.15)
            glRasterPos2f(15, WIN_H - 275)
            cooldown_left = (DRIVE_COOLDOWN - time_since_drive) / 1000
            text = f"Drive Cooldown: {cooldown_left:.1f}s"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        else:
            glColor3f(0.9, 0.15, 0.15)
            glRasterPos2f(15, WIN_H - 275)
            text = "Drive Mode Ready! (Z)"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    if perspective_mode:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WIN_W, 0, WIN_H)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        render_targeting()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    if override_active:
        glColor3f(1.0, 0.1, 0.1)
        y_pos = WIN_H - 305
        glRasterPos2f(15, y_pos)
        text = "OVERRIDE ACTIVE"
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        y_pos -= 30
        if divine_active:
            glRasterPos2f(15, y_pos)
            text = "DIVINE MODE ACTIVE"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            y_pos -= 30
            
        if limitless_ammo:
            glRasterPos2f(15, y_pos)
            text = "UNLIMITED AMMO ACTIVE"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            y_pos -= 30
            
        if perception_mode:
            glRasterPos2f(15, y_pos)
            text = "PERCEPTION MODE ACTIVE"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        if immortality_active:
            glRasterPos2f(15, y_pos)
            text = "IMMORTALITY ACTIVE"
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            y_pos -= 30

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glutSwapBuffers()

def initialize_simulation():
    """Initialize simulation with DIFFERENT LOGIC"""
    global next_boost_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Temporal Overdrive")
 
    for _ in range(MAX_THREATS):
        hostiles.append(spawn_threat())

    next_boost_time = int(time.time() * 1000) + BOOST_FREQUENCY
    
    next_boost_time = int(time.time() * 1000) + random.randint(1800, 5200)
    glutDisplayFunc(render_display)
    glutKeyboardFunc(process_input)
    glutSpecialFunc(process_special_keys)
    glutMouseFunc(process_mouse)
    glutIdleFunc(lambda: glutPostRedisplay())
    glutMainLoop()

if __name__ == "__main__":
    initialize_simulation()