# -*- coding: utf-8 -*- 
from ..core import *

class Optimizer(object): 
    '''Optimizer base class\n 
    ''' 
    def __init__(self, parameters): 
        self.params = parameters
     
    def step(self): 
        raise NotImplementedError 
    
    def zero_grad(self):
        for i in self.params(): 
            i.grad = None

class SGD(Optimizer):
    '''Implements stochastic gradient descent (optionally with momentum).\n 
    Args:
        params (iterable): iterable of parameters to optimize
        lr (float): learning rate  
        momentum (float): momentum factor Default: 0
        weight_decay (float) – weight decay (L2 penalty) Default: 0
    '''
    def __init__(self, parameters, lr=0.001, momentum=0, weight_decay=0):
        super().__init__(parameters)
        self.lr = lr
        self.m = momentum
        self.l2 = weight_decay
        self.v = {} 

    def step(self):
        for i, var in enumerate(self.params()): 
            if not var.requires_grad:
                continue
            assert var.data.shape == var.grad.shape
            if i not in self.v:  
                self.v[i] = np.zeros_like(var.grad) 
            self.v[i] = self.m * self.v[i] + (1 - self.m) * var.grad 
            var.data -= self.l2 * var.data
            var.data -= self.lr * self.v[i]

class Adadelta(Optimizer):
    '''Implements Adadelta algorithm.\n
    Args:
        parameters (iterable): iterable of parameters to optimize
        lr (float): coefficient that scale delta before it is applied to the parameters. Default: 1.0
        decay_rate (float): coefficient used for computing a running average of squared gradients. Default: 0.9
        eps (flaot): for numerical stability Default: 1e-06
        weight_decay (float): weight decay (L2 penalty) Default: 0

    Reference:
        ADADELTA: An Adaptive Learning Rate Method (https://arxiv.org/abs/1212.5701)
    '''
    def __init__(self, parameters, lr=1.0, decay_rate=0.9, eps=1e-06, weight_decay=0):
        super().__init__(parameters) 
        self.lr = lr
        self.rho = decay_rate 
        self.eps = eps 
        self.g = {} 
        self.u = {} 
        self.l2 = weight_decay
     
    def step(self): 
        for i, var in enumerate(self.params()): 
            if not var.requires_grad:
                continue
            if i not in self.g:
                self.g[i] = np.zeros_like(var.grad) 
            if i not in self.u: 
                self.u[i] = np.zeros_like(var.grad) 
            self.g[i] = self.rho * self.g[i] + (1-self.rho) * var.grad**2 
            update = -np.sqrt(self.u[i]+self.eps) * var.grad / np.sqrt(self.g[i]+self.eps) 
            self.u[i] = self.rho * self.u[i] + (1-self.rho) * update**2 
            var.data -= self.l2 * var.data
            var.data += self.lr * update 

class AdaGrad(Optimizer):
    '''Implements Adagrad algorithm.\n
    Args: 
        parameters (iterable): iterable of parameters to optimize
        lr (float): learning rate Default: 1e-02
        eps (flaot): for numerical stability Default: 1e-08
        weight_decay (float): weight decay (L2 penalty) Default: 0
    '''
    def __init__(self, parameters, lr=0.01, eps=1e-08, weight_decay=0):
        super().__init__(parameters)
        self.lr = lr
        self.eps = eps 
        self.l2 = weight_decay
        self.h = {} 
    
    def step(self): 
        for i, var in enumerate(self.params()): 
            if not var.requires_grad:
                continue
            if i not in self.h:  
                self.h[i] = np.zeros_like(var.grad) 
            self.h[i] += var.grad**2
            var.data -= self.l2 * var.data
            var.data -= self.lr * var.grad / np.sqrt(self.h[i]+self.eps)  

class RMSProp(Optimizer): 
    '''Implements RMSprop algorithm.\n
    Args: 
        parameters (iterable): iterable of parameters to optimize
        lr (float): learning rate Default: 1e-02
        alpha (float): smoothing constant Default: 0.99 
        eps (float): for numerical stability Default: 1e-08
        weight_decay (float): weight decay (L2 penalty) Default: 0
    '''
    def __init__(self, parameters, lr=0.01, alpha=0.99, eps=1e-08, weight_decay=0):
        super().__init__(parameters)
        self.lr = lr 
        self.alpha = alpha 
        self.eps = eps 
        self.h = {} 
        self.l2 = weight_decay
     
    def step(self): 
        for i, var in enumerate(self.params()): 
            if not var.requires_grad:
                continue
            if i not in self.h:  
                self.h[i] = np.zeros_like(var.grad) 
            self.h[i] = self.alpha * self.h[i] + (1-self.alpha) * var.grad**2 
            var.data -= self.l2 * var.data
            var.data -= self.lr * var.grad / np.sqrt(self.h[i]+self.eps) 

class Adam(Optimizer):
    '''Implements Adam algorithm.\n
    Args: 
        parameters (iterable): iterable of parameters to optimize
        lr (float): learning rate Default: 1e-02
        betas (tuple of float): coefficients used for computing running averages of gradient and its square Default: (0.9, 0.999)
        eps (float): for numerical stability Default: 1e-08
        weight_decay (float): weight decay (L2 penalty) Default: 0
    '''
    def __init__(self, parameters, lr=0.001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0):
        super().__init__(parameters)
        self.lr = lr 
        self.betas = betas 
        self.eps = eps 
        self.m = {}
        self.v = {} 
        self.l2 = weight_decay
        self.t = 0
     
    def step(self): 
        self.t += 1
        for i, var in enumerate(self.params()): 
            if not var.requires_grad:
                continue
            if i not in self.m:  
                self.m[i] = np.zeros_like(var.grad) 
            if i not in self.v:  
                self.v[i] = np.zeros_like(var.grad) 
            self.m[i] = self.betas[0] * self.m[i] + (1-self.betas[0]) * var.grad
            self.v[i] = self.betas[1] * self.v[i] + (1-self.betas[1]) * var.grad**2
            m = self.m[i] / (1-self.betas[0]**self.t)
            v = self.v[i] / (1-self.betas[1]**self.t)
            var.data -= self.l2 * var.data
            var.data -= self.lr * m / np.sqrt(v+self.eps) 

class RAdam(Optimizer):
    ''' Rectified Adam \n
    Args: 
        parameters (iterable): iterable of parameters to optimize
        lr (float): learning rate Default: 1e-02
        betas (tuple of float): coefficients used for computing running averages of gradient and its square Default: (0.9, 0.999)
        eps (float): for numerical stability Default: 1e-08
        weight_decay (float): weight decay (L2 penalty) Default: 0
    '''
    def __init__(self, parameters, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0):
        super().__init__(parameters)
        self.lr = lr 
        self.betas = betas 
        self.eps = eps
        self.m = {}
        self.v = {} 
        self.l2 = weight_decay
        self.t = 0
        self.rho = 2/(1-betas[1])-1

    def step(self):
        self.t += 1
        for i, var in enumerate(self.params()): 
            if not var.requires_grad:
                continue
            if i not in self.m:  
                self.m[i] = np.zeros_like(var.grad) 
            if i not in self.v:  
                self.v[i] = np.zeros_like(var.grad) 
            self.m[i] = self.betas[0] * self.m[i] + (1-self.betas[0]) * var.grad
            self.v[i] = self.betas[1] * self.v[i] + (1-self.betas[1]) * var.grad**2
            m = self.m[i] / (1-self.betas[0]**self.t)
            rho = self.rho - 2*self.t*self.betas[1]**self.t/(1-self.betas[1]**self.t)
            if self.t > 4:
                v = np.sqrt(self.v[i]/(1-self.betas[1]**self.t))+self.eps
                r = np.sqrt((rho-4)*(rho-2)*self.rho/((self.rho-4)*(self.rho-2)*rho))
                var.data -= self.l2 * var.data
                var.data -= self.lr * r * m / v 
            else:
                var.data -= self.l2 * var.data
                var.data -= self.lr * m
            
