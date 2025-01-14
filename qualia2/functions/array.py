# -*- coding: utf-8 -*- 
from ..core import *
from ..autograd import *

gather = Gather(None)
reshape = Reshape(None)
transpose = Transpose(None)
squeeze = Squeeze(None)
expand_dims = Expand_dims(None)

class ListConcat(Function):
    '''
    Concatenate list of Tensors 
    '''
    @staticmethod
    def forward(list):
        result = Tensor(np.concatenate([np.expand_dims(arr.data, axis=0) for arr in list], axis=0))
        result.set_creator(ListConcat.prepare(result.shape, *list))
        return result
    
    def calc_grad(self, dx):
        result = np.split(dx, len(self.var))
        return [np.squeeze(r, axis=0) for r in result]

listconcat = ListConcat(None)

class Concat(Function):
    @staticmethod
    def forward(*args, axis=1):
        result = Tensor(np.concatenate(tuple(i.data for i in args), axis)) 
        result.set_creator(Concat.prepare(result.shape, *args, axis=axis))
        return result

    def calc_grad(self, dx):
        s = [i.shape[self.kwargs['axis']] for i in self.var]
        split = [sum([s[n] for n in range(i+1)]) for i in range(len(s)-1)]
        result = np.split(dx, split, axis=self.kwargs['axis'])
        return result

concat = Concat(None)
concatenate = Concat(None)
