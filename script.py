class Multiplication:
    """Multiply number by multiplier."""
    def __init__(self, multiplier: int):
        """Initialize multiplier."""
        self.multiplier = multiplier

    def multiply(self, number: int) -> int:
        """Multiply number by multiplier."""
        return number * self.multiplier


# Display the result
multipication = Multiplication(5)
print(multipication.multiply(2))