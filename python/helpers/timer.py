import time
class Timer:
    def __init__(self, elapsed_init=0, text="Default"):
        self.elapsed = elapsed_init
        self.start_time = None
        self.text = text
        self.start()

    def start(self, msg=None)->None:
        self.start_time = time.perf_counter()
        
    def stop(self, msg=None)->None:
        self.elapsed = time.perf_counter() - self.start_time
        print(f'[Timer] {self.text} elapsed time: {self.elapsed} seconds ({msg})')
        
    def get_elapsed(self)->float:
        self.elapsed =  time.perf_counter() - self.start_time
        return self.elapsed