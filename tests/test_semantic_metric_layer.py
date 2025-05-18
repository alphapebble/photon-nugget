"""
Test the semantic metric layer.
"""
import sys
import os
import time
import math
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

from core.semantic_metric_layer import get_constant, evaluate_formula

def test_get_constant():
    """Test getting constants from the semantic metric layer."""
    print("Testing get_constant...")
    
    # Test getting a constant
    irradiance = get_constant('solar_panel.stc.irradiance')
    print(f"solar_panel.stc.irradiance = {irradiance}")
    assert irradiance == 1000.0
    
    # Test getting a nested constant
    rain_factor = get_constant('solar_panel.weather_impact.rain_factor')
    print(f"solar_panel.weather_impact.rain_factor = {rain_factor}")
    assert rain_factor == 0.7
    
    # Test getting a non-existent constant
    non_existent = get_constant('non.existent.constant')
    print(f"non.existent.constant = {non_existent}")
    assert non_existent is None
    
    print("get_constant tests passed!\n")

def test_evaluate_formula():
    """Test evaluating formulas from the semantic metric layer."""
    print("Testing evaluate_formula...")
    
    # Test evaluating a simple formula
    params = {'cloud_cover': 50}
    cloud_impact = evaluate_formula('solar_irradiance.cloud_impact', params)
    print(f"solar_irradiance.cloud_impact with cloud_cover=50 = {cloud_impact}")
    assert abs(cloud_impact - 0.625) < 0.001
    
    # Test evaluating a more complex formula
    params = {
        'day_of_year': 180,
        'radians': math.radians,
        'sin': math.sin
    }
    declination = evaluate_formula('solar_irradiance.declination_angle', params)
    print(f"solar_irradiance.declination_angle with day_of_year=180 = {declination}")
    assert abs(declination - 23.45 * math.sin(math.radians(360 * (284 + 180) / 365))) < 0.001
    
    # Test evaluating a formula with max/min functions
    params = {'demand': 100, 'production': 80}
    grid_purchases = evaluate_formula('financial.grid_purchases', params)
    print(f"financial.grid_purchases with demand=100, production=80 = {grid_purchases}")
    assert grid_purchases == 20
    
    print("evaluate_formula tests passed!\n")

def test_performance():
    """Test the performance of the semantic metric layer."""
    print("Testing performance...")
    
    # Parameters for the test
    iterations = 10000
    
    # Test formula evaluation performance
    params = {'cloud_cover': 50}
    
    start_time = time.time()
    for _ in range(iterations):
        evaluate_formula('solar_irradiance.cloud_impact', params)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(f"Evaluated 'solar_irradiance.cloud_impact' {iterations} times in {elapsed_time:.4f} seconds")
    print(f"Average time per evaluation: {(elapsed_time / iterations) * 1000:.4f} ms")
    
    print("Performance test completed!\n")

def main():
    """Run all tests."""
    print("Testing the semantic metric layer...\n")
    
    test_get_constant()
    test_evaluate_formula()
    test_performance()
    
    print("All tests passed!")

if __name__ == "__main__":
    main()
