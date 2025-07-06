# query_processor.py
from typing import Dict, List, Tuple
import re
from tagging import BUSINESS_TERMS, get_business_concept_hierarchy

class QueryProcessor:
    """Processes and categorizes natural language queries for semantic search."""
    
    def __init__(self):
        self.conceptual_patterns = [
            r'\b(find|show|get|search)\s+(all\s+)?(profitability|revenue|cost|growth|efficiency|margin|profit)',
            r'\b(where\s+are|locate)\s+(my\s+)?(.+\s+)?(metrics|calculations|ratios|analyses)',
            r'\b(profitability|revenue|cost|growth|efficiency)\s+(metrics|data|calculations)',
        ]
        
        self.functional_patterns = [
            r'\b(percentage|average|sum|count|conditional|lookup)\s+(calculations|formulas)',
            r'\b(show|find|get)\s+(formulas|calculations)\s+(that|with)',
            r'\b(vlookup|index|match|if|sumif|countif|average|sum)\s+(formulas|functions)',
        ]
        
        self.comparative_patterns = [
            r'\b(budget\s+vs\s+actual|actual\s+vs\s+budget)',
            r'\b(time\s+series|monthly|quarterly|yearly|historical)',
            r'\b(compare|comparison|versus|vs|against)',
            r'\b(trend|progression|change\s+over\s+time)',
            r'\b(benchmark|industry\s+standard|peer\s+analysis)',
        ]
    
    def categorize_query(self, query: str) -> Dict[str, any]:
        """Categorize query into conceptual, functional, or comparative type."""
        query_lower = query.lower()
        
        # Check for conceptual queries
        conceptual_score = sum(1 for pattern in self.conceptual_patterns 
                             if re.search(pattern, query_lower))
        
        # Check for functional queries  
        functional_score = sum(1 for pattern in self.functional_patterns
                             if re.search(pattern, query_lower))
        
        # Check for comparative queries
        comparative_score = sum(1 for pattern in self.comparative_patterns
                              if re.search(pattern, query_lower))
        
        # Determine primary category
        scores = {
            'conceptual': conceptual_score,
            'functional': functional_score, 
            'comparative': comparative_score
        }
        
        primary_category = max(scores, key=scores.get)
        confidence = max(scores.values()) / sum(scores.values()) if sum(scores.values()) > 0 else 0
        
        return {
            'primary_category': primary_category,
            'confidence': confidence,
            'scores': scores,
            'is_hybrid': sum(v > 0 for v in scores.values()) > 1
        }
    
    def extract_business_concepts(self, query: str) -> List[str]:
        """Extract relevant business concepts from query."""
        query_lower = query.lower()
        concepts = []
        
        # Check against business terms dictionary
        for concept, terms in BUSINESS_TERMS.items():
            # Check primary terms
            if any(term in query_lower for term in terms['primary']):
                concepts.append(concept)
            # Check synonyms
            elif any(synonym in query_lower for synonym in terms['synonyms']):
                concepts.append(concept)
            # Check patterns
            elif any(re.search(pattern, query_lower) for pattern in terms['patterns']):
                concepts.append(concept)
        
        return list(set(concepts))
    
    def expand_query_terms(self, query: str) -> List[str]:
        """Expand query with business synonyms and related terms."""
        query_lower = query.lower()
        expanded_terms = [query]
        
        # Add business synonyms
        for concept, terms in BUSINESS_TERMS.items():
            for term in terms['primary']:
                if term in query_lower:
                    # Add synonyms for this term
                    for synonym in terms['synonyms']:
                        if synonym not in query_lower:
                            expanded_terms.append(query_lower.replace(term, synonym))
        
        return expanded_terms
    
    def process_conceptual_query(self, query: str, concepts: List[str]) -> Dict[str, any]:
        """Process conceptual queries with business domain knowledge."""
        hierarchy = get_business_concept_hierarchy()
        
        # Find related concepts in hierarchy
        related_concepts = []
        for main_concept, sub_concepts in hierarchy.items():
            if any(concept in sub_concepts for concept in concepts):
                related_concepts.extend(sub_concepts)
        
        return {
            'type': 'conceptual',
            'target_concepts': concepts,
            'related_concepts': list(set(related_concepts)),
            'search_strategy': 'semantic_similarity',
            'filter_categories': concepts + related_concepts
        }
    
    def process_functional_query(self, query: str) -> Dict[str, any]:
        """Process functional queries focusing on formulas and calculations."""
        query_lower = query.lower()
        
        # Extract function types
        function_types = []
        if any(term in query_lower for term in ['percentage', '%', 'percent']):
            function_types.append('percentage')
        if any(term in query_lower for term in ['average', 'mean']):
            function_types.append('aggregation')
        if any(term in query_lower for term in ['sum', 'total', 'add']):
            function_types.append('aggregation')
        if any(term in query_lower for term in ['vlookup', 'lookup', 'index', 'match']):
            function_types.append('lookup')
        if any(term in query_lower for term in ['if', 'conditional', 'condition']):
            function_types.append('conditional')
        
        return {
            'type': 'functional',
            'function_types': function_types,
            'search_strategy': 'formula_analysis',
            'filter_categories': ['formula_' + ft for ft in function_types]
        }
    
    def process_comparative_query(self, query: str) -> Dict[str, any]:
        """Process comparative queries for analysis and benchmarking."""
        query_lower = query.lower()
        
        comparison_types = []
        if any(term in query_lower for term in ['budget', 'actual', 'forecast', 'target']):
            comparison_types.append('planning')
        if any(term in query_lower for term in ['time', 'trend', 'historical', 'series']):
            comparison_types.append('temporal')
        if any(term in query_lower for term in ['benchmark', 'industry', 'peer', 'standard']):
            comparison_types.append('benchmark')
        
        return {
            'type': 'comparative',
            'comparison_types': comparison_types,
            'search_strategy': 'contextual_analysis',
            'filter_categories': ['planning_metrics', 'time_series', 'benchmark_analysis']
        }
    
    def process_query(self, query: str) -> Dict[str, any]:
        """Main query processing pipeline."""
        # Step 1: Categorize query
        categorization = self.categorize_query(query)
        
        # Step 2: Extract business concepts
        concepts = self.extract_business_concepts(query)
        
        # Step 3: Expand query terms
        expanded_terms = self.expand_query_terms(query)
        
        # Step 4: Process based on category
        if categorization['primary_category'] == 'conceptual':
            processing_result = self.process_conceptual_query(query, concepts)
        elif categorization['primary_category'] == 'functional':
            processing_result = self.process_functional_query(query)
        elif categorization['primary_category'] == 'comparative':
            processing_result = self.process_comparative_query(query)
        else:
            # Default to conceptual if unclear
            processing_result = self.process_conceptual_query(query, concepts)
        
        return {
            'original_query': query,
            'categorization': categorization,
            'extracted_concepts': concepts,
            'expanded_terms': expanded_terms,
            'processing_result': processing_result
        }