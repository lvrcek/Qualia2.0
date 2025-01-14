# -*- coding: utf-8 -*-
from ..core import *
from .memory import Experience, PrioritizedMemory
import matplotlib.pyplot as plt
from logging import getLogger
logger = getLogger('QualiaLogger').getChild('rl')

class Trainer(object):
    ''' Trainer for RL agent\n
    Args:
        memory (deque): replay memory object
        capacity (int): capacity of the memory
        batch (int): batch size for training
        gamma (int): gamma value
    '''
    def __init__(self, memory, batch, capacity, gamma):
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
    
    def before_train(self, env, agent):
        self.env_name = str(env)
        self.agent_name = str(agent)
    
    def before_episode(self, env, agent):
        return env.reset(), False, 0

    def train_routine(self, env, agent, episodes=200, render=False, filename=None):
        for episode in range(episodes):
            state, done, steps = self.before_episode(env, agent)
            tmp_loss = []
            tmp_reward = []
            actions_dbg = []
            while not done:
                if render and (episode+1)%10==0:
                    env.render()
                action = agent(state)
                actions_dbg.append(action)
                next, reward, done, _ = env.step(action)
                self.memory.append(Experience(state, next, reward, action, done))
                if len(self.memory) > self.batch:
                    tmp_loss.append(self.experience_replay(episode, steps, agent))
                tmp_reward.append(reward.data[0])                
                state = next
                steps += 1
            if render and (episode+1)%10==0:
                env.close()
            self.after_episode(episode+1, steps, agent, tmp_loss, tmp_reward, filename)

    def experience_replay(self, episode, step_count, agent):
        experience, idx, weights = self.memory.sample(self.batch)
        action_value, target_action_value = agent.get_train_signal(experience, self.gamma)
        if isinstance(self.memory, PrioritizedMemory):
            priorities = np.abs(target_action_value.data.reshape(-1) - action_value.data.reshape(-1) + 1e-5)**weights
            self.memory.update_priorities(idx, priorities)
        loss = agent.update(action_value, target_action_value)
        return loss

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

    def after_train(self):
        logger.info('[*] training finished with best score: {}'.format(max(self.rewards)))
    
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
