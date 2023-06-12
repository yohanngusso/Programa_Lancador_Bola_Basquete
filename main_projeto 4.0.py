from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.base import runTouchApp
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty
from kivy.vector import Vector as Vec
from math import *
from kivy.core.audio import SoundLoader
from kivy.properties import StringProperty
import random

#Classe da bola
class Bola(Widget):

    estado = StringProperty("pronta")
    
    #construtor
    def __init__(self, **kwargs):
        super(Bola, self).__init__(**kwargs)
        #a bola tem o som de quicar
        self.som_quica = SoundLoader.load('./som_quica.wav')

    #define o estado inicial da bola
    def setEstadoInicial(self, x0, y0, cesta):
        self._x = x0
        self.x0 = x0
        self._y = y0
        self.y0 = y0
        self.v0 = 0
        self.pos = x0,y0
        self.theta = 0
        self.estado = "pronta" #estado inicial (vide diagrama de estado da bola)
        self.cesta = cesta
        self.raio = self.width / 2
        self.sentido = 'direita'
        
    #avisa o root que a bola mudou de estado
    def on_estado(self, instancia, valor):
        App.get_running_app().root.ObservaBola(valor)
        
    #move a bola
    def mover(self, velocidade, theta):
        #define a velocidade inicial e o angulo inicial da bola
        self.v0 = velocidade
        self.theta = theta

        #incremento de tempo (em segundos)
        self.dt = 5/60
        
        #tempo inicial
        self.t = 0

        #Toca o som (quica a bola)
        self.som_quica.play()
        
        #altera o estado da bola para o movimento
        self.estado = "em movimento"
        
        #para a animação, preciso usar o clock
        Clock.schedule_interval(self.moverIncremental, self.dt)          

    #Funcao callback do Clock para atualizar a posicao da bola
    def moverIncremental(self, dt):
        
        #verifica, com a cesta, se devo parar o movimento
        if (self.cesta.verificaBola(self) == False):
            return False
        
        #calcula nova posicao de x e y
        self._x = self.x0 + self.v0*cos(self.theta)*self.t
        self._y = self.y0 + self.v0*sin(self.theta)*self.t - self.g*self.t*self.t/2

        #Verifica se a bola bate na tabela
        if (self.cesta.verificaBola(self)== "tabela" and self.sentido == "direita"):
            self.sentido="esquerda"

        if self.sentido=="esquerda":
            self._x = Window.width - self.cesta.larguraTabela -(self._x+self.raio*4 - Window.width)
            

        #atribui a nova posição para a bola
        self.pos = Vec(self._x, self._y)
        
        #incrementa o tempo
        self.t = self.t + dt
    
        
#Classe da cesta
class Cesta(Widget):
    
    tolerancia = 20
    offsetX = 50
    offsetY = 33
    larguraTabela = 4
    alturaTabela = 100
    inicioTabela = 350
    
    def posicao(self, x, y):
        self.pos = x, y
        self.alvo = self.pos[0] + self.offsetX, self.pos[1] + self.offsetY
        self.pos_tabela = self.pos[0]+50, self.pos[1]+33
        self.tabela = self.pos_tabela[0] + self.larguraTabela, self.pos_tabela[1] + self.alturaTabela
    
    def verificaBola(self, bola):
        #condições para mudança de estado da bola
        #1. Quando a bola estiver abaixo da posição inicial (_y < y0)
        if bola._y < bola.y0:
            bola.estado = "repouso no chao"
            return False      
        
        #2. Quando a bola estiver sobre a cesta
        if (self.alvo[0] - self.tolerancia < bola._x + bola.raio < self.alvo[0] + self.tolerancia) and (self.alvo[1] - self.tolerancia < bola._y + bola.raio < self.alvo[1] + self.tolerancia):
            bola.estado = "repouso na cesta"
            return False

        #3. Quando a bola bater na tabela
        if (self.tabela[0]<bola._x+bola.raio) and (self.tabela[1]-self.alturaTabela < bola._y+bola.raio<self.tabela[1]):
            bola.estado = "retorno"
            return 'tabela'
            
        
        print("Centro Bola = (", bola._x+bola.raio, ",", bola._y + bola.raio, "), Alvo = ", self.alvo)
        return True
    
#Classe do jogador
class Jogador():
    def lancarBola(self, bola, velocidade, theta):
        
        App.get_running_app().root.IncrementaTentativa()
        
        #jogador lanca a bola
        bola.mover(velocidade, theta)
        

#nova classe, declarada no arquivo Lancador.kv
class Cenario(BoxLayout):
    #Construtor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Tamanho da janela
        Window.size = (400, 600)

        #Configura os sons
        self.som_erro = SoundLoader.load('./som_erro.wav')
        self.som_aplauso = SoundLoader.load('./som_aplauso.wav')
        
        #verifica se está tudo certo com os sons
        if self.som_erro and self.som_aplauso:
            print("Tamanho: som_erro %.3f segundos" % self.som_erro.length)
            print("Tamanho: som_aplauso %.3f segundos" % self.som_aplauso.length)
        
        #cria um jogador
        self.jogador = Jogador()
        
        #inicializa o jogo
        self.inicializar()
      
    # Funcao que controla a gravidade 
    def ControlaGravidade(self):
        if self.ids.spin_id.text == 'Terra(9.8)':
            self.bola.g = 9.81

        if self.ids.spin_id.text == 'Lua(1.6)':
            self.bola.g = 1.6

        if self.ids.spin_id.text == 'Jupiter(24.8)':
            self.bola.g = 24.8
            
        if self.ids.spin_id.text == 'Saturno(10.4)':
            self.bola.g = 10.4
            
    #Funcao para reiniciar o processo
    def inicializar(self):

        self.rand = random.randint(225, 400)

        #posicao inicial da bola
        self.bola.setEstadoInicial(1, 200, self.cesta)

        #posicao inicial da cesta
        self.cesta.posicao(300, self.rand)

        #limpa a mensagem de erro       
        self.ids.mensagem.text = ''

        self.ControlaGravidade()
        
    #o cenário fica em suspense, aguardando que o estado final da bola
    def ObservaBola(self, estadoBola):
        if estadoBola == "repouso na cesta":
            self.ids.mensagem.text = '[color=#0000FF]ACERTOU![/color]'
            #Toca o som (aplauso)
            self.som_aplauso.play()
            self.IncrementaAcerto()
            return False
        if estadoBola == "repouso no chao":
            self.ids.mensagem.text = '[color=#FF0000]ERROU[/color]'
            #Toca o som (erro)
            self.som_erro.play()
            return False
        
    #método disparado pelo on_release do botao
    def LancarClick(self):
        
       #velocidade e angulo inicial
        if float(self.ids.txVel.text) > 0 and float(self.ids.txAng.text) > 0 \
        and float(self.ids.txAng.text) < 90:
        
            v0 = float(self.ids.txVel.text)
            theta = float(self.ids.txAng.text) * pi/180        
        
            #jogador lanca a bola
            self.jogador.lancarBola(self.bola, v0, theta)
        
    #Funcao para sair do aplicativo
    def Sair(self):
        App.get_running_app().stop()

    #Funcao que incrementa todas as tentativas do usuário
    def IncrementaTentativa(self):
        self.ids.txTent.text = str(int(self.ids.txTent.text) + 1)

    #Funcao que incrementa todas os acertos de bola na cesta
    def IncrementaAcerto(self):
        self.ids.txAcertos.text = str(int(self.ids.txAcertos.text) + 1)
        
    #Funcao que controla os sons
    def ControlaSom(self):
        if self.ids.check_som.active:
            self.bola.som_quica.volume=0
            self.som_erro.volume=0
            self.som_aplauso.volume=0
        else:
            self.bola.som_quica.volume = 1
            self.som_erro.volume = 1
            self.som_aplauso.volume = 1

    

        
        
#Classe da aplicacao
class LancadorApp(App):
    # o método build, herdado da classe App, define quais componentes estarão no quadro
    def build(self):
        self.title = 'Lancador de Bolas de Basquete'
        return Cenario()   

#cria uma instancia da aplicação
meuApp = LancadorApp()

#Abre o quadro da aplicacao
meuApp.run()
