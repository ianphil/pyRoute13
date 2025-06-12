# pyRoute13

Python port of [Route13](https://github.com/MikeHopcroft/route13) - a framework for building simulators and optimizers for transportation networks.

## Overview

`pyRoute13` is a Python framework for building simulators and optimizers for transportation networks. It includes a number of naive, brute-force and heuristics based optimizers, but its pluggable architecture allows the use of more sophisticated optimizers, such as [linear programming solvers](https://en.wikipedia.org/wiki/Linear_programming) and ML models. 

`pyRoute13` scenarios include forklifts in warehouses, baggage carts at airports, and trucks on highways. Basically anything that involves workers or equipment moving loads over a network while satisfying constraints around delivery times, equipment capacities, and worker schedules.

### Key Features

- **Coroutine-based discrete event simulation** using Python generators
- **Pluggable optimizers** for route planning and job assignment
- **Flexible agent system** for modeling complex behaviors
- **Time-based simulation** with priority queue scheduling

## Installation

### Requirements

- Python 3.6 or higher
- pip package manager

### Install from source

Clone the repository:
```bash
git clone https://github.com/ianphil/pyRoute13.git
cd pyRoute13
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Examples

`pyRoute13` provides several example simulations that demonstrate the framework's capabilities:

```bash
# Run the simple simulator (3 carts, 4 jobs)
invoke simple

# Run the full simulator (24-hour simulation)
invoke full
```

You can also run the examples directly:
```bash
python pyRoute13/simple_simulator.py
python pyRoute13/full_simulator.py
```

### Development Commands

This project uses [invoke](http://www.pyinvoke.org/) for task management:

```bash
# Format code with Black (88 character line length)
invoke black

# Run tests with coverage
invoke test

# Run simple simulation demo
invoke simple

# Run full simulation demo  
invoke full
```

### Running Tests

Tests use nose as the test runner with coverage reporting:

```bash
# Run all tests
invoke test

# Run a specific test file
nosetests tests/unit_tests/test_agent.py
```

## Architecture

`pyRoute13` uses a coroutine-based architecture where agents (entities that perform actions) are implemented as Python generators that yield scheduling functions to a central timeline. This allows complex sequential behaviors to be written as simple, readable code.

### Core Components

- **Timeline**: Manages simulation time and schedules agent execution
- **Agents**: Entities that perform actions over time (drivers, dispatchers)
- **Environment**: Manages the simulation world (carts, jobs, locations)
- **Planners**: Optimize routes and job assignments
- **Generators**: Create synthetic workloads and schedules

For a detailed explanation of the coroutine architecture, see the [Coroutine Simulation Tutorial](docs/coroutine_simulation_tutorial.md).

## Project Structure

```
pyRoute13/
├── pyRoute13/
│   ├── api/
│   │   ├── core/          # Core simulation components
│   │   ├── agents/        # Agent implementations
│   │   ├── environment/   # Simulation world modeling
│   │   ├── planner/       # Optimization algorithms
│   │   └── generators/    # Synthetic data generation
│   ├── simple_simulator.py
│   └── full_simulator.py
├── tests/
│   ├── unit_tests/
│   └── integration_tests/
├── docs/
│   └── coroutine_simulation_tutorial.md
└── requirements.txt
```

## Documentation

- [Coroutine Simulation Tutorial](docs/coroutine_simulation_tutorial.md) - Learn how the coroutine-based simulation engine works
- [CLAUDE.md](CLAUDE.md) - Development guide for AI assistants

**Note**: This is a Python port of the original TypeScript Route13 project. Some documentation may still reference the TypeScript implementation. For Python-specific details, refer to the source code and the tutorials in the `docs/` directory.

## Examples

### Simple Simulation

The simple simulator demonstrates basic concepts with 3 carts and 4 jobs:

```python
from pyRoute13.api.core import timeline, agent
from pyRoute13.api.environment import environment, cart_factory, job_factory
from pyRoute13.api.agents import simple_dispatcher, driver

# Create core components
timeline = timeline.Timeline()
env = environment.Environment(...)
dispatcher = simple_dispatcher.SimpleDispatcher(timeline, env, trace)

# Add carts
cart_factory = cart_factory.Cart_Factory()
for i in range(3):
    cart = cart_factory.cart(capacity=10, location=0)
    env.add_cart(cart)
    agent.start(driver.drive(cart))

# Run simulation
timeline.main_loop()
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the same terms as the original Route13 project. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This is a Python port of the original [Route13](https://github.com/MikeHopcroft/route13) project by Mike Hopcroft.