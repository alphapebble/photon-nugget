# Semantic Metric Layer

Solar Sage implements a semantic metric layer that serves as a centralized repository for all metrics, formulas, and constants used throughout the system. This document explains the architecture and usage of this layer.

## Overview

The semantic metric layer provides several key benefits:

1. **Single Source of Truth**: All metrics and calculations are defined in one place
2. **Business Logic Separation**: Calculation logic is separated from application code
3. **Self-Documentation**: Each metric includes descriptions and metadata
4. **Consistency**: Ensures the same definitions are used everywhere
5. **Governance**: Provides a clear audit trail for all calculations
6. **Flexibility**: Makes it easy to modify calculations without changing code

## Architecture

The semantic metric layer consists of:

1. **YAML Definition File**: Contains all metrics, formulas, and constants
2. **Parser Module**: Loads and evaluates formulas at runtime using numexpr for performance and safety
3. **API**: Simple functions to access metrics and evaluate formulas

The system uses numexpr for formula evaluation, which provides:

- **Performance**: Faster evaluation of mathematical expressions
- **Safety**: Secure evaluation without using Python's eval
- **Vectorization**: Efficient handling of array operations
- **Fallback**: Automatic fallback to Python's eval for complex expressions

### Metric Definition Structure

Metrics are defined in `src/config/formulas.yaml` using a hierarchical structure:

```yaml
domain:
  subdomain:
    metric_name:
      value: 123.45 # For constants
      formula: "expression" # For calculated metrics
      description: "What this metric represents"
      units: "unit of measurement"
      tags: ["tag1", "tag2"] # Optional categorization
```

## Benefits

1. **Centralized Metric Definitions**: All metrics and formulas are defined in one place
2. **Consistent Calculations**: Ensures all components use the same formulas
3. **Self-Documenting**: Metrics include descriptions and units
4. **Easy to Extend**: Add new metrics without changing code
5. **Versioning**: Track changes to metrics over time
6. **Performance**: Uses numexpr for efficient formula evaluation
7. **Safety**: Secure evaluation without using Python's eval directly
8. **Fallback Mechanism**: Automatic fallback to Python's eval for complex expressions

## Using the Semantic Metric Layer

### In Code

The semantic metric layer provides two main functions:

1. `get_constant`: Retrieve a constant value
2. `evaluate_formula`: Evaluate a formula with the given parameters

```python
from core.semantic_metric_layer import get_constant, evaluate_formula

# Get a constant metric
irradiance = get_constant('solar_panel.stc.irradiance')  # Returns 1000.0

# Evaluate a calculated metric
params = {
    'day_of_year': 180,
    'radians': math.radians,
    'sin': math.sin
}
declination = evaluate_formula('solar_irradiance.declination_angle', params)
```

## Metric Domains

The semantic layer organizes metrics into logical domains:

### Solar Panel Metrics

Metrics related to solar panel characteristics and performance.

| Metric                                                | Type     | Description                                | Units    |
| ----------------------------------------------------- | -------- | ------------------------------------------ | -------- |
| `solar_panel.stc.irradiance`                          | Constant | Standard Test Conditions irradiance        | W/m²     |
| `solar_panel.stc.temperature`                         | Constant | Standard Test Conditions temperature       | °C       |
| `solar_panel.characteristics.temperature_coefficient` | Constant | Temperature coefficient for silicon panels | % per °C |
| `solar_panel.characteristics.efficiency`              | Constant | Typical solar panel efficiency             | Ratio    |
| `solar_panel.characteristics.area_per_kw`             | Constant | Panel area required per kW of capacity     | m²/kW    |
| `solar_panel.peak_sun_hours`                          | Constant | Assumed peak sun hours per day             | Hours    |

### Weather Impact Metrics

Metrics quantifying how weather conditions affect solar production.

| Metric                                                 | Type     | Description                                        | Units |
| ------------------------------------------------------ | -------- | -------------------------------------------------- | ----- |
| `solar_panel.weather_impact.rain_factor`               | Constant | Production factor during rain                      | Ratio |
| `solar_panel.weather_impact.snow_factor`               | Constant | Production factor during snow                      | Ratio |
| `solar_panel.weather_impact.fog_factor`                | Constant | Production factor during fog                       | Ratio |
| `solar_panel.weather_impact.precipitation_impact.rain` | Constant | Additional reduction per precipitation probability | Ratio |
| `solar_panel.weather_impact.precipitation_impact.snow` | Constant | Additional reduction per precipitation probability | Ratio |

### Solar Irradiance Metrics

Metrics for calculating solar irradiance based on position and atmospheric conditions.

| Metric                                        | Type     | Description                                   | Units   |
| --------------------------------------------- | -------- | --------------------------------------------- | ------- |
| `solar_irradiance.solar_constant`             | Constant | Solar constant at top of atmosphere           | W/m²    |
| `solar_irradiance.atmospheric_transmittance`  | Constant | Typical clear sky transmittance               | Ratio   |
| `solar_irradiance.altitude_scale_height`      | Constant | Scale height for air mass adjustment          | m       |
| `solar_irradiance.declination_angle`          | Formula  | Solar declination angle calculation           | Degrees |
| `solar_irradiance.hour_angle`                 | Formula  | Hour angle calculation                        | Degrees |
| `solar_irradiance.solar_elevation`            | Formula  | Solar elevation angle calculation             | Radians |
| `solar_irradiance.solar_azimuth`              | Formula  | Solar azimuth angle calculation               | Radians |
| `solar_irradiance.clear_sky_irradiance`       | Formula  | Clear sky irradiance calculation              | W/m²    |
| `solar_irradiance.air_mass`                   | Formula  | Air mass calculation with altitude adjustment | Ratio   |
| `solar_irradiance.cloud_impact`               | Formula  | Cloud cover impact on irradiance              | Ratio   |
| `solar_irradiance.daytime_irradiance_pattern` | Formula  | Daytime irradiance pattern with peak at noon  | W/m²    |

### Energy Production Metrics

Metrics for calculating energy production from solar panels.

| Metric                              | Type     | Description                            | Units |
| ----------------------------------- | -------- | -------------------------------------- | ----- |
| `energy.production`                 | Formula  | Energy production calculation          | kWh   |
| `energy.temperature_impact`         | Formula  | Temperature impact on panel efficiency | Ratio |
| `energy.production_factor`          | Formula  | Production factor relative to STC      | Ratio |
| `energy.demand_factors.weekend`     | Constant | Demand factor for weekends             | Ratio |
| `energy.demand_factors.weekday`     | Constant | Demand factor for weekdays             | Ratio |
| `energy.demand_factors.base_demand` | Constant | Base demand                            | kWh   |

### Financial Metrics

Metrics for calculating financial aspects of solar energy systems.

| Metric                                    | Type     | Description                                            | Units    |
| ----------------------------------------- | -------- | ------------------------------------------------------ | -------- |
| `financial.default_feed_in_tariff_factor` | Constant | Default feed-in tariff as fraction of electricity rate | Ratio    |
| `financial.grid_purchases`                | Formula  | Energy purchased from grid                             | kWh      |
| `financial.grid_exports`                  | Formula  | Energy exported to grid                                | kWh      |
| `financial.consumption_cost`              | Formula  | Cost of energy consumption                             | Currency |
| `financial.production_value`              | Formula  | Value of energy production                             | Currency |
| `financial.grid_purchase_cost`            | Formula  | Cost of energy purchased from grid                     | Currency |
| `financial.grid_export_revenue`           | Formula  | Revenue from energy exported to grid                   | Currency |
| `financial.net_savings`                   | Formula  | Net savings from solar system                          | Currency |
| `financial.system_cost_estimate`          | Formula  | Estimated system cost                                  | Currency |
| `financial.annual_savings_estimate`       | Formula  | Estimated annual savings                               | Currency |
| `financial.simple_payback_years`          | Formula  | Simple payback period                                  | Years    |

### Weather Estimation Metrics

Metrics for estimating weather-related values.

| Metric                                           | Type     | Description                                             | Units |
| ------------------------------------------------ | -------- | ------------------------------------------------------- | ----- |
| `weather.uv_irradiance_estimate`                 | Formula  | Base irradiance estimate from UV index                  | W/m²  |
| `weather.cloud_adjusted_irradiance`              | Formula  | Cloud-adjusted irradiance                               | W/m²  |
| `weather.maintenance.dry_days_threshold`         | Constant | Days without rain before panel cleaning might be needed | Days  |
| `weather.maintenance.high_temperature_threshold` | Constant | Threshold for high temperature warning                  | °C    |

## Formula Definitions

Below are the key formulas used in the system:

### Solar Position Formulas

```yaml
solar_irradiance:
  declination_angle:
    formula: "23.45 * sin(radians(360 * (284 + day_of_year) / 365))"
    description: "Solar declination angle calculation"

  hour_angle:
    formula: "15 * (hour - 12)"
    description: "Hour angle calculation (15 degrees per hour)"

  solar_elevation:
    formula: "asin(sin(lat_rad) * sin(declination_rad) + cos(lat_rad) * cos(declination_rad) * cos(hour_angle_rad))"
    description: "Solar elevation angle calculation"
```

### Energy Production Formulas

```yaml
energy:
  production:
    formula: "(irradiance * efficiency * area_per_kw * system_capacity_kw) / 1000"
    description: "Energy production calculation in kWh"
    units: "kWh"

  temperature_impact:
    formula: "1 + (temperature_coefficient * (temperature - stc_temperature))"
    description: "Temperature impact on panel efficiency"
```

### Financial Formulas

```yaml
financial:
  grid_purchases:
    formula: "max(0, demand - production)"
    description: "Energy purchased from grid when demand exceeds production"

  net_savings:
    formula: "production_value - grid_purchase_cost + grid_export_revenue"
    description: "Net savings from solar system"
```

## Extending the Semantic Metric Layer

To add new metrics:

1. Add the metric definition to `src/config/formulas.yaml`
2. Use the metric in your code with `get_constant` or `evaluate_formula`

Example of adding a new metric:

```yaml
# In formulas.yaml
battery:
  efficiency:
    charge: 0.95 # 95% charging efficiency
    discharge: 0.95 # 95% discharging efficiency
    description: "Battery charging and discharging efficiency"
    units: "Ratio"

  storage_calculation:
    formula: "energy_in * charge_efficiency"
    description: "Calculate energy stored in battery"
    units: "kWh"
```

```python
# In your code
from core.semantic_metric_layer import get_constant, evaluate_formula

params = {
    'energy_in': 10.0,  # kWh
    'charge_efficiency': get_constant('battery.efficiency.charge')
}
energy_stored = evaluate_formula('battery.storage_calculation', params)
```

## Formula Evaluation System

The semantic metric layer uses a multi-tiered approach to formula evaluation, selecting the most appropriate method based on the formula's complexity:

1. **numexpr**: For simple mathematical expressions (fastest)
2. **SymPy**: For complex symbolic mathematics (when available)
3. **Python's eval**: As a fallback for maximum flexibility (slowest and least secure)

### numexpr Evaluation

numexpr provides several advantages for simple mathematical expressions:

1. **Performance**: Significantly faster than Python's eval
2. **Safety**: Evaluates expressions in a restricted environment
3. **Vectorization**: Efficiently handles array operations

#### Supported Functions in numexpr

- Basic arithmetic: `+`, `-`, `*`, `/`, `**` (power)
- Trigonometric: `sin`, `cos`, `tan`, `arcsin`, `arccos`, `arctan`
- Logarithmic: `log`, `log10`, `exp`
- Other: `sqrt`, `abs`

#### Dynamic Function Replacement

The system uses a sophisticated dynamic function replacement mechanism to automatically convert Python math functions to their numexpr equivalents:

1. **Standard Replacements**: Common functions like `math.sin` → `sin` are predefined
2. **Dynamic Discovery**: Additional functions are discovered at runtime
3. **Regex-Based Matching**: Precise word boundary matching to avoid partial replacements
4. **Edge Case Handling**: Special handling for variable names that contain function names

### SymPy Evaluation

For more complex symbolic mathematics, the system uses SymPy when available:

1. **Symbolic Mathematics**: Handles complex mathematical expressions
2. **Advanced Functions**: Supports a wider range of mathematical functions
3. **Equation Solving**: Can solve equations symbolically
4. **Calculus**: Supports differentiation and integration

#### Supported Functions in SymPy

- All basic arithmetic and trigonometric functions
- Advanced functions: `Max`, `Min`, `Piecewise`
- Symbolic variables and constants
- Equation solving and manipulation

### Fallback Mechanism

For functions not supported by numexpr or SymPy, or when those libraries are not available, the system automatically falls back to Python's eval with a restricted environment.

### Specifying Evaluation Method

You can specify a preferred evaluation method for a formula in the YAML definition:

```yaml
solar_irradiance:
  complex_calculation:
    formula: "complex expression here"
    evaluation_method: "sympy" # Options: "auto", "numexpr", "sympy", "eval"
```

The available methods are:

- `auto`: Automatically select the best method (default)
- `numexpr`: Force numexpr evaluation
- `sympy`: Force SymPy evaluation
- `eval`: Force Python's eval evaluation

## Best Practices

1. **Document All Metrics**: Always include a description and units
2. **Use Consistent Units**: Document the units for all metrics
3. **Group Related Metrics**: Organize metrics into logical domains
4. **Validate Parameters**: Check that all required parameters are provided
5. **Handle Edge Cases**: Consider edge cases like division by zero
6. **Keep Formulas Simple**: Break complex calculations into smaller metrics
7. **Use Descriptive Names**: Choose clear, descriptive names for metrics
8. **Choose the Right Evaluation Method**:
   - Use `numexpr` for simple expressions (fastest)
   - Use `sympy` for complex symbolic mathematics
   - Use `eval` only when necessary for maximum flexibility
9. **Specify Evaluation Method**: For complex formulas, specify the preferred evaluation method
10. **Test Performance**: For critical formulas, test the performance of different evaluation methods
