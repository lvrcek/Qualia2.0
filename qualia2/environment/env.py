# -*- coding: utf-8 -*- 
from ..util import progressbar
import gym
import os
import matplotlib.pyplot as plt
from matplotlib import animation 
from logging import getLogger
logger = getLogger('QualiaLogger').getChild('env')

class Environment(object):
    '''Environment\n
    Wrapper class of gym.env for reinforcement learning.
    '''
    def __init__(self, env, agent, max_step, max_episodes):
        self.env = gym.make(env)
        self.env.reset()
        self.num_states = self.env.observation_space.shape[0]
        self.num_actions = self.env.action_space.n
        self.agent = agent
        self.max_steps = max_step
        self.max_episodes = max_episodes
        self.frames = []
        self.rewards = []
        self.path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(self.path + '/tmp/'): 
            os.makedirs(self.path + '/tmp/')
    
    def run(self):
        raise NotImplementedError

    def show(self):
        self.frames = []
        self.env.reset()
        for _ in range(200):
            self.env.render()
            self.env.step(self.env.action_space.sample())
            self.frames.append(self.env.render(mode='rgb_array'))
    
    def animate(self, filename):
        plt.clf()
        plt.figure(figsize=(self.frames[0].shape[1]/72.0, self.frames[0].shape[0]/72.0), dpi=72)
        result = plt.imshow(self.frames[0])
        plt.axis('off')
        video = animation.FuncAnimation(plt.gcf(), lambda t: result.set_data(self.frames[t]), frames=len(self.frames), interval=50)
        video.save(filename+'.mp4')
        plt.close()

    def simulate(self):
        self.frames = []
        state = self.env.reset()
        for step in range(self.max_steps):
            action = self.agent(state, 1e6, self.num_actions)
            nextstate, _, done, _ = self.env.step(int(action[0]))    
            state = nextstate
            self.frames.append(self.env.render(mode='rgb_array'))
            if done:
                break

    def plot_rewards(self):
        plt.clf()
        plt.plot(self.rewards)
        plt.ylabel('scores')
        plt.xlabel('episodes')
        plt.show()
