package simulation

import (
	"fmt"
	"math/rand"
	"time"
)

// CoffeeShop simulation example
type CoffeeShop struct {
	timeline         *Timeline
	ordersCompleted  int
	customersServed  []string
}

func NewCoffeeShop(timeline *Timeline) *CoffeeShop {
	return &CoffeeShop{
		timeline:        timeline,
		ordersCompleted: 0,
		customersServed: make([]string, 0),
	}
}

// GetCustomersServed returns the list of served customers
func (cs *CoffeeShop) GetCustomersServed() []string {
	return cs.customersServed
}

// GetOrdersCompleted returns the number of completed orders
func (cs *CoffeeShop) GetOrdersCompleted() int {
	return cs.ordersCompleted
}

// Customer creates a customer agent
func (cs *CoffeeShop) Customer(name string, arrivalTime float64, coffeeType string) Agent {
	steps := []func(*Timeline) ScheduleFunc{
		// Wait until arrival time
		func(t *Timeline) ScheduleFunc {
			return t.WaitUntil(arrivalTime)
		},
		// Arrive and order
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] %s arrives and orders %s\n", t.CurrentTime, name, coffeeType)
			
			// Start barista
			StartAgent(cs.Barista(name, coffeeType))
			
			// Wait for coffee preparation
			waitTimes := map[string]float64{
				"espresso":   2.0,
				"latte":      3.0,
				"cappuccino": 3.5,
			}
			waitTime, exists := waitTimes[coffeeType]
			if !exists {
				waitTime = 2.5
			}
			return t.Wait(waitTime)
		},
		// Receive coffee
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] %s receives %s and leaves happy!\n", t.CurrentTime, name, coffeeType)
			cs.customersServed = append(cs.customersServed, name)
			return nil // Done
		},
	}
	
	return NewGeneratorAgent(cs.timeline, steps)
}

// Barista creates a barista agent
func (cs *CoffeeShop) Barista(customerName string, coffeeType string) Agent {
	steps := []func(*Timeline) ScheduleFunc{
		// Start making coffee
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] Barista starts making %s for %s\n", t.CurrentTime, coffeeType, customerName)
			return t.Wait(0.5)
		},
		// Grind beans
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] - Grinding beans...\n", t.CurrentTime)
			return t.Wait(1.0)
		},
		// Brew
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] - Brewing...\n", t.CurrentTime)
			if coffeeType == "latte" || coffeeType == "cappuccino" {
				return t.Wait(0.5)
			}
			return nil // Skip milk steaming for espresso
		},
		// Steam milk (if needed)
		func(t *Timeline) ScheduleFunc {
			if coffeeType == "latte" || coffeeType == "cappuccino" {
				fmt.Printf("[%5.1f] - Steaming milk...\n", t.CurrentTime)
			}
			cs.ordersCompleted++
			return nil // Done
		},
	}
	
	return NewGeneratorAgent(cs.timeline, steps)
}

// ManufacturingLine simulation example
type ManufacturingLine struct {
	timeline           *Timeline
	completedProducts  int
}

func NewManufacturingLine(timeline *Timeline) *ManufacturingLine {
	return &ManufacturingLine{
		timeline:          timeline,
		completedProducts: 0,
	}
}

// GetCompletedProducts returns the number of completed products
func (ml *ManufacturingLine) GetCompletedProducts() int {
	return ml.completedProducts
}

// Product creates a product agent going through manufacturing stages
func (ml *ManufacturingLine) Product(productID int) Agent {
	steps := []func(*Timeline) ScheduleFunc{
		// Start manufacturing
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] Product %d starts manufacturing\n", t.CurrentTime, productID)
			return t.Wait(2.0)
		},
		// Assembly complete
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] Product %d - Assembly complete\n", t.CurrentTime, productID)
			return t.Wait(0.5)
		},
		// Quality check
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] Product %d - Quality check passed\n", t.CurrentTime, productID)
			return t.Wait(1.0)
		},
		// Packaging complete
		func(t *Timeline) ScheduleFunc {
			fmt.Printf("[%5.1f] Product %d - Packaging complete\n", t.CurrentTime, productID)
			ml.completedProducts++
			fmt.Printf("[%5.1f] Product %d finished! Total: %d\n", t.CurrentTime, productID, ml.completedProducts)
			return nil // Done
		},
	}
	
	return NewGeneratorAgent(ml.timeline, steps)
}

// NetworkSimulation example with retries
type NetworkSimulation struct {
	timeline           *Timeline
	successfulRequests int
	failedRequests     int
	rng               *rand.Rand
}

func NewNetworkSimulation(timeline *Timeline) *NetworkSimulation {
	return &NetworkSimulation{
		timeline:           timeline,
		successfulRequests: 0,
		failedRequests:     0,
		rng:               rand.New(rand.NewSource(time.Now().UnixNano())),
	}
}

// GetRequestStats returns successful and failed request counts
func (ns *NetworkSimulation) GetRequestStats() (int, int) {
	return ns.successfulRequests, ns.failedRequests
}

// Request creates a network request agent with retry logic
func (ns *NetworkSimulation) Request(requestID int, url string, maxRetries int) Agent {
	return &RequestAgent{
		timeline:    ns.timeline,
		requestID:   requestID,
		url:         url,
		maxRetries:  maxRetries,
		attempt:     0,
		simulation:  ns,
		currentStep: 0,
	}
}

// RequestAgent is a custom agent for handling network request retry logic
type RequestAgent struct {
	timeline    *Timeline
	requestID   int
	url         string
	maxRetries  int
	attempt     int
	simulation  *NetworkSimulation
	currentStep int
	done        bool
}

func (ra *RequestAgent) Next() ScheduleFunc {
	if ra.done {
		return nil
	}
	
	switch ra.currentStep {
	case 0: // Make request attempt
		if ra.attempt >= ra.maxRetries {
			fmt.Printf("[%5.1f] Request %d failed after %d attempts\n", ra.timeline.CurrentTime, ra.requestID, ra.maxRetries)
			ra.simulation.failedRequests++
			ra.done = true
			return nil
		}
		
		fmt.Printf("[%5.1f] Request %d to %s - Attempt %d\n", ra.timeline.CurrentTime, ra.requestID, ra.url, ra.attempt+1)
		
		// Exponential backoff delay
		delay := 0.1 + float64(ra.attempt)*0.5
		ra.attempt++
		ra.currentStep = 1
		
		return ra.timeline.Wait(delay)
		
	case 1: // Check result
		// Simulate 70% success rate
		if ra.simulation.rng.Float64() > 0.3 {
			fmt.Printf("[%5.1f] Request %d succeeded!\n", ra.timeline.CurrentTime, ra.requestID)
			ra.simulation.successfulRequests++
			ra.done = true
			return nil
		} else {
			fmt.Printf("[%5.1f] Request %d failed, retrying...\n", ra.timeline.CurrentTime, ra.requestID)
			ra.currentStep = 0 // Go back to retry
			return ra.timeline.Wait(0) // Continue immediately
		}
	}
	
	ra.done = true
	return nil
}