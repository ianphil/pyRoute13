# Go Coroutine-Based Discrete Event Simulation Framework

A Go port of the Python coroutine-based discrete event simulation framework. This demonstrates how to build time-based simulations using Go's interfaces, channels, and priority queues.

## Overview

This framework allows you to write complex sequential behaviors that execute over simulated time, making it perfect for modeling systems where multiple entities perform actions concurrently such as:

- Customer service systems (banks, coffee shops, call centers)
- Manufacturing processes  
- Computer networks
- Transportation systems
- Game AI behaviors

## Key Concepts

- **Agents**: Entities that perform actions over time, implemented as Go interfaces
- **Timeline**: Manages simulation time and schedules agent execution using a priority queue
- **Events**: Scheduled points in time when agents resume execution
- **Scheduling Functions**: Functions that agents yield to schedule their own resumption

## Architecture

### Core Components

- `timeline.go`: Timeline, Event, and priority queue implementation
- `agent.go`: Agent interface and various agent implementations  
- `examples.go`: Example simulations (coffee shop, manufacturing, network requests)
- `main.go`: CLI entry point to run examples

### Agent Types

1. **SimpleAgent**: Basic function-based agent
2. **GeneratorAgent**: Python generator-like sequential steps  
3. **CoroutineAgent**: Uses channels for sophisticated coroutine behavior
4. **Custom Agents**: Implement the Agent interface directly

## Usage

### Running Examples

```bash
# Run specific examples
go run main.go coffee        # Coffee shop simulation
go run main.go manufacturing # Manufacturing line simulation  
go run main.go network       # Network requests with retries
go run main.go all          # Run all examples

# Build and run
go build -o simulator
./simulator coffee
```

### Creating Your Own Simulation

```go
package main

import (
    "fmt"
    "github.com/ianphil/goRoute13/simulation"
)

// Simple timer example
func createTimer(timeline *simulation.Timeline, name string, duration float64) simulation.Agent {
    steps := []func(*simulation.Timeline) simulation.ScheduleFunc{
        func(t *simulation.Timeline) simulation.ScheduleFunc {
            fmt.Printf("[%.1f] %s started\n", t.CurrentTime, name)
            return t.Wait(duration)
        },
        func(t *simulation.Timeline) simulation.ScheduleFunc {
            fmt.Printf("[%.1f] %s finished!\n", t.CurrentTime, name)
            return nil // Done
        },
    }
    return simulation.NewGeneratorAgent(timeline, steps)
}

func main() {
    timeline := simulation.NewTimeline()
    
    // Start multiple timers
    simulation.StartAgent(createTimer(timeline, "Timer A", 5.0))
    simulation.StartAgent(createTimer(timeline, "Timer B", 3.0))
    
    timeline.Run()
}
```

## Go-Specific Features

### Priority Queue
Uses Go's `container/heap` for efficient event scheduling:

```go
type EventQueue []*Event

func (eq EventQueue) Len() int { return len(eq) }
func (eq EventQueue) Less(i, j int) bool { return eq[i].Time < eq[j].Time }
// ... heap.Interface implementation
```

### Agent Interface
Clean interface design for different agent types:

```go
type Agent interface {
    Next() ScheduleFunc
}

type ScheduleFunc func(agent Agent)
```

### Goroutine Integration
CoroutineAgent uses channels for advanced patterns:

```go
agent := simulation.NewCoroutineAgent(func(timeline *simulation.Timeline, yield chan<- simulation.ScheduleFunc) {
    yield <- timeline.Wait(1.0)
    fmt.Println("Action after 1 time unit")
    yield <- timeline.Wait(2.0)  
    fmt.Println("Action after 2 more time units")
})
```

## Examples

### Coffee Shop
Simulates customers arriving, ordering different coffee types, and baristas preparing orders with realistic timing.

### Manufacturing Line
Models products moving through assembly, quality check, and packaging stages.

### Network Requests  
Demonstrates retry logic with exponential backoff for failed network requests.

## Building and Testing

```bash
# Build
go build

# Run tests (when implemented)
go test ./...

# Run with specific example
go run main.go coffee
```

## Differences from Python Version

- Uses Go interfaces instead of Python generators
- Priority queue implemented with `container/heap`
- Multiple agent implementation patterns (SimpleAgent, GeneratorAgent, CoroutineAgent)
- Channels used for advanced coroutine-like behavior
- Strongly typed with Go's type system
- No external dependencies required

## Next Steps

- Add unit tests for all components
- Implement more complex examples  
- Add visualization support
- Performance benchmarking for large simulations
- Integration with Go's profiling tools