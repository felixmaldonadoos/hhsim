import sys

class Logger:
    COLOR_RESET = "\033[0m"
    COLOR_WHITE = "\033[97m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_RED = "\033[91m"

    def __init__(self, class_name: str):
        self.class_name = class_name

    def log(self, message: str, *args, bSuccess=False):
        color = self.COLOR_GREEN if bSuccess else self.COLOR_WHITE
        self._print("LOG", message, args, color)

    def warn(self, message: str, *args):
        self._print("WRN", message, args, self.COLOR_YELLOW)

    def error(self, message: str, *args):
        self._print("ERR", message, args, self.COLOR_RED)

    def _print(self, tag: str, message: str, args, color: str):
        formatted_args = ", ".join(repr(arg) for arg in args)
        suffix = f" ({formatted_args})" if args else ""
        output = f"[{tag}][{self.class_name}] {message}{suffix}"
        print(f"{color}{output}{self.COLOR_RESET}", file=sys.stderr if tag == "ERR" else sys.stdout)

    @staticmethod
    def run_tests():
        print("=== Logger Test Cases ===")
        logger = Logger("TestClass")

        # Plain log
        logger.log("Hello from log")

        # Log with args
        logger.log("Values are", 42, "alpha", [1, 2, 3])

        # Success log (green)
        logger.log("Operation successful", bSuccess=True)

        # Warning
        logger.warn("Low disk space", "/dev/sda1", "10% left")

        # Error
        logger.error("Unhandled exception", "NullPointerException", 500)

        print("=== End of Tests ===")


# Run the test cases if this file is executed directly
if __name__ == "__main__":
    Logger.run_tests()
