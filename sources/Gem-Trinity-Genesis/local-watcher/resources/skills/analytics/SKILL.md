```markdown
---
name: analytics
description: Skill for performing data analysis and generating insights from various data sources. This includes data aggregation, statistical analysis, visualization, and report generation. Designed for integration with marketing data sources like email campaign results and social media metrics.
version: 1.0.0
auto_generated: false
---

# analytics

## Purpose

This skill provides a comprehensive set of actions for analyzing data, generating insights, and creating reports. It is designed to work with various data sources, including CSV files, JSON files, and potentially databases (although database interactions are handled by a separate skill if needed). The primary focus is on providing analytical capabilities tailored to marketing data, such as email campaign performance and social media engagement.

## Usage

This skill can be invoked by other skills (e.g., `email-campaign`, `social-media`) or directly by the AI agent when data analysis is required. It offers actions for data loading, cleaning, transformation, analysis, visualization, and reporting.  It prioritizes using Python libraries like `pandas`, `numpy`, `scipy`, `matplotlib`, and `seaborn`.

## Actions

### 1. `load_data`

**Description:** Loads data from a specified file path into a pandas DataFrame. Supports CSV and JSON formats.  Can also infer schema.

**Parameters:**

*   `file_path` (string, required): The path to the data file.
*   `file_type` (string, optional, default: "csv"): The type of the data file. Supported values: "csv", "json".  If `file_type` is "csv" further parameters like `delimiter` and `header` are available.
*   `delimiter` (string, optional, default: ","): The delimiter used in the CSV file. Only applicable if `file_type` is "csv".
*   `header` (string or int or list of ints, optional, default: "infer"): Row number(s) to use as the column names, and the start of the data. Default behavior is to infer the column names: if no names are passed the behavior is identical to `header=0` and column names are inferred from the first line of the file, if column names are passed explicitly then the behavior is identical to `header=None`. Explicitly pass `header=0` to be able to replace existing names. The header can be a list of integers that specify row locations for a `MultiIndex` on the columns
*   `encoding` (string, optional, default: "utf-8"): Encoding to use for UTF when reading/writing (ex. `'utf-8'`). List of Python standard encodings.
*   `infer_schema` (boolean, optional, default: False): If True, attempt to infer the data types of the columns.  This can be useful for handling files where the data types are not explicitly specified.
*   `sheet_name` (string or int, optional, default: 0): Sheet name or sheet position from an excel file. Only applicable if `file_type` is "excel"

**Returns:**

*   A pandas DataFrame object.
*   Error message if the file cannot be loaded or parsed.

**Example:**

```python
# Load data from a CSV file
data = analytics.load_data(file_path="data.csv", file_type="csv")

# Load data from a JSON file
data = analytics.load_data(file_path="data.json", file_type="json")

# Load CSV with specific delimiter
data = analytics.load_data(file_path="data.csv", file_type="csv", delimiter=";")

# Load CSV with explicit header row (overwriting existing)
data = analytics.load_data(file_path="data.csv", file_type="csv", header=0)

# Load CSV with inferred schema
data = analytics.load_data(file_path="data.csv", file_type="csv", infer_schema=True)
```

**Error Handling:**

*   If the `file_path` does not exist, return an error message: "Error: File not found at {file_path}".
*   If the `file_type` is not supported, return an error message: "Error: Unsupported file type: {file_type}".
*   If the file cannot be parsed (e.g., invalid JSON format), return an error message: "Error: Could not parse file {file_path}.  Details: {exception message}".
*   If there's a encoding error return an error message "Error: Encoding error with file {file_path}. Details: {exception message}".

**Best Practices:**

*   Always specify the `file_type` explicitly to avoid ambiguity.
*   Use `infer_schema=True` when the data types in the file are not explicitly defined.  Be aware that this can be slower.
*   Handle potential file not found and parsing errors gracefully.
*   When working with CSVs containing non-standard delimiters, ensure the `delimiter` parameter is set correctly.
*   Always check the loaded data DataFrame (e.g., using `data.head()`) to ensure it has been loaded correctly.

### 2. `clean_data`

**Description:** Cleans a pandas DataFrame by handling missing values, removing duplicates, and converting data types.

**Parameters:**

*   `data` (pandas DataFrame, required): The DataFrame to be cleaned.
*   `missing_value_strategy` (string, optional, default: "drop"): Strategy for handling missing values. Supported values: "drop", "fillna", "impute".
    *   "drop": Removes rows containing missing values.
    *   "fillna": Fills missing values with a specified value. Requires `fillna_value`.
    *   "impute": Imputes missing values using a statistical method (e.g., mean, median, mode). Requires `impute_strategy` and `impute_column`.
*   `fillna_value` (any, optional, default: None): The value to use when `missing_value_strategy` is set to "fillna".  Must be compatible with the column datatype.
*   `impute_strategy` (string, optional, default: "mean"): The imputation strategy to use when `missing_value_strategy` is set to "impute". Supported values: "mean", "median", "most_frequent".
*   `impute_column` (string, optional, default: None): The column to apply imputation on when `missing_value_strategy` is set to "impute".
*   `remove_duplicates` (boolean, optional, default: True): Whether to remove duplicate rows from the DataFrame.
*   `convert_column_types` (dict, optional, default: None): A dictionary specifying column names and their desired data types (e.g., `{'column1': 'int', 'column2': 'float', 'column3': 'datetime64[ns]'}`).

**Returns:**

*   A cleaned pandas DataFrame.
*   Error message if the DataFrame is invalid or an unsupported strategy is used.

**Example:**

```python
# Drop rows with missing values
cleaned_data = analytics.clean_data(data=data, missing_value_strategy="drop")

# Fill missing values with 0
cleaned_data = analytics.clean_data(data=data, missing_value_strategy="fillna", fillna_value=0)

# Impute missing values using the mean of 'age' column
cleaned_data = analytics.clean_data(data=data, missing_value_strategy="impute", impute_strategy="mean", impute_column="age")

# Remove duplicate rows
cleaned_data = analytics.clean_data(data=data, remove_duplicates=True)

# Convert column types
cleaned_data = analytics.clean_data(data=data, convert_column_types={'date': 'datetime64[ns]', 'revenue': 'float'})

# Clean data with multiple operations
cleaned_data = analytics.clean_data(data=data, missing_value_strategy="fillna", fillna_value=0, remove_duplicates=True, convert_column_types={'date': 'datetime64[ns]'})
```

**Error Handling:**

*   If the `data` parameter is not a pandas DataFrame, return an error message: "Error: Input data must be a pandas DataFrame".
*   If an unsupported `missing_value_strategy` is specified, return an error message: "Error: Unsupported missing value strategy: {missing_value_strategy}".
*   If `fillna_value` is not provided when `missing_value_strategy` is "fillna", return an error message: "Error: fillna_value must be provided when missing_value_strategy is 'fillna'".
*   If `impute_strategy` is not supported return an error "Error: Unsupported impute strategy: {impute_strategy}".
*   If `impute_column` is not provided when `missing_value_strategy` is "impute", return an error message: "Error: impute_column must be provided when missing_value_strategy is 'impute'".
*   If a column specified in `convert_column_types` does not exist in the DataFrame, return an error message: "Error: Column '{column_name}' not found in DataFrame".
*   If a column conversion fails (e.g., converting a string to an integer), return an error message: "Error: Could not convert column '{column_name}' to type {desired_type}. Details: {exception message}".

**Best Practices:**

*   Always handle missing values appropriately, choosing the best strategy based on the data and analysis goals.
*   Remove duplicate rows unless duplicates are meaningful in the context of the data.
*   Convert column types to ensure data is stored and analyzed correctly.
*   Validate data cleaning results by checking the data types and distribution of values in each column.
*   Document data cleaning steps for reproducibility.

### 3. `analyze_data`

**Description:** Performs statistical analysis on a pandas DataFrame and generates insights.

**Parameters:**

*   `data` (pandas DataFrame, required): The DataFrame to be analyzed.
*   `analysis_type` (string, optional, default: "descriptive"): The type of analysis to perform. Supported values: "descriptive", "correlation", "regression", "groupby".
    *   "descriptive": Calculates descriptive statistics (e.g., mean, median, standard deviation) for numerical columns.
    *   "correlation": Calculates the correlation matrix between numerical columns.
    *   "regression": Performs linear regression. Requires `independent_variable` and `dependent_variable`.
    *   "groupby": Performs a groupby operation and calculates aggregate statistics. Requires `groupby_column` and `aggregate_function`.
*   `independent_variable` (string, optional, default: None): The independent variable for regression analysis. Required if `analysis_type` is "regression".
*   `dependent_variable` (string, optional, default: None): The dependent variable for regression analysis. Required if `analysis_type` is "regression".
*   `groupby_column` (string, optional, default: None): The column to group by for groupby analysis. Required if `analysis_type` is "groupby".
*   `aggregate_function` (string, optional, default: "mean"): The aggregate function to apply for groupby analysis.  Supported values: "mean", "sum", "median", "count", "min", "max".  Required if `analysis_type` is "groupby".

**Returns:**

*   A dictionary containing the analysis results. The structure of the dictionary depends on the `analysis_type`.
    *   For "descriptive": A dictionary of descriptive statistics for each numerical column.
    *   For "correlation": A correlation matrix as a pandas DataFrame.
    *   For "regression": A dictionary containing regression statistics (e.g., R-squared, coefficients).
    *   For "groupby": A pandas DataFrame containing the grouped results.
*   Error message if the DataFrame is invalid or an unsupported analysis type or parameters are specified.

**Example:**

```python
# Descriptive statistics
descriptive_stats = analytics.analyze_data(data=data, analysis_type="descriptive")

# Correlation analysis
correlation_matrix = analytics.analyze_data(data=data, analysis_type="correlation")

# Regression analysis
regression_results = analytics.analyze_data(data=data, analysis_type="regression", independent_variable="spend", dependent_variable="revenue")

# Groupby analysis
groupby_results = analytics.analyze_data(data=data, analysis_type="groupby", groupby_column="campaign", aggregate_function="sum")
```

**Error Handling:**

*   If the `data` parameter is not a pandas DataFrame, return an error message: "Error: Input data must be a pandas DataFrame".
*   If an unsupported `analysis_type` is specified, return an error message: "Error: Unsupported analysis type: {analysis_type}".
*   If `independent_variable` or `dependent_variable` are not provided when `analysis_type` is "regression", return an error message: "Error: independent_variable and dependent_variable must be provided when analysis_type is 'regression'".
*   If `groupby_column` or `aggregate_function` are not provided when `analysis_type` is "groupby", return an error message: "Error: groupby_column and aggregate_function must be provided when analysis_type is 'groupby'".
*   If an unsupported aggregate function is used, return an error "Error: Unsupported aggregate function: {aggregate_function}".
*   If a specified column does not exist in the DataFrame, return an error message: "Error: Column '{column_name}' not found in DataFrame".
*   If a mathematical operation fails (e.g., division by zero in correlation analysis), return an error message: "Error: Mathematical error during analysis. Details: {exception message}".
*   If there are no numerical columns for descriptive analysis or correlation, return an error "Error: No numerical columns found in DataFrame for {analysis_type} analysis."

**Best Practices:**

*   Choose the appropriate `analysis_type` based on the research question.
*   Ensure that the data is cleaned and preprocessed before performing analysis.
*   Interpret the results of the analysis carefully, considering the context of the data.
*   Validate the results of the analysis using other methods or data sources.
*   Regression analysis needs careful consideration of statistical assumptions.  Warn about possible invalidity if assumptions are grossly violated.

### 4. `visualize_data`

**Description:** Creates visualizations of data using matplotlib and seaborn.

**Parameters:**

*   `data` (pandas DataFrame, required): The DataFrame to be visualized.
*   `plot_type` (string, required): The type of plot to create. Supported values: "histogram", "scatter", "bar", "line", "boxplot".
*   `x_column` (string, optional, default: None): The column to use for the x-axis.  Required for "scatter", "bar", and "line" plots.
*   `y_column` (string, optional, default: None): The column to use for the y-axis. Required for "scatter", "bar", and "line" plots.
*   `title` (string, optional, default: None): The title of the plot.
*   `x_label` (string, optional, default: None): The label for the x-axis.
*   `y_label` (string, optional, default: None): The label for the y-axis.
*   `color` (string, optional, default: None): The color of the plot elements.
*   `file_path` (string, optional, default: "plot.png"): The path to save the plot image.  Supported formats: PNG, JPG, PDF.

**Returns:**

*   A message indicating the location where the plot was saved.
*   Error message if the DataFrame is invalid, the plot type is unsupported, or required parameters are missing.

**Example:**

```python
# Create a histogram
analytics.visualize_data(data=data, plot_type="histogram", x_column="age", title="Age Distribution", file_path="age_histogram.png")

# Create a scatter plot
analytics.visualize_data(data=data, plot_type="scatter", x_column="spend", y_column="revenue", title="Spend vs. Revenue", file_path="spend_vs_revenue.png")

# Create a bar plot
analytics.visualize_data(data=data, plot_type="bar", x_column="campaign", y_column="clicks", title="Clicks per Campaign", file_path="clicks_per_campaign.png")

# Create a line plot
analytics.visualize_data(data=data, plot_type="line", x_column="date", y_column="impressions", title="Impressions Over Time", file_path="impressions_over_time.png")

# Create a boxplot
analytics.visualize_data(data=data, plot_type="boxplot", x_column="category", y_column="sales", title="Sales per Category", file_path="sales_per_category.png")
```

**Error Handling:**

*   If the `data` parameter is not a pandas DataFrame, return an error message: "Error: Input data must be a pandas DataFrame".
*   If an unsupported `plot_type` is specified, return an error message: "Error: Unsupported plot type: {plot_type}".
*   If `x_column` or `y_column` are not provided when required by the `plot_type`, return an error message: "Error: x_column and y_column must be provided for {plot_type} plot".
*   If a specified column does not exist in the DataFrame, return an error message: "Error: Column '{column_name}' not found in DataFrame".
*   If there is an error saving the plot, return an error message: "Error: Could not save plot to {file_path}. Details: {exception message}".
*   If columns provided are not of a type usable in a plot (ex: object type used in scatter plot) return an error "Error: Incompatible datatypes for plot_type: {plot_type}. Check datatypes for x_column: {x_column} and y_column: {y_column}".

**Best Practices:**

*   Choose the appropriate `plot_type` based on the data and the message you want to convey.
*   Always include a title and axis labels to make the plot understandable.
*   Use color effectively to highlight important patterns in the data.
*   Save plots in a high-resolution format for clear presentation.
*   Consider the audience when designing visualizations.
*   Use a descriptive `file_path` so you can easily find the plot later.

### 5. `generate_report`

**Description:** Generates a summary report of the data analysis, including key findings, visualizations, and recommendations. The report is saved as a text file.

**Parameters:**

*   `data` (pandas DataFrame, required): The DataFrame used for analysis.
*   `analysis_results` (dict, optional): A dictionary containing the results of the data analysis (e.g., from `analyze_data`).
*   `file_path` (string, optional, default: "report.txt"): The path to save the report file.
*   `report_title` (string, optional, default: "Data Analysis Report"): The title of the report.
*   `insights` (list of strings, optional, default: []): A list of pre-generated insights to include in the report. This allows for the integration of insights derived outside of this function, from other AI skills, etc.

**Returns:**

*   A message indicating the location where the report was saved.
*   Error message if the DataFrame is invalid or the report cannot be generated.

**Example:**

```python
# Generate a report with analysis results
analytics.generate_report(data=data, analysis_results=descriptive_stats, file_path="descriptive_report.txt", report_title="Descriptive Statistics Report")

# Generate a report with custom insights
analytics.generate_report(data=data, file_path="custom_report.txt", report_title="Marketing Campaign Analysis", insights=["Campaign A performed significantly better than Campaign B.", "The conversion rate for mobile users is lower than for desktop users."])
```

**Error Handling:**

*   If the `data` parameter is not a pandas DataFrame, return an error message: "Error: Input data must be a pandas DataFrame".
*   If there is an error writing the report to file, return an error message: "Error: Could not save report to {file_path}. Details: {exception message}".

**Best Practices:**

*   Include a clear and concise summary of the key findings from the data analysis.
*   Refer to relevant visualizations in the report.
*   Provide actionable recommendations based on the analysis.
*   Use a consistent format and style for the report.
*   Tailor the report to the target audience.
*   Include the data source, analysis methods, and any limitations of the analysis in the report.
*   Use the `insights` parameter to include important findings from other AI skills or external sources.  This allows for a holistic report that combines different types of information.

## Dependencies

*   pandas
*   numpy
*   scipy (optional, for advanced statistical analysis)
*   matplotlib
*   seaborn (optional, for enhanced visualizations)

These libraries must be installed in the environment where the skill is used.

## Security Considerations

*   Ensure that the data files are stored securely and access is restricted to authorized users.
*   Be mindful of sensitive data when performing analysis and generating reports.
*   Sanitize any user inputs to prevent code injection or other security vulnerabilities.
*   Validate all data before using it for analysis, especially if the data comes from an untrusted source.
```