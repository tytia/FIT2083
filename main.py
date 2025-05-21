from parking import MultiLevelCarPark
from drivers import BottomUpDriver, TopDownDriver
import numpy as np
import sys

def main() -> None:
    # Initialize the carpark and drivers
    carpark = MultiLevelCarPark(levels=6, rows=10, cols=20)
    bottom_up_driver = BottomUpDriver(carpark)
    top_down_driver = TopDownDriver(carpark)
    sample_size = 1001

    try:
        capacities = list(map(float, sys.argv[1:]))
    except ValueError:
        print("Invalid input. Please provide capacities as floating point numbers.")
        return

    for i, capacity in enumerate(capacities):
        print(f"\nCapacity: {int(capacity * 100)}%")
        bottom_up_times, top_down_times = [], []
        for k in range(sample_size):
            # Set the capacity of the carpark
            carpark.set_capacity(capacity, seed=k + (i * sample_size))
            # Simulate the drivers moving through the carpark
            bottom_up_times.append(bottom_up_driver.search_for_parking())
            top_down_times.append(top_down_driver.search_for_parking())
            # Reset the drivers for the next iteration
            bottom_up_driver.reset()
            top_down_driver.reset()
        
        # calculate mean, median, stdev, min and max
        mean = np.mean(bottom_up_times)
        median = np.median(bottom_up_times)
        stdev = np.std(bottom_up_times)
        print(f"Bottom Up Driver - Mean: {mean:.2f}, Median: {median:.2f}, Stdev: {stdev:.2f}, Min: {min(bottom_up_times):.2f}, Max: {max(bottom_up_times):.2f}")
        
        mean = np.mean(top_down_times)
        median = np.median(top_down_times)
        stdev = np.std(top_down_times)
        print(f"Top Down Driver - Mean: {mean:.2f}, Median: {median:.2f}, Stdev: {stdev:.2f}, Min: {min(top_down_times):.2f}, Max: {max(top_down_times):.2f}")

if __name__ == "__main__":
    main()
    # visualization
    # carpark = MultiLevelCarPark(levels=6, rows=10, cols=20)
    # carpark.set_capacity(0.95, seed=3)
    # bottom_up_driver = BottomUpDriver(carpark)
    # bottom_up_driver.search_for_parking(visualize=True, delay=0.1)
    # # top_down_driver = TopDownDriver(carpark)
    # # top_down_driver.search_for_parking(visualize=True, delay=0.3)