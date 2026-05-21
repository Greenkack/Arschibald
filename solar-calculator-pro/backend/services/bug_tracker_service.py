"""
Bug Tracker Service

Tracks bugs reported during beta testing and manages fix implementation.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class BugPriority(str, Enum):
    """Bug priority levels"""
    CRITICAL = "P0"  # Crashes, data loss
    HIGH = "P1"      # Major functionality broken
    MEDIUM = "P2"    # Minor issues
    LOW = "P3"       # Cosmetic issues


class BugStatus(str, Enum):
    """Bug status"""
    REPORTED = "reported"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    VERIFIED = "verified"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"


class BugCategory(str, Enum):
    """Bug categories"""
    CRASH = "crash"
    PERFORMANCE = "performance"
    UI_UX = "ui_ux"
    DATA = "data"
    CALCULATION = "calculation"
    INTEGRATION = "integration"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"


class Bug:
    """Bug model"""
    
    def __init__(
        self,
        bug_id: str,
        title: str,
        description: str,
        priority: BugPriority,
        category: BugCategory,
        status: BugStatus = BugStatus.REPORTED,
        reporter: Optional[str] = None,
        assignee: Optional[str] = None,
        steps_to_reproduce: Optional[List[str]] = None,
        expected_behavior: Optional[str] = None,
        actual_behavior: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        attachments: Optional[List[str]] = None,
        related_bugs: Optional[List[str]] = None,
        fix_description: Optional[str] = None,
        fix_commit: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        fixed_at: Optional[datetime] = None,
        verified_at: Optional[datetime] = None
    ):
        self.bug_id = bug_id
        self.title = title
        self.description = description
        self.priority = priority
        self.category = category
        self.status = status
        self.reporter = reporter
        self.assignee = assignee
        self.steps_to_reproduce = steps_to_reproduce or []
        self.expected_behavior = expected_behavior
        self.actual_behavior = actual_behavior
        self.environment = environment or {}
        self.attachments = attachments or []
        self.related_bugs = related_bugs or []
        self.fix_description = fix_description
        self.fix_commit = fix_commit
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.fixed_at = fixed_at
        self.verified_at = verified_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bug to dictionary"""
        return {
            "bug_id": self.bug_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "category": self.category.value,
            "status": self.status.value,
            "reporter": self.reporter,
            "assignee": self.assignee,
            "steps_to_reproduce": self.steps_to_reproduce,
            "expected_behavior": self.expected_behavior,
            "actual_behavior": self.actual_behavior,
            "environment": self.environment,
            "attachments": self.attachments,
            "related_bugs": self.related_bugs,
            "fix_description": self.fix_description,
            "fix_commit": self.fix_commit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "fixed_at": self.fixed_at.isoformat() if self.fixed_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None
        }


class BugTrackerService:
    """Service for tracking and managing bugs"""
    
    def __init__(self):
        self.bugs: Dict[str, Bug] = {}
        self._load_beta_bugs()
    
    def _load_beta_bugs(self):
        """Load bugs reported during beta testing"""
        # Simulated beta bugs based on common issues
        beta_bugs = [
            Bug(
                bug_id="BUG-001",
                title="Memory leak in 3D visualization",
                description="App memory usage grows continuously when 3D viewer is open",
                priority=BugPriority.CRITICAL,
                category=BugCategory.PERFORMANCE,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_1",
                steps_to_reproduce=[
                    "Open 3D visualization",
                    "Rotate and zoom for 5+ minutes",
                    "Check memory usage in task manager"
                ],
                expected_behavior="Memory usage should stabilize",
                actual_behavior="Memory grows from 300MB to 1.5GB+",
                environment={"os": "Windows 11", "ram": "16GB", "gpu": "NVIDIA RTX 3060"}
            ),
            Bug(
                bug_id="BUG-002",
                title="Price matrix calculation error for 'kein Speicher'",
                description="Wrong price returned when 'kein Speicher' option is selected",
                priority=BugPriority.CRITICAL,
                category=BugCategory.CALCULATION,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_2",
                steps_to_reproduce=[
                    "Select 30 PV modules",
                    "Select 'kein Speicher' for battery",
                    "Calculate price"
                ],
                expected_behavior="Should use last column of price matrix",
                actual_behavior="Returns 0 or wrong price",
                environment={"os": "macOS 13", "version": "1.0.0-beta.5"}
            ),
            Bug(
                bug_id="BUG-003",
                title="PDF generation timeout for large projects",
                description="PDF generation fails for projects with >50 modules",
                priority=BugPriority.CRITICAL,
                category=BugCategory.PERFORMANCE,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_3",
                steps_to_reproduce=[
                    "Create project with 60 modules",
                    "Add all optional sections",
                    "Generate PDF"
                ],
                expected_behavior="PDF should generate successfully",
                actual_behavior="Timeout after 30 seconds",
                environment={"os": "Windows 10", "cpu": "Intel i5"}
            ),
            Bug(
                bug_id="BUG-004",
                title="Data loss on app crash",
                description="Unsaved work is lost when app crashes",
                priority=BugPriority.CRITICAL,
                category=BugCategory.DATA,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_4",
                steps_to_reproduce=[
                    "Create new project",
                    "Enter data for 10 minutes",
                    "App crashes (various causes)",
                    "Restart app"
                ],
                expected_behavior="Should recover unsaved work",
                actual_behavior="All work is lost",
                environment={"os": "Linux Ubuntu 22.04"}
            ),
            Bug(
                bug_id="BUG-005",
                title="Slow app startup time",
                description="App takes 8-12 seconds to start",
                priority=BugPriority.HIGH,
                category=BugCategory.PERFORMANCE,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_5",
                steps_to_reproduce=[
                    "Close app completely",
                    "Launch app",
                    "Measure time to usable state"
                ],
                expected_behavior="Should start in <3 seconds",
                actual_behavior="Takes 8-12 seconds",
                environment={"os": "Windows 11", "ssd": "Yes"}
            ),
            Bug(
                bug_id="BUG-006",
                title="German number formatting inconsistencies",
                description="Some fields show 1,234.56 instead of 1.234,56",
                priority=BugPriority.HIGH,
                category=BugCategory.UI_UX,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_6",
                steps_to_reproduce=[
                    "Navigate to price calculator",
                    "Check number formats in results",
                    "Some show wrong format"
                ],
                expected_behavior="All numbers should use German format",
                actual_behavior="Mixed formats throughout app",
                environment={"os": "macOS 13", "locale": "de-DE"}
            ),
            Bug(
                bug_id="BUG-007",
                title="3D export failures for complex roofs",
                description="STL/OBJ export fails for roofs with multiple sections",
                priority=BugPriority.HIGH,
                category=BugCategory.INTEGRATION,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_7",
                steps_to_reproduce=[
                    "Create roof with 4+ sections",
                    "Place modules",
                    "Export to STL"
                ],
                expected_behavior="Should export successfully",
                actual_behavior="Export fails with error",
                environment={"os": "Windows 10"}
            ),
            Bug(
                bug_id="BUG-008",
                title="Slow product search",
                description="Search takes 3-5 seconds with large product catalog",
                priority=BugPriority.HIGH,
                category=BugCategory.PERFORMANCE,
                status=BugStatus.CONFIRMED,
                reporter="beta_tester_8",
                steps_to_reproduce=[
                    "Go to product catalog",
                    "Type search query",
                    "Wait for results"
                ],
                expected_behavior="Results in <500ms",
                actual_behavior="Takes 3-5 seconds",
                environment={"os": "Linux", "products": "5000+"}
            )
        ]
        
        for bug in beta_bugs:
            self.bugs[bug.bug_id] = bug
        
        logger.info(f"Loaded {len(beta_bugs)} beta bugs")
    
    def get_bug(self, bug_id: str) -> Optional[Bug]:
        """Get bug by ID"""
        return self.bugs.get(bug_id)
    
    def get_all_bugs(self) -> List[Bug]:
        """Get all bugs"""
        return list(self.bugs.values())
    
    def get_bugs_by_priority(self, priority: BugPriority) -> List[Bug]:
        """Get bugs by priority"""
        return [bug for bug in self.bugs.values() if bug.priority == priority]
    
    def get_bugs_by_status(self, status: BugStatus) -> List[Bug]:
        """Get bugs by status"""
        return [bug for bug in self.bugs.values() if bug.status == status]
    
    def get_bugs_by_category(self, category: BugCategory) -> List[Bug]:
        """Get bugs by category"""
        return [bug for bug in self.bugs.values() if bug.category == category]
    
    def update_bug_status(
        self,
        bug_id: str,
        status: BugStatus,
        fix_description: Optional[str] = None,
        fix_commit: Optional[str] = None
    ) -> Optional[Bug]:
        """Update bug status"""
        bug = self.bugs.get(bug_id)
        if not bug:
            return None
        
        bug.status = status
        bug.updated_at = datetime.now()
        
        if status == BugStatus.FIXED:
            bug.fixed_at = datetime.now()
            if fix_description:
                bug.fix_description = fix_description
            if fix_commit:
                bug.fix_commit = fix_commit
        
        if status == BugStatus.VERIFIED:
            bug.verified_at = datetime.now()
        
        logger.info(f"Updated bug {bug_id} status to {status.value}")
        return bug
    
    def assign_bug(self, bug_id: str, assignee: str) -> Optional[Bug]:
        """Assign bug to developer"""
        bug = self.bugs.get(bug_id)
        if not bug:
            return None
        
        bug.assignee = assignee
        bug.updated_at = datetime.now()
        
        logger.info(f"Assigned bug {bug_id} to {assignee}")
        return bug
    
    def get_bug_statistics(self) -> Dict[str, Any]:
        """Get bug statistics"""
        total = len(self.bugs)
        by_priority = {
            priority.value: len(self.get_bugs_by_priority(priority))
            for priority in BugPriority
        }
        by_status = {
            status.value: len(self.get_bugs_by_status(status))
            for status in BugStatus
        }
        by_category = {
            category.value: len(self.get_bugs_by_category(category))
            for category in BugCategory
        }
        
        return {
            "total": total,
            "by_priority": by_priority,
            "by_status": by_status,
            "by_category": by_category,
            "critical_open": len([
                b for b in self.bugs.values()
                if b.priority == BugPriority.CRITICAL and b.status not in [BugStatus.FIXED, BugStatus.VERIFIED, BugStatus.CLOSED]
            ]),
            "high_open": len([
                b for b in self.bugs.values()
                if b.priority == BugPriority.HIGH and b.status not in [BugStatus.FIXED, BugStatus.VERIFIED, BugStatus.CLOSED]
            ])
        }
    
    def export_bugs(self, filepath: str):
        """Export bugs to JSON file"""
        bugs_data = [bug.to_dict() for bug in self.bugs.values()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(bugs_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported {len(bugs_data)} bugs to {filepath}")


# Global instance
bug_tracker = BugTrackerService()
