# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pyRoute13 is a Python port of the Route13 framework for building simulators and optimizers for transportation networks. It simulates scenarios like forklifts in warehouses, baggage carts at airports, and trucks on highways - essentially anything involving workers or equipment moving loads over a network while satisfying constraints around delivery times, equipment capacities, and worker schedules.

**Important Note**: This is a port from TypeScript (Route13) to Python. The documentation in the README.md and other files has not been updated from the original TypeScript version and still references TypeScript, Node.js, npm, and other JavaScript-specific tooling. When reading documentation, mentally translate TypeScript concepts to their Python equivalents.

## Development Commands

The project uses invoke for task management. Available commands:

```bash
# Code formatting (uses Black with line length 88)
invoke black

# Run all tests with coverage
invoke test

# Run the simple simulator demo
invoke simple

# Run the full simulator demo
invoke full
```

## Testing

- Tests use nose as the test runner
- Coverage is tracked for the environment, core, agents, and generators packages
- To run a specific test file: `nosetests tests/unit_tests/test_agent.py`
- Test files are located in `tests/unit_tests/` and `tests/integration_tests/`

## Architecture Overview

The codebase is organized into several key modules under `pyRoute13/api/`:

1. **Core** (`api/core/`): Fundamental components
   - `agent.py`: Coroutine-based agent system
   - `timeline.py`: Event scheduling and execution
   - `time.py`: Time utilities (HOUR, MINUTE, SECOND constants)
   - `condition.py`: Event condition handling

2. **Environment** (`api/environment/`): Simulation world modeling
   - `environment.py`: Main environment that manages carts, jobs, and routing
   - `cart.py` and `cart_factory.py`: Cart entities that transport loads
   - `job.py` and `job_factory.py`: Jobs (TransferJob, OutOfServiceJob)
   - `location.py`: Location management
   - `trace.py`: Event tracing and logging

3. **Agents** (`api/agents/`): Behavioral components
   - `driver.py`: Controls cart movement and job execution
   - `dispatcher.py`: Base dispatcher interface
   - `simple_dispatcher.py`: Basic job assignment
   - `planning_loop_dispatcher.py`: Advanced planning-based dispatcher

4. **Planner** (`api/planner/`): Optimization algorithms
   - `planner.py`: Base planning interface
   - `job_assigner.py`: Assigns jobs to carts
   - `route_planner.py`: Plans optimal routes
   - `route_calculator.py`: Calculates route metrics

5. **Generators** (`api/generators/`): Synthetic data generation
   - `transfer_generator.py`: Generates synthetic transfer jobs
   - `staffing_plan.py`: Generates crew schedules

## Key Concepts

- **Timeline**: Central event loop that drives the simulation
- **Agent**: Coroutine-based entities that yield actions to the timeline
- **Cart**: Vehicles that transport loads between locations
- **Job**: Work to be done (transfers, out-of-service periods)
- **Environment**: Manages the simulation world and provides estimators for:
  - Load/unload times
  - Transit times between locations
  - Route planning (next step calculation)

## Simulator Entry Points

- `simple_simulator.py`: Basic example with 3 carts and 4 jobs
- `full_simulator.py`: More complex simulation with planning loop dispatcher

When implementing new features, follow the existing coroutine-based agent pattern where agents yield actions to the timeline.