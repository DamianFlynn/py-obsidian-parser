class Multiplication:
    """Multiply number by multiplier."""
    def __init__(self, multiplier: float):
        """Initialize multiplier."""
        self.multiplier = multiplier

    def multiply(self, number: float) -> float:
        """Multiply number by multiplier."""
        return number * self.multiplier

