"""
Team Manager

Manager class for team CRUD operations in the Employee Controlling System.
Handles team creation, updates, deletions, and queries.

Requirements: Team-based organization and reporting
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from controlling.models import Team, Employee
from controlling.managers import ValidationError

logger = logging.getLogger(__name__)


class TeamManager:
    """
    Manager for team operations.
    
    Handles CRUD operations for teams and team-employee assignments.
    """
    
    def __init__(self, db: Session):
        """
        Initialize TeamManager with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_team(
        self,
        name: str,
        description: Optional[str] = None,
        team_leader_id: Optional[int] = None
    ) -> Team:
        """
        Create a new team.
        
        Args:
            name: Team name (unique)
            description: Optional team description
            team_leader_id: Optional employee ID for team leader
        
        Returns:
            Created Team object
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate name
        if not name or not name.strip():
            raise ValidationError("Team-Name darf nicht leer sein")
        
        name = name.strip()
        
        # Check for duplicate name
        existing = self.db.query(Team).filter(
            Team.name == name
        ).first()
        
        if existing:
            raise ValidationError(f"Team mit Namen '{name}' existiert bereits")
        
        # Validate team leader if provided
        if team_leader_id:
            leader = self.db.query(Employee).filter(
                Employee.id == team_leader_id,
                Employee.is_active == True
            ).first()
            
            if not leader:
                raise ValidationError(
                    f"Mitarbeiter mit ID {team_leader_id} nicht gefunden oder inaktiv"
                )
        
        # Create team
        team = Team(
            name=name,
            description=description.strip() if description else None,
            team_leader_id=team_leader_id,
            is_active=True
        )
        
        try:
            self.db.add(team)
            self.db.commit()
            self.db.refresh(team)
            logger.info(f"Team '{name}' created with ID {team.id}")
            return team
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create team '{name}': {e}")
            raise ValidationError(f"Team konnte nicht erstellt werden: {str(e)}")
    
    def get_team(self, team_id: int) -> Optional[Team]:
        """
        Get team by ID.
        
        Args:
            team_id: Team ID
        
        Returns:
            Team object or None if not found
        """
        return self.db.query(Team).filter(Team.id == team_id).first()
    
    def get_team_by_name(self, name: str) -> Optional[Team]:
        """
        Get team by name.
        
        Args:
            name: Team name
        
        Returns:
            Team object or None if not found
        """
        return self.db.query(Team).filter(Team.name == name).first()
    
    def list_teams(
        self,
        active_only: bool = True,
        include_employee_count: bool = False
    ) -> List[Team]:
        """
        List all teams.
        
        Args:
            active_only: Only include active teams
            include_employee_count: Add employee count to results
        
        Returns:
            List of Team objects
        """
        query = self.db.query(Team)
        
        if active_only:
            query = query.filter(Team.is_active == True)
        
        teams = query.order_by(Team.name).all()
        
        # Add employee count if requested
        if include_employee_count:
            for team in teams:
                team.employee_count = self.db.query(func.count(Employee.id)).filter(
                    Employee.team_id == team.id,
                    Employee.is_active == True
                ).scalar() or 0
        
        return teams
    
    def update_team(
        self,
        team_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        team_leader_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Team:
        """
        Update team information.
        
        Args:
            team_id: Team ID
            name: New team name
            description: New description
            team_leader_id: New team leader ID
            is_active: Active status
        
        Returns:
            Updated Team object
        
        Raises:
            ValidationError: If validation fails
        """
        team = self.get_team(team_id)
        
        if not team:
            raise ValidationError(f"Team mit ID {team_id} nicht gefunden")
        
        # Update name if provided
        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationError("Team-Name darf nicht leer sein")
            
            # Check for duplicate name (excluding current team)
            existing = self.db.query(Team).filter(
                Team.name == name,
                Team.id != team_id
            ).first()
            
            if existing:
                raise ValidationError(f"Team mit Namen '{name}' existiert bereits")
            
            team.name = name
        
        # Update description
        if description is not None:
            team.description = description.strip() if description else None
        
        # Update team leader
        if team_leader_id is not None:
            if team_leader_id > 0:
                leader = self.db.query(Employee).filter(
                    Employee.id == team_leader_id,
                    Employee.is_active == True
                ).first()
                
                if not leader:
                    raise ValidationError(
                        f"Mitarbeiter mit ID {team_leader_id} nicht gefunden oder inaktiv"
                    )
                
                team.team_leader_id = team_leader_id
            else:
                team.team_leader_id = None
        
        # Update active status
        if is_active is not None:
            team.is_active = is_active
        
        try:
            self.db.commit()
            self.db.refresh(team)
            logger.info(f"Team {team_id} updated")
            return team
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update team {team_id}: {e}")
            raise ValidationError(f"Team konnte nicht aktualisiert werden: {str(e)}")
    
    def delete_team(self, team_id: int, force: bool = False) -> bool:
        """
        Delete a team.
        
        Args:
            team_id: Team ID
            force: If True, removes team assignment from employees.
                   If False, fails if team has members.
        
        Returns:
            True if deleted successfully
        
        Raises:
            ValidationError: If team has members and force=False
        """
        team = self.get_team(team_id)
        
        if not team:
            raise ValidationError(f"Team mit ID {team_id} nicht gefunden")
        
        # Check for team members
        member_count = self.db.query(func.count(Employee.id)).filter(
            Employee.team_id == team_id,
            Employee.is_active == True
        ).scalar() or 0
        
        if member_count > 0 and not force:
            raise ValidationError(
                f"Team '{team.name}' hat {member_count} aktive Mitarbeiter. "
                "Mitarbeiter müssen erst einem anderen Team zugeordnet oder entfernt werden."
            )
        
        # Remove team assignment from employees if force=True
        if force and member_count > 0:
            self.db.query(Employee).filter(
                Employee.team_id == team_id
            ).update({"team_id": None})
        
        try:
            self.db.delete(team)
            self.db.commit()
            logger.info(f"Team {team_id} deleted")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete team {team_id}: {e}")
            raise ValidationError(f"Team konnte nicht gelöscht werden: {str(e)}")
    
    def assign_employee_to_team(
        self,
        employee_id: int,
        team_id: Optional[int]
    ) -> Employee:
        """
        Assign or remove employee from team.
        
        Args:
            employee_id: Employee ID
            team_id: Team ID or None to remove from team
        
        Returns:
            Updated Employee object
        
        Raises:
            ValidationError: If validation fails
        """
        from controlling.managers import EmployeeManager
        
        emp_manager = EmployeeManager(self.db)
        employee = emp_manager.get_employee(employee_id)
        
        if not employee:
            raise ValidationError(f"Mitarbeiter mit ID {employee_id} nicht gefunden")
        
        # Validate team if provided
        if team_id:
            team = self.get_team(team_id)
            if not team:
                raise ValidationError(f"Team mit ID {team_id} nicht gefunden")
            if not team.is_active:
                raise ValidationError(f"Team '{team.name}' ist inaktiv")
        
        # Update assignment
        employee.team_id = team_id
        
        try:
            self.db.commit()
            self.db.refresh(employee)
            logger.info(f"Employee {employee_id} assigned to team {team_id}")
            return employee
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to assign employee {employee_id} to team {team_id}: {e}")
            raise ValidationError(f"Zuordnung konnte nicht gespeichert werden: {str(e)}")
    
    def get_team_members(
        self,
        team_id: int,
        active_only: bool = True
    ) -> List[Employee]:
        """
        Get all members of a team.
        
        Args:
            team_id: Team ID
            active_only: Only include active employees
        
        Returns:
            List of Employee objects
        """
        query = self.db.query(Employee).filter(Employee.team_id == team_id)
        
        if active_only:
            query = query.filter(Employee.is_active == True)
        
        return query.order_by(
            Employee.last_name,
            Employee.first_name
        ).all()
    
    def get_team_statistics(self, team_id: int) -> Dict[str, Any]:
        """
        Get team statistics.
        
        Args:
            team_id: Team ID
        
        Returns:
            Dictionary with team statistics
        """
        team = self.get_team(team_id)
        
        if not team:
            raise ValidationError(f"Team mit ID {team_id} nicht gefunden")
        
        # Count active and inactive members
        active_count = self.db.query(func.count(Employee.id)).filter(
            Employee.team_id == team_id,
            Employee.is_active == True
        ).scalar() or 0
        
        inactive_count = self.db.query(func.count(Employee.id)).filter(
            Employee.team_id == team_id,
            Employee.is_active == False
        ).scalar() or 0
        
        # Get positions distribution
        from sqlalchemy import distinct
        position_query = self.db.query(
            Employee.position_id,
            func.count(Employee.id).label('count')
        ).filter(
            Employee.team_id == team_id,
            Employee.is_active == True
        ).group_by(Employee.position_id).all()
        
        positions = {}
        for pos_id, count in position_query:
            from controlling.models import Position
            position = self.db.query(Position).filter(Position.id == pos_id).first()
            if position:
                positions[position.name] = count
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "active_members": active_count,
            "inactive_members": inactive_count,
            "total_members": active_count + inactive_count,
            "positions": positions,
            "has_team_leader": team.team_leader_id is not None,
            "team_leader": team.team_leader.full_name if team.team_leader_id else None
        }
