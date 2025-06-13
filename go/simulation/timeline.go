package simulation

import (
	"container/heap"
	"fmt"
)

// ScheduleFunc is a function that schedules an agent to resume later
type ScheduleFunc func(agent Agent)

// Agent represents an entity that can be scheduled and executed
type Agent interface {
	// Next should return the next scheduling function, or nil if done
	Next() ScheduleFunc
}

// Event represents a scheduled event in the simulation
type Event struct {
	Time  float64
	Agent Agent
}

// EventQueue implements a priority queue for events using Go's heap interface
type EventQueue []*Event

func (eq EventQueue) Len() int { return len(eq) }

func (eq EventQueue) Less(i, j int) bool {
	return eq[i].Time < eq[j].Time
}

func (eq EventQueue) Swap(i, j int) {
	eq[i], eq[j] = eq[j], eq[i]
}

func (eq *EventQueue) Push(x interface{}) {
	*eq = append(*eq, x.(*Event))
}

func (eq *EventQueue) Pop() interface{} {
	old := *eq
	n := len(old)
	event := old[n-1]
	*eq = old[0 : n-1]
	return event
}

// Timeline manages simulation time and schedules agent execution
type Timeline struct {
	CurrentTime float64
	eventQueue  *EventQueue
}

// NewTimeline creates a new timeline
func NewTimeline() *Timeline {
	eq := &EventQueue{}
	heap.Init(eq)
	return &Timeline{
		CurrentTime: 0.0,
		eventQueue:  eq,
	}
}

// Schedule schedules an agent to resume at a specific time
func (t *Timeline) Schedule(time float64, agent Agent) error {
	if time < t.CurrentTime {
		return fmt.Errorf("cannot schedule event in the past: %f < %f", time, t.CurrentTime)
	}
	heap.Push(t.eventQueue, &Event{Time: time, Agent: agent})
	return nil
}

// Wait returns a scheduling function that resumes the agent after duration
func (t *Timeline) Wait(duration float64) ScheduleFunc {
	return func(agent Agent) {
		t.Schedule(t.CurrentTime+duration, agent)
	}
}

// WaitUntil returns a scheduling function that resumes the agent at specific time
func (t *Timeline) WaitUntil(time float64) ScheduleFunc {
	return func(agent Agent) {
		t.Schedule(time, agent)
	}
}

// Run executes the simulation until no more events remain
func (t *Timeline) Run() {
	for t.eventQueue.Len() > 0 {
		event := heap.Pop(t.eventQueue).(*Event)
		t.CurrentTime = event.Time
		StartAgent(event.Agent)
	}
}

// HasEvents returns true if there are pending events
func (t *Timeline) HasEvents() bool {
	return t.eventQueue.Len() > 0
}