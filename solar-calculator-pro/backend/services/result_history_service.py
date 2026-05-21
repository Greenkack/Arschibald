"""
Result History Service

Handles business logic for calculation result history, versioning, and comparison.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
import secrets

from backend.models.result_history_models import (
    ResultHistory, ResultTag, ResultShare, ResultComparison
)
from backend.models.result_history_schemas import (
    ResultHistoryCreate, ResultHistoryUpdate, ResultSearchRequest,
    ResultComparisonCreate, ResultShareCreate, ResultType
)
from backend.core.exceptions import APIError


class ResultHistoryService:
    """Service for managing calculation result history"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Result History CRUD
    
    def create_result(
        self,
        user_id: int,
        data: ResultHistoryCreate
    ) -> ResultHistory:
        """Create a new result history entry"""
        # Create result
        result = ResultHistory(
            user_id=user_id,
            project_id=data.project_id,
            result_type=data.result_type.value,
            result_name=data.result_name,
            description=data.description,
            input_data=data.input_data,
            output_data=data.output_data,
            parent_id=data.parent_id
        )
        
        # Set version number
        if data.parent_id:
            parent = self.get_result(data.parent_id, user_id)
            result.version = parent.version + 1
        
        self.db.add(result)
        self.db.flush()
        
        # Add tags
        if data.tags:
            for tag_name in data.tags:
                tag = ResultTag(result_id=result.id, tag_name=tag_name.strip())
                self.db.add(tag)
        
        self.db.commit()
        self.db.refresh(result)
        
        return result
    
    def get_result(
        self,
        result_id: int,
        user_id: int,
        include_archived: bool = False
    ) -> ResultHistory:
        """Get a result by ID"""
        query = self.db.query(ResultHistory).filter(
            ResultHistory.id == result_id,
            ResultHistory.user_id == user_id
        )
        
        if not include_archived:
            query = query.filter(ResultHistory.is_archived == False)
        
        result = query.first()
        if not result:
            raise APIError(404, "Result not found")
        
        return result
    
    def update_result(
        self,
        result_id: int,
        user_id: int,
        data: ResultHistoryUpdate
    ) -> ResultHistory:
        """Update a result"""
        result = self.get_result(result_id, user_id, include_archived=True)
        
        # Update fields
        if data.result_name is not None:
            result.result_name = data.result_name
        if data.description is not None:
            result.description = data.description
        if data.is_favorite is not None:
            result.is_favorite = data.is_favorite
        if data.is_archived is not None:
            result.is_archived = data.is_archived
        
        # Update tags
        if data.tags is not None:
            # Remove old tags
            self.db.query(ResultTag).filter(
                ResultTag.result_id == result_id
            ).delete()
            
            # Add new tags
            for tag_name in data.tags:
                tag = ResultTag(result_id=result_id, tag_name=tag_name.strip())
                self.db.add(tag)
        
        self.db.commit()
        self.db.refresh(result)
        
        return result
    
    def delete_result(self, result_id: int, user_id: int) -> None:
        """Delete a result"""
        result = self.get_result(result_id, user_id, include_archived=True)
        self.db.delete(result)
        self.db.commit()
    
    # Result Search and Filtering
    
    def search_results(
        self,
        user_id: int,
        search: ResultSearchRequest
    ) -> Tuple[List[ResultHistory], int]:
        """Search and filter results"""
        query = self.db.query(ResultHistory).filter(
            ResultHistory.user_id == user_id
        )
        
        # Apply filters
        if search.query:
            query = query.filter(
                or_(
                    ResultHistory.result_name.ilike(f"%{search.query}%"),
                    ResultHistory.description.ilike(f"%{search.query}%")
                )
            )
        
        if search.result_type:
            query = query.filter(ResultHistory.result_type == search.result_type.value)
        
        if search.is_favorite is not None:
            query = query.filter(ResultHistory.is_favorite == search.is_favorite)
        
        if search.is_archived is not None:
            query = query.filter(ResultHistory.is_archived == search.is_archived)
        else:
            query = query.filter(ResultHistory.is_archived == False)
        
        if search.date_from:
            query = query.filter(ResultHistory.created_at >= search.date_from)
        
        if search.date_to:
            query = query.filter(ResultHistory.created_at <= search.date_to)
        
        if search.project_id:
            query = query.filter(ResultHistory.project_id == search.project_id)
        
        if search.tags:
            # Filter by tags
            for tag in search.tags:
                query = query.filter(
                    ResultHistory.tags.any(ResultTag.tag_name == tag)
                )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(ResultHistory, search.sort_by)
        if search.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (search.page - 1) * search.page_size
        results = query.offset(offset).limit(search.page_size).all()
        
        return results, total
    
    def get_favorites(self, user_id: int, limit: int = 20) -> List[ResultHistory]:
        """Get favorite results"""
        return self.db.query(ResultHistory).filter(
            ResultHistory.user_id == user_id,
            ResultHistory.is_favorite == True,
            ResultHistory.is_archived == False
        ).order_by(desc(ResultHistory.updated_at)).limit(limit).all()
    
    def get_recent_results(self, user_id: int, limit: int = 10) -> List[ResultHistory]:
        """Get recent results"""
        return self.db.query(ResultHistory).filter(
            ResultHistory.user_id == user_id,
            ResultHistory.is_archived == False
        ).order_by(desc(ResultHistory.created_at)).limit(limit).all()
    
    # Result Versioning
    
    def get_version_tree(self, result_id: int, user_id: int) -> Dict[str, Any]:
        """Get version tree for a result"""
        result = self.get_result(result_id, user_id)
        
        # Get parent
        parent = None
        if result.parent_id:
            parent = self.get_result(result.parent_id, user_id, include_archived=True)
        
        # Get children
        children = self.db.query(ResultHistory).filter(
            ResultHistory.parent_id == result_id,
            ResultHistory.user_id == user_id
        ).order_by(ResultHistory.version).all()
        
        # Get all versions in the tree
        root_id = result.parent_id or result.id
        all_versions = self.db.query(ResultHistory).filter(
            or_(
                ResultHistory.id == root_id,
                ResultHistory.parent_id == root_id
            ),
            ResultHistory.user_id == user_id
        ).order_by(ResultHistory.version).all()
        
        return {
            "current": result,
            "parent": parent,
            "children": children,
            "all_versions": all_versions
        }
    
    def create_version(
        self,
        parent_id: int,
        user_id: int,
        data: ResultHistoryCreate
    ) -> ResultHistory:
        """Create a new version of a result"""
        parent = self.get_result(parent_id, user_id)
        
        # Set parent_id in data
        data.parent_id = parent_id
        
        # Create new version
        return self.create_result(user_id, data)
    
    # Result Comparison
    
    def create_comparison(
        self,
        user_id: int,
        data: ResultComparisonCreate
    ) -> ResultComparison:
        """Create a result comparison"""
        # Verify all results exist and belong to user
        for result_id in data.result_ids:
            self.get_result(result_id, user_id)
        
        comparison = ResultComparison(
            user_id=user_id,
            comparison_name=data.comparison_name,
            description=data.description,
            result_ids=data.result_ids,
            comparison_type=data.comparison_type.value,
            metrics_to_compare=data.metrics_to_compare
        )
        
        self.db.add(comparison)
        self.db.commit()
        self.db.refresh(comparison)
        
        return comparison
    
    def get_comparison(self, comparison_id: int, user_id: int) -> ResultComparison:
        """Get a comparison by ID"""
        comparison = self.db.query(ResultComparison).filter(
            ResultComparison.id == comparison_id,
            ResultComparison.user_id == user_id
        ).first()
        
        if not comparison:
            raise APIError(404, "Comparison not found")
        
        return comparison
    
    def get_comparisons(self, user_id: int) -> List[ResultComparison]:
        """Get all comparisons for a user"""
        return self.db.query(ResultComparison).filter(
            ResultComparison.user_id == user_id
        ).order_by(desc(ResultComparison.created_at)).all()
    
    def delete_comparison(self, comparison_id: int, user_id: int) -> None:
        """Delete a comparison"""
        comparison = self.get_comparison(comparison_id, user_id)
        self.db.delete(comparison)
        self.db.commit()
    
    def compare_results(
        self,
        result_ids: List[int],
        user_id: int,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare multiple results"""
        # Get all results
        results = [self.get_result(rid, user_id) for rid in result_ids]
        
        # Calculate differences
        differences = self._calculate_differences(results, metrics)
        
        # Generate summary
        summary = self._generate_comparison_summary(results, differences)
        
        return {
            "results": results,
            "differences": differences,
            "summary": summary
        }
    
    def _calculate_differences(
        self,
        results: List[ResultHistory],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Calculate differences between results"""
        if len(results) < 2:
            return {}
        
        differences = {}
        
        # Compare output data
        for key in results[0].output_data.keys():
            if metrics and key not in metrics:
                continue
            
            values = []
            for result in results:
                if key in result.output_data:
                    values.append(result.output_data[key])
            
            if values:
                differences[key] = {
                    "values": values,
                    "min": min(values) if all(isinstance(v, (int, float)) for v in values) else None,
                    "max": max(values) if all(isinstance(v, (int, float)) for v in values) else None,
                    "avg": sum(values) / len(values) if all(isinstance(v, (int, float)) for v in values) else None,
                    "range": max(values) - min(values) if all(isinstance(v, (int, float)) for v in values) else None
                }
        
        return differences
    
    def _generate_comparison_summary(
        self,
        results: List[ResultHistory],
        differences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comparison summary"""
        return {
            "result_count": len(results),
            "result_types": list(set(r.result_type for r in results)),
            "date_range": {
                "earliest": min(r.created_at for r in results),
                "latest": max(r.created_at for r in results)
            },
            "metrics_compared": len(differences),
            "significant_differences": [
                key for key, data in differences.items()
                if data.get("range") and data["range"] > 0
            ]
        }
    
    # Result Sharing
    
    def create_share(
        self,
        user_id: int,
        data: ResultShareCreate
    ) -> ResultShare:
        """Create a result share"""
        # Verify result exists and belongs to user
        self.get_result(data.result_id, user_id)
        
        # Generate share token
        share_token = secrets.token_urlsafe(32)
        
        share = ResultShare(
            result_id=data.result_id,
            shared_by_user_id=user_id,
            shared_with_user_id=data.shared_with_user_id,
            share_token=share_token,
            is_public=data.is_public,
            can_edit=data.can_edit,
            expires_at=data.expires_at
        )
        
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        
        return share
    
    def get_share_by_token(self, share_token: str) -> ResultShare:
        """Get a share by token"""
        share = self.db.query(ResultShare).filter(
            ResultShare.share_token == share_token
        ).first()
        
        if not share:
            raise APIError(404, "Share not found")
        
        # Check if expired
        if share.expires_at and share.expires_at < datetime.utcnow():
            raise APIError(403, "Share has expired")
        
        # Update access info
        share.accessed_at = datetime.utcnow()
        share.access_count += 1
        self.db.commit()
        
        return share
    
    def get_shares_for_result(
        self,
        result_id: int,
        user_id: int
    ) -> List[ResultShare]:
        """Get all shares for a result"""
        self.get_result(result_id, user_id)
        
        return self.db.query(ResultShare).filter(
            ResultShare.result_id == result_id,
            ResultShare.shared_by_user_id == user_id
        ).all()
    
    def delete_share(self, share_id: int, user_id: int) -> None:
        """Delete a share"""
        share = self.db.query(ResultShare).filter(
            ResultShare.id == share_id,
            ResultShare.shared_by_user_id == user_id
        ).first()
        
        if not share:
            raise APIError(404, "Share not found")
        
        self.db.delete(share)
        self.db.commit()
    
    # Statistics
    
    def get_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get result statistics for a user"""
        # Total results
        total_results = self.db.query(func.count(ResultHistory.id)).filter(
            ResultHistory.user_id == user_id,
            ResultHistory.is_archived == False
        ).scalar()
        
        # Results by type
        results_by_type = {}
        for result_type in ResultType:
            count = self.db.query(func.count(ResultHistory.id)).filter(
                ResultHistory.user_id == user_id,
                ResultHistory.result_type == result_type.value,
                ResultHistory.is_archived == False
            ).scalar()
            results_by_type[result_type.value] = count
        
        # Favorite count
        favorite_count = self.db.query(func.count(ResultHistory.id)).filter(
            ResultHistory.user_id == user_id,
            ResultHistory.is_favorite == True,
            ResultHistory.is_archived == False
        ).scalar()
        
        # Archived count
        archived_count = self.db.query(func.count(ResultHistory.id)).filter(
            ResultHistory.user_id == user_id,
            ResultHistory.is_archived == True
        ).scalar()
        
        # Recent results
        recent_results = self.get_recent_results(user_id, limit=5)
        
        # Tags usage
        tags_usage = {}
        tags = self.db.query(
            ResultTag.tag_name,
            func.count(ResultTag.id).label("count")
        ).join(ResultHistory).filter(
            ResultHistory.user_id == user_id,
            ResultHistory.is_archived == False
        ).group_by(ResultTag.tag_name).all()
        
        for tag_name, count in tags:
            tags_usage[tag_name] = count
        
        return {
            "total_results": total_results,
            "results_by_type": results_by_type,
            "favorite_count": favorite_count,
            "archived_count": archived_count,
            "recent_results": recent_results,
            "tags_usage": tags_usage
        }
