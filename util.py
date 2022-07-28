import random
import string

def generateNumber(length: int) -> str:
    return "".join(random.SystemRandom().choices(string.digits, k=length))
    # generated = defaultVal + constString[random.randint(0,len(constString)-1)]
    # if(length == 1):
    #     return generated
    # else:
    #     return generateNumber(length-1, generated)

def generateAlphaDigit(length: int) -> str:
    return "".join(random.SystemRandom().choices(string.ascii_letters+string.digits, k=length))