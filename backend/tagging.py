# tagging.py
from typing import List, Dict, Set
import re

# Business term dictionaries for comprehensive classification
BUSINESS_TERMS = {
    'profitability': {
        'primary': ['profit', 'margin', 'ebitda', 'ebit', 'earnings', 'net income', 'operating income'],
        'synonyms': ['bottom line', 'profitability', 'margins', 'net profit', 'gross profit', 'operating profit'],
        'patterns': [r'\bprofit\b', r'\bmargin\b', r'\bearnings\b', r'\bebitda\b']
    },
    'revenue': {
        'primary': ['revenue', 'sales', 'income', 'receipts', 'turnover'],
        'synonyms': ['top line', 'gross sales', 'net sales', 'total sales', 'sales revenue'],
        'patterns': [r'\brevenue\b', r'\bsales\b', r'\bincome\b', r'\bturnover\b']
    },
    'cost': {
        'primary': ['cost', 'expense', 'expenditure', 'overhead', 'opex', 'capex'],
        'synonyms': ['costs', 'expenses', 'spending', 'outlay', 'outgoing', 'cogs'],
        'patterns': [r'\bcost\b', r'\bexpense\b', r'\boverhead\b', r'\bcogs\b']
    },
    'growth': {
        'primary': ['growth', 'increase', 'expansion', 'rise'],
        'synonyms': ['yoy', 'qoq', 'mom', 'cagr', 'change', 'variance', 'delta'],
        'patterns': [r'\bgrowth\b', r'\byoy\b', r'\bqoq\b', r'\bcagr\b', r'%\s*change']
    },
    'efficiency': {
        'primary': ['efficiency', 'productivity', 'utilization', 'performance'],
        'synonyms': ['roi', 'roe', 'roa', 'roic', 'turnover', 'ratio', 'yield'],
        'patterns': [r'\broi\b', r'\broe\b', r'\broa\b', r'\bturnover\b', r'\bratio\b']
    },
    'liquidity': {
        'primary': ['cash', 'liquidity', 'working capital', 'current ratio'],
        'synonyms': ['cash flow', 'liquid assets', 'quick ratio', 'cash position'],
        'patterns': [r'\bcash\b', r'\bliquidity\b', r'working\s+capital']
    },
    'leverage': {
        'primary': ['debt', 'leverage', 'liability', 'borrowing'],
        'synonyms': ['debt ratio', 'debt to equity', 'gearing', 'financial leverage'],
        'patterns': [r'\bdebt\b', r'\bleverage\b', r'debt\s+to\s+equity']
    }
}

# Formula function classifications
FORMULA_FUNCTIONS = {
    'aggregation': ['sum', 'average', 'count', 'max', 'min', 'median'],
    'lookup': ['vlookup', 'hlookup', 'index', 'match', 'xlookup'],
    'conditional': ['if', 'sumif', 'countif', 'averageif', 'sumifs', 'countifs'],
    'mathematical': ['round', 'abs', 'sqrt', 'power', 'log'],
    'text': ['concatenate', 'left', 'right', 'mid', 'len', 'trim'],
    'date': ['today', 'now', 'year', 'month', 'day', 'date']
}

# Business context patterns for better classification
CONTEXT_PATTERNS = {
    'time_series': [r'\b(q[1-4]|quarter|yr\d+|year|monthly|annual)\b'],
    'percentage': [r'%|percent|margin|rate|ratio'],
    'currency': [r'\$|revenue|cost|profit|expense|price|value'],
    'comparative': [r'\bvs\b|versus|compared|budget|actual|forecast|target']
}


def extract_business_synonyms(text: str) -> Set[str]:
    """Extract business synonyms and related terms from text."""
    text_lower = text.lower()
    synonyms = set()
    
    # Check for compound terms first
    compound_terms = [
        ('gross profit', 'profitability'),
        ('net profit', 'profitability'), 
        ('operating profit', 'profitability'),
        ('profit margin', 'profitability'),
        ('gross margin', 'profitability'),
        ('net margin', 'profitability'),
        ('total revenue', 'revenue'),
        ('net revenue', 'revenue'),
        ('sales revenue', 'revenue'),
        ('operating expense', 'cost'),
        ('cost of goods sold', 'cost'),
        ('return on investment', 'efficiency'),
        ('return on equity', 'efficiency'),
        ('working capital', 'liquidity'),
        ('cash flow', 'liquidity')
    ]
    
    for term, category in compound_terms:
        if term in text_lower:
            synonyms.add(category)
    
    return synonyms


def classify_by_formula(formula_info: Dict) -> List[str]:
    """Classify metrics based on formula analysis."""
    categories = []
    
    if not formula_info:
        return categories
    
    functions = formula_info.get('functions', [])
    operations = formula_info.get('operations', [])
    
    # Function-based classification
    for func_category, func_list in FORMULA_FUNCTIONS.items():
        if any(func.lower() in [f.lower() for f in functions] for func in func_list):
            categories.append(f'formula_{func_category}')
    
    # Operation-based classification
    if 'division' in operations:
        categories.append('ratio_calculation')
    if 'subtraction' in operations:
        categories.append('variance_calculation')
    if 'multiplication' in operations:
        categories.append('scaling_calculation')
    
    return categories


def classify_metric(row_text: str, formula_info: Dict = None, column_types: Dict = None) -> List[str]:
    """Enhanced metric classification with business context understanding."""
    text = row_text.lower()
    categories = []
    
    # Primary business concept classification
    for concept, terms in BUSINESS_TERMS.items():
        # Check primary terms
        if any(term in text for term in terms['primary']):
            categories.append(concept)
        
        # Check synonyms
        elif any(synonym in text for synonym in terms['synonyms']):
            categories.append(concept)
        
        # Check regex patterns
        elif any(re.search(pattern, text) for pattern in terms['patterns']):
            categories.append(concept)
    
    # Extract compound business synonyms
    compound_categories = extract_business_synonyms(text)
    categories.extend(list(compound_categories))
    
    # Context-based classification
    for context, patterns in CONTEXT_PATTERNS.items():
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            categories.append(context)
    
    # Formula-based classification
    if formula_info:
        formula_categories = classify_by_formula(formula_info)
        categories.extend(formula_categories)
    
    # Column type-based classification
    if column_types:
        for col_type in column_types.values():
            if col_type in ['percentage', 'currency', 'ratio']:
                categories.append(col_type)
    
    # Special business logic classifications
    if any(term in text for term in ['budget', 'actual', 'forecast', 'target']):
        categories.append('planning_metrics')
    
    if any(term in text for term in ['benchmark', 'industry', 'peer', 'competitor']):
        categories.append('benchmark_analysis')
    
    # Remove duplicates and return
    return list(set(categories))


def get_business_concept_hierarchy() -> Dict[str, List[str]]:
    """Return hierarchical business concept relationships."""
    return {
        'financial_performance': ['profitability', 'revenue', 'cost', 'efficiency'],
        'growth_metrics': ['growth', 'variance_calculation', 'time_series'],
        'financial_position': ['liquidity', 'leverage', 'working_capital'],
        'operational_metrics': ['efficiency', 'productivity', 'utilization'],
        'analytical_tools': ['ratio_calculation', 'benchmark_analysis', 'planning_metrics']
    }


def explain_classification(categories: List[str], row_text: str) -> str:
    """Provide human-readable explanation of why content was classified."""
    if not categories:
        return "No specific business classification found."
    
    explanations = []
    text_lower = row_text.lower()
    
    for category in categories:
        if category == 'profitability':
            if 'margin' in text_lower:
                explanations.append("Contains margin calculations (profitability metric)")
            elif 'profit' in text_lower:
                explanations.append("Contains profit-related data (profitability metric)")
        elif category == 'revenue':
            explanations.append("Contains revenue/sales data (top-line metric)")
        elif category == 'cost':
            explanations.append("Contains cost/expense data (operational metric)")
        elif category == 'growth':
            explanations.append("Contains growth or change metrics (performance indicator)")
        elif category == 'efficiency':
            explanations.append("Contains efficiency ratios (performance metric)")
        elif category == 'percentage':
            explanations.append("Contains percentage-based calculations")
        elif category == 'ratio_calculation':
            explanations.append("Contains ratio calculations (analytical metric)")
    
    return "; ".join(explanations) if explanations else f"Classified as: {', '.join(categories)}"
