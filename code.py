from settings import *
from sumobot import *
import time

# Set offsets to zero, place a large object about 6-10 inches from the sumobot,
#  and confirm that the same distance is measured with both TOF sensors.
#  Adjust offsets as needed.
tof_left.offset = 0
tof_right.offset = -60

# Initialize the current conditions
conditions = get_conditions()

# Define FSM states
IDLE        = 0 # Sitting around doing nothing - can be exited by hitting the start button (BUTTON 0)
WAITING     = 1 # Waiting to start the battle - following the start routine, will exit to searching
SEARCHING   = 2 # Looking for an opponent
CHARGING    = 3 # Moving towards what bot things is an opponent
RETREATING  = 4 # Moving away from the opponent
AVOIDING    = 5 # Found the edge of the doyho and is moving around.

# FSM variables
current_state = IDLE
previous_state = IDLE
last_state_change_time = 0
timers = [0] * 6 # Give each state a timer for things like blinking lights, moving motors

# FSM update function
def update_fsm():
    global current_state, previous_state, last_state_change_time, conditions

    if current_state == IDLE:
        # Code to run if we are entering this state for the first time
        if not current_state == previous_state:
            previous_state = IDLE
            pixels.fill(0)
            print("entered IDLE")
        # Code to run while updating the current state
        # Waiting for the button release to start the competition
        event = conditions['key_events'] # to simplify typing
        if event and event.key_number == 0 and event.pressed:
            print("Button pressed, charged and ready to start.")
            pixels.fill((255,0,0))
        elif event and event.key_number == 0 and event.released:
            print("Button released, moving to waiting state")
            current_state = WAITING
            last_state_change_time = time.monotonic()
        # If the state was changed, then we are exiting this state so clean up if necessary
        if not current_state == IDLE:
            print("left IDLE")


    elif current_state == WAITING:
        # Wait for 5 seconds before starting
        # Code to run if we are entering this state for the first time
        pixels_on = [(0
        if not current_state == previous_state:
            previous_state = WAITING
            pixels.fill((0,0,255))
            print("entered WAITING")
            pixels_on = True
        if time.monotonic() - last_state_change_time >= WAITING_TIME:
            print("Transitioning to IDLE state.")
            current_state = IDLE
            last_state_change_time = time.monotonic()
        elif
        # If the state was changed, then we are exiting this state so clean up if necessary
        if not current_state == WAITING:
            print("left WAITING")
'''
    elif current_state == SEARCHING:
        # Search for the opponent by scanning with TOF sensors
        if ir_left.value == False or ir_right.value == False:
            print("Edge detected, transitioning to AVOIDING state.")
            current_state = AVOIDING
            last_state_change_time = time.monotonic()
        elif tof_left.range < 100 or tof_right.range < 100:
            print("Opponent detected, transitioning to CHARGING state.")
            current_state = CHARGING
            last_state_change_time = time.monotonic()
        else:
            # Perform search movements (arcing)
            soft_right()  # Adjust as needed to implement the arc-search strategy

    elif current_state == CHARGING:
        # Charge towards the opponent
        drive_forward()
        # Check for edge detection while charging
        if ir_left.value == False or ir_right.value == False:
            print("Edge detected while charging, transitioning to AVOIDING state.")
            current_state = AVOIDING
            last_state_change_time = time.monotonic()
        # Retreat after a set time
        elif time.monotonic() - last_state_change_time >= RETREAT_TIME:
            print("Retreating after charge, transitioning to RETREATING state.")
            current_state = RETREATING
            last_state_change_time = time.monotonic()

    elif current_state == RETREATING:
        # Move backward after charging to avoid stalling
        drive_backward()
        if time.monotonic() - last_state_change_time >= 1:  # Retreat for 1 second
            print("Retreat complete, transitioning to SEARCHING state.")
            current_state = SEARCHING
            last_state_change_time = time.monotonic()

    elif current_state == AVOIDING:
        # Avoid the edge of the ring
        stop_motors()
        if ir_left.value == False:
            hard_right()  # Turn away from the left edge
        elif ir_right.value == False:
            hard_left()  # Turn away from the right edge

        # After turning for 0.5 second, return to SEARCHING
        if time.monotonic() - last_state_change_time >= 0.5:
            print("Edge avoided, transitioning to SEARCHING state.")
            current_state = SEARCHING
            last_state_change_time = time.monotonic()
'''

while True:
    conditions = get_conditions()
    update_fsm()  # Update the FSM in each iteration
    time.sleep(0.01)  # Small delay to prevent overwhelming the processor

