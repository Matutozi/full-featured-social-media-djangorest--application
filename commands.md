#FILE THAT STORES ALL COMMANDS

#to get secret key
from django.core.management.utils import get_random_secret_key
secret_key = get_random_secret_key()
secret_key