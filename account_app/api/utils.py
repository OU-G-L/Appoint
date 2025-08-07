import random


def generate_otp():
    """
    Generates a 6-digit numeric One-Time Password (OTP) as a string.

    Returns:
        str: A string representing a 6-digit OTP (e.g., '483920').
    """
    return str(random.randint(100000, 999999))  # Random 6-digit number as string
