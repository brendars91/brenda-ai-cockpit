```markdown
---
name: calculator
description: Skill for performing a wide range of mathematical computations, from basic arithmetic to complex expressions. Designed to accurately process numerical data, financial figures, and quantitative metrics for the StockAnalysisAgent, enabling calculations of profit/loss, percentage changes, ratios, and other critical indicators.
version: 1.0.0
auto_generated: false
---

# calculator

## Purpose

The `calculator` skill provides robust and accurate computational capabilities essential for the `StockAnalysisAgent`. Its primary purpose is to evaluate mathematical expressions, perform arithmetic operations, and derive numerical insights from financial data. This skill enables the agent to process raw numbers obtained from other sources (like `web_search`) and transform them into actionable metrics, such as calculating percentage gains/losses, market capitalization, price-to-earnings ratios, dividend yields, and other financial indicators critical for comprehensive stock analysis.

## Functionality

This skill supports standard arithmetic operations and the evaluation of complex mathematical expressions. It is designed to handle integers, floating-point numbers, and expressions involving multiple operations, ensuring precision suitable for financial analysis.

Key functionalities include:
*   **Basic Arithmetic**: Addition (`+`), subtraction (`-`), multiplication (`*`), division (`/`).
*   **Exponentiation**: (`**` or `^`).
*   **Parentheses**: Support for nested parentheses to control order of operations.
*   **Signed Numbers**: Handling of positive and negative numbers.
*   **Floating-Point Precision**: Accurate calculations with decimal numbers.
*   **Order of Operations (PEMDAS/BODMAS)**: Correctly evaluates expressions based on standard mathematical rules.

## Actions

The `calculator` skill exposes a single, powerful action for evaluating mathematical expressions.

### `calculate(expression: str)`

Evaluates a given mathematical expression string and returns the numerical result.

#### Description

This action takes a string representing a mathematical expression, parses it, and computes its value. It adheres to standard mathematical order of operations and handles various numerical inputs. This is the core utility for performing any numerical computation within the agent's workflow.

#### Parameters

*   `expression` (required, type: `str`): The mathematical expression to be evaluated. The expression can include numbers (integers and floats), arithmetic operators (`+`, `-`, `*`, `/`, `**`, `^`), and parentheses `()`.

#### Returns

*   `float` or `int`: The numerical result of the evaluated expression. The return type will be `int` if the result is a whole number, otherwise `float`.
*   `str`: An error message if the expression is invalid (e.g., syntax error, division by zero).

#### Usage Examples

**Example 1: Basic Profit Calculation**

An agent might use this after retrieving buying and selling prices and share count.

```python
# Agent's thought process:
# 1. Fetch buying price: $150
# 2. Fetch selling price: $175
# 3. Fetch number of shares: 100
# 4. Construct expression for total profit.

calculator.calculate(expression="(175 - 150) * 100")
# Expected Output: 2500.0 (representing $2500 profit)
```

**Example 2: Percentage Change Calculation**

Used to determine the percentage gain or loss of a stock over a period.

```python
# Agent's thought process:
# 1. Fetch initial price: $120
# 2. Fetch current price: $135
# 3. Construct expression for percentage gain.

calculator.calculate(expression="((135 - 120) / 120) * 100")
# Expected Output: 12.5 (representing a 12.5% gain)
```

**Example 3: Market Capitalization Calculation**

Combining shares outstanding with current share price.

```python
# Agent's thought process:
# 1. Fetch shares outstanding: 5,000,000
# 2. Fetch current share price: $23.75
# 3. Construct expression for market capitalization.

calculator.calculate(expression="5000000 * 23.75")
# Expected Output: 118750000.0 (representing $118.75 million market cap)
```

**Example 4: Complex Financial Ratio (e.g., P/E Ratio with derived EPS)**

Assuming the agent needs to calculate Earnings Per Share (EPS) first.

```python
# Agent's thought process:
# 1. Fetch current share price: $180
# 2. Fetch total net income: $50,000,000
# 3. Fetch diluted shares outstanding: 20,000,000
# 4. Calculate EPS first, then P/E.

# Step 1: Calculate EPS (Net Income / Diluted Shares)
eps_expression = "50000000 / 20000000"
# Expected Intermediate Output for EPS: 2.5

# Step 2: Calculate P/E (Current Share Price / EPS)
# Agent would typically call calculate twice or chain operations if supported by the agent's reasoning.
# For simplicity, assuming the agent can integrate intermediate results:
calculator.calculate(expression="180 / (50000000 / 20000000)")
# Expected Output: 72.0 (representing a P/E ratio of 72x)
```

## Best Practices

*   **Clarity and Parentheses**: Always use parentheses to explicitly define the order of operations, even when it might seem implied. This avoids ambiguity and ensures correct evaluation, especially in complex financial formulas.
    *   **Good**: `((100 + 20) / 1.05) - 50`
    *   **Bad**: `100 + 20 / 1.05 - 50` (might lead to misinterpretation if not strictly adhering to PEMDAS)
*   **Input Validation by Agent**: While the `calculator` skill handles some errors, the `StockAnalysisAgent` should perform preliminary validation of numerical inputs before constructing expressions. Ensure numbers are indeed numbers and within reasonable bounds where applicable.
*   **Precision Management**: Be aware of floating-point arithmetic limitations. For financial reporting, consider explicit rounding of results to a specific number of decimal places after the calculation, using the agent's internal logic or another dedicated skill if available. The `calculator` skill will return the most precise float possible.
*   **Dedicated for Computation**: Use this skill purely for mathematical calculations. Do not attempt to use it for data retrieval, string manipulation, or logical comparisons. These tasks should be handled by other specialized skills or the agent's core reasoning.
*   **Conciseness**: Construct the `expression` parameter as a single, self-contained mathematical string for each `calculate` call. Avoid breaking down simple calculations into multiple calls if they can be expressed in one.

## Edge Cases and Error Handling

The `calculator` skill is designed to provide informative feedback for invalid operations.

*   **Division by Zero**: If an expression results in division by zero, the skill will return an error message (e.g., `"Error: Division by zero."` or raise an exception that the agent should catch and interpret).
    ```python
    calculator.calculate(expression="10 / 0")
    # Expected Output: "Error: Division by zero." (or similar error message/exception)
    ```
*   **Invalid Syntax**: Expressions that do not conform to valid mathematical syntax will result in an error. This includes unmatched parentheses, invalid operators, or non-numeric characters where numbers are expected.
    ```python
    calculator.calculate(expression="10 + (5 * 2")  # Unmatched parenthesis
    # Expected Output: "Error: Invalid expression syntax."

    calculator.calculate(expression="10 dollars + 5") # Non-numeric text
    # Expected Output: "Error: Invalid characters in expression."

    calculator.calculate(expression="5 ** * 2") # Malformed operator
    # Expected Output: "Error: Invalid expression syntax."
    ```
*   **Overflow/Underflow**: While less common in typical financial analysis, extremely large or small numbers that exceed the floating-point representation limits may result in `inf`, `-inf`, or `NaN` (Not a Number) or errors depending on the underlying computational engine. The agent should be prepared to handle these values if they can occur in the data sources.

## Integration Notes

The `calculator` skill is a foundational component for the `StockAnalysisAgent`.

*   **Complementary to `web_search`**: The typical workflow involves using `web_search` to retrieve raw financial data (e.g., current stock price, quarterly earnings, shares outstanding), and then passing this numerical data to the `calculator` skill to perform computations and derive meaningful metrics.
*   **Agent Orchestration**: The `StockAnalysisAgent` is responsible for intelligently combining information from `web_search` with the computational power of `calculator`. The agent must formulate the correct mathematical expressions based on the analytical task at hand.
*   **Error Handling Strategy**: The agent should implement robust error handling around `calculator` calls. If the `calculate` action returns an error string, the agent should be able to interpret it, log the error, and potentially attempt a different approach or inform the user about the issue.

## Future Enhancements

*   **Mathematical Functions**: Extend support for common mathematical functions relevant to finance, such as `sqrt()` (square root), `log()` (logarithm), `abs()` (absolute value), `round()`.
*   **Statistical Functions**: Integrate basic statistical functions like `sum()`, `avg()`, `min()`, `max()` if operating on lists of numbers becomes a common pattern.
*   **Units and Currency**: Add optional parsing or handling of units and currency symbols to allow more natural language expressions, though this might increase complexity.
*   **Variable Support**: Allow the agent to define temporary variables within an expression or across multiple calls for multi-step computations.