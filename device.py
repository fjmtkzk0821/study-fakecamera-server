class Device:
    def __init__(self, name, ip, secret):
        self.name = name
        self.ip = ip
        self.__secret = secret
    
    def verify(self, secret) -> bool:
        return self.__secret == secret