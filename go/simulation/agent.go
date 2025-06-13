package simulation

// StartAgent resumes an agent by calling Next() and executing the returned scheduling function
func StartAgent(agent Agent) {
	if scheduleFunc := agent.Next(); scheduleFunc != nil {
		scheduleFunc(agent)
	}
}

// SimpleAgent is a concrete implementation of Agent using a function generator pattern
type SimpleAgent struct {
	generator func() ScheduleFunc
	done      bool
}

// NewSimpleAgent creates a new SimpleAgent with a generator function
func NewSimpleAgent(generator func() ScheduleFunc) *SimpleAgent {
	return &SimpleAgent{
		generator: generator,
		done:      false,
	}
}

// Next implements the Agent interface
func (sa *SimpleAgent) Next() ScheduleFunc {
	if sa.done {
		return nil
	}
	
	scheduleFunc := sa.generator()
	if scheduleFunc == nil {
		sa.done = true
	}
	return scheduleFunc
}

// CoroutineAgent implements a more sophisticated agent using channels for coroutine-like behavior
type CoroutineAgent struct {
	stepChan chan ScheduleFunc
	doneChan chan bool
	started  bool
}

// NewCoroutineAgent creates a new CoroutineAgent
func NewCoroutineAgent(agentFunc func(*Timeline, chan<- ScheduleFunc)) *CoroutineAgent {
	stepChan := make(chan ScheduleFunc, 1)
	doneChan := make(chan bool, 1)
	
	agent := &CoroutineAgent{
		stepChan: stepChan,
		doneChan: doneChan,
		started:  false,
	}
	
	// Start the agent goroutine
	go func() {
		defer func() {
			close(stepChan)
			doneChan <- true
		}()
		
		// Create a mock timeline for the agent function
		timeline := NewTimeline()
		agentFunc(timeline, stepChan)
	}()
	
	return agent
}

// Next implements the Agent interface
func (ca *CoroutineAgent) Next() ScheduleFunc {
	select {
	case scheduleFunc, ok := <-ca.stepChan:
		if !ok {
			return nil // Channel closed, agent is done
		}
		return scheduleFunc
	case <-ca.doneChan:
		return nil // Agent completed
	}
}

// GeneratorAgent provides a Python generator-like interface for Go
type GeneratorAgent struct {
	steps []func(*Timeline) ScheduleFunc
	index int
	timeline *Timeline
}

// NewGeneratorAgent creates a new GeneratorAgent with predefined steps
func NewGeneratorAgent(timeline *Timeline, steps []func(*Timeline) ScheduleFunc) *GeneratorAgent {
	return &GeneratorAgent{
		steps:    steps,
		index:    0,
		timeline: timeline,
	}
}

// Next implements the Agent interface
func (ga *GeneratorAgent) Next() ScheduleFunc {
	if ga.index >= len(ga.steps) {
		return nil // No more steps
	}
	
	step := ga.steps[ga.index]
	ga.index++
	return step(ga.timeline)
}