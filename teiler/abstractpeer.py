from abc import abstractmethod

class AbstractPeer:
    
    # __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, id, name, address, port):
        ''' Have a constructor with these parameters '''
        
    @abstractmethod
    def __str__(self):
        ''' return self.id '''

    @abstractmethod
    def __eq__(self, other):
        """needed to be able to remove items from peers form the list"""
        ''' Should be like:
        if self.id == other.id:
            if self.address == other.address:
                if self.port == other.port:
                    return True
        return False
        '''
