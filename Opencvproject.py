

import cv2
import numpy as np
import random
import time
import math
import mediapipe as mp

# ==========================
# Camera setup
# ==========================
cap = cv2.VideoCapture(0)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

effects = ['fire', 'ice', 'lightning', 'energy', 'portal', 'nebula']
effect_idx = 0
effect = effects[effect_idx]

col_pal = {
    'fire': [(0,100,255),(0,140,255),(0,180,255),(0,220,255),(0,255,255)],
    'ice': [(255,220,220),(255,255,255),(255,200,200),(240,255,255),(220,240,255)],
    'lightning': [(255,255,255),(255,255,220),(255,240,200),(220,200,255),(255,180,255)],
    'energy': [(255,0,255),(220,0,220),(255,50,255),(200,0,200),(180,0,180)],
    'portal': [(220,0,120),(180,50,220),(120,120,255),(255,0,180),(200,80,255)],
    'nebula': [(200,50,255),(255,100,200),(100,100,255),(255,150,200),(150,80,255)]
}


key_effects = {
    ord('1'): 'fire',
    ord('2'): 'ice',
    ord('3'): 'lightning',
    ord('4'): 'energy',
    ord('5'): 'portal',
    ord('6'): 'nebula'
}


class Particle:
    def __init__(self, x, y, vx, vy, radius, color, life, max_life, effect):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.radius = radius
        self.color = color
        self.life = life
        self.max_life = max_life
        self.effect = effect
        self.trail = []
        self.pulse = random.uniform(0, 2 * math.pi)
        self.angle = random.uniform(0, 2*math.pi)
        self.rotation_speed = random.uniform(-0.3, 0.3)
        self.spiral_angle = 0

    def update(self):
        # Trails for special effects
        if self.effect in ['energy','lightning','nebula']:
            self.trail.append((self.x,self.y))
            if len(self.trail) > 8:
                self.trail.pop(0)

        if self.effect == 'fire':
            self.vy -= 0.5
            self.vx *= 0.98
            self.vx += random.uniform(-0.3,0.3)
        elif self.effect == 'ice':
            self.vy += 0.25
            self.vx *= 0.95
            self.vx += random.uniform(-0.2,0.2)
        elif self.effect == 'lightning':
            self.vx += random.uniform(-2,2)
            self.vy += random.uniform(-2,2)
            self.vx *= 0.9
            self.vy *= 0.9
        elif self.effect == 'energy':
            self.vx += random.uniform(-1.2,1.2)
            self.vy += random.uniform(-1.2,1.2)
            self.vx *= 0.95
            self.vy *= 0.95
        elif self.effect in ['portal','nebula']:
            self.spiral_angle += 0.1
            self.angle += self.rotation_speed
            dx = self.x - w/2
            dy = self.y - h/2
            dist = math.hypot(dx,dy)+1
            pull_strength = 0.15
            self.vx -= (dx/dist)*pull_strength
            self.vy -= (dy/dist)*pull_strength
            self.vx += math.cos(self.spiral_angle)*0.5
            self.vy += math.sin(self.spiral_angle)*0.5

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Life decay
        decay = 0.018
        if self.effect in ['lightning','energy']:
            decay = 0.04
        self.life -= decay

        # Radius decay
        if self.effect in ['lightning','energy']:
            self.radius *= 0.9
        else:
            self.radius *= 0.97

    def is_alive(self):
        return self.life>0 and self.radius>0.3 and -50<=self.x<w+50 and -50<=self.y<h+50

    def draw(self, frame, glow_canvas):
        intensity = self.life/self.max_life
        # Trail
        if self.effect in ['energy','lightning','nebula']:
            for i,(tx,ty) in enumerate(self.trail):
                trail_int = (i/len(self.trail))*intensity*0.6
                trail_color = tuple(int(c*trail_int) for c in self.color)
                trail_radius = max(1,int(self.radius*0.6*(i/len(self.trail))))
                cv2.circle(frame,(int(tx),int(ty)),trail_radius,trail_color,-1)
        # Glow
        glow_mults = {'fire':4.5,'ice':3.5,'lightning':4,'energy':4,'portal':4,'nebula':4}
        glow_mult = glow_mults.get(self.effect,3.5)
        glow_radius = int(self.radius*glow_mult)
        glow_color = tuple(int(c*intensity*0.7) for c in self.color)
        cv2.circle(glow_canvas,(int(self.x),int(self.y)),glow_radius,glow_color,-1)
        # Core
        cv2.circle(frame,(int(self.x),int(self.y)),max(1,int(self.radius)),tuple(int(c*intensity) for c in self.color),-1)
        # Bright center
        bright_radius = max(1,int(self.radius*0.5))
        bright_color = (255,255,255) if self.effect in ['lightning','energy'] else tuple([int(255*intensity)]*3)
        cv2.circle(frame,(int(self.x),int(self.y)),bright_radius,bright_color,-1)

particles = []
MAX_PARTICLES = 800

def detect_palm(frame,display_frame):
    """Detect palm center using MediaPipe"""
    rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    if results.multi_hand_landmarks and results.multi_handedness:
        for idx, hand_handedness in enumerate(results.multi_handedness):
            hand_landmarks = results.multi_hand_landmarks[idx]
            lm = hand_landmarks.landmark
            wrist_x, wrist_y = lm[0].x*w, lm[0].y*h
            index_x, index_y = lm[5].x*w, lm[5].y*h
            pinky_x, pinky_y = lm[17].x*w, lm[17].y*h
            # Cross product to check palm
            ax, ay = index_x-wrist_x, index_y-wrist_y
            bx, by = pinky_x-wrist_x, pinky_y-wrist_y
            if ax*by - ay*bx > 0:
                center_x = sum([lm[i].x*w for i in [0,5,9,13,17]])/5
                center_y = sum([lm[i].y*h for i in [0,5,9,13,17]])/5
                size = int(math.hypot(index_x-pinky_x,index_y-pinky_y)*2.2)
                effect_color = col_pal[effect][0]
                mp_draw.draw_landmarks(display_frame,hand_landmarks,mp_hands.HAND_CONNECTIONS,
                                       mp_draw.DrawingSpec(color=effect_color,thickness=2),
                                       mp_draw.DrawingSpec(color=tuple(int(c*0.7) for c in effect_color),thickness=2))
                # Palm circle
                cv2.circle(display_frame,(int(center_x),int(center_y)),18,effect_color,-1)
                cv2.circle(display_frame,(int(center_x),int(center_y)),18,(255,255,255),3)
                cv2.circle(display_frame,(int(center_x),int(center_y)),8,(255,255,255),-1)
                return (center_x,center_y,size), hand_landmarks
    return None,None

def create_particle(center,effect_name):
    x,y,size = center
    offset = size/3
    px, py = x+random.uniform(-offset,offset), y+random.uniform(-offset,offset)
    # Particle behavior
    behaviors = {
        'fire':{'vx':(-4,4),'vy':(-18,-10),'life':(1.2,3.0),'radius':(8,30)},
        'ice':{'vx':(-6,6),'vy':(-14,-5),'life':(1.5,2.8),'radius':(6,24)},
        'lightning':{'vx':(-15,15),'vy':(-15,15),'life':(0.2,0.7),'radius':(2,10)},
        'energy':{'vx':(-10,10),'vy':(-10,10),'life':(1.2,2.5),'radius':(5,18)},
        'portal':{'vx':(-7,7),'vy':(-7,7),'life':(2.5,4.5),'radius':(10,30)},
        'nebula':{'vx':(-6,6),'vy':(-6,6),'life':(2.5,4.5),'radius':(10,30)}
    }
    behavior = behaviors.get(effect_name,behaviors['fire'])
    vx = random.uniform(*behavior['vx'])
    vy = random.uniform(*behavior['vy'])
    life = random.uniform(*behavior['life'])
    radius = random.uniform(*behavior['radius'])
    color = random.choice(col_pal[effect_name])
    return Particle(px,py,vx,vy,radius,color,life,life,effect_name)

def update_particles():
    global particles
    for p in particles:
        p.update()
    particles = [p for p in particles if p.is_alive()]

def draw_particles(frame):
    glow_canvas = np.zeros((h,w,3),dtype=np.uint8)
    for p in particles: p.draw(frame,glow_canvas)
    blur_amounts = {'portal':22,'nebula':22,'lightning':12,'energy':12,'fire':16,'ice':14}
    blur_amt = blur_amounts.get(effect,16)
    glow_blur = cv2.GaussianBlur(glow_canvas,(0,0),blur_amt)
    frame[:] = cv2.add(frame,glow_blur)

# ==========================
# Main loop
# ==========================
effect_cooldown = 0.035
last_effect_time = 0
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame,1)
    display_frame = frame.copy()
    current_time = time.time()
    frame_count += 1

    palm, hand_landmarks = detect_palm(frame,display_frame)
    if palm and current_time-last_effect_time>effect_cooldown:
        burst = 18 if effect in ['lightning','energy'] else 14
        for _ in range(burst):
            if len(particles)<MAX_PARTICLES:
                particles.append(create_particle(palm,effect))
        if hand_landmarks:
            lm = hand_landmarks.landmark
            for tip in [4,8,12,16,20]:
                tx, ty = lm[tip].x*w, lm[tip].y*h
                tip_particles = 5 if effect in ['lightning','energy'] else 4
                for _ in range(tip_particles):
                    if len(particles)<MAX_PARTICLES:
                        particles.append(create_particle((tx,ty,palm[2]//6),effect))
        last_effect_time = current_time

    update_particles()
    draw_particles(display_frame)

    # HUD
    effect_color = col_pal[effect][0]
    cv2.rectangle(display_frame,(5,5),(380,130),(0,0,0),-1)
    cv2.rectangle(display_frame,(5,5),(380,130),effect_color,3)
    pulse_val = int(abs(math.sin(frame_count*0.1))*100)+155
    pulse_color = tuple(min(255,int(c*pulse_val/255)) for c in effect_color)
    cv2.putText(display_frame,f"Effect: {effect.upper()}",(15,40),cv2.FONT_HERSHEY_SIMPLEX,1.2,pulse_color,2)
    cv2.putText(display_frame,f"Particles: {len(particles)}/{MAX_PARTICLES}",(15,80),cv2.FONT_HERSHEY_SIMPLEX,0.8,effect_color,2)
    cv2.putText(display_frame,"Press 1-6 to change effect",(15,120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(200,200,255),2)

    cv2.imshow("ULTIMATE Hand Magic - 6 Effects",display_frame)

    # Key controls - simplified for 6 effects
    key = cv2.waitKey(1)&0xFF
    if key == ord('q'):
        break
    elif key in key_effects and key_effects[key] != effect:
        effect = key_effects[key]
        effect_idx = effects.index(effect)
        particles = []
        print(f"Switched to {effect} effect")

cap.release()
cv2.destroyAllWindows()