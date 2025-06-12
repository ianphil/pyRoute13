# Coroutine-Based Discrete Event Simulation Tutorial

## Introduction

This tutorial will teach you how to build time-based simulations using Python generators (coroutines) and a priority queue. This powerful pattern allows you to write complex sequential behaviors that execute over simulated time, making it perfect for modeling systems where multiple entities perform actions concurrently.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [The Magic Behind the Pattern](#the-magic-behind-the-pattern)
3. [Building Blocks](#building-blocks)
4. [Step-by-Step Examples](#step-by-step-examples)
5. [Exercises](#exercises)
6. [Common Patterns](#common-patterns)
7. [Advanced Topics](#advanced-topics)

## Core Concepts

### What is Discrete Event Simulation?

Discrete Event Simulation (DES) models systems as a sequence of events that occur at specific points in time. Between events, the system state remains unchanged. This is perfect for modeling:
- Customer service systems (banks, coffee shops, call centers)
- Manufacturing processes
- Computer networks
- Transportation systems
- Game AI behaviors

### Why Use Coroutines?

Traditional approaches to simulation often involve complex state machines or callback systems. Coroutines allow us to write simulation logic that looks like normal sequential code:

```python
# Traditional approach (complex state machine)
if self.state == "WAITING_TO_ORDER":
    if current_time >= arrival_time:
        self.state = "ORDERING"
elif self.state == "ORDERING":
    if current_time >= order_complete_time:
        self.state = "WAITING_FOR_COFFEE"
# ... many more states

# Coroutine approach (simple and readable)
yield self.timeline.wait_until(arrival_time)
print("Customer arrives and orders")
yield self.timeline.wait(coffee_prep_time)
print("Customer receives coffee")
```

## The Magic Behind the Pattern

### 1. Agents as Generators

An "agent" is any entity in your simulation that performs actions over time. In our pattern, agents are Python generators that yield scheduling functions:

```python
def customer_agent(timeline):
    # This is a generator function (note the yield statements)
    yield timeline.wait(1.0)  # Wait 1 time unit
    print("Customer action happens here")
    yield timeline.wait(2.0)  # Wait 2 more time units
    print("Another action")
    # When the function returns, the agent is done
```

### 2. The Yield Dance

Here's the clever part: when an agent yields, it doesn't yield data - it yields a **function** that knows how to schedule the agent to resume later:

```python
# Inside the Timeline class
def wait(self, duration):
    def schedule_function(agent):
        # This function "captures" the current time and duration
        self.schedule(self.current_time + duration, agent)
    return schedule_function
```

### 3. The Scheduling Loop

The timeline maintains a priority queue of events, each containing:
- When to execute (time)
- What to execute (the agent/generator to resume)

```python
def run(self):
    while self.event_queue:
        event = heapq.heappop(self.event_queue)  # Get earliest event
        self.current_time = event.time           # Advance time
        start_agent(event.agent)                 # Resume the agent
```

## Building Blocks

Let's examine the key components from our example:

### Event Class
```python
@dataclass(order=True)
class Event:
    time: float
    agent: Any = field(compare=False)  # The generator to resume
```
- Uses `@dataclass` for automatic comparison based on time
- The priority queue uses this comparison to order events

### Timeline Class
```python
class Timeline:
    def __init__(self):
        self.current_time = 0.0
        self.event_queue = []
    
    def schedule(self, time: float, agent: Generator):
        heapq.heappush(self.event_queue, Event(time, agent))
    
    def wait(self, duration: float) -> Callable:
        def schedule_function(agent):
            self.schedule(self.current_time + duration, agent)
        return schedule_function
```

### Start Agent Function
```python
def start_agent(agent: Generator):
    try:
        scheduling_function = next(agent)
        scheduling_function(agent)  # Pass the agent to its own scheduling function
    except StopIteration:
        pass  # Agent has finished
```

## Step-by-Step Examples

### Example 1: Simple Timer

Let's start with the simplest possible example:

```python
def countdown_timer(timeline, name, duration):
    print(f"[{timeline.current_time}] {name} started")
    yield timeline.wait(duration)
    print(f"[{timeline.current_time}] {name} finished!")

# Usage
timeline = Timeline()
start_agent(countdown_timer(timeline, "Timer A", 5.0))
start_agent(countdown_timer(timeline, "Timer B", 3.0))
timeline.run()

# Output:
# [0.0] Timer A started
# [0.0] Timer B started
# [3.0] Timer B finished!
# [5.0] Timer A finished!
```

### Example 2: Sequential Process

A process with multiple stages:

```python
def manufacturing_process(timeline, product_id):
    # Stage 1: Assembly
    print(f"[{timeline.current_time}] Product {product_id}: Starting assembly")
    yield timeline.wait(2.0)
    
    # Stage 2: Quality Check
    print(f"[{timeline.current_time}] Product {product_id}: Quality check")
    yield timeline.wait(0.5)
    
    # Stage 3: Packaging
    print(f"[{timeline.current_time}] Product {product_id}: Packaging")
    yield timeline.wait(1.0)
    
    print(f"[{timeline.current_time}] Product {product_id}: Complete!")
```

### Example 3: Interacting Agents

The coffee shop example shows agents that interact:

```python
def customer(self, name, arrival_time, coffee_type):
    # Wait to arrive
    yield self.timeline.wait_until(arrival_time)
    print(f"[{self.timeline.current_time}] {name} arrives")
    
    # Start a barista (another agent)
    start_agent(self.barista(name, coffee_type))
    
    # Wait for coffee to be ready
    yield self.timeline.wait(coffee_prep_time)
    print(f"[{self.timeline.current_time}] {name} receives coffee")
```

## Exercises

### Exercise 1: Traffic Light
Create a traffic light simulation where:
- The light cycles: Green (30s) → Yellow (5s) → Red (25s)
- Cars arrive randomly and must wait for green
- Track how many cars pass through

### Exercise 2: Elevator System
Model an elevator that:
- Takes 2 seconds to move between floors
- Takes 3 seconds for passengers to enter/exit
- Must serve multiple passenger requests efficiently

### Exercise 3: Restaurant Kitchen
Simulate a kitchen where:
- Orders arrive throughout the day
- Different dishes take different prep times
- Multiple chefs work in parallel
- Some dishes require multiple stages

## Common Patterns

### Pattern 1: Infinite Loop Agent
```python
def monitoring_agent(timeline):
    while True:
        yield timeline.wait(10.0)  # Check every 10 time units
        print(f"[{timeline.current_time}] System check")
```

### Pattern 2: Conditional Waiting
```python
def smart_agent(timeline, condition_checker):
    while not condition_checker():
        yield timeline.wait(1.0)  # Poll every 1 time unit
    print("Condition met!")
```

### Pattern 3: Resource Management
```python
class ResourcePool:
    def __init__(self, timeline, capacity):
        self.timeline = timeline
        self.available = capacity
        self.waiting_agents = []
    
    def acquire(self):
        if self.available > 0:
            self.available -= 1
            yield self.timeline.wait(0)  # Continue immediately
        else:
            # Add to waiting list and suspend
            # (Implementation details omitted for brevity)
```

### Pattern 4: Event Broadcasting
```python
def publisher(timeline, subscribers):
    yield timeline.wait(5.0)
    event_data = "Something happened!"
    
    # Start all subscribers to handle the event
    for subscriber in subscribers:
        start_agent(subscriber(timeline, event_data))
```

## Advanced Topics

### 1. Agent Communication

Agents can communicate through shared state:

```python
class MessageQueue:
    def __init__(self):
        self.messages = []
    
def sender(timeline, queue):
    yield timeline.wait(1.0)
    queue.messages.append("Hello!")
    
def receiver(timeline, queue):
    while not queue.messages:
        yield timeline.wait(0.1)  # Poll for messages
    message = queue.messages.pop(0)
    print(f"Received: {message}")
```

### 2. Priority-Based Scheduling

You can extend events to include priority:

```python
@dataclass(order=True)
class PriorityEvent:
    time: float
    priority: int  # Lower number = higher priority
    agent: Any = field(compare=False)
```

### 3. Stochastic Simulations

Add randomness for more realistic simulations:

```python
import random

def customer_with_random_delay(timeline):
    # Random arrival time between 0 and 5
    arrival = random.uniform(0, 5)
    yield timeline.wait_until(arrival)
    
    # Random service time
    service_time = random.expovariate(1/3.0)  # Exponential distribution
    yield timeline.wait(service_time)
```

### 4. Performance Considerations

- Use `yield from` for delegating to sub-generators
- Consider memory usage with many concurrent agents
- Profile your simulation to find bottlenecks

## Debugging Tips

1. **Add Trace Output**: Include timestamp in all print statements
2. **Visualize the Queue**: Print the event queue state at key points
3. **Step-by-Step Mode**: Modify the timeline to pause between events
4. **Assert Invariants**: Check system state consistency after each event

## Conclusion

The coroutine-based simulation pattern provides a powerful yet intuitive way to model complex time-based systems. By yielding scheduling functions, we can write sequential-looking code that executes over simulated time, making our simulations both efficient and maintainable.

### Next Steps
1. Try implementing the exercises
2. Extend the pattern for your specific domain
3. Explore integration with visualization libraries
4. Consider performance optimizations for large-scale simulations

Remember: The key insight is that agents yield **functions that schedule their own resumption**, not data. This simple pattern enables sophisticated time-based behaviors with remarkably clean code.