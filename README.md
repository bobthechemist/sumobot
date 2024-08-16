# sumobot

My version of the [IBiB](www.ibib.us) sumobot software. Not a fork since it's a completely different paradigm. 

## FSM Approach

Treating the sumobot as a finite state machine with the following conditions, states, and actions/behaviors

- Conditions
    - button  (GP20 on RP2040) press/release (used to exit idle state)
    - left/right TOF sensors (used to detect opponent)
    - left/right edge detectors (used to detect edge of doyho)
- States
    - IDLE - not doing anything
        - Enter: upon power up
        - Update: upon key press update neopixel to (0x00FF00)
        - Exit: upon key release, change state to WAITING
    - WAITING - getting ready to fight
        - Enter: 
        - Update: check 10 second timer, update flashing LEDs (0x00FF00) 2 hz frequency
        - Exit: upon termination of timer, change state to SEARCHING
    - SEARCHING - looking for an opponent
        - Enter:
        - Update:
        - Exit: 
    - CHARGING - heading towards the opponent
    - RETREATING - backing up from opponent (possibly includes rerouting around opponent)
    - AVOIDING - responding to an edge detection
- Actions (behaviors)
    - drive forward (speed, *acceleration*, duration)
        - Values in parentheses are user-defined, italicized are not implemented and merely ideas to consider.
        - 
    - drive backward (speed, duration)
        - No current means of detecting edge, so sensors are not helpful here
        - Enter on  

## Implementation

- Actions are definitions that can be stored in a library. They accept parameters that affect the behavior of the sumobot such as how fast it charges and how wide of an arc the bot uses to find an opponent.
- There are two main search approaches: arc expansion and spiral search pattern. The first is a bit easier to implement and may be more robust with the edge limits, would like to incorporate sensor-guided adjustments
- 