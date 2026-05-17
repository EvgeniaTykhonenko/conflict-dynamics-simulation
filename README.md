# Simulation of Strategic Interventions in Conflict Dynamics

This repository contains the Python implementation of the mathematical model developed for the bachelor's thesis: **"Simulation of Strategic Interventions in Conflict Dynamics"**.

The project introduces a hybrid stochastic model that integrates **Markov Chains** (for discrete phase transitions between 'Peace' and 'Conflict') with **ARIMA-based logic** (Resilience Index and political shocks) to account for institutional memory and time autocorrelation.

## Project Structure

* `data/` - Folder for the Civil Conflict Ceasefire (CFD) Dataset (must be downloaded separately).
* `src/` - Contains the main Python scripts:
  * `preprocessing.py` - Transforms event-based CFD data into discrete time series ($\Delta t = 1$ month).
  * `monte_carlo_sim.py` - Runs the hybrid Monte Carlo simulation (1000 iterations over a 60-month horizon).
* `results/` - Stores generated visual outputs, including frequency distributions of peace duration.
* `requirements.txt` - List of required Python libraries.

## Methodology

The simulation evaluates three primary strategic scenarios:
1. **Base Scenario:** No external interventions.
2. **Diplomatic Mediation:** Implementation of the $u_{dip}$ control vector.
3. **Military Enforcement/Sanctions:** Implementation of the $u_{enf}$ control vector.

The algorithmic core relies on dynamic probability correction, allowing the system to model society's "habituation" to peace, shifting the equilibrium distribution calculated by traditional memoryless Markov models.

## Installation and Usage

1. Clone the repository:
   ```bash
   git clone [https://github.com/EvgeniaTykhonenko/conflict-dynamics-simulation.git](https://github.com/EvgeniaTykhonenko/conflict-dynamics-simulation.git)
   cd conflict-dynamics-simulation
