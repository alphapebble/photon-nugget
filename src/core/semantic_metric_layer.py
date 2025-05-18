"""
Semantic Metric Layer for Solar Sage.

This module provides utilities for loading and evaluating metrics and formulas
from the semantic metric layer defined in YAML configuration.
Uses numexpr for efficient and safe formula evaluation, with SymPy for
more complex symbolic mathematics when needed.
"""
import os
import yaml
import math
import re
import numpy as np
import numexpr as ne
from typing import Dict, Any, List, Union, Callable, Optional
from pathlib import Path
from functools import lru_cache
from core.logging import get_logger

logger = get_logger(__name__)

# Try to import SymPy, but don't fail if it's not available
try:
    import sympy
    from sympy import symbols, sympify, lambdify
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    logger.warning("SymPy not available. Advanced symbolic math features will be disabled.")

# Define standard math function replacements for numexpr
MATH_REPLACEMENTS = {
    # Basic math functions
    'math.sin': 'sin',
    'math.cos': 'cos',
    'math.tan': 'tan',
    'math.asin': 'arcsin',
    'math.acos': 'arccos',
    'math.atan': 'arctan',
    'math.log': 'log',
    'math.log10': 'log10',
    'math.sqrt': 'sqrt',
    'math.exp': 'exp',
    'math.pow': 'power',
    'math.fabs': 'abs',

    # Direct function names (without math. prefix)
    'sin': 'sin',
    'cos': 'cos',
    'tan': 'tan',
    'asin': 'arcsin',
    'acos': 'arccos',
    'atan': 'arctan',
    'log': 'log',
    'log10': 'log10',
    'sqrt': 'sqrt',
    'exp': 'exp',
    'pow': 'power',
    'abs': 'abs',
}

# Try to dynamically discover additional functions
try:
    # Get functions that are common to both `math` and `numexpr`
    math_funcs = {name for name in dir(math) if callable(getattr(math, name))}

    # Try to get numexpr function names if available
    try:
        # This is an implementation detail and might change
        numexpr_funcs = set(ne.expressions.functions.keys())
    except (AttributeError, ImportError):
        numexpr_funcs = set()

    # Find additional functions not in our standard list
    for func in math_funcs:
        math_func_name = f'math.{func}'
        if math_func_name not in MATH_REPLACEMENTS and func in numexpr_funcs:
            MATH_REPLACEMENTS[math_func_name] = func
            MATH_REPLACEMENTS[func] = func
            logger.debug(f"Added dynamic replacement: {math_func_name} -> {func}")

    logger.debug(f"Using {len(MATH_REPLACEMENTS)} function replacements for numexpr")
except Exception as e:
    logger.warning(f"Failed to discover additional replacements: {e}")

# Type for formula parameters
FormulaParams = Dict[str, Union[float, int, bool, str, Callable]]

class SemanticMetricLayer:
    """Parser for the semantic metric layer defined in YAML."""

    def __init__(self, metrics_path: str = None):
        """
        Initialize the semantic metric layer.

        Args:
            metrics_path: Path to the metrics YAML file
        """
        if metrics_path is None:
            # Default path is in the config directory
            root_dir = Path(__file__).parent.parent.parent
            metrics_path = os.path.join(root_dir, "src", "config", "formulas.yaml")

        self.metrics_path = metrics_path
        self.metrics = self._load_metrics()
        logger.info(f"Loaded semantic metric layer from {metrics_path}")

    @lru_cache(maxsize=1)
    def _load_metrics(self) -> Dict[str, Any]:
        """
        Load metrics from YAML file.

        Returns:
            Dictionary of metrics
        """
        try:
            with open(self.metrics_path, 'r') as f:
                metrics = yaml.safe_load(f)
            return metrics
        except Exception as e:
            logger.error(f"Error loading metrics from {self.metrics_path}: {e}")
            return {}

    def get_constant(self, path: str) -> Union[float, int, bool, str, None]:
        """
        Get a constant value from the semantic metric layer.

        Args:
            path: Dot-separated path to the metric (e.g., 'solar_panel.stc.irradiance')

        Returns:
            Metric value or None if not found
        """
        try:
            value = self.metrics
            for key in path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError) as e:
            logger.warning(f"Metric not found at path {path}: {e}")
            return None

    def get_formula(self, path: str) -> Dict[str, Any]:
        """
        Get a formula definition from the semantic metric layer.

        Args:
            path: Dot-separated path to the formula metric (e.g., 'solar_irradiance.clear_sky_irradiance')

        Returns:
            Formula definition or empty dict if not found
        """
        try:
            metric_def = self.get_constant(path)
            if isinstance(metric_def, dict) and 'formula' in metric_def:
                return metric_def
            logger.warning(f"No formula metric found at path {path}")
            return {}
        except Exception as e:
            logger.warning(f"Error getting formula metric at path {path}: {e}")
            return {}

    def evaluate_formula(self, path: str, params: FormulaParams) -> float:
        """
        Evaluate a formula metric with the given parameters.

        This method tries different evaluation strategies in the following order:
        1. numexpr for simple mathematical expressions (fastest)
        2. SymPy for complex symbolic mathematics (if available)
        3. Python's eval as a fallback (most flexible but slowest and least secure)

        Args:
            path: Dot-separated path to the formula metric
            params: Dictionary of parameter values

        Returns:
            Result of the formula evaluation
        """
        formula_def = self.get_formula(path)
        if not formula_def:
            logger.error(f"Formula metric not found at path {path}")
            return 0.0

        formula_str = formula_def['formula']

        # Check if the formula has a preferred evaluation method
        preferred_method = formula_def.get('evaluation_method', 'auto')

        # If the preferred method is 'sympy' and SymPy is available, use it directly
        if preferred_method == 'sympy' and SYMPY_AVAILABLE:
            logger.debug(f"Using SymPy for formula {path} (preferred method)")
            sympy_result = self._sympy_evaluate(formula_str, params)
            if sympy_result is not None:
                return sympy_result
            # Fall back to other methods if SymPy fails

        # If the preferred method is 'eval', use the fallback directly
        if preferred_method == 'eval':
            logger.debug(f"Using eval for formula {path} (preferred method)")
            return self._fallback_evaluate(formula_str, params)

        # For 'auto' or 'numexpr' or if the preferred method failed, try numexpr first
        # Process the formula for numexpr compatibility
        processed_formula = self._process_formula_for_numexpr(formula_str)

        # If the formula can't be processed for numexpr, try SymPy next
        if processed_formula is None:
            if SYMPY_AVAILABLE:
                logger.debug(f"Formula {path} not compatible with numexpr, trying SymPy")
                sympy_result = self._sympy_evaluate(formula_str, params)
                if sympy_result is not None:
                    return sympy_result

            # If numexpr and SymPy both fail, use the fallback
            logger.debug(f"Using fallback evaluation for formula {path}")
            return self._fallback_evaluate(formula_str, params)

        # Create local variables for numexpr
        local_dict = {
            # Constants
            'pi': math.pi,
            'e': math.e,
        }

        # Add the parameters to the local dict
        local_dict.update(params)

        try:
            # Evaluate the formula using numexpr
            result = ne.evaluate(processed_formula, local_dict=local_dict)

            # Handle scalar vs array results
            if hasattr(result, 'item'):
                return float(result.item())
            return float(result)
        except Exception as e:
            logger.debug(f"Error evaluating formula metric '{processed_formula}' with numexpr: {e}")

            # Try SymPy next if available
            if SYMPY_AVAILABLE:
                logger.debug(f"Trying SymPy for formula {path} after numexpr failed")
                sympy_result = self._sympy_evaluate(formula_str, params)
                if sympy_result is not None:
                    return sympy_result

            # If both numexpr and SymPy fail, use the fallback
            logger.debug(f"Using fallback evaluation for formula {path} after all other methods failed")
            return self._fallback_evaluate(formula_str, params)

    def _process_formula_for_numexpr(self, formula: str) -> Optional[str]:
        """
        Process a formula string to make it compatible with numexpr.

        Args:
            formula: Original formula string

        Returns:
            Processed formula string for numexpr or None if not compatible
        """
        # Check for functions that numexpr doesn't support well
        unsupported_functions = ['max(', 'min(', 'atan2(', 'radians(', 'degrees(']
        for func in unsupported_functions:
            if func in formula:
                logger.debug(f"Formula contains {func} which is not well supported by numexpr, using fallback: {formula}")
                return None

        # Check for callable parameters (like math.sin passed as a parameter)
        # But don't reject formulas that just happen to contain these strings as part of variable names
        if 'radians' in formula or 'sin' in formula or 'cos' in formula:
            for param in ['radians', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan']:
                # Only consider it a callable parameter if it's a standalone word
                # This avoids rejecting formulas with variable names like 'sinx'
                if re.search(rf'\b{param}\b', formula) and param + '(' not in formula:
                    logger.debug(f"Formula may contain callable parameter {param}, using fallback: {formula}")
                    return None

        # Apply dynamic function replacements
        processed = formula

        # First, handle function calls with parentheses to avoid double replacements
        for pattern, replacement in MATH_REPLACEMENTS.items():
            if '(' not in pattern and pattern + '(' in processed:
                # Replace function calls like 'sin(' with 'sin('
                processed = re.sub(rf'\b{re.escape(pattern)}\(', f"{replacement}(", processed)

        # Then handle function names without parentheses
        for pattern, replacement in MATH_REPLACEMENTS.items():
            if '(' not in pattern:
                # Replace function names like 'math.sin' with 'sin'
                processed = re.sub(rf'\b{re.escape(pattern)}\b', replacement, processed)

        # Replace and/or/not with &/|/~
        logical_replacements = {
            ' and ': ' & ',
            ' or ': ' | ',
            ' not ': ' ~ ',
        }

        for old, new in logical_replacements.items():
            processed = processed.replace(old, new)

        return processed

    def _sympy_evaluate(self, formula_str: str, params: FormulaParams) -> Optional[float]:
        """
        Evaluate a formula using SymPy for symbolic mathematics.

        Args:
            formula_str: Original formula string
            params: Dictionary of parameter values

        Returns:
            Result of the formula evaluation or None if evaluation fails
        """
        if not SYMPY_AVAILABLE:
            logger.debug("SymPy not available, skipping symbolic evaluation")
            return None

        try:
            # Create symbols for all parameters
            param_symbols = {name: symbols(name) for name in params.keys()
                            if not callable(params[name])}

            # Handle callable parameters separately
            callable_params = {name: params[name] for name in params.keys()
                              if callable(params[name])}

            # Process the formula for SymPy compatibility
            processed_formula = formula_str

            # Replace Python math functions with SymPy equivalents
            replacements = {
                'math.sin': 'sympy.sin',
                'math.cos': 'sympy.cos',
                'math.tan': 'sympy.tan',
                'math.asin': 'sympy.asin',
                'math.acos': 'sympy.acos',
                'math.atan': 'sympy.atan',
                'math.log': 'sympy.log',
                'math.log10': 'lambda x: sympy.log(x, 10)',
                'math.sqrt': 'sympy.sqrt',
                'math.exp': 'sympy.exp',
                'math.pow': 'lambda x, y: x**y',
                'max(': 'sympy.Max(',
                'min(': 'sympy.Min(',
            }

            for old, new in replacements.items():
                processed_formula = processed_formula.replace(old, new)

            # For callable parameters, we need special handling
            if callable_params:
                logger.debug("Formula contains callable parameters, which are not directly supported by SymPy")
                return None

            # Parse the formula with SymPy
            expr = sympify(processed_formula, locals=param_symbols)

            # Create a lambda function from the expression
            func = lambdify(list(param_symbols.values()), expr, modules=['numpy', 'sympy'])

            # Evaluate the function with parameter values
            param_values = [params[name] for name in param_symbols.keys()]
            result = func(*param_values)

            return float(result)
        except Exception as e:
            logger.debug(f"SymPy evaluation failed for formula {formula_str}: {e}")
            return None

    def _fallback_evaluate(self, formula_str: str, params: FormulaParams) -> float:
        """
        Fallback evaluation method using Python's eval for functions not supported by numexpr.

        Args:
            formula_str: Original formula string
            params: Dictionary of parameter values

        Returns:
            Result of the formula evaluation
        """
        logger.debug(f"Using fallback evaluation for formula: {formula_str}")

        # Create a safe evaluation environment with math functions
        eval_env = {
            # Basic math functions
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'atan2': math.atan2,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            'sqrt': math.sqrt,
            'pow': math.pow,
            'abs': abs,
            'max': max,
            'min': min,

            # Constants
            'pi': math.pi,
            'e': math.e,

            # Conversion functions
            'radians': math.radians,
            'degrees': math.degrees,
        }

        # Add the parameters to the environment
        eval_env.update(params)

        try:
            # Evaluate the formula
            result = eval(formula_str, {"__builtins__": {}}, eval_env)
            return float(result)
        except Exception as e:
            logger.error(f"Fallback evaluation failed for formula {formula_str}: {e}")
            return 0.0

    def reload_metrics(self):
        """Reload metrics from the YAML file."""
        # Clear the cache to force reload
        self._load_metrics.cache_clear()
        self.metrics = self._load_metrics()
        logger.info(f"Reloaded semantic metric layer from {self.metrics_path}")


# Singleton instance for global use
_metric_layer = None

def get_metric_layer() -> SemanticMetricLayer:
    """
    Get the global semantic metric layer instance.

    Returns:
        Semantic metric layer instance
    """
    global _metric_layer
    if _metric_layer is None:
        _metric_layer = SemanticMetricLayer()
    return _metric_layer

def get_constant(path: str) -> Union[float, int, bool, str, None]:
    """
    Get a constant value from the semantic metric layer.

    Args:
        path: Dot-separated path to the metric

    Returns:
        Metric value or None if not found
    """
    return get_metric_layer().get_constant(path)

def evaluate_formula(path: str, params: FormulaParams) -> float:
    """
    Evaluate a formula metric with the given parameters.

    Args:
        path: Dot-separated path to the formula metric
        params: Dictionary of parameter values

    Returns:
        Result of the formula evaluation
    """
    return get_metric_layer().evaluate_formula(path, params)

def reload_metrics():
    """Reload metrics from the YAML file."""
    get_metric_layer().reload_metrics()
