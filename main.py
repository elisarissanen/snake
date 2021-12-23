import pygame
import random

#####################################
# Ohjelmoinnin jatkokurssi 2021     #
# Elisa Rissanen Osa 12 Oma peli    #
#####################################

# VAIKEUSTASO: Mitä isompi luku, sitä hitaampi mato (default: 10)
vaikeustaso = 10

### Known unsolved issues: ###
# Hedelmät voi spawnata score-ruudun alle: yläruutuun olisi voinut tehdä erillisen pistelaskuri-yläikkunan
# Peli ei ole gridi-pohjalla, joka tuo vähän omanlaisensa fiiliksen - säätöjä voi tehdä vaikeustason, hedelmän hitboxin, ja snaken kasvun mukaan; tarviin gametesterin tähän

class Snake:
    def __init__(self):
        pygame.init()

        # Näytön koko
        ruudun_koko = 12
        sarakkeet = 20
        rivit = 30
        self.naytto_leveys = sarakkeet * ruudun_koko
        self.naytto_korkeus = rivit * ruudun_koko
        self.naytto = pygame.display.set_mode((self.naytto_leveys, self.naytto_korkeus))

        self.kello = pygame.time.Clock()
        self.fontti = pygame.font.SysFont("ebrima", 18)
        pygame.display.set_caption("Snake game")

        self.state = "starting" # game states: starting, playing, gameover
        self.silmukka()

    def silmukka(self):
        while True:
            if self.state == "starting":
                self.start_event()
                self.start_draw()
            elif self.state == "playing":
                self.play_event()
                self.play_draw()
            elif self.state == "gameover":
                self.gameover_event()
                self.gameover_draw()
            self.kello.tick(60)

    # Tuottaa annetusta tekstistä ja sijainnista standardisoidun tekstin
    def piirra_teksti(self, input_teksti, positio, vari):
        teksti = self.fontti.render(input_teksti, True, vari)
        tekstin_koko = teksti.get_size()
        positio[0] = positio[0] - tekstin_koko[0]//2
        positio[1] = positio[1] - tekstin_koko[1]//2
        self.naytto.blit(teksti, positio)

### Aloitusikkuna ###
    def start_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            # Alustaa uuden pelin välilyönnillä
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.new_game()
                self.state = 'playing'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()
    def start_draw(self):
        self.naytto.fill((0,0,0))
        self.piirra_teksti('SNAKE', [self.naytto_leveys/2, self.naytto_korkeus/2 - 25], (0,255,0))
        self.piirra_teksti('PRESS SPACE TO START', [self.naytto_leveys/2, self.naytto_korkeus/2], (255,255,255))
        self.piirra_teksti('SCORE', [self.naytto_leveys/2,10], (255,255,255))
        pygame.display.update()

### Peli ###
    # Alustaa madon määritykset pelin alussa
    def new_game(self):
        self.direction = ""
        self.snake_size = 10
        self.score = 0
        self.x = self.naytto_leveys / 2
        self.y = self.naytto_korkeus / 2
        self.x_speed = 0
        self.y_speed = 0
        # Alustetaan lista, joka seuraa madon pikseleitä
        self.snake_pixel = []
        self.snake_length = 1

        # Randomoidaan targetti (hedelmä) ensimmäisen kerran
        self.target_x = round(random.randrange(0, self.naytto_leveys-self.snake_size) / 10.0) * 10.0
        self.target_y = round(random.randrange(0, self.naytto_korkeus-self.snake_size) / 10.0) * 10.0

    # Pisteiden piirtäminen pelin aikana
    def draw_score(self):
        pisteet = self.score
        self.piirra_teksti('SCORE: ' + str(pisteet), [self.naytto_leveys/2,10], (255,255,255))

    # Piirtää madon
    def draw_snake(self):
        for pixel in self.snake_pixel:
            pygame.draw.rect(self.naytto, (0,255,0), [pixel[0], pixel[1], self.snake_size, self.snake_size])

    def play_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "gameover"
            # Pelaajan näppäinsyötteet, ei anna siirtyä suoraan vastakkaiseen suuntaan (collision suoraan matoon itseensä)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != "right":
                    self.x_speed = -self.snake_size
                    self.y_speed = 0
                    self.direction = "left"
                if event.key == pygame.K_RIGHT and self.direction !="left":
                    self.x_speed = self.snake_size
                    self.y_speed = 0
                    self.direction = "right"
                if event.key == pygame.K_UP and self.direction !="down":
                    self.x_speed = 0
                    self.y_speed = -self.snake_size
                    self.direction = "up"
                if event.key == pygame.K_DOWN and self.direction !="up":
                    self.x_speed = 0
                    self.y_speed = self.snake_size
                    self.direction = "down"

        # Seinään ajamisen tarkistaminen
        if self.x >= self.naytto_leveys or self.x < 0 or self.y >= self.naytto_korkeus or self.y < 0:
            self.state = "gameover"

        # Madon sijainti ja vaikeustason huomiointi
        self.x += self.x_speed/vaikeustaso
        self.y += self.y_speed/vaikeustaso

    def play_draw(self):
        self.naytto.fill((0,0,0))

        # Piirretään targetti
        pygame.draw.rect(self.naytto, (255,165,0), [self.target_x, self.target_y, self.snake_size, self.snake_size])

        # Tarkistetaan jos target löydetty ja pidetään mato oikean pituisena
        self.snake_pixel.append([self.x, self.y])
        if len(self.snake_pixel) > self.snake_length:
            del self.snake_pixel[0]
 
        # Pysäytetään peli, jos mato ajaa itseensä
        # Tarkistetaan, jos madon pää on samassa pikselissä, kuin joku sen muu pikseli ja ajetaan peli game over tilaan
        for pixel in self.snake_pixel[:-1]:
            if self.x == pixel[0] and self.y == pixel[1]:
                self.state = "gameover"
        
        self.draw_snake()
        self.draw_score()

        pygame.display.update()

        # Targetin syöminen, generoidaan uusi random target, lisätään madon pituutta ja lisätään scorea
        s = 3 # hitboxin kokoa pystyy säätämään (default: 3)
        if (self.x >= self.target_x - s and self.x <= self.target_x + s) and (self.y >= self.target_y - s and self.y <= self.target_y + s):
            self.target_x = round(random.randrange(0, self.naytto_leveys-self.snake_size) / 10.0) * 10.0
            self.target_y = round(random.randrange(0, self.naytto_korkeus-self.snake_size) / 10.0) * 10.0
            self.snake_length += 5 # tästä pystyy säätämään madon kasvun määrää (default: 5)
            self.score += 1

### Game over ruutu ###
    def gameover_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            # Uuden pelin alustaminen välilyönnistä
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.new_game()
                self.state = 'playing'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()

    def gameover_draw(self):
        self.naytto.fill((0,0,0))
        self.piirra_teksti('GAME OVER', [self.naytto_leveys/2, self.naytto_korkeus/2 - 25], (255,0, 0))
        self.piirra_teksti('PRESS SPACE TO PLAY AGAIN', [self.naytto_leveys/2, self.naytto_korkeus/2], (255,255,255))
        self.draw_score()
        pygame.display.update()

if __name__ == "__main__":
    Snake()