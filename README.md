# HA National Grid

## Sensors
This integration provides the following sensors:
- Demand Flexibility Service (DFS) indicating the current state of the DFS offered by NG ESO
  - **Inactive**: No DFS requirement until midnight.
  - **Scheduled**: There is a DFS requirement between now and midnight. Timings can be seen in the session_start and session_end attributes.
  - **Active**: There is an active DFS requirement now. Timings can be seen in the session_start and session_end attributes.

## Installation