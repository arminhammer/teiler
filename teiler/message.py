import json

class Message(object):
    """message to be sent across the wire"""
    def __init__(self, command, sessionID="0000"):
        self.command = command
        self.sessionID = sessionID
        
    def __str__(self):
        return self.serialize()
    
    def serialize(self):
        return json.dumps(self.__dict__)