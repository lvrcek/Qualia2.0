# -*- coding: utf-8 -*- 
from ..core import *
from ..util import download_progress
from ..autograd import Tensor
import os

class DataLoader(object):
    def __init__(self):
        self.training = True 
        self.train_data = None
        self.train_label = None
        self.test_data = None
        self.test_label = None
        self.batch = 1
        print('[*] preparing data...')
        print('    this might take few minutes.') 

    def __repr__(self):
        print('{}'.format(self.__class__.__name__))
        
    def __str__(self):
        return self.__class__.__name__
    
    def __len__(self):
        if self.training:
            return self.train_data.shape[0] // self.batch
        else:
            return self.test_data.shape[0] // self.batch

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.training:
            return self._itr(self.train_data, self.train_label)
        else:
            return self._itr(self.test_data, self.test_label)
            
    def _itr(self, data, label):
        if len(self) <= self.idx:
            self.idx = 0
            self.shuffle()
            raise StopIteration
        if label is not None:
            features = data[self.idx*self.batch:(self.idx+1)*self.batch]
            target = label[self.idx*self.batch:(self.idx+1)*self.batch]
            self.idx += 1
            return Tensor(features, requires_grad=False), Tensor(target, requires_grad=False)
        else:
            features = data[self.idx*self.batch:(self.idx+1)*self.batch]
            self.idx += 1
            return Tensor(features, requires_grad=False)
    
    def download(self, url, filename=None):
        
        if not os.path.exists(home_dir + '/data/download/{}/'.format(self.__class__.__name__.lower())):  
            os.makedirs(home_dir + '/data/download/{}/'.format(self.__class__.__name__.lower())) 
        data_dir = home_dir+'/data/download/{}'.format(self.__class__.__name__.lower())
        if filename is None:
            from urllib.parse import urlparse
            parts = urlparse(url)
            filename = os.path.basename(parts.path)
        cache = os.path.join(data_dir, filename)
        if not os.path.exists(cache): 
            from urllib.request import urlretrieve
            urlretrieve(url, cache, reporthook=download_progress) 

    def extract(filename):
        data_dir = home_dir+'/data/download/{}'.format(self.__class__.__name__.lower())
        cache = os.path.join(data_dir, filename)
        if '.tar.gz' in filename:
            import tarfile
            tarfile.open(cache, 'r:gz').extractall(data_dir+'/')
        elif '.zip' in filename:
            import zipfile
            zipfile.ZipFile(cache).extractall(data_dir+'/')
        else:
            raise Exception('[*] not supported extension')
            
    def shuffle(self):
        if self.training:
            self.train_data, self.train_label = self._shuffle(self.train_data, self.train_label)
        else:
            self.test_data, self.test_label = self._shuffle(self.test_data, self.test_label)
    
    def _shuffle(self, data, label):
        i = np.random.permutation(data.shape[0])
        new_data = data[i]
        if label is not None:
            new_label = label[i]    
        else:
            new_label = None
        return new_data, new_label

    def show(self):
        raise NotImplementedError

    @staticmethod
    def to_one_hot(label, num_class):
        if isinstance(label, Tensor):
            one_hot = np.zeros((len(label.data), num_class), dtype=np.int32)    
        else:
            one_hot = np.zeros((len(label), num_class), dtype=np.int32)
        for c in range(num_class):
            one_hot[:,c][label==c] = 1
        return one_hot

    @staticmethod
    def to_vector(label):
        if isinstance(label, Tensor):
            return np.argmax(label.data, axis=1)
        else:
            return np.argmax(label, axis=1)
        
class ImageLoader(DataLoader):
    @property
    def shape(self):
        assert self.train_data is not None
        return self.train_data[0].shape
    
    @staticmethod
    def horizontal_flip(image):
        image = image[:, :, :, ::-1]
        return image

    @staticmethod
    def vertical_flip(image):
        image = image[:, :, ::-1, :]
        return image
