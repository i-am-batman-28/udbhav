"""
Calculator Module with Advanced Operations

This module provides a comprehensive calculator with basic arithmetic operations,
advanced mathematical functions, and error handling capabilities.

Author: AI Assistant
Date: 2025-10-26
Version: 1.0.0
"""

import math
from typing import Union, List, Optional
from decimal import Decimal, InvalidOperation


class Calculator:
    """
    A comprehensive calculator class that provides various mathematical operations.
    
    This class implements basic arithmetic operations (addition, subtraction,
    multiplication, division) as well as advanced mathematical functions
    (trigonometry, logarithms, exponentials).
    
    Attributes:
        precision (int): The number of decimal places for rounding results.
        history (List[str]): A list storing the history of all calculations.
    """
    
    def __init__(self, precision: int = 2):
        """
        Initialize the Calculator with specified precision.
        
        Args:
            precision (int): Number of decimal places for results. Defaults to 2.
            
        Raises:
            ValueError: If precision is negative.
        """
        # Validate the precision parameter
        if precision < 0:
            raise ValueError("Precision must be a non-negative integer")
        
        # Initialize instance variables
        self.precision = precision
        self.history = []
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Add two numbers together.
        
        This method performs addition of two numbers and returns the result
        rounded to the specified precision.
        
        Args:
            a (Union[int, float]): The first number to add.
            b (Union[int, float]): The second number to add.
            
        Returns:
            float: The sum of a and b, rounded to precision decimal places.
            
        Example:
            >>> calc = Calculator(precision=2)
            >>> calc.add(5, 3)
            8.0
        """
        # Perform the addition operation
        result = a + b
        
        # Round the result to the specified precision
        rounded_result = round(result, self.precision)
        
        # Store the operation in history
        self.history.append(f"{a} + {b} = {rounded_result}")
        
        # Return the final result
        return rounded_result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Subtract one number from another.
        
        This method performs subtraction of two numbers and returns the result
        rounded to the specified precision.
        
        Args:
            a (Union[int, float]): The number to subtract from.
            b (Union[int, float]): The number to subtract.
            
        Returns:
            float: The difference between a and b, rounded to precision.
            
        Example:
            >>> calc = Calculator(precision=2)
            >>> calc.subtract(10, 3)
            7.0
        """
        # Perform the subtraction operation
        result = a - b
        
        # Round the result to the specified precision
        rounded_result = round(result, self.precision)
        
        # Store the operation in history
        self.history.append(f"{a} - {b} = {rounded_result}")
        
        # Return the final result
        return rounded_result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Multiply two numbers together.
        
        This method performs multiplication of two numbers and returns the result
        rounded to the specified precision.
        
        Args:
            a (Union[int, float]): The first number to multiply.
            b (Union[int, float]): The second number to multiply.
            
        Returns:
            float: The product of a and b, rounded to precision.
            
        Example:
            >>> calc = Calculator(precision=2)
            >>> calc.multiply(4, 5)
            20.0
        """
        # Perform the multiplication operation
        result = a * b
        
        # Round the result to the specified precision
        rounded_result = round(result, self.precision)
        
        # Store the operation in history
        self.history.append(f"{a} × {b} = {rounded_result}")
        
        # Return the final result
        return rounded_result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divide one number by another.
        
        This method performs division of two numbers and returns the result
        rounded to the specified precision. It includes proper error handling
        for division by zero.
        
        Args:
            a (Union[int, float]): The dividend (number to be divided).
            b (Union[int, float]): The divisor (number to divide by).
            
        Returns:
            float: The quotient of a divided by b, rounded to precision.
            
        Raises:
            ZeroDivisionError: If attempting to divide by zero.
            
        Example:
            >>> calc = Calculator(precision=2)
            >>> calc.divide(10, 2)
            5.0
        """
        # Check for division by zero
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        
        # Perform the division operation
        result = a / b
        
        # Round the result to the specified precision
        rounded_result = round(result, self.precision)
        
        # Store the operation in history
        self.history.append(f"{a} ÷ {b} = {rounded_result}")
        
        # Return the final result
        return rounded_result
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> float:
        """
        Raise a number to a specified power.
        
        This method calculates the power of a base number raised to an exponent
        and returns the result rounded to the specified precision.
        
        Args:
            base (Union[int, float]): The base number.
            exponent (Union[int, float]): The exponent to raise the base to.
            
        Returns:
            float: The result of base raised to exponent, rounded to precision.
            
        Example:
            >>> calc = Calculator(precision=2)
            >>> calc.power(2, 3)
            8.0
        """
        # Calculate the power using the ** operator
        result = base ** exponent
        
        # Round the result to the specified precision
        rounded_result = round(result, self.precision)
        
        # Store the operation in history
        self.history.append(f"{base}^{exponent} = {rounded_result}")
        
        # Return the final result
        return rounded_result
    
    def square_root(self, number: Union[int, float]) -> float:
        """
        Calculate the square root of a number.
        
        This method calculates the square root of a given number and returns
        the result rounded to the specified precision. It includes validation
        to ensure the input is non-negative.
        
        Args:
            number (Union[int, float]): The number to calculate the square root of.
            
        Returns:
            float: The square root of the number, rounded to precision.
            
        Raises:
            ValueError: If the number is negative.
            
        Example:
            >>> calc = Calculator(precision=2)
            >>> calc.square_root(16)
            4.0
        """
        # Validate that the number is non-negative
        if number < 0:
            raise ValueError("Cannot calculate square root of a negative number")
        
        # Calculate the square root using math.sqrt
        result = math.sqrt(number)
        
        # Round the result to the specified precision
        rounded_result = round(result, self.precision)
        
        # Store the operation in history
        self.history.append(f"√{number} = {rounded_result}")
        
        # Return the final result
        return rounded_result
    
    def get_history(self) -> List[str]:
        """
        Retrieve the calculation history.
        
        This method returns a list of all calculations performed by this
        calculator instance.
        
        Returns:
            List[str]: A list containing all calculation records.
            
        Example:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            >>> calc.get_history()
            ['5 + 3 = 8.0']
        """
        # Return a copy of the history list to prevent external modification
        return self.history.copy()
    
    def clear_history(self) -> None:
        """
        Clear all calculation history.
        
        This method removes all records from the calculation history.
        
        Example:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            >>> calc.clear_history()
            >>> calc.get_history()
            []
        """
        # Clear the history list
        self.history.clear()
