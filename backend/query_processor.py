# query_processor.py
from typing import Dict, List
import re
from tagging import (
    BUSINESS_TERMS, 
    get_business_concept_hierarchy,
    detect_financial_intent,
    extract_temporal_entities,
    expand_financial_synonyms
)

class QueryProcessor:
    """Enhanced query processor for financial data analysis and semantic search."""
    
    def __init__(self):
        # Original patterns for backward compatibility
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
        # Use the enhanced synonym expansion from tagging module
        return expand_financial_synonyms(query)
    
    def detect_query_intent(self, query: str) -> Dict[str, any]:
        """
        Detect the financial intent of a query using enhanced pattern matching.
        
        Args:
            query: The user's natural language query
            
        Returns:
            Dictionary containing intent analysis results
        """
        return detect_financial_intent(query)
    
    def extract_temporal_context(self, query: str) -> Dict[str, any]:
        """
        Extract temporal context from the query (dates, periods, ranges).
        
        Args:
            query: The user's natural language query
            
        Returns:
            Dictionary containing temporal entities and context
        """
        return extract_temporal_entities(query)
    
    def reformulate_query(self, query: str, intent: Dict[str, any]) -> List[str]:
        """
        Reformulate the query based on detected intent for better retrieval.
        
        Args:
            query: The original query
            intent: The detected intent information
            
        Returns:
            List of reformulated query variations
        """
        reformulated_queries = [query]
        primary_intent = intent.get('primary_intent', 'general_query')
        
        # Intent-specific reformulations
        if primary_intent == 'spending_analysis':
            reformulated_queries.extend([
                f"total expenses {query}",
                f"spending breakdown {query}",
                f"cost analysis {query}"
            ])
        elif primary_intent == 'budgeting':
            reformulated_queries.extend([
                f"budget vs actual {query}",
                f"planned spending {query}",
                f"budget variance {query}"
            ])
        elif primary_intent == 'trend_analysis':
            reformulated_queries.extend([
                f"trend over time {query}",
                f"growth pattern {query}",
                f"time series {query}"
            ])
        elif primary_intent == 'category_analysis':
            reformulated_queries.extend([
                f"category breakdown {query}",
                f"spending by type {query}",
                f"classification {query}"
            ])
        elif primary_intent == 'transaction_search':
            reformulated_queries.extend([
                f"find transactions {query}",
                f"search payments {query}",
                f"locate purchases {query}"
            ])
        elif primary_intent == 'comparison':
            reformulated_queries.extend([
                f"compare {query}",
                f"versus analysis {query}",
                f"benchmark {query}"
            ])
        
        return reformulated_queries[:5]  # Limit to 5 variations
    
    def process_conceptual_query(self, query: str, concepts: List[str]) -> Dict[str, any]:
        """Process conceptual queries with business domain knowledge."""
        hierarchy = get_business_concept_hierarchy()
        
        # Find related concepts in hierarchy
        related_concepts = []
        for sub_concepts in hierarchy.values():
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
        """
        Enhanced query processing pipeline with financial intent detection.
        
        Args:
            query: The user's natural language query
            
        Returns:
            Comprehensive query analysis including intent, temporal context, and processing results
        """
        # Step 1: Detect financial intent (primary enhancement)
        intent_analysis = self.detect_query_intent(query)
        
        # Step 2: Extract temporal context
        temporal_context = self.extract_temporal_context(query)
        
        # Step 3: Original categorization (for backward compatibility)
        categorization = self.categorize_query(query)
        
        # Step 4: Extract business concepts
        concepts = self.extract_business_concepts(query)
        
        # Step 5: Expand query terms with synonyms
        expanded_terms = self.expand_query_terms(query)
        
        # Step 6: Reformulate query based on intent
        reformulated_queries = self.reformulate_query(query, intent_analysis)
        
        # Step 7: Enhanced processing based on intent (priority) or category (fallback)
        primary_intent = intent_analysis.get('primary_intent', 'general_query')
        
        if primary_intent in ['spending_analysis', 'budgeting', 'trend_analysis', 'category_analysis']:
            # Use conceptual processing for these financial intents
            processing_result = self.process_conceptual_query(query, concepts)
            processing_result['search_strategy'] = 'financial_semantic_search'
        elif primary_intent == 'transaction_search':
            # Use functional processing for transaction searches
            processing_result = self.process_functional_query(query)
            processing_result['search_strategy'] = 'transaction_search'
        elif primary_intent == 'comparison':
            # Use comparative processing for comparison queries
            processing_result = self.process_comparative_query(query)
            processing_result['search_strategy'] = 'comparative_analysis'
        else:
            # Fallback to original categorization logic
            if categorization['primary_category'] == 'conceptual':
                processing_result = self.process_conceptual_query(query, concepts)
            elif categorization['primary_category'] == 'functional':
                processing_result = self.process_functional_query(query)
            elif categorization['primary_category'] == 'comparative':
                processing_result = self.process_comparative_query(query)
            else:
                # Default to conceptual if unclear
                processing_result = self.process_conceptual_query(query, concepts)
        
        # Step 8: Enhance processing result with temporal filters
        if temporal_context['has_temporal_context']:
            processing_result['temporal_filters'] = temporal_context['temporal_entities']
            processing_result['temporal_types'] = temporal_context['temporal_types']
        
        return {
            'original_query': query,
            'intent_analysis': intent_analysis,
            'temporal_context': temporal_context,
            'categorization': categorization,
            'extracted_concepts': concepts,
            'expanded_terms': expanded_terms,
            'reformulated_queries': reformulated_queries,
            'processing_result': processing_result
        }