import random


def generate_customer_id() -> str:
    """Generate an ID in the format xxxx-xxxx using A-Z and digits."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    def part() -> str:
        return "".join(random.choice(alphabet) for _ in range(4))
    return f"{part()}-{part()}"
