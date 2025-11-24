"""
Lead Management System Demo
Demonstrates all features of the lead management system
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"


class LeadManagementDemo:
    """Demo class for lead management system"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def print_section(self, title: str):
        """Print section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_result(self, title: str, data: Any):
        """Print result"""
        print(f"\n{title}:")
        print(json.dumps(data, indent=2, default=str))
    
    # 1. Lead Capture
    
    def demo_lead_capture(self):
        """Demonstrate lead capture from various sources"""
        self.print_section("1. LEAD CAPTURE")
        
        # Website lead
        website_lead = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max.mustermann@example.com",
            "phone": "+49 30 12345678",
            "company": "Solar Solutions GmbH",
            "job_title": "Facility Manager",
            "city": "Berlin",
            "postal_code": "10115",
            "country": "Germany",
            "source": "website",
            "priority": "high",
            "estimated_value": 75000.00,
            "interested_in": ["solar", "battery"],
            "notes": "Interested in 50kW solar system with battery storage"
        }
        
        response = self.session.post(f"{self.base_url}/leads/", json=website_lead)
        lead1 = response.json()
        self.print_result("Website Lead Created", lead1)
        
        # Referral lead
        referral_lead = {
            "first_name": "Anna",
            "last_name": "Schmidt",
            "email": "anna.schmidt@example.com",
            "phone": "+49 89 98765432",
            "company": "Green Energy AG",
            "source": "referral",
            "priority": "medium",
            "estimated_value": 45000.00,
            "interested_in": ["solar"],
            "notes": "Referred by existing customer"
        }
        
        response = self.session.post(f"{self.base_url}/leads/", json=referral_lead)
        lead2 = response.json()
        self.print_result("Referral Lead Created", lead2)
        
        return lead1["id"], lead2["id"]
    
    # 2. Lead Scoring
    
    def demo_lead_scoring(self, lead_id: int):
        """Demonstrate lead scoring system"""
        self.print_section("2. LEAD SCORING")
        
        # Create scoring rules
        rules = [
            {
                "name": "High Value Lead",
                "description": "Leads with estimated value over 50k",
                "category": "demographic",
                "field": "estimated_value",
                "operator": "greater_than",
                "value": "50000",
                "points": 25,
                "active": True,
                "priority": 10
            },
            {
                "name": "Enterprise Company",
                "description": "Company name contains GmbH or AG",
                "category": "demographic",
                "field": "company",
                "operator": "contains",
                "value": "GmbH",
                "points": 15,
                "active": True,
                "priority": 8
            },
            {
                "name": "High Priority",
                "description": "High or urgent priority leads",
                "category": "engagement",
                "field": "priority",
                "operator": "equals",
                "value": "high",
                "points": 10,
                "active": True,
                "priority": 5
            }
        ]
        
        for rule in rules:
            response = self.session.post(f"{self.base_url}/leads/scoring-rules", json=rule)
            self.print_result(f"Scoring Rule Created: {rule['name']}", response.json())
        
        # Get score breakdown
        response = self.session.get(f"{self.base_url}/leads/{lead_id}/score")
        self.print_result("Lead Score Breakdown", response.json())
        
        # Recalculate all scores
        response = self.session.post(f"{self.base_url}/leads/recalculate-scores")
        self.print_result("Recalculate Scores", response.json())
    
    # 3. Lead Assignment
    
    def demo_lead_assignment(self, lead_id: int):
        """Demonstrate lead assignment"""
        self.print_section("3. LEAD ASSIGNMENT")
        
        # Create assignment rules
        assignment_rule = {
            "name": "High Value to Senior Rep",
            "description": "Assign high-value leads to senior sales rep",
            "conditions": {
                "priority": "high",
                "estimated_value": ">50000"
            },
            "assign_to_user_id": 5,
            "assignment_method": "direct",
            "active": True,
            "priority": 10
        }
        
        response = self.session.post(f"{self.base_url}/leads/assignment-rules", json=assignment_rule)
        self.print_result("Assignment Rule Created", response.json())
        
        # Manual assignment
        assignment = {
            "lead_id": lead_id,
            "assign_to_user_id": 5
        }
        
        response = self.session.post(f"{self.base_url}/leads/{lead_id}/assign", json=assignment)
        self.print_result("Lead Assigned", response.json())
    
    # 4. Lead Activities
    
    def demo_lead_activities(self, lead_id: int):
        """Demonstrate lead activity tracking"""
        self.print_section("4. LEAD ACTIVITIES")
        
        # Create activities
        activities = [
            {
                "activity_type": "call",
                "subject": "Initial consultation call",
                "description": "Discussed solar requirements and site assessment",
                "outcome": "interested",
                "duration_minutes": 30
            },
            {
                "activity_type": "email",
                "subject": "Sent product information",
                "description": "Sent brochures and case studies",
                "outcome": "opened"
            },
            {
                "activity_type": "meeting",
                "subject": "Site visit scheduled",
                "description": "Scheduled on-site assessment for next week",
                "scheduled_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
        ]
        
        for activity in activities:
            response = self.session.post(f"{self.base_url}/leads/{lead_id}/activities", json=activity)
            self.print_result(f"Activity Created: {activity['activity_type']}", response.json())
        
        # Get all activities
        response = self.session.get(f"{self.base_url}/leads/{lead_id}/activities")
        self.print_result("All Lead Activities", response.json())
    
    # 5. Lead Nurturing
    
    def demo_lead_nurturing(self, lead_id: int):
        """Demonstrate lead nurturing campaigns"""
        self.print_section("5. LEAD NURTURING")
        
        # Create nurturing campaign
        campaign = {
            "campaign_name": "Solar Education Series",
            "campaign_type": "educational",
            "total_steps": 5
        }
        
        response = self.session.post(f"{self.base_url}/leads/{lead_id}/nurturing", json=campaign)
        self.print_result("Nurturing Campaign Created", response.json())
        
        # Get active campaigns
        response = self.session.get(f"{self.base_url}/leads/nurturing/active")
        self.print_result("Active Nurturing Campaigns", response.json())
    
    # 6. Lead Updates
    
    def demo_lead_updates(self, lead_id: int):
        """Demonstrate lead updates"""
        self.print_section("6. LEAD UPDATES")
        
        # Update lead status
        update = {
            "status": "qualified",
            "priority": "urgent",
            "next_follow_up_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "notes": "Qualified lead - ready for proposal"
        }
        
        response = self.session.put(f"{self.base_url}/leads/{lead_id}", json=update)
        self.print_result("Lead Updated", response.json())
    
    # 7. Lead Conversion
    
    def demo_lead_conversion(self, lead_id: int):
        """Demonstrate lead conversion"""
        self.print_section("7. LEAD CONVERSION")
        
        # Convert lead to customer
        customer_id = 100  # Assume customer was created
        response = self.session.post(f"{self.base_url}/leads/{lead_id}/convert?customer_id={customer_id}")
        self.print_result("Lead Converted", response.json())
    
    # 8. Lead Filtering
    
    def demo_lead_filtering(self):
        """Demonstrate lead filtering"""
        self.print_section("8. LEAD FILTERING")
        
        # Filter by status
        response = self.session.get(f"{self.base_url}/leads/?status=qualified&limit=10")
        self.print_result("Qualified Leads", response.json())
        
        # Filter by score
        response = self.session.get(f"{self.base_url}/leads/?min_score=50&limit=10")
        self.print_result("High Score Leads (50+)", response.json())
        
        # Search leads
        response = self.session.get(f"{self.base_url}/leads/?search=Solar&limit=10")
        self.print_result("Search Results for 'Solar'", response.json())
        
        # Combined filters
        response = self.session.get(
            f"{self.base_url}/leads/?status=qualified&source=website&min_score=40&limit=10"
        )
        self.print_result("Combined Filters", response.json())
    
    # 9. Analytics
    
    def demo_analytics(self):
        """Demonstrate analytics and reporting"""
        self.print_section("9. ANALYTICS & REPORTING")
        
        # Dashboard metrics
        response = self.session.get(f"{self.base_url}/leads/analytics/dashboard")
        self.print_result("Dashboard Metrics", response.json())
        
        # Conversion tracking
        start_date = (datetime.now() - timedelta(days=90)).isoformat()
        end_date = datetime.now().isoformat()
        
        response = self.session.get(
            f"{self.base_url}/leads/conversion/tracking?start_date={start_date}&end_date={end_date}"
        )
        self.print_result("Conversion Tracking (Last 90 Days)", response.json())
        
        # Source analytics
        response = self.session.get(
            f"{self.base_url}/leads/analytics/sources?start_date={start_date}&end_date={end_date}"
        )
        self.print_result("Source Analytics", response.json())
    
    # 10. Bulk Operations
    
    def demo_bulk_operations(self):
        """Demonstrate bulk operations"""
        self.print_section("10. BULK OPERATIONS")
        
        # Get all leads
        response = self.session.get(f"{self.base_url}/leads/?limit=100")
        leads_data = response.json()
        self.print_result(f"Total Leads: {leads_data['total']}", {
            "total": leads_data["total"],
            "page": leads_data["page"],
            "total_pages": leads_data["total_pages"]
        })
        
        # Get scoring rules
        response = self.session.get(f"{self.base_url}/leads/scoring-rules")
        self.print_result("All Scoring Rules", response.json())
        
        # Get assignment rules
        response = self.session.get(f"{self.base_url}/leads/assignment-rules")
        self.print_result("All Assignment Rules", response.json())
    
    def run_full_demo(self):
        """Run complete demo"""
        print("\n" + "=" * 80)
        print("  LEAD MANAGEMENT SYSTEM - COMPLETE DEMO")
        print("=" * 80)
        
        try:
            # 1. Lead Capture
            lead1_id, lead2_id = self.demo_lead_capture()
            
            # 2. Lead Scoring
            self.demo_lead_scoring(lead1_id)
            
            # 3. Lead Assignment
            self.demo_lead_assignment(lead1_id)
            
            # 4. Lead Activities
            self.demo_lead_activities(lead1_id)
            
            # 5. Lead Nurturing
            self.demo_lead_nurturing(lead2_id)
            
            # 6. Lead Updates
            self.demo_lead_updates(lead1_id)
            
            # 7. Lead Filtering
            self.demo_lead_filtering()
            
            # 8. Analytics
            self.demo_analytics()
            
            # 9. Bulk Operations
            self.demo_bulk_operations()
            
            # 10. Lead Conversion (optional - comment out if not ready)
            # self.demo_lead_conversion(lead1_id)
            
            print("\n" + "=" * 80)
            print("  DEMO COMPLETED SUCCESSFULLY!")
            print("=" * 80 + "\n")
            
        except Exception as e:
            print(f"\nError during demo: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main function"""
    demo = LeadManagementDemo()
    
    print("\nLead Management System Demo")
    print("=" * 80)
    print("\nThis demo will showcase all features of the lead management system:")
    print("1. Lead Capture")
    print("2. Lead Scoring")
    print("3. Lead Assignment")
    print("4. Lead Activities")
    print("5. Lead Nurturing")
    print("6. Lead Updates")
    print("7. Lead Filtering")
    print("8. Analytics")
    print("9. Bulk Operations")
    print("\nMake sure the backend server is running on http://localhost:8000")
    
    input("\nPress Enter to start the demo...")
    
    demo.run_full_demo()


if __name__ == "__main__":
    main()
