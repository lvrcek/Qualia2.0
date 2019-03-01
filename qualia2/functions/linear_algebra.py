# -*- coding: utf-8 -*- 
from ..core import *
from ..autograd import *

matmul = Matmul(None)

class Tensordot(Function):
    def __init__(self, output_shape, *args, **kwargs):
        super().__init__(output_shape, *args, **kwargs)
        self.need_transpose = None
        self.tp_a = None
        self.tp_b = None
        self.rev_a = None
        self.rev_b = None
        self.rev_c = None
 
    @staticmethod
    def forward(a, b, axes=1):
        result = Tensor(np.tensordot(a.data, b.data, axes=axes)) 
        result.set_creator(Tensordot.prepare(result.shape,a,b,axes=axes))
        return result

    def calc_grad(self, dx):
        if self.need_transpose is None:
            self.need_transpose = False 
            if type(self.kwargs['axes']) is tuple: 
                self.need_transpose = True 
                if type(self.kwargs['axes'][0]) is int: 
                    self.kwargs['axes'] = ((self.kwargs['axes'][0],),(self.kwargs['axes'][1],)) 
                self.tp_a = [i for i in range(len(self.var[0].shape)) if i not in self.kwargs['axes'][0]] + list(self.kwargs['axes'][0]) 
                self.tp_b = list(self.kwargs['axes'][1]) + [i for i in range(len(self.var[1].shape)) if i not in self.kwargs['axes'][1]] 
                self.kwargs['axes'] = len(self.kwargs['axes'][0]) 
            self.rev_b = [i for i in range(len(self.var[1].shape))][self.kwargs['axes']:] 
            self.rev_a = [i for i in range(len(self.var[0].shape))][:-self.kwargs['axes']] 
            self.rev_c = [i for i in range(len(dx.shape))][-len(self.rev_b):]

        if not self.need_transpose: 
            da = np.tensordot(dx, self.var[1].data, axes=(self.rev_c,self.rev_b))  
        else: 
            result = np.tensordot(dx, np.transpose(self.var[1].data, self.tp_b), axes=(self.rev_c,self.rev_b)) 
            da = np.transpose(result, [tuple(self.tp_a).index(i) for i in range(len(self.tp_a))])
        
        if not self.need_transpose: 
            db = np.tensordot(self.var[0].data, dx, axes=(self.rev_a,self.rev_a))  
        else: 
            result = np.tensordot(np.transpose(self.var[0].data,self.tp_a), dx, axes=(self.rev_a,self.rev_a)) 
            db = np.transpose(result, [tuple(self.tp_b).index(i) for i in range(len(self.tp_b))])
        return da, db

tensordot = Tensordot(None)

def linear(x, weight, bias=None): 
    tmp = tensordot(x, weight, axes=1) 
    if bias is not None:
        return tmp + bias
    return tmp 