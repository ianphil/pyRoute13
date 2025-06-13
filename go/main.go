package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/ianphil/goRoute13/simulation"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		return
	}

	example := strings.ToLower(os.Args[1])
	
	switch example {
	case "coffee", "coffeeshop":
		runCoffeeShopExample()
	case "manufacturing", "factory":
		runManufacturingExample()
	case "network", "requests":
		runNetworkExample()
	case "all":
		runAllExamples()
	default:
		fmt.Printf("Unknown example: %s\n", example)
		printUsage()
	}
}

func printUsage() {
	fmt.Println("Usage: go run main.go <example>")
	fmt.Println()
	fmt.Println("Available examples:")
	fmt.Println("  coffee         - Coffee shop simulation with customers and baristas")
	fmt.Println("  manufacturing  - Manufacturing line with sequential stages")
	fmt.Println("  network        - Network requests with retry logic")
	fmt.Println("  all            - Run all examples")
}

func runCoffeeShopExample() {
	fmt.Println(strings.Repeat("=", 70))
	fmt.Println("COFFEE SHOP SIMULATION")
	fmt.Println(strings.Repeat("=", 70))

	timeline := simulation.NewTimeline()
	shop := simulation.NewCoffeeShop(timeline)

	// Schedule customers
	simulation.StartAgent(shop.Customer("Alice", 0.0, "espresso"))
	simulation.StartAgent(shop.Customer("Bob", 0.5, "latte"))
	simulation.StartAgent(shop.Customer("Charlie", 1.0, "cappuccino"))

	timeline.Run()
	fmt.Printf("\nSimulation complete! Served %d customers\n", len(shop.GetCustomersServed()))
	fmt.Printf("Orders completed: %d\n", shop.GetOrdersCompleted())
}

func runManufacturingExample() {
	fmt.Println(strings.Repeat("=", 70))
	fmt.Println("MANUFACTURING LINE SIMULATION")
	fmt.Println(strings.Repeat("=", 70))

	timeline := simulation.NewTimeline()
	factory := simulation.NewManufacturingLine(timeline)

	// Start manufacturing products at different times
	simulation.StartAgent(factory.Product(1))
	
	// Stagger subsequent products
	simulation.StartAgent(simulation.NewGeneratorAgent(timeline, []func(*simulation.Timeline) simulation.ScheduleFunc{
		func(t *simulation.Timeline) simulation.ScheduleFunc {
			return t.Wait(1.5)
		},
		func(t *simulation.Timeline) simulation.ScheduleFunc {
			simulation.StartAgent(factory.Product(2))
			return t.Wait(1.5)
		},
		func(t *simulation.Timeline) simulation.ScheduleFunc {
			simulation.StartAgent(factory.Product(3))
			return nil
		},
	}))

	timeline.Run()
	fmt.Printf("\nManufactured %d products\n", factory.GetCompletedProducts())
}

func runNetworkExample() {
	fmt.Println(strings.Repeat("=", 70))
	fmt.Println("NETWORK REQUEST SIMULATION")
	fmt.Println(strings.Repeat("=", 70))

	timeline := simulation.NewTimeline()
	network := simulation.NewNetworkSimulation(timeline)

	// Simulate multiple concurrent requests
	urls := []string{"api.example.com", "data.service.io", "backend.app.net"}
	for i, url := range urls {
		simulation.StartAgent(network.Request(i+1, url, 3))
	}

	timeline.Run()
	successful, failed := network.GetRequestStats()
	fmt.Printf("\nSuccessful: %d, Failed: %d\n", successful, failed)
}

func runAllExamples() {
	runCoffeeShopExample()
	fmt.Println()
	
	runManufacturingExample()
	fmt.Println()
	
	runNetworkExample()
}