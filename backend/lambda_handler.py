import sys
import os

# This tells Python to look in the current folder for libraries
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from mangum import Mangum
from main import app

lambda_handler = Mangum(app)