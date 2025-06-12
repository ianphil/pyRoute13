#!/usr/bin/env python
"""
Simplified Coroutine-Based Discrete Event Simulation Framework

This demonstrates how to build a time-based simulation using Python generators
(coroutines) and a priority queue. This pattern allows writing complex 
sequential behaviors that execute over simulated time.

Key concepts:
- Agents are generators that yield scheduling functions
- Timeline manages a priority queue of future events
- Events resume agents at specific simulation times
"""

import heapq
from typing import Generator, Callable, Any
from dataclasses import dataclass, field


@dataclass(order=True)
class Event:
    """An event scheduled to occur at a specific time."""
    time: float
    agent: Any = field(compare=False)  # The generator to resume
    
    def __repr__(self):
        return f"Event(time={self.time})"


class Timeline:
    """Manages simulation time and schedules agent execution."""
    
    def __init__(self):
        self.current_time = 0.0
        self.event_queue = []
        
    def schedule(self, time: float, agent: Generator):
        """Schedule an agent to resume at a specific time."""
        if time < self.current_time:
            raise ValueError(f"Cannot schedule event in the past: {time} < {self.current_time}")
        heapq.heappush(self.event_queue, Event(time, agent))
        
    def wait(self, duration: float) -> Callable:
        """Returns a function that schedules the agent to resume after duration."""
        def schedule_function(agent):
            self.schedule(self.current_time + duration, agent)
        return schedule_function
        
    def wait_until(self, time: float) -> Callable:
        """Returns a function that schedules the agent to resume at specific time."""
        def schedule_function(agent):
            self.schedule(time, agent)
        return schedule_function
        
    def run(self):
        """Run the simulation until no more events."""
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            start_agent(event.agent)
            

def start_agent(agent: Generator):
    """Resume an agent by calling next() and executing the yielded function."""
    try:
        scheduling_function = next(agent)
        if callable(scheduling_function):
            scheduling_function(agent)
        else:
            raise TypeError(f"Agent yielded non-callable: {scheduling_function}")
    except StopIteration:
        # Agent has finished
        pass


# ============================================================================
# EXAMPLE: Coffee Shop Simulation
# ============================================================================

class CoffeeShop:
    """Example simulation: A coffee shop with customers and baristas."""
    
    def __init__(self, timeline: Timeline):
        self.timeline = timeline
        self.orders_completed = 0
        self.customers_served = []
        
    def customer(self, name: str, arrival_time: float, coffee_type: str):
        """A customer agent that arrives, orders, and receives coffee."""
        # Wait until arrival time
        yield self.timeline.wait_until(arrival_time)
        print(f"[{self.timeline.current_time:5.1f}] {name} arrives and orders {coffee_type}")
        
        # Start the barista making coffee
        start_agent(self.barista(name, coffee_type))
        
        # Wait for coffee (different times for different types)
        wait_times = {"espresso": 2.0, "latte": 3.0, "cappuccino": 3.5}
        yield self.timeline.wait(wait_times.get(coffee_type, 2.5))
        
        # Receive coffee
        print(f"[{self.timeline.current_time:5.1f}] {name} receives {coffee_type} and leaves happy!")
        self.customers_served.append(name)
        
    def barista(self, customer_name: str, coffee_type: str):
        """A barista agent that makes coffee."""
        print(f"[{self.timeline.current_time:5.1f}] Barista starts making {coffee_type} for {customer_name}")
        
        # Grind beans
        yield self.timeline.wait(0.5)
        print(f"[{self.timeline.current_time:5.1f}] - Grinding beans...")
        
        # Brew
        yield self.timeline.wait(1.0)
        print(f"[{self.timeline.current_time:5.1f}] - Brewing...")
        
        # Add milk for lattes and cappuccinos
        if coffee_type in ["latte", "cappuccino"]:
            yield self.timeline.wait(0.5)
            print(f"[{self.timeline.current_time:5.1f}] - Steaming milk...")
            
        self.orders_completed += 1


# ============================================================================
# EXAMPLE: Simple Manufacturing Line
# ============================================================================

class ManufacturingLine:
    """Example simulation: A simple manufacturing process."""
    
    def __init__(self, timeline: Timeline):
        self.timeline = timeline
        self.completed_products = 0
        
    def product(self, product_id: int):
        """A product moving through manufacturing stages."""
        print(f"[{self.timeline.current_time:5.1f}] Product {product_id} starts manufacturing")
        
        # Stage 1: Assembly
        yield self.timeline.wait(2.0)
        print(f"[{self.timeline.current_time:5.1f}] Product {product_id} - Assembly complete")
        
        # Stage 2: Quality Check
        yield self.timeline.wait(0.5)
        print(f"[{self.timeline.current_time:5.1f}] Product {product_id} - Quality check passed")
        
        # Stage 3: Packaging
        yield self.timeline.wait(1.0)
        print(f"[{self.timeline.current_time:5.1f}] Product {product_id} - Packaging complete")
        
        self.completed_products += 1
        print(f"[{self.timeline.current_time:5.1f}] Product {product_id} finished! Total: {self.completed_products}")


# ============================================================================
# EXAMPLE: Network Request Simulation
# ============================================================================

class NetworkSimulation:
    """Example simulation: Network requests with retries."""
    
    def __init__(self, timeline: Timeline):
        self.timeline = timeline
        self.successful_requests = 0
        self.failed_requests = 0
        
    def request(self, request_id: int, url: str, max_retries: int = 3):
        """A network request that might need retries."""
        attempt = 0
        
        while attempt < max_retries:
            print(f"[{self.timeline.current_time:5.1f}] Request {request_id} to {url} - Attempt {attempt + 1}")
            
            # Simulate network delay
            yield self.timeline.wait(0.1 + attempt * 0.5)  # Exponential backoff
            
            # Simulate success/failure (would be actual network call)
            import random
            if random.random() > 0.3:  # 70% success rate
                print(f"[{self.timeline.current_time:5.1f}] Request {request_id} succeeded!")
                self.successful_requests += 1
                return
            else:
                print(f"[{self.timeline.current_time:5.1f}] Request {request_id} failed, retrying...")
                attempt += 1
                
        print(f"[{self.timeline.current_time:5.1f}] Request {request_id} failed after {max_retries} attempts")
        self.failed_requests += 1


def run_examples():
    """Run all example simulations."""
    
    print("=" * 70)
    print("COFFEE SHOP SIMULATION")
    print("=" * 70)
    
    timeline = Timeline()
    shop = CoffeeShop(timeline)
    
    # Schedule customers
    start_agent(shop.customer("Alice", arrival_time=0.0, coffee_type="espresso"))
    start_agent(shop.customer("Bob", arrival_time=0.5, coffee_type="latte"))
    start_agent(shop.customer("Charlie", arrival_time=1.0, coffee_type="cappuccino"))
    
    timeline.run()
    print(f"\nSimulation complete! Served {len(shop.customers_served)} customers")
    
    print("\n" + "=" * 70)
    print("MANUFACTURING LINE SIMULATION")
    print("=" * 70)
    
    timeline = Timeline()
    factory = ManufacturingLine(timeline)
    
    # Start manufacturing products at different times
    for i in range(3):
        start_agent(factory.product(product_id=i+1))
        # Stagger the starts
        if i < 2:
            start_agent(delay_start(timeline, i * 1.5))
            
    timeline.run()
    print(f"\nManufactured {factory.completed_products} products")
    
    print("\n" + "=" * 70)
    print("NETWORK REQUEST SIMULATION")
    print("=" * 70)
    
    timeline = Timeline()
    network = NetworkSimulation(timeline)
    
    # Simulate multiple concurrent requests
    urls = ["api.example.com", "data.service.io", "backend.app.net"]
    for i, url in enumerate(urls):
        start_agent(network.request(request_id=i+1, url=url))
        
    timeline.run()
    print(f"\nSuccessful: {network.successful_requests}, Failed: {network.failed_requests}")


def delay_start(timeline: Timeline, delay: float):
    """Helper to delay starting the next product."""
    yield timeline.wait(delay)


if __name__ == "__main__":
    run_examples()