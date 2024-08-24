# These settings affect the behaviors of your sumobot, such as how fast it moves and
#   how wide of an arc it searches.

MAX_SPEED = 1 # Ranges from 0 (doesn't move at all) to 1 (as fast as possible)
MAX_DISTANCE = 500

TURN_DURATION = 0.2 # Number of seconds that the bot spends turning.

CHARGE_DURATION = 5 # Time to charge before giving up

AVOIDANCE_TIME = 1 # Time to spend during the edge avoidance movement

# NONE OF THE VALUES BELOW SHOULD BE CHANGED

WAITING_TIME = 5 # DO NOT CHANGE THIS VALUE! It is the time your bot waits to start battling and must be the same for all bots

LOG_LEVEL = 20 # Sets amount of logging. See below for values, but the way the code is currently written, must use numbers.
'''
LOG_NOTSET      =  0
LOG_DEBUG       = 10
LOG_INFO        = 20
LOG_WARNING     = 30
LOG_ERROR       = 40
LOG_CRITICAL    = 50
'''
