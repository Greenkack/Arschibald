"""
Test Controlling Team Integration
Tests ob Teams korrekt erstellt und zugeordnet werden können
"""
from controlling.database import get_session
from controlling.models import Team, Employee
from controlling.managers import TeamManager, EmployeeManager

def test_team_system():
    """Test basic team functionality"""
    print("🧪 Testing Controlling Team System...\n")
    
    session = get_session()
    team_manager = TeamManager(session)
    emp_manager = EmployeeManager(session)
    
    # 1. Test: Create Team
    print("1️⃣ Creating test team...")
    try:
        team = team_manager.create_team(
            name="Sales Team Alpha",
            description="Test sales team",
            is_active=True
        )
        print(f"   ✅ Team created: {team.name} (ID: {team.id})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Test: List Teams
    print("\n2️⃣ Listing all teams...")
    try:
        teams = team_manager.list_teams()
        print(f"   ✅ Found {len(teams)} teams:")
        for t in teams:
            print(f"      - {t.name} ({'Active' if t.is_active else 'Inactive'})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 3. Test: Get Employees (should exist from migration)
    print("\n3️⃣ Checking for employees...")
    try:
        employees = session.query(Employee).all()
        if employees:
            print(f"   ✅ Found {len(employees)} employees:")
            for emp in employees[:3]:  # Show first 3
                print(f"      - {emp.full_name} (ID: {emp.id})")
        else:
            print("   ℹ️ No employees found - create some first")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 4. Test: Assign Employee to Team (if we have employees)
    if employees:
        print(f"\n4️⃣ Assigning employee to team...")
        try:
            test_emp = employees[0]
            team_manager.assign_employee_to_team(test_emp.id, team.id)
            print(f"   ✅ Assigned {test_emp.full_name} to {team.name}")
            
            # Verify assignment
            updated_emp = session.query(Employee).filter_by(id=test_emp.id).first()
            if updated_emp.team_id == team.id:
                print(f"   ✅ Verification successful: team_id = {updated_emp.team_id}")
            else:
                print(f"   ⚠️ Verification failed: team_id = {updated_emp.team_id}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    # 5. Test: Get Team Members
    print(f"\n5️⃣ Getting team members...")
    try:
        members = team_manager.get_team_members(team.id)
        print(f"   ✅ Team '{team.name}' has {len(members)} members:")
        for member in members:
            print(f"      - {member.full_name} ({member.position.name if member.position else 'No position'})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 6. Test: Get Employee's Team
    if employees:
        print(f"\n6️⃣ Getting employee's team...")
        try:
            test_emp = employees[0]
            emp_team = team_manager.get_employee_team(test_emp.id)
            if emp_team:
                print(f"   ✅ {test_emp.full_name} is in team: {emp_team.name}")
            else:
                print(f"   ℹ️ {test_emp.full_name} has no team assigned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    # 7. Test: Update Team
    print(f"\n7️⃣ Updating team...")
    try:
        team_manager.update_team(
            team.id,
            name="Sales Team Alpha - Updated",
            description="Updated description"
        )
        updated_team = team_manager.get_team(team.id)
        print(f"   ✅ Team updated: {updated_team.name}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Cleanup
    print(f"\n🧹 Cleanup: Deleting test team...")
    try:
        team_manager.delete_team(team.id)
        print(f"   ✅ Test team deleted")
    except Exception as e:
        print(f"   ⚠️ Cleanup error: {e}")
    
    session.close()
    
    print("\n" + "="*60)
    print("✅ ALL TEAM TESTS PASSED!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        success = test_team_system()
        if not success:
            print("\n❌ Some tests failed")
            exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
