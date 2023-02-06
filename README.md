# UK National Grid

## Sensors
This integration provides a sensor for the UK National Grid Demand Flexibility Service (DFS) indicating the current state of the DFS offered by NG ESO. Named based on the entry added to configuration.yaml, it can have the following states:
State | Description | Attributes
----- | ----------- | ----------
Inactive | No DFS requirement until midnight. | `session_start`: null, `session_end`: null
Scheduled | There is a DFS requirement between now and midnight. | `session_start`: Start of the scheduled session, `session_end`: End of the scheduled session.
Active | There is an active DFS requirement now. | `session_start`: Start of the active session, `session_end`: End of the active session.

## Disclaimers
- This is the first HA integration I've done and first time I've ever really done anything with Python. Use at your own risk!
- Known "to-dos" include HA unique ID assignment and loggers for example.
- The nature of the National Grid DFS means that there isn't much changing data for extensive testing. In theory this code can work against multiple DFS requirements in the same 24 hour window. In practice, who knows... The optional parameters scattered around the sensor and nationalGrid modules are specifically to allow setting against old dates and data.

## Installation
1. Copy to custom_components folder:
```
cd custom_components
wget -X GET https://github.com/KeithB/ha-nationalgrid/archive/refs/heads/main.zip -O main.zip
gunzip main.zip
```

2. Add entry to configuration.yaml. The following will create a sensor National_Grid_UK_DFS:
```
sensor:
  - platform: national_grid
    name: "National_Grid_UK"
```

3. Restart Home Assistant.