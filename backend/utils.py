import pandas as pd
import re
from typing import Dict, List, Any
from tagging import classify_metric, explain_classification, get_business_concept_hierarchy


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect column types for better business context understanding."""
    column_types = {}

    for col in df.columns:
        col_lower = col.lower()
        sample_values = df[col].dropna().astype(str)

        # First check data type - if it's string/object, it's likely categorical unless proven otherwise
        if df[col].dtype in ['object', 'string']:
            # For string columns, only classify as special types if there are strong indicators
            percentage_values = sample_values.str.contains(
                '%').sum() if len(sample_values) > 0 else 0
            mostly_percentages = percentage_values > len(
                sample_values) * 0.5  # More than 50% contain %

            if ('percent' in col_lower or 'margin' in col_lower or 'growth' in col_lower or
                    'rate' in col_lower or col_lower.endswith('%')) and mostly_percentages:
                column_types[col] = 'percentage'
            elif 'date' in col_lower or 'year' in col_lower or 'month' in col_lower or 'quarter' in col_lower:
                column_types[col] = 'date'
            elif sample_values.str.contains('=').any():
                column_types[col] = 'formula'
            else:
                column_types[col] = 'categorical'

        # For numeric columns, apply business logic
        elif df[col].dtype in ['float64', 'int64']:
            # Check for percentage columns (numeric values between 0-1 or 0-100)
            if (df[col].max() <= 1.0 and df[col].min() >= 0) or 'percent' in col_lower:
                column_types[col] = 'percentage'
            # Check for currency/monetary columns
            elif ('amount' in col_lower or 'price' in col_lower or 'cost' in col_lower or
                  'revenue' in col_lower or 'income' in col_lower or 'profit' in col_lower or
                  'expense' in col_lower or sample_values.str.contains('$').any()):
                column_types[col] = 'currency'
            # Check for ratio columns
            elif ('ratio' in col_lower or 'turnover' in col_lower or 'roi' in col_lower or 'roe' in col_lower):
                column_types[col] = 'ratio'
            else:
                column_types[col] = 'numeric'

        # Default fallback for any other data types
        else:
            column_types[col] = 'text'

    return column_types


def extract_formula_info(value: str) -> Dict[str, Any]:
    """Extract information from formula strings."""
    if not isinstance(value, str) or not value.startswith('='):
        return {}

    formula_info = {'raw_formula': value}

    # Common function patterns
    functions = re.findall(
        r'\b(SUM|AVERAGE|COUNT|IF|VLOOKUP|INDEX|MATCH|SUMIF|COUNTIF)\b', value.upper())
    if functions:
        formula_info['functions'] = functions

    # Mathematical operations
    operations = []
    if '+' in value:
        operations.append('addition')
    if '-' in value:
        operations.append('subtraction')
    if '*' in value:
        operations.append('multiplication')
    if '/' in value:
        operations.append('division')
    if operations:
        formula_info['operations'] = operations

    return formula_info


def create_business_context(col_name: str, value: Any, col_type: str) -> str:
    """Create business context description for a column-value pair."""
    col_lower = col_name.lower()

    # Format value based on type
    if col_type == 'percentage':
        if isinstance(value, (int, float)):
            if value <= 1.0:
                formatted_value = f"{value:.1%}"
            else:
                formatted_value = f"{value}%"
        else:
            formatted_value = str(value)
    elif col_type == 'currency':
        if isinstance(value, (int, float)):
            formatted_value = f"${value:,.0f}"
        else:
            formatted_value = str(value)
    else:
        formatted_value = str(value)

    # Add business context
    context_parts = []

    # Revenue-related context
    if any(term in col_lower for term in ['revenue', 'sales', 'income']):
        context_parts.append('revenue metric')

    # Cost-related context
    elif any(term in col_lower for term in ['cost', 'expense', 'overhead']):
        context_parts.append('cost metric')

    # Profitability context
    elif any(term in col_lower for term in ['profit', 'margin', 'ebitda']):
        context_parts.append('profitability metric')

    # Growth context
    elif any(term in col_lower for term in ['growth', 'change', 'increase']):
        context_parts.append('growth metric')

    # Efficiency context
    elif any(term in col_lower for term in ['roi', 'roe', 'turnover', 'efficiency']):
        context_parts.append('efficiency metric')

    # Time context
    if any(term in col_lower for term in ['yr1', 'yr2', 'year', 'q1', 'q2', 'q3', 'q4', 'quarter']):
        context_parts.append('time-series data')

    if context_parts:
        context_desc = f" ({', '.join(context_parts)})"
    else:
        context_desc = ""

    return f"{col_name}: {formatted_value}{context_desc}"


def dataframe_to_documents(df: pd.DataFrame) -> List[Dict]:
    """Convert DataFrame to documents with enhanced business context."""
    from langchain.schema import Document

    # Detect column types
    column_types = detect_column_types(df)

    docs = []
    for i, row in df.iterrows():
        # Create enhanced row text with business context
        row_parts = []
        formula_info = {}

        for col in df.columns:
            if pd.notnull(row[col]):
                col_type = column_types.get(col, 'text')

                # Extract formula information if present
                if col_type == 'formula':
                    formula_info[col] = extract_formula_info(str(row[col]))

                # Create business context description
                context_desc = create_business_context(col, row[col], col_type)
                row_parts.append(context_desc)

        # Create the main text
        row_text = ", ".join(row_parts)

        # Classify the row using enhanced tagging system
        row_categories = classify_metric(row_text, formula_info, column_types)

        # Enhanced metadata - flatten complex structures for ChromaDB compatibility
        metadata = {
            "row_index": i,
            "column_types_json": str({col: column_types[col] for col in df.columns}),
            "formula_info_json": str(formula_info) if formula_info else "",
            "categories_json": str(row_categories),
            "business_concepts_json": str(list(set(row_categories))),
            "classification_explanation": explain_classification(row_categories, row_text),
            "business_hierarchy_json": str(get_business_concept_hierarchy())
        }

        docs.append(Document(page_content=row_text, metadata=metadata))

    return docs
