# tagging.py
from typing import List, Dict, Set
import re

# Enhanced business term dictionaries for comprehensive financial analysis
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
    },
    # New financial categories for enhanced analysis
    'investment': {
        'primary': ['investment', 'asset', 'portfolio', 'securities', 'stocks', 'bonds'],
        'synonyms': ['holdings', 'investments', 'capital allocation', 'investment portfolio'],
        'patterns': [r'\binvestment\b', r'\basset\b', r'\bportfolio\b', r'\bsecurities\b']
    },
    'budgeting': {
        'primary': ['budget', 'forecast', 'plan', 'target', 'allocation'],
        'synonyms': ['budgeted', 'planned', 'projected', 'estimated', 'allocated'],
        'patterns': [r'\bbudget\b', r'\bforecast\b', r'\bplan\b', r'\btarget\b']
    },
    'variance': {
        'primary': ['variance', 'deviation', 'difference', 'gap', 'variance analysis'],
        'synonyms': ['vs actual', 'over budget', 'under budget', 'favorable', 'unfavorable'],
        'patterns': [r'\bvariance\b', r'\bdeviation\b', r'\bvs\s+actual\b', r'\bover\s+budget\b']
    },
    'valuation': {
        'primary': ['valuation', 'value', 'worth', 'market cap', 'enterprise value'],
        'synonyms': ['fair value', 'market value', 'book value', 'intrinsic value'],
        'patterns': [r'\bvaluation\b', r'\bmarket\s+cap\b', r'\benterprise\s+value\b']
    },
    'tax': {
        'primary': ['tax', 'taxes', 'tax expense', 'tax rate', 'tax burden'],
        'synonyms': ['taxation', 'tax liability', 'tax benefit', 'deferred tax'],
        'patterns': [r'\btax\b', r'\btaxes\b', r'\btax\s+expense\b', r'\btax\s+rate\b']
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

# Financial intent categories for query understanding
FINANCIAL_INTENT_PATTERNS = {
    'spending_analysis': {
        'patterns': [
            r'\b(total|sum|amount)\s+(spent|expenses?|costs?)\b',
            r'\bhow\s+much\s+(did\s+i\s+spend|spent|spending)\b',
            r'\bspending\s+(analysis|breakdown|summary)\b',
            r'\bexpense\s+(report|analysis|breakdown)\b'
        ],
        'keywords': ['spent', 'spending', 'expenses', 'expenditure', 'outflow']
    },
    'budgeting': {
        'patterns': [
            r'\b(budget|budgeted|planned)\s+(vs|versus|compared\s+to)\s+(actual|spent)\b',
            r'\b(over|under)\s+budget\b',
            r'\bbudget\s+(variance|analysis|tracking)\b',
            r'\bhow\s+much\s+(left|remaining)\s+in\s+budget\b'
        ],
        'keywords': ['budget', 'planned', 'allocated', 'forecast', 'target']
    },
    'trend_analysis': {
        'patterns': [
            r'\b(trend|trends|trending|pattern)\b',
            r'\b(over\s+time|monthly|quarterly|yearly)\b',
            r'\b(increase|decrease|growth|decline)\s+(over|in)\b',
            r'\b(compare|comparison)\s+(months|quarters|years)\b'
        ],
        'keywords': ['trend', 'growth', 'change', 'increase', 'decrease', 'pattern']
    },
    'category_analysis': {
        'patterns': [
            r'\b(category|categories|type|types)\s+(breakdown|analysis|summary)\b',
            r'\bspending\s+by\s+category\b',
            r'\bhow\s+much\s+(on|for)\s+\w+\b',
            r'\b(most|least)\s+expensive\s+category\b'
        ],
        'keywords': ['category', 'type', 'classification', 'breakdown']
    },
    'transaction_search': {
        'patterns': [
            r'\b(find|show|search)\s+(transactions?|payments?|purchases?)\b',
            r'\btransactions?\s+(for|from|to|with)\b',
            r'\b(payments?|purchases?)\s+(made|to|from)\b',
            r'\b(specific|particular)\s+transaction\b'
        ],
        'keywords': ['transaction', 'payment', 'purchase', 'transfer', 'charge']
    },
    'comparison': {
        'patterns': [
            r'\b(compare|comparison|vs|versus)\b',
            r'\b(higher|lower|more|less)\s+than\b',
            r'\b(best|worst|highest|lowest)\b',
            r'\b(month|quarter|year)\s+over\s+(month|quarter|year)\b'
        ],
        'keywords': ['compare', 'versus', 'higher', 'lower', 'best', 'worst']
    }
}

# Temporal patterns for date/time understanding
TEMPORAL_PATTERNS = {
    'relative_time': [
        r'\b(last|past|previous)\s+(month|quarter|year|week)\b',
        r'\b(this|current)\s+(month|quarter|year|week)\b',
        r'\b(next|upcoming)\s+(month|quarter|year|week)\b',
        r'\b(today|yesterday|tomorrow)\b',
        r'\b(\d+)\s+(days?|weeks?|months?|years?)\s+ago\b'
    ],
    'specific_periods': [
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\b(q[1-4]|quarter\s+[1-4])\b',
        r'\b(20\d{2}|19\d{2})\b',
        r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b',
        r'\b(\d{1,2})-(\d{1,2})-(\d{2,4})\b'
    ],
    'time_ranges': [
        r'\b(from|between)\s+\w+\s+(to|and)\s+\w+\b',
        r'\b(since|until|before|after)\s+\w+\b',
        r'\b(first|last)\s+(half|quarter)\s+of\b',
        r'\b(ytd|year\s+to\s+date|mtd|month\s+to\s+date)\b'
    ]
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


def detect_financial_intent(query: str) -> Dict[str, any]:
    """
    Detect financial intent from a query using pattern matching.
    
    Args:
        query: The user's query string
        
    Returns:
        Dictionary containing detected intent, confidence, and matched patterns
    """
    query_lower = query.lower()
    intent_scores = {}
    matched_patterns = {}
    
    # Check each intent category
    for intent_name, intent_config in FINANCIAL_INTENT_PATTERNS.items():
        score = 0
        patterns = []
        
        # Check pattern matches
        for pattern in intent_config['patterns']:
            if re.search(pattern, query_lower, re.IGNORECASE):
                score += 2
                patterns.append(pattern)
        
        # Check keyword matches
        for keyword in intent_config['keywords']:
            if keyword in query_lower:
                score += 1
        
        if score > 0:
            intent_scores[intent_name] = score
            matched_patterns[intent_name] = patterns
    
    # Determine primary intent
    if intent_scores:
        primary_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[primary_intent] / sum(intent_scores.values())
        
        return {
            'primary_intent': primary_intent,
            'confidence': confidence,
            'all_intents': intent_scores,
            'matched_patterns': matched_patterns
        }
    else:
        return {
            'primary_intent': 'general_query',
            'confidence': 0.0,
            'all_intents': {},
            'matched_patterns': {}
        }


def extract_temporal_entities(query: str) -> Dict[str, any]:
    """
    Extract temporal entities (dates, periods, ranges) from a query.
    
    Args:
        query: The user's query string
        
    Returns:
        Dictionary containing temporal entities and their types
    """
    query_lower = query.lower()
    temporal_entities = {
        'relative_time': [],
        'specific_periods': [],
        'time_ranges': []
    }
    
    # Extract each type of temporal entity
    for entity_type, patterns in TEMPORAL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            if matches:
                temporal_entities[entity_type].extend(matches)
    
    # Determine if query has temporal context
    has_temporal_context = any(temporal_entities.values())
    
    return {
        'has_temporal_context': has_temporal_context,
        'temporal_entities': temporal_entities,
        'temporal_types': [k for k, v in temporal_entities.items() if v]
    }


def expand_financial_synonyms(query: str) -> List[str]:
    """
    Expand a query with financial synonyms and related terms.
    
    Args:
        query: The original query string
        
    Returns:
        List of expanded query variations
    """
    expanded_queries = [query]
    query_lower = query.lower()
    
    # For each business term, find matches and create variations
    for terms in BUSINESS_TERMS.values():
        # Check if any primary term is in the query
        for primary_term in terms['primary']:
            if primary_term in query_lower:
                # Create variations with synonyms
                for synonym in terms['synonyms']:
                    expanded_query = query_lower.replace(primary_term, synonym)
                    if expanded_query != query_lower:
                        expanded_queries.append(expanded_query)
    
    return list(set(expanded_queries))[:5]  # Limit to 5 variations


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
        elif category == 'budgeting':
            explanations.append("Contains budget or planning data")
        elif category == 'variance':
            explanations.append("Contains variance or comparison analysis")
        elif category == 'investment':
            explanations.append("Contains investment or asset data")
        elif category == 'tax':
            explanations.append("Contains tax-related information")
        elif category == 'valuation':
            explanations.append("Contains valuation or market data")
    
    return "; ".join(explanations) if explanations else f"Classified as: {', '.join(categories)}"
