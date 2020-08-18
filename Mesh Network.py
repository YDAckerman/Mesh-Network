# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 22:33:18 2020

@author": nnicholson
"""

#import everything
import os, pygame, sys, random
from pygame.locals import *

#EDIT THESE VALUES
settings = {
    'signalSpeed':5, #Each signal will propagate at the rate of 1 pixel per n frames. Lower = faster
    'signalTTL':15, #Max number of times a signal will be relayed
    'signalStrength':350, #Pixel radius a signal can reach before it decays
    'startingNodeCount':30, #Number of nodes in the network (will be randomly distributed in space)
    'nodeSize':20, #Pixel height and width of the squares representing each node
    'colorPalette': [(90, 125, 124),(243, 222, 138),(235,148,134),(127, 176, 105),(74,111,165)], #Colors to pick from
    'screenWidth':1200, #Pygame window width
    'screenHeight':1100} #Pygame window height


#Network class that will handle the main loop and contain nodes and signals
class Network:
    def __init__(self,settings):
        self.running = False
        self.nodeList = []
        self.signalList = []
        self.IDincrementers = {'Node':0,'Signal':0}
        self.colorPalette = settings['colorPalette']
        self.screenWidth = settings['screenWidth']
        self.screenHeight = settings['screenHeight']
        self.signalSpeed = settings['signalSpeed']
        self.signalTTL = settings['signalTTL']
        self.signalStrength = settings['signalStrength']
        self.startingNodeCount = settings['startingNodeCount']
        self.nodeSize = settings['nodeSize']
    
    def run(self):
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        background = pygame.Surface((self.screenWidth,self.screenHeight))
        background.fill((0,0,0))
        self.screen.blit(background, (0, 0))
        for i in range(self.startingNodeCount):
            node = Node(myNetwork,myNetwork.generateID('Node'),['colorchange'])
            node.setDimensions(random.randint(50,self.screenWidth-50),random.randint(50, self.screenHeight-50),self.nodeSize,self.nodeSize)
            node.setColor((255,255,255))
            self.addNode(node)
        while self.running:
            self.screen.blit(background, (0, 0))
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX = pygame.mouse.get_pos()[0]
                    mouseY = pygame.mouse.get_pos()[1]
                    if event.button == 1:
                        node = Node(myNetwork,myNetwork.generateID('Node'),['colorchange'])
                        node.setDimensions(mouseX, mouseY,self.nodeSize,self.nodeSize)
                        node.setColor((255,255,255))
                        self.addNode(node)
                    elif event.button == 3:
                        mouseRect = pygame.Rect(mouseX,mouseY, self.nodeSize, self.nodeSize)
                        for node in self.nodeList:
                            if pygame.Rect.colliderect(node.rect, mouseRect):
                                node.kill()
            if self.signalList == [] and self.nodeList != []:
                newColor = random.choice(self.colorPalette)
                newSignal = random.choice(self.nodeList).createSignal(['colorchange'], newColor, color=newColor)
                self.signalList.append(newSignal)
            for signal in self.signalList:
                signal.propagate()
                signal.draw(self.screen)
                
            for node in self.nodeList:
                node.draw(self.screen)
                
            self.cleanUp()
            pygame.display.update()
            
        pygame.quit()
                
    def addNode(self,node):
        self.nodeList.append(node)
        
    def addSignal(self,signal):
        self.signalList.append(signal)
        
    def generateID(self,type):
        self.IDincrementers[type] += 1
        return self.IDincrementers[type]
    
    def cleanUp(self):
        self.signalList = [signal for signal in self.signalList if signal.alive]
        self.nodeList = [node for node in self.nodeList if node.alive]
        
    def randomColor(self):
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    
#Node class that relays and processes signals according to managed-flood principles
#In this version, all nodes are subscribed to the single address 'colorchange', and all signals send to that address   
class Node:
    def __init__(self,network,ID,subscriptionList):
        self.network = network
        self.ID = ID
        self.subscriptionList = subscriptionList
        self.cache = []
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.color = (0,0,0)
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)
        self.alive = True
        
    def receiveSignal(self,signal):
        subscribes = False
        if signal.ID not in self.cache:
            signal.decrementTTL()
            self.relaySignal(signal)
            self.cache.append(signal.ID)
            for address in signal.addressList:
                if address in self.subscriptionList:
                    subscribes = True
            if subscribes:
                self.processSignal(signal)
                
    def processSignal(self,signal):
        self.setColor(signal.colorInstruction)
                                
    def relaySignal(self,signal):
        relayedSignal = Signal(signal.network, 
                               signal.ID, 
                               self, 
                               signal.addressList,
                               signal.colorInstruction, 
                               TTL = signal.TTL, 
                               strength = self.network.signalStrength,
                               speed = self.network.signalSpeed,
                               color = signal.color)
        self.network.addSignal(relayedSignal)
        
    def createSignal(self, addressList, colorInstruction,color):
        signal = Signal(self.network, 
                        self.network.generateID('Signal'), 
                        self, 
                        ['colorchange'],
                        colorInstruction,
                        TTL = self.network.signalTTL, 
                        strength = self.network.signalStrength,
                        speed = self.network.signalSpeed,
                        color = color)
        self.cache.append(signal.ID)
        return signal
                
    def setDimensions(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def setColor(self, color):
        self.color = color;
        
    def draw(self,screen):
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)
        pygame.draw.rect(screen, self.color, self.rect)
        
    def kill(self):
        self.alive = False
        
        
#Signal class that propagates at speed and alerts nodes when it touches them        
class Signal:
    def __init__(self, network, ID, originNode, addressList, colorInstruction, TTL = 10,strength=300,speed = 8,color = (0,0,0)):
        self.network = network
        self.ID = ID
        self.addressList = addressList
        self.color = color
        self.colorInstruction = colorInstruction
        self.alive = True
        self.originNode = originNode
        self.x = originNode.x + originNode.width//2
        self.y = originNode.y + originNode.height//2
        self.radius = 10
        self.rect = pygame.Rect(self.x, self.y,self.radius,self.radius)
        self.TTL = TTL
        self.strength = strength
        self.speed = speed #lower is faster
        self.speedCounter = 0
        
    def setID(self,ID):
        self.ID = ID
        
    def setColor(self, color):
        self.color = color
        
    def setColorInstruction(self,color):
        self.colorInstruction = color
        
    def propagate(self):
        self.speedCounter += 1
        if self.speedCounter >= self.speed:
            self.speedCounter = 0
            self.radius += 1
            self.rect = pygame.Rect(self.x-self.radius, self.y-self.radius,self.radius*2,self.radius*2)
            for node in [node for node in self.network.nodeList]:
                if pygame.Rect.colliderect(self.rect, node.rect):
                    node.receiveSignal(self)
            if self.radius >= self.strength or self.TTL <= 0:
                self.kill()
                
        
    def decrementTTL(self):
        self.TTL -= 1
    
    def draw(self,screen):
        pygame.draw.circle(screen, self.color, (self.x,self.y), self.radius,min(self.radius,1))
        
    def kill(self):
        self.alive = False
        

myNetwork = Network(settings)
myNetwork.run()