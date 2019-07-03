# -*- coding: utf-8 -*-
from collections import namedtuple
import matplotlib.pyplot as plt
from logging import getLogger
logger = getLogger('QualiaLogger').getChild('rl')

Experience = namedtuple('Experience', ['state','next','reward','action','done'])

class Trainer(object):
    ''' Trainer \n
    Args:
        memory (deque): replay memory object
        capacity (int): capacity of the memory
        batch (int): batch size for training
        gamma (int): gamma value
    '''
    def __init__(self, memory, batch=50, capacity=1024, gamma=0.9):
        self.batch = batch
        self.capacity = capacity
        self.gamma = gamma
        self.memory = memory(maxlen=capacity)
        self.losses = []
        self.rewards = []

    def __repr__(self):
        print('{}'.format(self.__class__.__name__))

    def train(self, env, model, episodes=200, render=False, filename=None):
        raise NotImplementedError

    def before_episode(self, env, agent):
        return env.reset(), False, 0

    def after_episode(self, episode, steps, agent, loss, reward, filename=None):
        agent.episode_count += 1
        self.rewards.append(sum(reward))
        if len(loss) > 0:
            self.losses.append(sum(loss)/len(loss))
            logger.info('[*] Episode: {} - steps: {} loss: {:.04} reward: {}'.format(episode, steps, self.losses[-1], self.rewards[-1]))
        else:
            logger.info('[*] Episode: {} - steps: {} loss: ---- reward: {}'.format(episode, steps, self.rewards[-1]))
        
        if filename is not None:
            if len(self.rewards) > 2:
                if self.rewards[-1] >= max(self.rewards[:-2]):
                    agent.save(filename) 
    
    def before_train(self, env, agent):
        self.env_name = str(env)
        self.agent_name = str(agent)

    def train_routine(self, env, agent, episodes=200, render=False, filename=None):
        for episode in range(episodes):
            state, done, steps = self.before_episode(env, agent)
            tmp_loss = []
            tmp_reward = []
            while not done:
                if render:
                    env.render()
                action = agent.policy(state)
                next, reward, done, info = env.step(action)
                experience = Experience(state, next, reward, action, done)
                self.memory.append(experience)
                if len(self.memory) > self.batch:
                    tmp_loss.append(self.experience_replay(episode, steps, agent))
                tmp_reward.append(reward.data[0])                
                state = next
                steps += 1
            self.after_episode(episode+1, steps, agent, tmp_loss, tmp_reward, filename)

    def experience_replay(self, episode, step_count, agent):
        return agent.update(self.memory.sample(self.batch), self.gamma)
    
    def plot(self, filename=None):
        plt.subplot(2, 1, 1)
        plt.plot([i for i in range(len(self.losses))], self.losses)
        plt.title('training losses and rewards of {} agent in {} task'.format(self.agent_name, self.env_name))
        plt.ylabel('episode average loss')
        plt.subplot(2, 1, 2)
        plt.plot([i for i in range(len(self.rewards))], self.rewards)
        plt.xlabel('episodes')
        plt.ylabel('episode reward')
        plt.show()
        if filename is not None:
            plt.savefig(filename)