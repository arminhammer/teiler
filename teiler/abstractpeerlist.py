from abc import ABCMeta, abstractmethod

class AbstractPeerList:
    
    #__metaclass__ = ABCMeta
    
    @abstractmethod
    def contains(self, peerID, peerAddress, peerPort):
        ''' Have a method to test if the list contains a cetain peer '''
        
        '''
        for i in range(self.count()):
            item = self.item(i)
            if peerID == item.id:
                if(peerAddress == item.address):
                    if(int(peerPort) == item.port):
                        return True
        return False
        '''
    
        
    @abstractmethod
    def iterAllItems(self):
        ''' Method to iterate over all items in the list '''
        
        '''
        for i in range(self.count()):
            yield self.item(i)
        '''
        
    @abstractmethod
    def addItem(self):
        ''' Add an item to the list '''
        
    @abstractmethod    
    def removeItemWidget(self):
        ''' Remove an item from the list '''
        