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
timer = [0] * 6 # Give each state a timer for things like blinking lights, moving motors
microstate = None # Needed a global variable in some states (e.g. in what direction is an edge being avoided

# FSM update function
def update_fsm():
    global current_state, previous_state, microstate, last_state_change_time, conditions

    if current_state == IDLE:
        # Code to run if we are entering this state for the first time
        if not current_state == previous_state:
            previous_state = IDLE
            pixels.fill(0)
            move(STOP)
            log("entered IDLE", LOG_INFO)

        # Code to run while updating the current state
        # Waiting for the button release to start the competition

        event = conditions['key_events'] # to simplify typing
        if event and event.key_number == 0 and event.pressed:
            log("Button pressed, charged and ready to start.", LOG_INFO)
            pixels.fill((255,0,0))
        elif event and event.key_number == 0 and event.released:
            log("Button released, moving to waiting state", LOG_INFO)
            current_state = WAITING
            last_state_change_time = time.monotonic()

        # If the state was changed, then we are exiting this state so clean up if necessary
        if not current_state == IDLE:
            log("left IDLE", LOG_INFO)


    elif current_state == WAITING:
        # Wait for 5 seconds before starting
        pixels_on = (0,0,255)
        pixels_off = (0,0,0)

        # Code to run if upon entering state
        if not current_state == previous_state:
            previous_state = WAITING
            pixels.fill(pixels_on)
            log("entered WAITING", LOG_INFO)
            timer[WAITING] = last_state_change_time # Start the light blinking timer

        # Code to update current state
        if time.monotonic() - last_state_change_time >= WAITING_TIME:
            pixels.fill(pixels_off)
            current_state = SEARCHING
            last_state_change_time = time.monotonic()
        elif time.monotonic() - timer[WAITING] > 0.5:
            # In this state, both pixels are the same color
            timer[WAITING] = time.monotonic()
            log(f'Pixel status in WAITING {pixels}', LOG_DEBUG)
            if pixels[0] == pixels_on:
                pixels.fill(pixels_off)
            else:
                pixels.fill(pixels_on)

        # Code to run upon exiting state
        if not current_state == WAITING:
            log("left WAITING state", LOG_INFO)

    elif current_state == SEARCHING:
        # Search for the opponent by scanning with TOF sensors
        pixels_on = (0,255,0)
        pixels_off = (0,0,0)

        # Code to run if upon entering state
        if not current_state == previous_state:
            previous_state = SEARCHING
            pixels.fill(pixels_on)
            log("entered SEARCHING", LOG_INFO)
            timer[SEARCHING] = last_state_change_time # Start a timer

        # Code to update current state
        if conditions["edge_left"] or conditions["edge_right"]:
            print("Edge detected, transitioning to AVOIDING state.")
            current_state = AVOIDING
            last_state_change_time = time.monotonic()
        elif conditions["tof_left"] < 100 or conditions["tof_right"] < 100:
            print("Opponent detected, transitioning to CHARGING state.")
            current_state = CHARGING
            last_state_change_time = time.monotonic()
        else:
            # Perform search movements (arcing)
            move(HARD_RIGHT)  # Adjust as needed to implement the arc-search strategy

        # Code to run upon exiting state
        if not current_state == SEARCHING:
            log("left SEARCHING state", LOG_INFO)

    elif current_state == CHARGING:
        # Head towards opponent
        pixels_on = (255,255,0)
        pixels_off = (0,0,0)


        # Code to run if upon entering state
        if not current_state == previous_state:
            previous_state = CHARGING
            pixels.fill(pixels_on)
            log("entered CHARGING", LOG_INFO)
            timer[CHARGING] = last_state_change_time # Start a timer

        # Code to update current state
        if conditions["edge_left"] or conditions["edge_right"]:
            print("Edge detected, transitioning to AVOIDING state.")
            current_state = AVOIDING
            last_state_change_time = time.monotonic()
        if abs(conditions["tof_diff"]) > 20: # Bot might be heading in the wrong direction
            log("Shifting approach", LOG_DEBUG)
            if conditions["tof_diff"] > 0: # Bot needs to turn right
                move(RIGHT)
            else:
                move(LEFT)
        else:
            move(FORWARD)
        if time.monotonic() - timer[CHARGING] > CHARGE_DURATION: # Been charging for too long, give up
            log("Stalemate detected, retreating", LOG_INFO)
            current_state = RETREATING
            last_state_change_time = time.monotonic()

        # Code to run upon exiting state
        if not current_state == CHARGING:
            log("left CHARGING state", LOG_INFO)

    elif current_state == RETREATING:
        # Hard turn followed by a short backup. Hard-coded now, but settings will be helpful here
        pixels_on = (0,255,255)
        pixels_off = (0,0,0)


        # Code to run if upon entering state
        if not current_state == previous_state:
            previous_state = RETREATING
            pixels.fill(pixels_on)
            log("entered RETREATING", LOG_INFO)
            timer[RETREATING] = last_state_change_time # Start a timer
            move(HARD_LEFT)

        # Code to update current state
        if conditions["edge_left"] or conditions["edge_right"]:
            log("Edge detected, transitioning to AVOIDING state.", LOG_INFO)
            current_state = AVOIDING
            last_state_change_time = time.monotonic()
        if time.monotonic() - timer[RETREATING] > 0.5:
            move(BACKWARD)
        if time.monotonic() - timer[RETREATING] > 1:
            log("Done with retreate", LOG_INFO)
            current_state = SEARCHING
            last_state_change_time = time.monotonic()

        # Code to run upon exiting state
        if not current_state == RETREATING:
            log("left RETREATING state", LOG_INFO)
            # make sure we aren't moving
            move(STOP)

    elif current_state == AVOIDING:
        # Avoid edge based upon what triggered the detection
        pixels_on = (255,255,255)
        pixels_off = (0,0,0)


        # Code to run if upon entering state
        if not current_state == previous_state:
            previous_state = AVOIDING
            pixels.fill(pixels_on)
            log("entered AVOIDING", LOG_INFO)
            timer[AVOIDING] = last_state_change_time # Start a timer
            if conditions["edge_left"]:
                if conditions["edge_right"]: # hit edge straight on, so back-up and turn
                    microstate = 0
                else:
                    microstate = 1
            elif conditions["edge_right"]: # Shouldn't need elif, but just in case.
                microstate = -1


        # Code to update current state
        # perform movement

        if microstate == -1: # The right edge triggered this state
            move(BACK_LEFT)
        elif microstate == 1:
            move(BACK_RIGHT)
        else:
            move(BACKWARD)
        if time.monotonic() - timer[AVOIDING] > AVOIDANCE_TIME/2:
            if microstate == 0: # we need to do another turn
                move(HARD_LEFT)
            else:
                pass
        if time.monotonic() - timer[AVOIDING] > AVOIDANCE_TIME:
            log("Done with AVOIDING", LOG_INFO)
            current_state = SEARCHING
            last_state_change_time = time.monotonic()

        # Code to run upon exiting state
        if not current_state == AVOIDING:
            log("left AVOIDING state", LOG_INFO)
            # make sure we aren't moving
            move(STOP)
            # clear the microstate
            microstate = None

    # If we get here, something is wrong, so bail
    else:
        log("I don't know what to do, so heading to IDLE",LOG_CRITICAL)
        current_state = IDLE
'''


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
    # Stop bot with key press
    if not conditions['key_events'] is None and conditions['key_events'].key_number == 1 and conditions['key_events'].pressed:
        current_state = IDLE
    update_fsm()  # Update the FSM in each iteration
    time.sleep(0.01)  # Small delay to prevent overwhelming the processor

