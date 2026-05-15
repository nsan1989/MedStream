import random
import requests


# OTP generate function.
def generate_otp():
    return str(random.randint(100000, 999999))
