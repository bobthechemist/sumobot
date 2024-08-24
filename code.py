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
state = {
    "IDLE"      : 0, # Sitting around doing nothing - can be exited by hitting the start button (BUTTON 0)
    "WAITING"   : 1, # Waiting to start the battle - following the start routine, will exit to searching
    "SEARCHING" : 2, # Looking for an opponent
    "CHARGING"  : 3, # Moving towards what bot thinks is an opponent
    "RETREATING": 4, # Moving away from the opponent
    "AVOIDING"  : 5, # Found the edge of the doyho and is moving around.
    "TESTING"   : 6, # A special state for debugging
}


state_name = {v: k for k, v in state.items()}

# FSM variables
current_state = state["IDLE"]
previous_state = state["TESTING"]
last_state_change_time = 0
timer = [0] * len(state) # Give each state a timer for things like blinking lights, moving motors
microstate = None # Needed a global variable in some states (e.g. in what direction is an edge being avoided
testing = False # Set to true to enter the TESTING state instead of starting a match

# FSM update function
def update_fsm():
    global current_state, previous_state, microstate, last_state_change_time, conditions, testing

    if current_state == state["IDLE"]:
        '''
        What does this state do?
        '''
        # Variables useful for this state
        pixels_on = (255,0,0)
        pixels_off = (0,0,0)
        event = conditions['key_events'] # to simplify typing

        # Enter state
        if not current_state == previous_state:
            previous_state = current_state
            pixels.fill(pixels_off)
            move(STOP)
            log(f"Entered {state_name[current_state]} state.", LOG_INFO)

        # Update state
        if event and event.key_number == 0 and event.pressed:
            pixels.fill(pixels_on)
            if testing: # Will switch to TESTING
                log("Will switch to TESTING state when button is released.", LOG_INFO)
            else:
                pixels.fill(pixels_on)
        elif event and event.key_number == 0 and event.released:
            if testing:
                current_state = state["TESTING"]
            else:
                current_state = state["WAITING"]
            last_state_change_time = time.monotonic()
            log(f"Button released, will switch to {state_name[current_state]}", LOG_INFO)

        # Exit state
        if not current_state == previous_state:
            log(f"Left {state_name[current_state]} state.", LOG_INFO)
            pixels.fill(pixels_off)
# /// end of IDLE state ///

    elif current_state == state["WAITING"]:
        '''
        What does this state do?
        '''
        pixels_on = (0,0,255)
        pixels_off = (0,0,0)

        # Enter
        if not current_state == previous_state:
            previous_state = current_state
            pixels.fill(pixels_on)
            log(f"Entered {state_name[current_state]} state.", LOG_INFO)
            timer[current_state] = last_state_change_time # Start the light blinking timer

        # Update
        if time.monotonic() - last_state_change_time >= WAITING_TIME:
            pixels.fill(pixels_off)
            current_state = state["SEARCHING"]
            last_state_change_time = time.monotonic()
        elif time.monotonic() - timer[current_state] > 0.5:
            # In this state, both pixels are the same color
            timer[current_state] = time.monotonic()
            log(f'Pixel status in WAITING {pixels}', LOG_DEBUG)
            if pixels[0] == pixels_on:
                pixels.fill(pixels_off)
            else:
                pixels.fill(pixels_on)

        # Exit state
        if not current_state == previous_state:
            log(f"Left {state_name[current_state]} state.", LOG_INFO)
            pixels.fill(pixels_off)
# /// end of WAITING state ///

    elif current_state == state["SEARCHING"]:
        '''
        What does this state do?
        '''
        pixels_on = (0,255,0)
        pixels_off = (0,0,0)

        # Enter
        if not current_state == previous_state:
            previous_state = current_state
            pixels.fill(pixels_on)
            log(f"Entered {state_name[current_state]} state.", LOG_INFO)
            timer[current_state] = last_state_change_time # What is timer used for?

        # Update
        if conditions["edge_left"] or conditions["edge_right"]:
            log("Edge detected, switching to AVOIDING state.", LOG_INFO)
            current_state = state["AVOIDING"]
            last_state_change_time = time.monotonic()
        elif conditions["tof_left"] < MAX_DISTANCE or conditions["tof_right"] < MAX_DISTANCE:
            log("Opponent detected, switching to CHARGING state.", LOG_INFO)
            current_state = state["CHARGING"]
            last_state_change_time = time.monotonic()
        else:
            # Perform search movements (arcing)
            move(HARD_RIGHT)  # Adjust as needed to implement the arc-search strategy

        # Exit state
        if not current_state == previous_state:
            log(f"Left {state_name[current_state]} state.", LOG_INFO)
            pixels.fill(pixels_off)
# /// end of SEARCHING state ///

    elif current_state == state["CHARGING"]:
        '''
        What does this state do?
        '''
        pixels_on = (255,255,0)
        pixels_off = (0,0,0)

        # Enter
        if not current_state == previous_state:
            previous_state = current_state
            pixels.fill(pixels_on)
            log(f"Entered {state_name[current_state]} state.", LOG_INFO)
            timer[current_state] = last_state_change_time # What is timer used for?

        # Code to update current state
        if conditions["edge_left"] or conditions["edge_right"]:
            print("Edge detected, transitioning to AVOIDING state.")
            current_state = state["AVOIDING"]
            last_state_change_time = time.monotonic()
        if abs(conditions["tof_diff"]) > 20: # Bot might be heading in the wrong direction
            log("Shifting approach", LOG_DEBUG)
            if conditions["tof_diff"] > 0: # Bot needs to turn right
                move(RIGHT)
            else:
                move(LEFT)
        else:
            move(FORWARD)
        if time.monotonic() - timer[current_state] > CHARGE_DURATION: # Been charging for too long, give up
            log("Stalemate detected, retreating", LOG_INFO)
            current_state = state["RETREATING"]
            last_state_change_time = time.monotonic()

        # Exit state
        if not current_state == previous_state:
            log(f"Left {state_name[current_state]} state.", LOG_INFO)
            pixels.fill(pixels_off)
# /// end of CHARGING state ///

    elif current_state == state["RETREATING"]:
        '''
        What does this state do?
        '''
        pixels_on = (0,255,255)
        pixels_off = (0,0,0)

        # Enter
        if not current_state == previous_state:
            previous_state = current_state
            pixels.fill(pixels_on)
            log(f"Entered {state_name[current_state]} state.", LOG_INFO)
            timer[current_state] = last_state_change_time # What is timer used for?
            move(HARD_LEFT)

        # Code to update current state
        if conditions["edge_left"] or conditions["edge_right"]:
            log("Edge detected, switching to AVOIDING state.", LOG_INFO)
            current_state = state["AVOIDING"]
            last_state_change_time = time.monotonic()
        if time.monotonic() - timer[current_state] > 0.5:
            move(BACKWARD)
        if time.monotonic() - timer[current_state] > 1:
            log("Done with retreate", LOG_INFO)
            current_state = state["SEARCHING"]
            last_state_change_time = time.monotonic()

        # Exit state
        if not current_state == previous_state:
            log(f"Left {state_name[current_state]} state.", LOG_INFO)
            pixels.fill(pixels_off)
            move(STOP)
# /// end of RETREATING state ///

    elif current_state == state["AVOIDING"]:
        '''
        What does this state do?
        '''
        pixels_on = (255,255,255)
        pixels_off = (0,0,0)

        # Enter
        if not current_state == previous_state:
            previous_state = current_state
            pixels.fill(pixels_on)
            log(f"Entered {state_name[current_state]} state.", LOG_INFO)
            timer[current_state] = last_state_change_time # What is timer used for?
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
        if time.monotonic() - timer[current_state] > AVOIDANCE_TIME/2:
            if microstate == 0: # we need to do another turn
                move(HARD_LEFT)
            else:
                pass
        if time.monotonic() - timer[current_state] > AVOIDANCE_TIME:
            log("Switching to SEARCHING state.", LOG_INFO)
            current_state = state["SEARCHING"]
            last_state_change_time = time.monotonic()

        # Exit state
        if not current_state == previous_state:
            log(f"Left {state_name[current_state]} state.", LOG_INFO)
            pixels.fill(pixels_off)
            # make sure we aren't moving
            move(STOP)
            # clear the microstate
            microstate = None
# /// end of AVOIDING state ///

    elif current_state == TESTING:
        '''
        What does this state do?
        '''
        # Some variables for this state
        pixels_on = (255,0,0)
        pixels_off = (0,0,0)

        # Enter
        if not current_state == previous_state:
            previous_state = current_state
            pixels.fill(pixels_on)
            log(f"Entered {state_name[current_state]} state.", LOG_INFO)
            timer[current_state] = last_state_change_time # What is timer used for?
        # Update
        else:
            log("Updating state", LOG_INFO)
            current_state = state["IDLE"]
        # Exit
        if not current_state == previous_state:
            log("Leaving state", LOG_INFO)
            pixels.fill(pixels_off)
# /// end of TESTING state ///

    # If we get here, something is wrong, so bail
    else:
        log("I don't know what to do, so heading to IDLE",LOG_CRITICAL)
        current_state = state["IDLE"]


while True:
    conditions = get_conditions()
    # Stop bot with key press
    if not conditions['key_events'] is None and conditions['key_events'].key_number == 1 and conditions['key_events'].pressed:
        current_state = state["IDLE"]
    update_fsm()  # Update the FSM in each iteration
    time.sleep(0.01)  # Small delay to prevent overwhelming the processor

