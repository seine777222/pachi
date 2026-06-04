import pyxel
import random
import math
import json
import os

# 状態の定義
STATE_IDLE = 0
STATE_SPIN_ALL = 1
STATE_SPIN_OUTER = 2
STATE_SLIP = 3
STATE_SPIN_CENTER = 4
STATE_REACH = 5
STATE_SP_CHANCE = 6
STATE_SP_REACH = 7
STATE_WIN_PAUSE = 8
STATE_WIN = 9
STATE_ROULETTE = 10
STATE_LOSE = 11
STATE_PREMIUM_FLASH = 12
STATE_ZENKAITEN = 13
STATE_REVIVAL_WAIT = 14
STATE_REVIVAL = 15
STATE_ROULETTE_STOP = 16
STATE_CLEAR = 17    
STATE_RANKING = 18  
STATE_PROMOTION = 19
STATE_TITLE = 20
STATE_SP9_EVOLVE = 21  
STATE_SP9_REACH = 22   

class PachinkoGame:
    def __init__(self):
        pyxel.init(160, 120, title="Pyxel Pachinko Ultimate", fps=60)
        pyxel.mouse(True)
        
        image_data = [
            "00077000" "00777700" "00777700" "00007700" "07777770" "00777700" "07777770" "00777700" "00777700" "00077000",
            "00777000" "07700770" "07700770" "00077700" "07700000" "07700770" "07700770" "07700770" "07700770" "00777700",
            "07777000" "07700770" "00000770" "00777700" "07700000" "07700000" "00000770" "07700770" "07700770" "07700770",
            "00077000" "00000770" "00000770" "07707700" "07777700" "07700000" "00000770" "07700770" "07700770" "07700770",
            "00077000" "00007700" "00077700" "07707700" "00000770" "07777700" "00007700" "00777700" "07700770" "07700770",
            "00077000" "00077000" "00000770" "07777770" "00000770" "07700770" "00007700" "07700770" "00777770" "07700770",
            "00077000" "00770000" "00000770" "00007700" "00000770" "07700770" "00077000" "07700770" "00000770" "07700770",
            "00077000" "07700000" "00000770" "00007700" "00000770" "07700770" "00077000" "07700770" "00000770" "07700770",
            "00077000" "07777770" "07700770" "00007700" "07700770" "07700770" "00077000" "07700770" "07700770" "00777700",
            "07777700" "07777770" "00777700" "00007700" "00777700" "00777700" "00077000" "00777700" "00777700" "00077000",
            "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000",
            "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000" "00000000",
        ]
        pyxel.images[0].set(0, 0, image_data)

        self.state = STATE_TITLE
        self.prev_state = STATE_TITLE
        self.timer = 0
        self.spins = 0
        self.total_spins = 0
        self.wins = 0
        self.score = 10000
        self.use_limit = True
        
        self.is_kakuken = False
        self.is_super_kakuken = False
        self.st_count = 0             
        self.renchan = 0              
        self.won_pt = 0
        self.is_all_five = False
        
        self.is_jackpot = False
        self.is_premium = False
        self.premium_type = 0
        self.is_slip = False
        self.slip_target = -1
        self.is_revival = False
        self.is_double_reach = False 
        self.yokoku_color = 0
        self.sp_type = 0 
        
        self.sp9_final_targets = [0] * 5
        
        self.is_auto = False
        self.force_promotion = False 
        
        self.is_lucky_reach = False
        self.is_chance_text = False
        self.guarantee_kakuken = False
        
        # ✨ 番号ズレを解消！ちゃんと15個になったよ〜
        self.force_mode = 0
        self.force_names = [
            "OFF",                           # 0
            "FORCE: HIT [ALL 5 MATCH]",      # 1
            "FORCE: HIT [7] (SUPER)",        # 2
            "FORCE: HIT [3] (KAKUKEN)",      # 3
            "FORCE: HIT [2] (NORMAL ST)",    # 4
            "FORCE: PREM [ZENKAITEN]",       # 5
            "FORCE: PREM [ALL 7]",           # 6
            "FORCE: HIT [REVIVAL]",          # 7
            "FORCE: HIT [DOUBLE]",           # 8
            "FORCE: MISS [SLIP -> SP2]",     # 9
            "FORCE: MISS [SP4 SLOW]",        # 10
            "FORCE: MISS [SP5]",             # 11 ✨ ここが抜けてたの！
            "FORCE: MISS [SP6 REV-SUPER]",   # 12
            "FORCE: MISS [DOUBLE SP7]",      # 13
            "FORCE: HIT [PROMOTION]",        # 14
            "FORCE: HIT [SP9 REVERSE]"       # 15
        ]
        
        self.ranking = self.load_ranking()
        
        self.has_save = (self.load_game_data() is not None)
        self.title_cursor = 1 if self.has_save else 0
        
        self.roulette_base_data = [(300, 6), (750, 11), (1200, 14), (1500, 8), (3000, 9), (7500, 10)]
        self.roulette_super_data = [(3000, 9), (4500, 10), (3000, 9), (4500, 10), (3000, 9), (7500, 10)]
        self.active_roulette_data = self.roulette_base_data
        
        self.roulette_idx = 0
        self.roulette_y = 0.0

        self.reel_y = [0.0] * 5
        self.reels = [0, 1, 2, 3, 4]
        self.targets = [0] * 5
        self.stopped = [True] * 5
        self.stopping = [False] * 5
        self.reach_steps = 0
        
        self.reel_coords = [
            (20, 8),   # 0: TL
            (108, 8),  # 1: TR
            (64, 34),  # 2: C
            (20, 60),  # 3: BL
            (108, 60)  # 4: BR
        ]

        # サウンド
        pyxel.sounds[0].set("c4d4", "t", "3", "n", 2)
        pyxel.sounds[1].set("b3e4", "p", "5", "f", 5)
        pyxel.sounds[2].set("c3d#3f#3a3c4a3f#3d#3", "s", "4", "v", 15)
        pyxel.sounds[3].set("c2g2c3g2d2a2d3a2", "p", "5", "n", 6)
        pyxel.sounds[4].set("e2b2e3b2f#2c#3f#3c#3", "s", "6", "v", 8)
        pyxel.sounds[5].set("g2d3g3d3a2e3a3e3", "p", "6", "f", 10)
        pyxel.sounds[6].set("c3e3g3c4e3g3c4e4", "p", "5", "v", 6)
        pyxel.sounds[7].set("c2e2g2c3e2g2c3e3g2c3e3g3c3e3g3c4", "p", "6", "n", 8)
        pyxel.sounds[8].set("c2c3c4", "s", "6", "s", 10)
        pyxel.sounds[9].set("e4", "t", "4", "f", 15)
        pyxel.sounds[10].set("a3", "p", "6", "f", 2)
        pyxel.sounds[11].set("c3e3g3c4", "p", "6", "n", 15)
        pyxel.sounds[12].set("f2a2c3f2a2c3", "s", "5", "v", 6)
        pyxel.sounds[13].set("g2d3b2g2d3b2", "p", "5", "n", 8)
        pyxel.sounds[14].set("e3c3a2e3c3a2", "s", "6", "v", 8)
        pyxel.sounds[15].set("c3e3g3c4 d3f#3a3d4 e3g#3b3e4 f3a3c4f4 g3b3d4g4", "p", "6", "n", 8)
        pyxel.sounds[16].set("e2a2c3e3 a2c3e3a3 c3e3a3c4 e3a3c4e4", "p", "5", "v", 8)
        pyxel.sounds[17].set("c2e2g2c3 e2g2c3e3 g2c3e3g3 c3e3g3c4", "p", "5", "v", 10)

        pyxel.run(self.update, self.draw)

    def load_game_data(self):
        if os.path.exists("save.json"):
            try:
                with open("save.json", "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_game_data(self):
        data = {
            "score": self.score,
            "spins": self.spins,
            "total_spins": self.total_spins,
            "wins": self.wins,
            "use_limit": self.use_limit,
            "is_kakuken": self.is_kakuken,
            "is_super_kakuken": self.is_super_kakuken,
            "st_count": self.st_count,
            "renchan": self.renchan
        }
        try:
            with open("save.json", "w") as f:
                json.dump(data, f)
        except:
            pass

    def load_ranking(self):
        if os.path.exists("ranking.json"):
            with open("ranking.json", "r") as f:
                return json.load(f)
        return []

    def save_ranking(self, spins):
        self.ranking.append(spins)
        self.ranking.sort()
        self.ranking = self.ranking[:5] 
        with open("ranking.json", "w") as f:
            json.dump(self.ranking, f)

    def get_yokoku_color(self, is_hit):
        r = random.randint(1, 100)
        if is_hit:
            if r <= 5: return 12     
            elif r <= 15: return 11  
            elif r <= 45: return 8   
            else: return 10          
        else:
            if r <= 50: return 12    
            elif r <= 80: return 11  
            elif r <= 99: return 8   
            else: return 10          

    def get_sp_type(self, is_hit):
        r = random.randint(1, 1000)
        if is_hit:
            if r <= 50: return 0    
            elif r <= 100: return 1 
            elif r <= 200: return 2 
            elif r <= 350: return 4 
            elif r <= 450: return 5 
            elif r <= 600: return 8 
            elif r <= 700: return 6 
            elif r <= 850: return 9
            else: return 3          
        else:
            if r <= 850: return 0   
            elif r <= 950: return 1 
            elif r <= 975: return 2 
            elif r <= 985: return 5 
            elif r <= 995: return 4 
            elif r <= 997: return 8 
            elif r <= 999: return 9 
            else: return 6          

    def setup_win(self):
        self.is_auto = False 
        self.wins += 1
        self.spins = 0
        self.renchan += 1
        
        t = self.targets[2]
        if t == 6:
            self.is_super_kakuken = True
            self.is_kakuken = True
            self.active_roulette_data = self.roulette_super_data
            self.st_count = 0
        elif t % 2 == 0:
            self.is_super_kakuken = False
            self.is_kakuken = True
            self.active_roulette_data = self.roulette_base_data
            self.st_count = 0
        else:
            self.is_super_kakuken = False
            self.is_kakuken = False
            self.active_roulette_data = self.roulette_base_data
            self.st_count = 5 
            
        self.state = STATE_WIN
        self.timer = 0

    def update(self):
        self.timer += 1
        is_clicked = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        is_auto_btn_clicked = False
        start_game = False
        
        if self.state == STATE_TITLE:
            if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_UP):
                if self.has_save:
                    self.title_cursor = 1 - self.title_cursor
                    pyxel.play(0, 10)
            
            if self.title_cursor == 0:
                if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_RIGHT):
                    self.use_limit = not self.use_limit
                    pyxel.play(0, 10)
            
            if is_clicked:
                if 40 <= pyxel.mouse_x <= 120 and 45 <= pyxel.mouse_y <= 60:
                    if self.title_cursor == 0:
                        start_game = True
                    self.title_cursor = 0
                elif 32 <= pyxel.mouse_x <= 128 and 62 <= pyxel.mouse_y <= 75 and self.title_cursor == 0:
                    self.use_limit = not self.use_limit
                    pyxel.play(0, 10)
                elif 40 <= pyxel.mouse_x <= 120 and 80 <= pyxel.mouse_y <= 95 and self.has_save:
                    if self.title_cursor == 1:
                        start_game = True
                    self.title_cursor = 1
                    
            if pyxel.btnp(pyxel.KEY_SPACE) or start_game:
                if self.title_cursor == 0:
                    self.score = 10000
                    self.spins = 0
                    self.total_spins = 0
                    self.wins = 0
                    self.renchan = 0
                    self.is_kakuken = False
                    self.is_super_kakuken = False
                    self.st_count = 0
                    self.save_game_data() 
                else:
                    data = self.load_game_data()
                    self.score = data.get("score", 10000)
                    self.spins = data.get("spins", 0)
                    self.total_spins = data.get("total_spins", 0)
                    self.wins = data.get("wins", 0)
                    self.use_limit = data.get("use_limit", True)
                    self.is_kakuken = data.get("is_kakuken", False)
                    self.is_super_kakuken = data.get("is_super_kakuken", False)
                    self.st_count = data.get("st_count", 0)
                    self.renchan = data.get("renchan", 0)
                    
                self.state = STATE_IDLE
                pyxel.play(0, 9)

        if self.state != STATE_TITLE:
            if is_clicked and 125 <= pyxel.mouse_x <= 158 and 109 <= pyxel.mouse_y <= 119:
                is_auto_btn_clicked = True
                self.is_auto = not self.is_auto
                
            if pyxel.btnp(pyxel.KEY_A):
                self.is_auto = not self.is_auto
                
        if self.state == STATE_IDLE:
            if pyxel.btnp(pyxel.KEY_UP):
                self.force_mode = (self.force_mode - 1) % len(self.force_names)
                pyxel.play(0, 10)
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.force_mode = (self.force_mode + 1) % len(self.force_names)
                pyxel.play(0, 10)

        ODDS = [0, 2, 4, 6, 8]
        step_val = 2 if self.is_super_kakuken else 1

        speed = [0.0] * 5
        if self.state == STATE_SPIN_ALL: speed = [1.0] * 5
        elif self.state == STATE_SPIN_OUTER: speed = [0.0, 0.0, 1.0, 1.0, 1.0]
        elif self.state == STATE_SLIP:
            if self.slip_target != -1: speed[self.slip_target] = 0.5
        elif self.state == STATE_SPIN_CENTER: speed[2] = 1.0
        elif self.state == STATE_REACH: speed[2] = 0.5
        elif self.state == STATE_SP_CHANCE: speed[2] = 0.25
        elif self.state == STATE_ZENKAITEN: speed = [0.25] * 5
        elif self.state == STATE_REVIVAL: speed[2] = 1.0
        elif self.state == STATE_PROMOTION: speed = [1.0] * 5
        elif self.state == STATE_SP9_EVOLVE: speed = [0.0] * 5
        elif self.state == STATE_SP9_REACH: speed = [0.5, 0.5, 0.0, 0.5, 0.5] 
        
        elif self.state == STATE_SP_REACH:
            if self.sp_type == 4:
                dist = (self.targets[2] - self.reels[2]) % 10
                slow_dists = [0, step_val, (10 - step_val) % 10]
                if dist in slow_dists: speed[2] = 0.1 
                else: speed[2] = 1.5 
            elif self.sp_type == 5: speed[2] = 0.25
            elif self.sp_type == 6: speed[2] = 0.5
            elif self.sp_type == 8: speed[2] = 0.5 
            elif self.sp_type == 7:
                dist1 = (self.targets[0] - self.reels[2]) % 10
                dist2 = (self.targets[1] - self.reels[2]) % 10
                slow_dists = [0, step_val, (10 - step_val) % 10]
                if dist1 in slow_dists or dist2 in slow_dists: speed[2] = 0.1
                else: speed[2] = 1.5
            else: speed[2] = 0.25 

        for i in range(5):
            if not self.stopped[i]:
                is_reverse = (self.state == STATE_SP_REACH and self.sp_type in [5, 6] and i == 2)
                
                if is_reverse:
                    self.reel_y[i] -= speed[i] 
                    if self.reel_y[i] <= 0.0:
                        if self.stopping[i] and self.reels[i] == self.targets[i]:
                            self.reel_y[i] = 0.0
                            self.stopped[i] = True
                            self.stopping[i] = False
                            pyxel.play(0, 1)
                        else:
                            self.reel_y[i] += 12.0
                            self.reels[i] = (self.reels[i] - step_val) % 10 
                            if i == 2: self.reach_steps += 1
                else:
                    self.reel_y[i] += speed[i]
                    if self.reel_y[i] >= 12.0:
                        self.reel_y[i] -= 12.0
                        self.reels[i] = (self.reels[i] + step_val) % 10
                        
                        if i == 2 and self.state in [STATE_REACH, STATE_SP_REACH, STATE_ZENKAITEN]:
                            self.reach_steps += 1
                        elif i == 0 and self.state == STATE_SP9_REACH:
                            self.reach_steps += 1 
                        
                        if self.state == STATE_PROMOTION and self.timer > 90:
                            self.stopping[i] = True

                        if self.stopping[i] and self.reels[i] == self.targets[i]:
                            self.reel_y[i] = 0.0
                            self.stopped[i] = True
                            self.stopping[i] = False
                            pyxel.play(0, 1)

        do_spin = False
        if self.state == STATE_IDLE:
            if self.is_auto: do_spin = True
            elif pyxel.btnp(pyxel.KEY_SPACE): do_spin = True
            elif is_clicked and not is_auto_btn_clicked: do_spin = True

            if do_spin:
                is_free_spin = self.is_kakuken or self.is_super_kakuken
                if not is_free_spin:
                    if self.score < 10:
                        do_spin = False
                        self.is_auto = False
                    else:
                        self.score -= 10
                        self.save_game_data() 

        if self.state == STATE_IDLE and do_spin:
            prob = 200 if (self.is_kakuken or self.st_count > 0) else 20
            
            if not self.is_kakuken and self.st_count > 0:
                self.st_count -= 1
                if self.st_count == 0:
                    self.renchan = 0
            
            self.spins += 1
            self.total_spins += 1 
            self.timer = 0
            self.stopped = [False] * 5
            self.stopping = [False] * 5
            self.reach_steps = 0
            self.yokoku_color = 0
            self.is_slip = False
            self.slip_target = -1
            self.is_revival = False
            self.premium_type = 0
            self.force_promotion = False
            self.is_all_five = False
            self.is_double_reach = False
            self.sp_type = 0
            self.is_lucky_reach = False
            self.is_chance_text = False
            
            av_targets = ODDS if self.is_super_kakuken else list(range(10))
            
            if self.is_super_kakuken:
                for i in range(5):
                    if self.reels[i] % 2 != 0:
                        self.reels[i] = (self.reels[i] + 1) % 10
            
            if self.guarantee_kakuken:
                self.guarantee_kakuken = False
                self.is_jackpot = True
                self.force_mode = 0 
                
                t = random.choice([0, 2, 4, 6, 8]) 
                self.targets = [t] * 5
                
                if random.randint(1, 100) <= 40:
                    self.is_double_reach = True
                    t2 = random.choice([x for x in av_targets if x != t])
                    if random.randint(0, 1) == 0: self.targets[1] = self.targets[3] = t2
                    else: self.targets[0] = self.targets[4] = t2
                    self.sp_type = 7 
                else:
                    if random.randint(0, 1) == 0:
                        self.targets[1] = random.choice([x for x in av_targets if x != t])
                        self.targets[3] = random.choice([x for x in av_targets if x != self.targets[1] and x != t])
                    else:
                        self.targets[0] = random.choice([x for x in av_targets if x != t])
                        self.targets[4] = random.choice([x for x in av_targets if x != self.targets[0] and x != t])
                    self.sp_type = self.get_sp_type(True)

            elif self.force_mode == 0:
                self.is_jackpot = (random.randint(1, 1000) <= prob)
                self.is_premium = (self.is_jackpot and random.randint(1, 100) <= 2)
                self.premium_type = random.choice([1, 2, 3]) if self.is_premium else 0
                
                if self.is_jackpot:
                    t = random.choice(av_targets)
                    self.targets = [t] * 5 
                    
                    if not self.is_premium and random.randint(1, 100) > 20:
                        if random.randint(1, 100) <= 40:
                            self.is_double_reach = True
                            t2 = random.choice([x for x in av_targets if x != t])
                            if random.randint(0, 1) == 0: self.targets[1] = self.targets[3] = t2
                            else: self.targets[0] = self.targets[4] = t2
                            self.sp_type = 7 
                        else:
                            if random.randint(0, 1) == 0:
                                self.targets[1] = random.choice([x for x in av_targets if x != t])
                                self.targets[3] = random.choice([x for x in av_targets if x != self.targets[1] and x != t])
                            else:
                                self.targets[0] = random.choice([x for x in av_targets if x != t])
                                self.targets[4] = random.choice([x for x in av_targets if x != self.targets[0] and x != t])
                            self.sp_type = self.get_sp_type(True)
                    else:
                        self.sp_type = self.get_sp_type(True)
                    
                    if not self.is_premium and random.randint(0, 4) == 0:
                        self.is_revival = True
                        self.targets[2] = (self.targets[2] + random.choice([-step_val, step_val])) % 10

                    if random.randint(0, 1) == 0:
                        self.yokoku_color = self.get_yokoku_color(True)
                else:
                    self.targets = [random.choice(av_targets) for _ in range(5)]
                    
                    while self.targets[0] == self.targets[2] and self.targets[2] == self.targets[4]:
                        self.targets[2] = random.choice(av_targets)
                    while self.targets[1] == self.targets[2] and self.targets[2] == self.targets[3]:
                        self.targets[2] = random.choice(av_targets)
                        
                    if random.randint(0, 4) == 0:
                        if random.randint(1, 100) <= 5:
                            self.is_double_reach = True
                            self.targets[4] = self.targets[0]
                            self.targets[3] = self.targets[1]
                            while self.targets[2] == self.targets[0] or self.targets[2] == self.targets[1]:
                                self.targets[2] = random.choice(av_targets)
                            self.sp_type = 7
                        else:
                            if random.randint(0, 1) == 0:
                                self.targets[4] = self.targets[0]
                                while self.targets[2] == self.targets[0]: self.targets[2] = random.choice(av_targets)
                            else:
                                self.targets[3] = self.targets[1]
                                while self.targets[2] == self.targets[1]: self.targets[2] = random.choice(av_targets)
                                
                            self.sp_type = self.get_sp_type(False)
                            if self.sp_type == 4:
                                self.targets[2] = (self.targets[0] if self.targets[0]==self.targets[4] else self.targets[1]) + random.choice([-step_val, step_val])
                                self.targets[2] %= 10
                            
                            if random.randint(0, 3) == 0:
                                self.is_slip = True
                                if self.targets[4] == self.targets[0]:
                                    self.slip_target = 4
                                    self.targets[4] = (self.targets[4] - step_val) % 10
                                else:
                                    self.slip_target = 3
                                    self.targets[3] = (self.targets[3] - step_val) % 10
                        if random.randint(0, 2) == 0:
                            self.yokoku_color = self.get_yokoku_color(False)
            else:
                if self.force_mode == 1: self.is_jackpot=True; self.is_premium=False; self.targets=[6]*5; self.sp_type=3; self.yokoku_color=10
                elif self.force_mode == 2: self.is_jackpot=True; self.is_premium=False; self.targets=[6,1,6,2,6]; self.sp_type=3; self.yokoku_color=10
                elif self.force_mode == 3: self.is_jackpot=True; self.is_premium=False; self.targets=[2,1,2,4,2]; self.sp_type=2; self.yokoku_color=8
                elif self.force_mode == 4: self.is_jackpot=True; self.is_premium=False; self.targets=[1,3,1,5,1]; self.sp_type=1; self.yokoku_color=12
                elif self.force_mode == 5: self.is_jackpot=True; self.is_premium=True; self.premium_type=1; self.targets=[6]*5; self.yokoku_color=10
                elif self.force_mode == 6: self.is_jackpot=True; self.is_premium=True; self.premium_type=2; self.targets=[6]*5; self.sp_type=3; self.yokoku_color=10
                elif self.force_mode == 7: self.is_jackpot=True; self.is_premium=False; self.targets=[6,1,7,2,6]; self.sp_type=2; self.is_revival=True; self.yokoku_color=8
                elif self.force_mode == 8: self.is_jackpot=True; self.is_premium=False; self.targets=[6,1,6,1,6]; self.sp_type=7; self.is_double_reach=True; self.yokoku_color=10
                elif self.force_mode == 9: self.is_jackpot=False; self.is_premium=False; self.targets=[2,8,5,9,1]; self.is_slip=True; self.slip_target=4; self.sp_type=2; self.yokoku_color=11
                elif self.force_mode == 10: self.is_jackpot=False; self.is_premium=False; self.targets=[2,1,3,4,2]; self.sp_type=4; self.yokoku_color=8
                elif self.force_mode == 11: self.is_jackpot=False; self.is_premium=False; self.targets=[2,1,3,4,2]; self.sp_type=5; self.yokoku_color=8
                elif self.force_mode == 12: self.is_jackpot=False; self.is_premium=False; self.targets=[2,1,3,4,2]; self.sp_type=6; self.yokoku_color=10
                elif self.force_mode == 13: self.is_jackpot=False; self.is_premium=False; self.targets=[6,1,2,1,6]; self.sp_type=7; self.is_double_reach=True; self.yokoku_color=10
                elif self.force_mode == 14: self.is_jackpot=True; self.is_premium=False; self.targets=[1]*5; self.sp_type=2; self.yokoku_color=8; self.force_promotion=True
                elif self.force_mode == 15: self.is_jackpot=True; self.is_premium=False; self.targets=[4]*5; self.sp_type=9; self.yokoku_color=12

            if self.sp_type == 9:
                self.sp9_final_targets = self.targets[:]
                self.is_double_reach = False 
                fake_target = random.choice([x for x in av_targets if x != self.sp9_final_targets[2]])
                self.targets[0] = self.targets[4] = fake_target
                self.targets[1] = random.choice([x for x in av_targets if x != fake_target])
                self.targets[3] = random.choice([x for x in av_targets if x != self.targets[1] and x != fake_target])
                self.targets[2] = self.sp9_final_targets[2] 

            if self.targets[0] == self.targets[1] == self.targets[2] == self.targets[3] == self.targets[4]:
                self.is_all_five = True

            if self.is_jackpot and random.randint(1, 100) <= 5:
                self.is_lucky_reach = True
                
            base_prob = 200 if (self.is_kakuken or self.st_count > 0) else 20
            p_chance_hit = 0.20
            p_chance_miss = p_chance_hit * base_prob / (1000 - base_prob)
            self.is_chance_text = (random.random() <= (p_chance_hit if self.is_jackpot else p_chance_miss))

            if self.premium_type == 1:
                self.state = STATE_PREMIUM_FLASH
                self.reels = [6] * 5
            else:
                self.state = STATE_SPIN_ALL

        elif self.state == STATE_PREMIUM_FLASH:
            if self.timer > 120:
                self.state = STATE_ZENKAITEN
                self.timer = 0
                self.reach_steps = 0

        elif self.state == STATE_ZENKAITEN:
            if self.reach_steps >= 30:
                self.stopping = [True] * 5
            if all(self.stopped):
                self.state = STATE_WIN_PAUSE
                self.timer = 0

        elif self.state == STATE_SPIN_ALL:
            if self.timer > 40:
                self.stopping[0] = True
                self.stopping[1] = True
            if self.stopped[0] and self.stopped[1]:
                self.state = STATE_SPIN_OUTER
                self.timer = 0

        elif self.state == STATE_SPIN_OUTER:
            if self.timer > 40:
                self.stopping[3] = True
                self.stopping[4] = True
            if self.stopped[3] and self.stopped[4]:
                if self.is_slip:
                    self.state = STATE_SLIP
                elif self.targets[0] == self.targets[4] or self.targets[1] == self.targets[3]:
                    self.state = STATE_REACH
                else:
                    self.state = STATE_SPIN_CENTER
                self.timer = 0

        elif self.state == STATE_SLIP:
            if self.timer == 30:
                pyxel.play(0, 9)
                self.targets[self.slip_target] = (self.targets[self.slip_target] + step_val) % 10
                self.stopped[self.slip_target] = False
                self.stopping[self.slip_target] = True
            if self.timer > 30 and self.stopped[self.slip_target]:
                if self.targets[0] == self.targets[4] or self.targets[1] == self.targets[3]:
                    self.state = STATE_REACH
                else:
                    self.state = STATE_SPIN_CENTER
                self.timer = 0

        elif self.state == STATE_SPIN_CENTER:
            if self.timer > 30: self.stopping[2] = True
            if self.stopped[2]:
                self.state = STATE_LOSE
                self.timer = 0

        elif self.state == STATE_REACH:
            if self.sp_type == 0 or self.sp_type == 9: 
                if self.reach_steps >= 20 and not self.stopping[2]:
                    self.stopping[2] = True
            else:
                if self.reach_steps >= 20 and not self.stopping[2]:
                    self.state = STATE_SP_CHANCE
                    self.timer = 0
                    
            if self.stopped[2]:
                if self.sp_type == 9: 
                    self.state = STATE_SP9_EVOLVE
                    self.timer = 0
                else:
                    if (self.targets[0] == self.targets[4] and self.targets[2] == self.targets[0]) or \
                       (self.targets[1] == self.targets[3] and self.targets[2] == self.targets[1]):
                        self.state = STATE_WIN_PAUSE
                    else:
                        if self.is_revival: self.state = STATE_REVIVAL_WAIT
                        else: self.state = STATE_LOSE
                    self.timer = 0

        elif self.state == STATE_SP_CHANCE:
            if self.timer > 90:
                self.state = STATE_SP_REACH
                self.timer = 0
                self.reach_steps = 0

        elif self.state == STATE_SP_REACH:
            limit = 10
            if self.sp_type == 4: limit = 20
            elif self.sp_type == 5: limit = 15
            elif self.sp_type == 6: limit = 25
            elif self.sp_type == 8: limit = 25 
            elif self.sp_type == 7: limit = 30 
            
            if self.reach_steps >= limit and not self.stopping[2]:
                self.stopping[2] = True
                
            if self.stopped[2]:
                if (self.targets[0] == self.targets[4] and self.targets[2] == self.targets[0]) or \
                   (self.targets[1] == self.targets[3] and self.targets[2] == self.targets[1]):
                    self.state = STATE_WIN_PAUSE
                else:
                    if self.is_revival: self.state = STATE_REVIVAL_WAIT
                    else: self.state = STATE_LOSE
                self.timer = 0

        elif self.state == STATE_SP9_EVOLVE:
            if self.timer > 60:
                self.state = STATE_SP9_REACH
                self.timer = 0
                self.reach_steps = 0
                self.targets = self.sp9_final_targets[:]
                self.stopped[0] = self.stopped[1] = self.stopped[3] = self.stopped[4] = False
                self.stopping[0] = self.stopping[1] = self.stopping[3] = self.stopping[4] = False
                pyxel.play(0, 14)

        elif self.state == STATE_SP9_REACH:
            if self.reach_steps >= 30 and not self.stopping[0]:
                self.stopping[0] = self.stopping[1] = self.stopping[3] = self.stopping[4] = True
                
            if all(self.stopped):
                if (self.targets[0] == self.targets[4] and self.targets[2] == self.targets[0]) or \
                   (self.targets[1] == self.targets[3] and self.targets[2] == self.targets[1]):
                    self.state = STATE_WIN_PAUSE
                else:
                    if self.is_revival: self.state = STATE_REVIVAL_WAIT
                    else: self.state = STATE_LOSE
                self.timer = 0

        elif self.state == STATE_REVIVAL_WAIT:
            if self.timer > 60:
                self.state = STATE_REVIVAL
                if self.targets[0] == self.targets[4] and self.targets[1] == self.targets[3]:
                    self.targets[2] = random.choice([self.targets[0], self.targets[1]])
                elif self.targets[0] == self.targets[4]: self.targets[2] = self.targets[0]
                else: self.targets[2] = self.targets[1]
                
                self.stopped[2] = False
                self.stopping[2] = True
                pyxel.play(0, 8) 
                self.timer = 0
                
        elif self.state == STATE_REVIVAL:
            if self.stopped[2]:
                self.state = STATE_WIN_PAUSE
                self.timer = 0

        elif self.state == STATE_WIN_PAUSE:
            if self.timer > 60:
                is_super_prom = self.is_super_kakuken and self.targets[2] in [0, 2, 4, 8] and random.randint(1, 100) <= 10
                is_norm_prom = self.targets[2] in [1, 3, 5, 7, 9] and random.randint(1, 100) <= 20
                
                if is_super_prom or is_norm_prom or self.force_promotion:
                    self.state = STATE_PROMOTION
                    self.timer = 0
                    t = 6 if is_super_prom else random.choice([0, 2, 4, 6, 8]) 
                    self.targets = [t] * 5
                    self.stopped = [False] * 5
                    self.stopping = [False] * 5
                    self.is_all_five = True 
                else:
                    self.setup_win()

        elif self.state == STATE_PROMOTION:
            if all(self.stopped):
                self.setup_win()

        elif self.state == STATE_WIN:
            if self.timer > 180:
                self.state = STATE_ROULETTE
                self.timer = 0
                self.roulette_y = 0.0

        elif self.state == STATE_ROULETTE:
            self.roulette_y += 2.0 
            if self.roulette_y >= 20.0:
                self.roulette_y -= 20.0
                self.roulette_idx = (self.roulette_idx - 1) % len(self.active_roulette_data)
                pyxel.play(0, 10) 
                
            stop_pressed = pyxel.btnp(pyxel.KEY_SPACE) or (is_clicked and not is_auto_btn_clicked)
            if (self.timer > 60 and stop_pressed) or self.timer >= 240:
                self.state = STATE_ROULETTE_STOP 
                self.timer = 0
                self.roulette_y = 0.0 
                pt, _ = self.active_roulette_data[self.roulette_idx]
                
                if self.is_all_five:
                    self.won_pt = pt * 2
                else:
                    self.won_pt = pt
                    
                self.score += self.won_pt
                pyxel.play(0, 11)
                self.save_game_data() 

        elif self.state == STATE_ROULETTE_STOP:
            if self.timer > 120: 
                pt, _ = self.active_roulette_data[self.roulette_idx]
                if pt == 7500:
                    self.guarantee_kakuken = True

                if self.use_limit and self.score >= 50000:
                    self.save_ranking(self.total_spins)
                    self.state = STATE_CLEAR
                else:
                    self.state = STATE_LOSE
                self.timer = 0

        elif self.state == STATE_CLEAR:
            stop_pressed = pyxel.btnp(pyxel.KEY_SPACE) or (is_clicked and not is_auto_btn_clicked)
            if self.timer > 60 and stop_pressed:
                self.state = STATE_RANKING
                
        elif self.state == STATE_RANKING:
            stop_pressed = pyxel.btnp(pyxel.KEY_SPACE) or (is_clicked and not is_auto_btn_clicked)
            if stop_pressed:
                self.has_save = False 
                self.title_cursor = 0
                self.state = STATE_TITLE
                
                self.score = 10000
                self.spins = 0
                self.total_spins = 0
                self.wins = 0
                self.renchan = 0
                self.is_kakuken = False
                self.is_super_kakuken = False
                self.st_count = 0
                self.is_auto = False
                self.save_game_data()

        elif self.state == STATE_LOSE:
            stop_pressed = pyxel.btnp(pyxel.KEY_SPACE) or (is_clicked and not is_auto_btn_clicked)
            if stop_pressed or (self.is_auto and self.timer > 45):
                if not self.is_kakuken and self.st_count == 0:
                    self.renchan = 0
                self.state = STATE_IDLE
                self.timer = 0

        if self.state != self.prev_state:
            if self.state in [STATE_TITLE, STATE_IDLE, STATE_WIN_PAUSE, STATE_LOSE, STATE_SLIP, STATE_ROULETTE, STATE_REVIVAL_WAIT, STATE_ROULETTE_STOP, STATE_RANKING]:
                pyxel.stop(1)
            elif self.state == STATE_SPIN_ALL: pyxel.play(1, 0, loop=True)
            elif self.state == STATE_REACH: pyxel.play(1, 2, loop=True)
            elif self.state == STATE_SP_CHANCE: pyxel.stop(1)
            elif self.state == STATE_SP_REACH:
                if self.sp_type == 1: pyxel.play(1, 3, loop=True)
                elif self.sp_type == 2: pyxel.play(1, 4, loop=True)
                elif self.sp_type == 4: pyxel.play(1, 12, loop=True)
                elif self.sp_type == 5: pyxel.play(1, 13, loop=True) 
                elif self.sp_type == 6: pyxel.play(1, 14, loop=True) 
                elif self.sp_type == 7: pyxel.play(1, 16, loop=True) 
                elif self.sp_type == 8: pyxel.play(1, 14, loop=True) 
                else: pyxel.play(1, 5, loop=True)
            elif self.state == STATE_SP9_EVOLVE:
                pyxel.stop(1)
                pyxel.play(0, 12)
            elif self.state == STATE_SP9_REACH:
                pyxel.play(1, 4, loop=True) 
            elif self.state == STATE_PREMIUM_FLASH:
                pyxel.stop(1)
                pyxel.play(0, 8)
            elif self.state == STATE_ZENKAITEN: pyxel.play(1, 6, loop=True)
            elif self.state == STATE_PROMOTION:
                pyxel.stop(1)
                pyxel.play(0, 8)
            elif self.state == STATE_WIN:
                if self.is_super_kakuken: pyxel.play(1, 15)
                else: pyxel.play(1, 7)
            elif self.state == STATE_CLEAR:
                pyxel.play(1, 17) 
            self.prev_state = self.state

    def draw_colored_number(self, num, x, y, scale_val):
        img_u = num * 8
        if num == 6:
            pyxel.pal(7, 0)
            pyxel.blt(x - 2, y, 0, img_u, 0, 8, 12, 0, scale=scale_val)
            pyxel.blt(x + 2, y, 0, img_u, 0, 8, 12, 0, scale=scale_val)
            pyxel.blt(x, y - 2, 0, img_u, 0, 8, 12, 0, scale=scale_val)
            pyxel.blt(x, y + 2, 0, img_u, 0, 8, 12, 0, scale=scale_val)
            pyxel.pal(7, 10)
            pyxel.blt(x, y, 0, img_u, 0, 8, 12, 0, scale=scale_val)
        elif num == 9:
            pyxel.pal(7, 11)
            pyxel.blt(x, y, 0, img_u, 0, 8, 12, 0, scale=scale_val)
        elif num % 2 == 1:
            pyxel.pal(7, 12)
            pyxel.blt(x, y, 0, img_u, 0, 8, 12, 0, scale=scale_val)
        else:
            pyxel.pal(7, 8)
            pyxel.blt(x, y, 0, img_u, 0, 8, 12, 0, scale=scale_val)
        pyxel.pal()

    def draw(self):
        if self.state == STATE_TITLE:
            pyxel.cls(1)
            pyxel.text(40, 20, "PYXEL PACHINKO", 10 if self.timer % 20 < 10 else 7)
            pyxel.text(60, 28, "ULTIMATE", 10 if self.timer % 20 < 10 else 7)
            
            c0 = 10 if self.title_cursor == 0 else 5
            pyxel.rectb(40, 45, 80, 15, c0)
            pyxel.text(58, 50, "NEW GAME", 7 if self.title_cursor == 0 else 5)
            
            if self.title_cursor == 0:
                limit_text = "< LIMIT 50000: ON >" if self.use_limit else "< LIMIT 50000: OFF >"
                pyxel.text(32, 65, limit_text, 10 if self.timer % 10 < 5 else 7)
            
            if self.has_save:
                c1 = 10 if self.title_cursor == 1 else 5
                pyxel.rectb(40, 80, 80, 15, c1)
                pyxel.text(60, 85, "CONTINUE", 7 if self.title_cursor == 1 else 5)
            else:
                pyxel.rectb(40, 80, 80, 15, 1)
                pyxel.text(60, 85, "CONTINUE", 1)
            return

        if self.state == STATE_SP_CHANCE: pyxel.cls(0)
        elif self.state == STATE_SP_REACH:
            if self.sp_type == 1: pyxel.cls(11)
            elif self.sp_type == 2: pyxel.cls(8) 
            elif self.sp_type == 4: pyxel.cls(2) 
            elif self.sp_type == 5: pyxel.cls(12) 
            elif self.sp_type == 6: pyxel.cls(14) 
            elif self.sp_type == 7: pyxel.cls(5 if self.timer % 10 < 5 else 1) 
            elif self.sp_type == 8: pyxel.cls(10 if self.timer % 30 < 3 else 1) 
            else: pyxel.cls(10)                  
        elif self.state in [STATE_WIN, STATE_PREMIUM_FLASH, STATE_ZENKAITEN, STATE_CLEAR] or (self.state == STATE_REACH and self.is_premium):
            colors = [8, 9, 10, 11, 12, 14, 8]
            pyxel.cls(colors[(self.timer // 10) % len(colors)])
        elif self.state in [STATE_REVIVAL, STATE_PROMOTION]:
            pyxel.cls(10 if self.timer % 20 < 10 else 9)
        elif self.state in [STATE_SP9_EVOLVE, STATE_SP9_REACH]:
            pyxel.cls(1) 
        elif self.is_super_kakuken:
            pyxel.cls(2) 
        elif self.is_kakuken:
            pyxel.cls(8) 
        else:
            pyxel.cls(1) 

        if self.state in [STATE_SPIN_ALL, STATE_SPIN_OUTER] and self.yokoku_color != 0:
            if self.timer % 16 < 8:
                pyxel.rectb(0, 0, 160, 120, self.yokoku_color)
                pyxel.rectb(1, 1, 158, 118, self.yokoku_color)
                
        if self.state in [STATE_SPIN_ALL, STATE_SPIN_OUTER] and self.is_chance_text:
            pyxel.text(62, 55, "CHANCE!!", 9 if self.timer % 4 < 2 else 10)

        colors = [8, 9, 10, 11, 12, 14]
        c = colors[(self.timer // 5) % len(colors)]
        
        if self.is_super_kakuken: pyxel.text(2, 2, "SUPER KAKUKEN RUSH!!", c)
        elif self.is_kakuken: pyxel.text(2, 2, "KAKUKEN MODE", 10 if self.timer % 10 < 5 else 7)
        elif self.st_count > 0: pyxel.text(2, 2, f"ST CHANCE: {self.st_count}", 11)

        if self.renchan > 0 and self.state not in [STATE_CLEAR, STATE_RANKING]:
            pyxel.text(62, 90, f"{self.renchan} RENCHAN!!", 10 if self.timer % 10 < 5 else 7)
            
        if self.state not in [STATE_CLEAR, STATE_RANKING]:
            pyxel.text(115, 2, f"TOTAL:{self.total_spins}", 7)
            
        if self.state == STATE_IDLE:
            is_free_spin = self.is_kakuken or self.is_super_kakuken
            cost_text = "FREE!" if is_free_spin else "-10 PT"
            
            if self.is_auto:
                pyxel.text(40, 103, f"AUTO PLAY ({cost_text})", 10 if self.timer % 10 < 5 else 7)
            else:
                if not is_free_spin and self.score < 10:
                    pyxel.text(40, 103, "NO POINTS...", 8 if self.timer % 10 < 5 else 7)
                else:
                    pyxel.text(40, 103, f"TAP TO SPIN ({cost_text})", 7)
                
            if self.force_mode != 0:
                pyxel.rect(0, 103, 40, 7, 0)
                pyxel.text(2, 104, self.force_names[self.force_mode], 10 if self.timer % 16 < 8 else 7)
            else:
                pyxel.text(2, 104, "[UP] DBG", 13)
                
            if self.guarantee_kakuken:
                pyxel.text(40, 93, "NEXT: 100% FEVER!!", 10 if self.timer % 4 < 2 else 9)
                
        elif self.state == STATE_REACH:
            col = 10 if not self.is_premium else [8,9,10,11,12][(self.timer//5)%5]
            if self.is_lucky_reach:
                reach_text = "DOUBLE LUCKY!" if self.is_double_reach else "LUCKY!"
                col = 9 if self.timer % 4 < 2 else 10
            else:
                reach_text = "DOUBLE REACH!" if self.is_double_reach else "REACH!"
            pyxel.text(62 if self.is_double_reach else 68, 22, reach_text, col)
            
        elif self.state == STATE_SLIP: pyxel.text(66, 22, "SLIP..!", 11)
        elif self.state == STATE_SP_CHANCE: pyxel.text(55, 55, ">>>> EVOLUTION <<<<", 7)
        elif self.state == STATE_SP_REACH:
            if self.sp_type == 7:
                pyxel.text(68, 14, "SUPER!", 10 if self.timer % 4 < 2 else 7)
                pyxel.text(60, 22, "[CROSS FIRE]", 10 if self.timer % 4 < 2 else 7)
            elif self.sp_type == 8:
                pyxel.text(68, 14, "SUPER!", 10 if self.timer % 8 < 4 else 7)
                pyxel.text(64, 22, "[THUNDER]", 10 if self.timer % 8 < 4 else 7)
            else:
                pyxel.text(68, 22, "SUPER!", 10 if self.timer % 4 < 2 else 7)
                
        elif self.state == STATE_SP9_EVOLVE:
            pyxel.text(60, 55, "STAY...?!", 7)
        elif self.state == STATE_SP9_REACH:
            pyxel.text(55, 22, "REVERSE RUSH!!", 10 if self.timer % 8 < 4 else 7)
            
        elif self.state == STATE_ZENKAITEN:
            pyxel.text(50, 22, "SUPER LUCKY!!", 0)
        elif self.state == STATE_PROMOTION:
            pyxel.text(35, 22, ">>> PROMOTION CHANCE!! <<<", 7)
        elif self.state == STATE_WIN:
            for j, char in enumerate("FEVER!!"):
                char_y = 20 + int(math.sin(self.timer * 0.15 + j) * 4)
                pyxel.text(65 + j * 5, char_y, char, 10 if self.timer % 8 < 4 else 7)
        elif self.state == STATE_ROULETTE:
            pyxel.text(50, 22, "BONUS ROULETTE!", 10)
            if self.is_all_five:
                pyxel.text(40, 85, "ALL 5 MATCH = x2 POINTS!!", 10 if self.timer % 10 < 5 else 7)
            box_x, box_y, box_w, box_h = 45, 40, 70, 40
            pyxel.rect(box_x, box_y, box_w, box_h, 0)
            pyxel.clip(box_x, box_y, box_w, box_h)
            for i in range(-2, 3):
                idx = (self.roulette_idx - i) % len(self.active_roulette_data)
                pt, col = self.active_roulette_data[idx]
                y_draw = box_y + 17 + i * 20 + int(self.roulette_y)
                text_str = f"{pt} PT"
                pyxel.text(box_x + 35 - len(text_str) * 2, y_draw, text_str, col)
            pyxel.clip()
            pyxel.rectb(box_x - 2, box_y - 2, box_w + 4, box_h + 4, 13)
            pyxel.tri(box_x - 6, box_y + 20, box_x - 2, box_y + 18, box_x - 2, box_y + 22, 8)
            pyxel.tri(box_x + box_w + 6, box_y + 20, box_x + box_w + 2, box_y + 18, box_x + box_w + 2, box_y + 22, 8)

        elif self.state == STATE_ROULETTE_STOP:
            pyxel.text(50, 22, "BONUS ROULETTE!", 10)
            box_x, box_y, box_w, box_h = 45, 40, 70, 40
            pyxel.rect(box_x, box_y, box_w, box_h, 0)
            pt, base_col = self.active_roulette_data[self.roulette_idx]
            
            mult_str = " x2" if self.is_all_five else ""
            text_str = f"{pt}{mult_str} = {self.won_pt} PT!!"
            
            jump = int(math.sin(self.timer * 0.3) * 5)
            col = base_col if self.timer % 6 < 3 else 7 
            text_x = box_x + (box_w - len(text_str) * 4) // 2
            pyxel.text(text_x, box_y + 17 + jump, text_str, col)
            pyxel.rectb(box_x - 2, box_y - 2, box_w + 4, box_h + 4, 10 if self.timer % 8 < 4 else 13)

        elif self.state in [STATE_LOSE, STATE_REVIVAL_WAIT]:
            pyxel.text(70, 22, "END", 13)
        elif self.state == STATE_REVIVAL:
            pyxel.text(45, 22, ">>> REVIVAL!! <<<", 7)
            
        elif self.state == STATE_CLEAR:
            pyxel.text(35, 30, "CONGRATULATIONS!!", 10 if self.timer % 10 < 5 else 7)
            pyxel.text(35, 50, "50000 PT REACHED!", 9)
            pyxel.text(35, 75, f"TOTAL SPINS : {self.total_spins}", 11)
            if self.timer > 60:
                pyxel.text(45, 100, "- TAP TO NEXT -", 7)
                
        elif self.state == STATE_RANKING:
            pyxel.text(50, 15, "--- RANKING ---", 10)
            for i, r_spins in enumerate(self.ranking):
                pyxel.text(40, 35 + i * 12, f"RANK {i+1} : {r_spins} SPINS", 7)
            pyxel.text(30, 100, "TAP TO TITLE", 7)

        if self.state not in [STATE_CLEAR, STATE_RANKING]:
            pyxel.rect(0, 110, 160, 10, 0)
            pyxel.text(2, 112, f"SPIN:{self.spins}", 7)
            pyxel.text(45, 112, f"WINS:{self.wins}", 10)
            pyxel.text(85, 112, f"PT:{self.score}", 11)
            
            btn_bg = 10 if self.is_auto else 5
            btn_fg = 0 if self.is_auto else 7
            pyxel.rect(125, 110, 33, 9, btn_bg)
            pyxel.text(131, 112, "AUTO", btn_fg)
            if self.is_auto and self.timer % 20 < 10:
                pyxel.rectb(125, 110, 33, 9, 7)

        if self.state not in [STATE_ROULETTE, STATE_ROULETTE_STOP, STATE_CLEAR, STATE_RANKING]:
            col1 = 10 if self.timer % 4 < 2 else 9
            col2 = 11 if self.timer % 4 < 2 else 3
            
            is_reach1 = (self.targets[0] == self.targets[4] and self.state >= STATE_REACH) or self.state in [STATE_SP9_EVOLVE, STATE_SP9_REACH]
            is_reach2 = (self.targets[1] == self.targets[3] and self.state >= STATE_REACH) or self.state in [STATE_SP9_EVOLVE, STATE_SP9_REACH]
            
            c1 = col1 if is_reach1 or self.state == STATE_WIN else 13
            c2 = col2 if is_reach2 or self.state == STATE_WIN else 13
            
            pyxel.line(36, 32, 124, 84, c1)
            pyxel.line(124, 32, 36, 84, c2)

            for i in range(5):
                x, y_base = self.reel_coords[i]
                w = 32
                h = 48
                
                pyxel.rect(x, y_base, w, h, 0)
                pyxel.clip(x, y_base, w, h)
                
                current_num = self.reels[i]
                
                step_val = 1
                if self.is_super_kakuken:
                    if all(t in [0,2,4,6,8] for t in self.targets):
                        step_val = 2
                        
                next_num = (current_num + step_val) % 10
                scroll_y = int(self.reel_y[i] * 4)
                
                if self.premium_type == 2 and self.state not in [STATE_WIN_PAUSE, STATE_WIN]:
                    current_num, next_num = 6, 6
                if self.premium_type == 3 and self.state == STATE_SP_REACH and i == 2:
                    current_num, next_num = self.targets[2], self.targets[2]
                
                jump_offset = 0
                if self.state == STATE_WIN:
                    jump_offset = int(math.sin(self.timer * 0.2 + i * 1.5) * 6)
                    
                scale_val = 4.0
                if self.state == STATE_SP_REACH and i == 2:
                    if self.sp_type == 6: scale_val = 4.0 + math.sin(self.timer * 0.1) * 1.2
                    elif self.sp_type == 5: scale_val = 4.0 + math.sin(self.timer * 0.1) * 0.8
                    elif self.sp_type == 4: scale_val = 4.0 + math.sin(self.timer * 0.15) * 0.6
                    elif self.sp_type == 8: scale_val = 4.0 + math.sin(self.timer * 0.3) * 1.0 
                    elif self.sp_type == 7: scale_val = 4.0 + math.sin(self.timer * 0.2) * 0.5 
                    else: scale_val = 4.0 + math.sin(self.timer * 0.1) * 0.4
                elif self.state == STATE_SP9_REACH and i != 2:
                    scale_val = 4.0 + math.sin(self.timer * 0.2) * 0.5
                
                draw_x = x + 12
                draw_y = y_base + scroll_y + 22 + jump_offset
                
                self.draw_colored_number(current_num, draw_x, draw_y, scale_val)
                self.draw_colored_number(next_num, draw_x, draw_y - 48, scale_val)
                
                pyxel.clip()
                border_col = 10 if (self.state in [STATE_WIN, STATE_ZENKAITEN, STATE_REVIVAL, STATE_PROMOTION] and self.timer % 16 < 8) else 13
                pyxel.rectb(x - 2, y_base - 2, w + 4, h + 4, border_col)

PachinkoGame()