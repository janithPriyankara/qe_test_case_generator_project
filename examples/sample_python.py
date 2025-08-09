"""
Example source files for testing the MDTD system
"""

# Example Python functions to test
def add(a, b):
    """Add two numbers together"""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a + b

def is_prime(n):
    """Check if a number is prime"""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def validate_email(email):
    """Validate email address format"""
    import re
    if not isinstance(email, str):
        raise TypeError("Email must be a string")

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

class Calculator:
    """Simple calculator class"""

    def __init__(self):
        self.history = []

    def calculate(self, operation, x, y):
        """Perform calculation and store in history"""
        if operation == 'add':
            result = x + y
        elif operation == 'subtract':
            result = x - y
        elif operation == 'multiply':
            result = x * y
        elif operation == 'divide':
            if y == 0:
                raise ValueError("Cannot divide by zero")
            result = x / y
        else:
            raise ValueError("Invalid operation")

        self.history.append(f"{x} {operation} {y} = {result}")
        return result

    def get_history(self):
        """Get calculation history"""
        return self.history.copy()
