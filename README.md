
# F1 Race Strategy Simulator

A Python and Oracle SQL application that simulates Formula 1 race strategies to determine the optimal tyre compounds, pit stop windows, and predicted race times.

The simulator evaluates thousands of possible strategies using driver performance, team performance, circuit characteristics, tyre degradation, and race conditions to recommend the fastest strategy.

## Features

### Race Strategy Optimization
- Simulates thousands of possible race strategies
- Evaluates one-stop, two-stop, and three-stop strategies
- Determines optimal tyre compound sequences
- Calculates optimal pit stop laps
- Compares strategies based on predicted total race time
- Allows tyre compounds to be reused throughout a race
- Enforces the requirement to use at least two different dry tyre compounds

### Tyre Management
- Models Soft, Medium, and Hard tyre compounds
- Accounts for tyre degradation throughout each stint
- Uses compound-specific tyre lifespan estimates
- Calculates lap times based on tyre age and performance
- Evaluates different stint lengths to minimize total race time

### Circuit Characteristics
- Accounts for circuit length and track characteristics
- Incorporates circuit-specific pit lane time losses
- Considers different levels of tyre wear
- Accounts for overtaking difficulty
- Penalizes additional pit stops at circuits where overtaking is difficult

### Driver and Team Performance
- Uses historical driver performance at individual circuits
- Incorporates historical team performance
- Considers driver and team average lap times
- Uses historical race results to estimate performance
- Excludes DNF results from performance averages

### Race Simulation
- Simulates race strategies lap by lap
- Accounts for changing fuel loads throughout a race
- Models tyre degradation over each stint
- Considers starting grid position
- Applies early-race traffic effects
- Includes pit stop time losses in total race time calculations

### Strategy Comparison
- Identifies the fastest overall race strategy
- Displays recommended tyre compounds
- Displays the number of pit stops and optimal pit laps
- Calculates estimated total race time
- Compares the fastest one-stop and two-stop strategies
- Displays the total number of simulations performed

## Technologies
- Python
- Oracle SQL
- Oracle Database

## Database

The application uses a relational Oracle database containing:

- Drivers
- Circuits
- Tyres
- Races
- Driver Results
- Driver Circuit History
- Team Circuit History

SQL queries retrieve historical performance data and circuit information used by the simulation engine.

## How It Works

1. The user selects a driver, starting position, and circuit.
2. The application retrieves relevant information from the Oracle database.
3. The simulation engine generates feasible tyre and pit stop combinations.
4. Each strategy is simulated lap by lap.
5. The application calculates predicted total race times.
6. Strategies are compared to identify the fastest option.
7. The recommended strategy and alternative strategies are displayed.


## Future Development

Planned improvements include:

- Live race strategy adjustments based on changing race conditions
- Safety car, virtual safety car, and red flag scenarios
- Weather forecasting and changing track conditions
- Real-time tracking of surrounding drivers and their race strategies
- Predicting competitors' pit stop windows and tyre choices
- Evaluating undercut and overcut opportunities against nearby drivers
- Accounting for traffic and potential position losses after pit stops
- Adjusting strategies based on gaps to drivers ahead and behind
- Comparing the fastest theoretical strategy against strategies that maximize track position
- Recalculating optimal strategies as competitors make pit stops or change their approach
