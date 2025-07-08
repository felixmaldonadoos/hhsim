import sys
import time
class ProgressBar:
    def __init__(self, total, prefix='', bar_length=40):
        self.total = total
        self.prefix = prefix
        self.bar_length = bar_length
        self.current = 0

    def update(self, current, label=''):
        self.current = current + 1
        percent = float(self.current) / self.total
        filled_length = int(round(self.bar_length * percent))
        bar = '=' * filled_length + '-' * (self.bar_length - filled_length)
        progress_msg = f'\r{self.prefix} [{bar}] {percent * 100:.1f}% ({self.current}/{self.total}) {label}'
        sys.stdout.write(progress_msg)
        sys.stdout.flush()

    def finish(self):
        sys.stdout.write('\n')
        sys.stdout.flush()


if __name__ == "__main__":
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)


    tasks = list(range(20))  # compute fib(0) to fib(9)
    pb = ProgressBar(total=len(tasks), prefix="Computing Fibonacci ")

    for i, n in enumerate(tasks, start=1):
        result = fibonacci(n)
        pb.update(i, label=f"fib({n}) = {result}")
        time.sleep(0.1)  # Simulate some delay

    pb.finish()
    print("All Fibonacci computations complete.")