
import json

MSG_TYPE_DATA = 0x00
MSG_TYPE_ACK = 0x01
MSG_TYPE_DATA_ACK = MSG_TYPE_DATA | MSG_TYPE_ACK
MSG_TYPE_CHAT = 0x02
MSG_TYPE_JOIN = 0x03
MSG_TYPE_LEAVE = 0x04
MSG_TYPE_ERROR = 0x05
MSG_TYPE_CREATE_ACCOUNT = 0x06

class Datagram:
    def __init__(self, mtype: int, msg: str, sz: int = 0):
        self.mtype = mtype
        self.msg = msg
        self.sz = len(self.msg)
        
    def to_json(self):
        return json.dumps(self.__dict__)    
    
    @staticmethod
    def from_json(json_str):
        return Datagram(**json.loads(json_str))
    
    def to_bytes(self):
        return json.dumps(self.__dict__).encode('utf-8')
    
    @staticmethod
    def from_bytes(json_bytes):
        return Datagram(**json.loads(json_bytes.decode('utf-8')))