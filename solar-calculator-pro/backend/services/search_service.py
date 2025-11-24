"""
Search Service for Solar Calculator Pro

Provides comprehensive search functionality across all entities including:
- Projects (solar, heat pump, combined)
- Customers
- Products
- Documents
- Offers
- Contracts

Features:
- Full-text search
- Fuzzy matching
- Advanced filtering
- Search suggestions
- Search analytics
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session
import re
from difflib import SequenceMatcher


class SearchService:
    """Service for handling search and filter operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self._search_history = []
    
    def global_search(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 50,
        fuzzy: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform global search across all entity types
        
        Args:
            query: Search query string
            entity_types: List of entity types to search (None = all)
            limit: Maximum results per entity type
            fuzzy: Enable fuzzy matching
            
        Returns:
            Dictionary with entity types as keys and result lists as values
        """
        if not query or len(query.strip()) < 2:
            return {}
        
        query = query.strip()
        self._log_search(query)
        
        # Default to all entity types if none specified
        if entity_types is None:
            entity_types = [
                'projects', 'customers', 'products', 
                'documents', 'offers', 'contracts'
            ]
        
        results = {}
        
        if 'projects' in entity_types:
            results['projects'] = self._search_projects(query, limit, fuzzy)
        
        if 'customers' in entity_types:
            results['customers'] = self._search_customers(query, limit, fuzzy)
        
        if 'products' in entity_types:
            results['products'] = self._search_products(query, limit, fuzzy)
        
        if 'documents' in entity_types:
            results['documents'] = self._search_documents(query, limit, fuzzy)
        
        if 'offers' in entity_types:
            results['offers'] = self._search_offers(query, limit, fuzzy)
        
        if 'contracts' in entity_types:
            results['contracts'] = self._search_contracts(query, limit, fuzzy)
        
        return results
    
    def _search_projects(
        self, 
        query: str, 
        limit: int, 
        fuzzy: bool
    ) -> List[Dict[str, Any]]:
        """Search solar/heat pump projects"""
        # Placeholder - would query actual project tables
        results = []
        
        # Example structure
        search_fields = ['name', 'customer_name', 'project_type', 'status']
        
        # Build query with OR conditions across fields
        # In real implementation, would use SQLAlchemy ORM
        
        return results[:limit]
    
    def _search_customers(
        self, 
        query: str, 
        limit: int, 
        fuzzy: bool
    ) -> List[Dict[str, Any]]:
        """Search customers"""
        results = []
        
        # Search fields: name, email, phone, address, company
        search_fields = ['name', 'email', 'phone', 'address', 'company']
        
        return results[:limit]
    
    def _search_products(
        self, 
        query: str, 
        limit: int, 
        fuzzy: bool
    ) -> List[Dict[str, Any]]:
        """Search products"""
        results = []
        
        # Search fields: name, manufacturer, category, model, description
        search_fields = ['name', 'manufacturer', 'category', 'model', 'description']
        
        return results[:limit]
    
    def _search_documents(
        self, 
        query: str, 
        limit: int, 
        fuzzy: bool
    ) -> List[Dict[str, Any]]:
        """Search documents"""
        results = []
        
        # Search fields: title, description, tags, content
        search_fields = ['title', 'description', 'tags']
        
        return results[:limit]
    
    def _search_offers(
        self, 
        query: str, 
        limit: int, 
        fuzzy: bool
    ) -> List[Dict[str, Any]]:
        """Search offers"""
        results = []
        
        # Search fields: offer_number, customer_name, status, products
        search_fields = ['offer_number', 'customer_name', 'status']
        
        return results[:limit]
    
    def _search_contracts(
        self, 
        query: str, 
        limit: int, 
        fuzzy: bool
    ) -> List[Dict[str, Any]]:
        """Search contracts"""
        results = []
        
        # Search fields: contract_number, customer_name, status, type
        search_fields = ['contract_number', 'customer_name', 'status', 'type']
        
        return results[:limit]
    
    def fuzzy_match(self, query: str, text: str, threshold: float = 0.6) -> bool:
        """
        Perform fuzzy string matching
        
        Args:
            query: Search query
            text: Text to match against
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            True if similarity >= threshold
        """
        if not query or not text:
            return False
        
        query = query.lower()
        text = text.lower()
        
        # Exact match
        if query in text:
            return True
        
        # Calculate similarity ratio
        ratio = SequenceMatcher(None, query, text).ratio()
        return ratio >= threshold
    
    def get_search_suggestions(
        self, 
        partial_query: str, 
        limit: int = 10
    ) -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        if not partial_query or len(partial_query) < 2:
            return []
        
        suggestions = []
        
        # Get suggestions from search history
        history_suggestions = self._get_history_suggestions(partial_query, limit)
        suggestions.extend(history_suggestions)
        
        # Get suggestions from entity names
        entity_suggestions = self._get_entity_suggestions(partial_query, limit)
        suggestions.extend(entity_suggestions)
        
        # Remove duplicates and limit
        suggestions = list(dict.fromkeys(suggestions))
        return suggestions[:limit]
    
    def _get_history_suggestions(
        self, 
        partial_query: str, 
        limit: int
    ) -> List[str]:
        """Get suggestions from search history"""
        partial_lower = partial_query.lower()
        
        suggestions = [
            term for term in self._search_history
            if term.lower().startswith(partial_lower)
        ]
        
        return suggestions[:limit]
    
    def _get_entity_suggestions(
        self, 
        partial_query: str, 
        limit: int
    ) -> List[str]:
        """Get suggestions from entity names"""
        # Would query database for matching entity names
        # Placeholder implementation
        suggestions = []
        
        return suggestions[:limit]
    
    def _log_search(self, query: str):
        """Log search query for analytics and suggestions"""
        if query and query not in self._search_history:
            self._search_history.append(query)
            
            # Keep only last 100 searches
            if len(self._search_history) > 100:
                self._search_history = self._search_history[-100:]
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """
        Get search analytics data
        
        Returns:
            Dictionary with analytics data
        """
        return {
            'total_searches': len(self._search_history),
            'recent_searches': self._search_history[-10:] if self._search_history else [],
            'popular_searches': self._get_popular_searches(),
            'search_trends': self._get_search_trends()
        }
    
    def _get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular search terms"""
        # Count frequency of each search term
        frequency = {}
        for term in self._search_history:
            frequency[term] = frequency.get(term, 0) + 1
        
        # Sort by frequency
        popular = sorted(
            frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [
            {'term': term, 'count': count}
            for term, count in popular[:limit]
        ]
    
    def _get_search_trends(self) -> Dict[str, Any]:
        """Get search trends over time"""
        # Placeholder - would analyze search patterns over time
        return {
            'trending_up': [],
            'trending_down': [],
            'stable': []
        }


class FilterService:
    """Service for handling advanced filtering operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def apply_filters(
        self,
        entity_type: str,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = 'asc',
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Apply filters to entity query
        
        Args:
            entity_type: Type of entity to filter
            filters: Dictionary of filter criteria
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            page: Page number (1-indexed)
            page_size: Number of results per page
            
        Returns:
            Dictionary with filtered results and metadata
        """
        # Build base query based on entity type
        query = self._get_base_query(entity_type)
        
        # Apply filters
        query = self._apply_filter_conditions(query, entity_type, filters)
        
        # Get total count before pagination
        total_count = self._get_count(query)
        
        # Apply sorting
        if sort_by:
            query = self._apply_sorting(query, entity_type, sort_by, sort_order)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute query
        results = self._execute_query(query, entity_type)
        
        return {
            'results': results,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'has_next': page * page_size < total_count,
            'has_prev': page > 1
        }
    
    def _get_base_query(self, entity_type: str):
        """Get base query for entity type"""
        # Placeholder - would return actual SQLAlchemy query
        return None
    
    def _apply_filter_conditions(
        self, 
        query, 
        entity_type: str, 
        filters: Dict[str, Any]
    ):
        """Apply filter conditions to query"""
        # Placeholder - would apply actual filter conditions
        return query
    
    def _get_count(self, query) -> int:
        """Get total count from query"""
        # Placeholder - would execute count query
        return 0
    
    def _apply_sorting(
        self, 
        query, 
        entity_type: str, 
        sort_by: str, 
        sort_order: str
    ):
        """Apply sorting to query"""
        # Placeholder - would apply actual sorting
        return query
    
    def _execute_query(self, query, entity_type: str) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        # Placeholder - would execute actual query
        return []
    
    def get_filter_options(self, entity_type: str) -> Dict[str, Any]:
        """
        Get available filter options for entity type
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Dictionary with available filter options
        """
        options = {
            'projects': {
                'project_type': ['solar', 'heatpump', 'combined'],
                'status': ['draft', 'active', 'completed', 'archived'],
                'date_range': True,
                'price_range': True
            },
            'customers': {
                'customer_type': ['residential', 'commercial', 'industrial'],
                'status': ['active', 'inactive', 'prospect'],
                'date_range': True
            },
            'products': {
                'category': ['pv_module', 'inverter', 'battery', 'heatpump'],
                'manufacturer': [],  # Would be populated from database
                'price_range': True,
                'availability': ['in_stock', 'out_of_stock', 'discontinued']
            },
            'documents': {
                'document_type': ['contract', 'invoice', 'datasheet', 'manual'],
                'status': ['draft', 'final', 'archived'],
                'date_range': True
            },
            'offers': {
                'status': ['draft', 'sent', 'accepted', 'rejected', 'expired'],
                'date_range': True,
                'price_range': True
            },
            'contracts': {
                'contract_type': ['installation', 'maintenance', 'warranty'],
                'status': ['active', 'completed', 'cancelled'],
                'date_range': True
            }
        }
        
        return options.get(entity_type, {})


class SavedSearchService:
    """Service for managing saved searches"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_search(
        self,
        user_id: int,
        name: str,
        entity_type: str,
        query: str,
        filters: Dict[str, Any],
        is_public: bool = False
    ) -> Dict[str, Any]:
        """
        Save a search for later use
        
        Args:
            user_id: ID of user saving the search
            name: Name for the saved search
            entity_type: Type of entity being searched
            query: Search query string
            filters: Filter criteria
            is_public: Whether search is public
            
        Returns:
            Saved search data
        """
        saved_search = {
            'id': self._generate_id(),
            'user_id': user_id,
            'name': name,
            'entity_type': entity_type,
            'query': query,
            'filters': filters,
            'is_public': is_public,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Would save to database
        
        return saved_search
    
    def get_saved_searches(
        self,
        user_id: int,
        include_public: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get saved searches for user
        
        Args:
            user_id: ID of user
            include_public: Include public saved searches
            
        Returns:
            List of saved searches
        """
        # Would query database
        return []
    
    def delete_saved_search(self, search_id: int, user_id: int) -> bool:
        """
        Delete a saved search
        
        Args:
            search_id: ID of search to delete
            user_id: ID of user (for authorization)
            
        Returns:
            True if deleted successfully
        """
        # Would delete from database
        return True
    
    def update_saved_search(
        self,
        search_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a saved search
        
        Args:
            search_id: ID of search to update
            user_id: ID of user (for authorization)
            updates: Fields to update
            
        Returns:
            Updated search data
        """
        # Would update in database
        return {}
    
    def _generate_id(self) -> int:
        """Generate unique ID for saved search"""
        # Placeholder - would use database auto-increment
        return 1
