import pandas as pd
import re
import json
from typing import Dict, List, Any
from fastapi import HTTPException, UploadFile
from tagging import classify_metric, explain_classification, get_business_concept_hierarchy

# Optional magic import for MIME type detection
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


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

        # Enhanced metadata - use JSON for safe parsing
        metadata = {
            "row_index": i,
            "column_types_json": json.dumps({col: column_types[col] for col in df.columns}),
            "formula_info_json": json.dumps(formula_info) if formula_info else "{}",
            "categories_json": json.dumps(row_categories),
            "business_concepts_json": json.dumps(list(set(row_categories))),
            "classification_explanation": explain_classification(row_categories, row_text),
            "business_hierarchy_json": json.dumps(get_business_concept_hierarchy())
        }

        docs.append(Document(page_content=row_text, metadata=metadata))

    return docs


def explain_relevance(query_analysis, doc_categories, doc_content):
    """Generate explanation for why this result is relevant to the query."""
    extracted_concepts = query_analysis.get('extracted_concepts', [])
    query_type = query_analysis.get('categorization', {}).get(
        'primary_category', 'unknown')

    # Find matching concepts
    matching_concepts = [
        concept for concept in extracted_concepts if concept in doc_categories]

    if matching_concepts:
        return f"Matches {', '.join(matching_concepts)} concepts from your {query_type} query"
    elif doc_categories:
        return f"Contains {', '.join(doc_categories[:2])} data relevant to your search"
    else:
        # Use doc_content for basic text similarity explanation
        return f"Text similarity match with your query (content: {doc_content[:50]}...)"


async def validate_csv_file(file: UploadFile):
    """Comprehensive CSV file validation for security and performance."""
    
    # 1. File size validation (10MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    file_size = 0
    contents = b''
    
    # Read file in chunks to check size without loading everything
    while chunk := await file.read(8192):  # 8KB chunks
        file_size += len(chunk)
        contents += chunk
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    # Reset file pointer for later reading
    await file.seek(0)
    
    # 2. Filename validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Check file extension
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="Only CSV files are supported"
        )
    
    # Sanitize filename (remove dangerous characters)
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    if any(char in file.filename for char in dangerous_chars):
        raise HTTPException(
            status_code=400,
            detail="Filename contains invalid characters"
        )
    
    # 3. MIME type validation (optional, if magic is available)
    if MAGIC_AVAILABLE:
        try:
            mime_type = magic.from_buffer(contents[:1024], mime=True)
            allowed_mime_types = ['text/csv', 'text/plain', 'application/csv']
            if mime_type not in allowed_mime_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Expected CSV, got {mime_type}"
                )
        except Exception:
            # If magic fails, continue without MIME validation
            pass
    
    # 4. Content validation - ensure it's actually CSV-like
    try:
        # Try to read first few lines as CSV
        content_str = contents.decode('utf-8')[:1000]  # First 1000 chars
        lines = content_str.split('\n')[:5]  # First 5 lines
        
        # Basic CSV structure check
        if len(lines) < 2:
            raise HTTPException(
                status_code=400,
                detail="File must contain at least a header and one data row"
            )
        
        # Check for reasonable number of columns (between 1-100)
        first_line_columns = len(lines[0].split(','))
        if first_line_columns < 1 or first_line_columns > 100:
            raise HTTPException(
                status_code=400,
                detail="Invalid CSV structure: too few or too many columns"
            )
            
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File encoding not supported. Please use UTF-8"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file format"
        )


def sanitize_query_input(query_text: str, max_length: int = 500) -> str:
    """Sanitize and validate user query input for security."""
    
    if not query_text:
        raise HTTPException(
            status_code=400,
            detail="Query text is required"
        )
    
    # 1. Length validation
    if len(query_text) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long. Maximum length is {max_length} characters"
        )
    
    # 2. Remove potentially dangerous characters
    # Allow alphanumeric, spaces, basic punctuation for business queries
    import string
    allowed_chars = string.ascii_letters + string.digits + string.punctuation + string.whitespace
    
    # Remove any non-printable characters
    sanitized = ''.join(char for char in query_text if char in allowed_chars)
    
    # 3. Remove excessive whitespace
    sanitized = ' '.join(sanitized.split())
    
    # 4. Enhanced suspicious pattern detection
    suspicious_patterns = [
        # Prompt injection patterns
        'ignore previous instructions',
        'ignore above',
        'ignore all previous',
        'system prompt',
        'you are now',
        'pretend to be',
        'act as if',
        'new instructions:',
        'override previous',
        
        # Code execution patterns  
        'execute',
        'run command',
        'exec(',
        'eval(',
        'system(',
        '__import__',
        'subprocess',
        'os.system',
        'shell',
        'bash',
        'cmd',
        
        # Script injection patterns
        '<script',
        '</script>',
        'javascript:',
        'data:text/html',
        'vbscript:',
        'onclick',
        'onerror',
        'onload',
        
        # SQL injection patterns
        'union select',
        'drop table',
        'delete from',
        'insert into',
        'update set',
        '--',
        '/*',
        '*/',
        'or 1=1',
        'and 1=1',
        
        # File system patterns
        '../',
        '..\\',
        '/etc/passwd',
        '/etc/shadow',
        'c:\\windows',
        
        # Network patterns
        'http://',
        'https://',
        'ftp://',
        'file://',
        'smtp://'
    ]
    
    query_lower = sanitized.lower()
    for pattern in suspicious_patterns:
        if pattern in query_lower:
            raise HTTPException(
                status_code=400,
                detail="Query contains potentially unsafe content"
            )
    
    # 5. Ensure minimum length for meaningful queries
    if len(sanitized.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Query must be at least 2 characters long"
        )
    
    return sanitized.strip()
