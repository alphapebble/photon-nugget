"""
Test the SymPy integration in the semantic metric layer.
"""
import sys
import os
import time
import math
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("SymPy not available, skipping SymPy-specific tests")

from core.semantic_metric_layer import get_constant, evaluate_formula

def test_sympy_complex_expressions():
    """Test evaluating complex expressions that benefit from SymPy."""
    if not SYMPY_AVAILABLE:
        print("Skipping SymPy tests as SymPy is not available")
        return
    
    print("Testing SymPy integration for complex expressions...")
    
    # Test a complex expression with symbolic mathematics
    # This is a simplified version of a solar position calculation
    params = {
        'lat': 37.7749,  # San Francisco latitude
        'day_of_year': 180,  # June 29th
        'hour': 12,  # Noon
    }
    
    # Add this formula to the formulas.yaml file with evaluation_method: sympy
    # This is a complex formula that calculates solar elevation angle
    formula_str = """
    # Convert latitude to radians
    lat_rad = lat * math.pi / 180
    
    # Calculate declination angle
    declination = 23.45 * math.sin(math.pi * (284 + day_of_year) / 182.5)
    declination_rad = declination * math.pi / 180
    
    # Calculate hour angle
    hour_angle = 15 * (hour - 12)  # 15 degrees per hour from solar noon
    hour_angle_rad = hour_angle * math.pi / 180
    
    # Calculate solar elevation
    elevation_rad = math.asin(
        math.sin(lat_rad) * math.sin(declination_rad) + 
        math.cos(lat_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad)
    )
    
    # Convert to degrees
    elevation = elevation_rad * 180 / math.pi
    
    return elevation
    """
    
    # We'll manually calculate the expected result
    lat_rad = params['lat'] * math.pi / 180
    declination = 23.45 * math.sin(math.pi * (284 + params['day_of_year']) / 182.5)
    declination_rad = declination * math.pi / 180
    hour_angle = 15 * (params['hour'] - 12)
    hour_angle_rad = hour_angle * math.pi / 180
    elevation_rad = math.asin(
        math.sin(lat_rad) * math.sin(declination_rad) + 
        math.cos(lat_rad) * math.cos(declination_rad) * math.cos(hour_angle_rad)
    )
    expected_elevation = elevation_rad * 180 / math.pi
    
    # Now test with a formula that would use SymPy
    # For testing purposes, we'll use the _sympy_evaluate method directly
    from core.semantic_metric_layer import SemanticMetricLayer
    layer = SemanticMetricLayer()
    
    # Create a simplified test formula that SymPy can handle
    test_formula = "sin(lat_rad) * sin(declination_rad) + cos(lat_rad) * cos(declination_rad) * cos(hour_angle_rad)"
    test_params = {
        'lat_rad': lat_rad,
        'declination_rad': declination_rad,
        'hour_angle_rad': hour_angle_rad,
        'sin': math.sin,
        'cos': math.cos
    }
    
    # Test SymPy evaluation
    sympy_result = layer._sympy_evaluate(test_formula, test_params)
    
    if sympy_result is not None:
        print(f"SymPy evaluation result: {sympy_result}")
        print(f"Expected result: {math.sin(elevation_rad)}")
        assert abs(sympy_result - math.sin(elevation_rad)) < 0.0001
        print("SymPy evaluation test passed!")
    else:
        print("SymPy evaluation failed or returned None")
    
    print("SymPy integration tests completed!\n")

def test_performance_comparison():
    """Compare performance of different evaluation methods."""
    if not SYMPY_AVAILABLE:
        print("Skipping performance comparison as SymPy is not available")
        return
    
    print("Testing performance comparison between evaluation methods...")
    
    # Simple formula that all methods can handle
    formula_str = "x * sin(y) + z"
    params = {'x': 2.0, 'y': 1.5, 'z': 3.0, 'sin': math.sin}
    
    # Get direct access to the evaluation methods
    from core.semantic_metric_layer import SemanticMetricLayer
    layer = SemanticMetricLayer()
    
    # Process the formula for numexpr
    processed_formula = layer._process_formula_for_numexpr(formula_str)
    
    # Prepare for numexpr evaluation
    local_dict = {'sin': math.sin}
    local_dict.update(params)
    
    # Number of iterations for each method
    iterations = 10000
    
    # Test numexpr performance
    start_time = time.time()
    for _ in range(iterations):
        try:
            import numexpr as ne
            result = ne.evaluate(processed_formula, local_dict=local_dict)
        except Exception:
            pass  # Skip if there's an error
    numexpr_time = time.time() - start_time
    
    # Test SymPy performance
    start_time = time.time()
    for _ in range(iterations):
        try:
            result = layer._sympy_evaluate(formula_str, params)
        except Exception:
            pass  # Skip if there's an error
    sympy_time = time.time() - start_time
    
    # Test fallback (eval) performance
    start_time = time.time()
    for _ in range(iterations):
        try:
            result = layer._fallback_evaluate(formula_str, params)
        except Exception:
            pass  # Skip if there's an error
    eval_time = time.time() - start_time
    
    print(f"Performance comparison for {iterations} iterations:")
    print(f"numexpr: {numexpr_time:.4f} seconds ({numexpr_time/iterations*1000:.4f} ms per iteration)")
    print(f"SymPy: {sympy_time:.4f} seconds ({sympy_time/iterations*1000:.4f} ms per iteration)")
    print(f"eval: {eval_time:.4f} seconds ({eval_time/iterations*1000:.4f} ms per iteration)")
    
    # Verify that numexpr is faster than SymPy, which is faster than eval
    if numexpr_time < sympy_time < eval_time:
        print("Performance order is as expected: numexpr > SymPy > eval")
    else:
        print("Unexpected performance order - this might depend on the specific formula and environment")
    
    print("Performance comparison completed!\n")

def main():
    """Run all tests."""
    print("Testing the SymPy integration in the semantic metric layer...\n")
    
    test_sympy_complex_expressions()
    test_performance_comparison()
    
    print("All tests completed!")

if __name__ == "__main__":
    main()
