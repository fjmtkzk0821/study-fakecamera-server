import multiprocessing as mp

class ProcessPool:
    def __init__(self) -> None:
        self.p_list = []

    def append(self, p: mp.Process):
        self.p_list.append(p)

    def start(self):
        for p in self.p_list:
            p.start()
    
    def join(self):
        for p in self.p_list:
            p.join()

    def kill(self):
        for p in self.p_list:
            p.kill()