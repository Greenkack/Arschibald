"""
CRM Advanced Service Demo

This script demonstrates the usage of the CRM Advanced Service.

Requirements: 1.3, 6.1
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from services.crm_advanced_service import CRMAdvancedService


def demo_lead_scoring():
    """Demonstrate lead scoring functionality."""
    print("\n" + "="*60)
    print("LEAD SCORING DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Calculate lead score
        print("\n1. Calculating lead score...")
        score_result = crm_service.calculate_lead_score(lead_id=1)
        print(f"   Lead Score: {score_result}")
        
        # Get all lead scores
        print("\n2. Getting all lead scores...")
        scores = crm_service.get_lead_scores(filters={'min_score': 50})
        print(f"   Found {len(scores) if isinstance(scores, list) else 0} leads")
        
        # Update scoring weights
        print("\n3. Updating scoring weights...")
        weights = {
            'engagement': 0.3,
            'demographics': 0.2,
            'behavior': 0.5
        }
        result = crm_service.update_lead_score_weights(weights)
        print(f"   Weights updated: {result}")
        
    except Exception as e:
        print(f"   Note: {e}")
        print("   (This is expected if legacy modules are not available)")


def demo_pipeline_automation():
    """Demonstrate pipeline automation."""
    print("\n" + "="*60)
    print("PIPELINE AUTOMATION DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        print("\n1. Automating pipeline stage...")
        rules = {
            'qualification_threshold': 70,
            'assignment_threshold': 80
        }
        result = crm_service.automate_pipeline_stage(lead_id=1, rules=rules)
        print(f"   Automation result: {result}")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_email_campaigns():
    """Demonstrate email campaign management."""
    print("\n" + "="*60)
    print("EMAIL CAMPAIGN DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Create campaign
        print("\n1. Creating email campaign...")
        campaign_data = {
            'name': 'Summer Promotion 2024',
            'subject': 'Special Solar Panel Offer!',
            'content': '<html><body><h1>Save 20% on Solar Panels!</h1></body></html>',
            'segment_id': 1
        }
        campaign_id = crm_service.create_email_campaign(campaign_data)
        print(f"   Campaign created with ID: {campaign_id}")
        
        # Send campaign
        print("\n2. Sending campaign...")
        send_result = crm_service.send_campaign_email(
            campaign_id=campaign_id,
            recipient_ids=[1, 2, 3, 4, 5]
        )
        print(f"   Campaign sent: {send_result}")
        
        # Get analytics
        print("\n3. Getting campaign analytics...")
        analytics = crm_service.get_campaign_analytics(campaign_id)
        print(f"   Analytics: {analytics}")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_customer_segmentation():
    """Demonstrate customer segmentation."""
    print("\n" + "="*60)
    print("CUSTOMER SEGMENTATION DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Create segment
        print("\n1. Creating customer segment...")
        segment_data = {
            'name': 'High Value Customers',
            'criteria': {
                'lifetime_value': {'min': 10000},
                'engagement_score': {'min': 70}
            },
            'description': 'Customers with high lifetime value and engagement'
        }
        segment_id = crm_service.create_customer_segment(segment_data)
        print(f"   Segment created with ID: {segment_id}")
        
        # Get segment customers
        print("\n2. Getting segment customers...")
        customers = crm_service.get_segment_customers(segment_id)
        print(f"   Found {len(customers) if isinstance(customers, list) else 0} customers")
        
        # Analyze segment
        print("\n3. Analyzing segment...")
        analysis = crm_service.analyze_segment(segment_id)
        print(f"   Analysis: {analysis}")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_forecasting():
    """Demonstrate sales forecasting."""
    print("\n" + "="*60)
    print("SALES FORECASTING DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Generate sales forecast
        print("\n1. Generating quarterly sales forecast...")
        forecast = crm_service.generate_sales_forecast(
            period='quarter',
            parameters={'confidence_level': 0.95}
        )
        print(f"   Forecast: {forecast}")
        
        # Get pipeline forecast
        print("\n2. Getting pipeline forecast...")
        pipeline_forecast = crm_service.get_pipeline_forecast()
        print(f"   Pipeline forecast: {pipeline_forecast}")
        
        # Analyze accuracy
        print("\n3. Analyzing forecast accuracy...")
        accuracy = crm_service.analyze_forecast_accuracy('month')
        print(f"   Accuracy: {accuracy}")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_contract_management():
    """Demonstrate contract management."""
    print("\n" + "="*60)
    print("CONTRACT MANAGEMENT DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Create contract
        print("\n1. Creating contract...")
        contract_data = {
            'customer_id': 123,
            'contract_type': 'service',
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=365),
            'value': 50000.0,
            'terms': {
                'payment_schedule': 'monthly',
                'auto_renewal': True
            }
        }
        contract_id = crm_service.create_contract(contract_data)
        print(f"   Contract created with ID: {contract_id}")
        
        # Get contract
        print("\n2. Getting contract details...")
        contract = crm_service.get_contract(contract_id)
        print(f"   Contract: {contract}")
        
        # Get expiring contracts
        print("\n3. Getting expiring contracts...")
        expiring = crm_service.get_expiring_contracts(days=30)
        print(f"   Found {len(expiring) if isinstance(expiring, list) else 0} expiring contracts")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_warranty_tracking():
    """Demonstrate warranty tracking."""
    print("\n" + "="*60)
    print("WARRANTY TRACKING DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Register warranty
        print("\n1. Registering warranty...")
        warranty_data = {
            'product_id': 456,
            'customer_id': 123,
            'purchase_date': datetime.now(),
            'warranty_period_months': 24,
            'terms': {
                'coverage': 'full',
                'transferable': False
            }
        }
        warranty_id = crm_service.register_warranty(warranty_data)
        print(f"   Warranty registered with ID: {warranty_id}")
        
        # Get warranty status
        print("\n2. Getting warranty status...")
        status = crm_service.get_warranty_status(warranty_id)
        print(f"   Status: {status}")
        
        # Get active warranties
        print("\n3. Getting active warranties...")
        active = crm_service.get_active_warranties(customer_id=123)
        print(f"   Found {len(active) if isinstance(active, list) else 0} active warranties")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_customer_feedback():
    """Demonstrate customer feedback system."""
    print("\n" + "="*60)
    print("CUSTOMER FEEDBACK DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Submit feedback
        print("\n1. Submitting customer feedback...")
        feedback_data = {
            'customer_id': 123,
            'rating': 5,
            'category': 'service',
            'comment': 'Excellent service and professional installation!',
            'metadata': {
                'installation_date': datetime.now().isoformat(),
                'technician_id': 42
            }
        }
        feedback_id = crm_service.submit_feedback(feedback_data)
        print(f"   Feedback submitted with ID: {feedback_id}")
        
        # Get feedback
        print("\n2. Getting feedback details...")
        feedback = crm_service.get_feedback(feedback_id)
        print(f"   Feedback: {feedback}")
        
        # Analyze feedback
        print("\n3. Analyzing feedback...")
        analysis = crm_service.analyze_feedback(filters={'category': 'service'})
        print(f"   Analysis: {analysis}")
        
        # Get trends
        print("\n4. Getting feedback trends...")
        trends = crm_service.get_feedback_trends('month')
        print(f"   Trends: {trends}")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_geo_mapping():
    """Demonstrate geo mapping functionality."""
    print("\n" + "="*60)
    print("GEO MAPPING DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Geocode address
        print("\n1. Geocoding address...")
        location = crm_service.geocode_address("Hauptstraße 123, 10115 Berlin, Germany")
        print(f"   Location: {location}")
        
        # Get customers in area
        print("\n2. Getting customers in area...")
        center = {'lat': 52.5200, 'lon': 13.4050}  # Berlin
        customers = crm_service.get_customers_in_area(center, radius_km=10.0)
        print(f"   Found {len(customers) if isinstance(customers, list) else 0} customers within 10km")
        
        # Optimize route
        print("\n3. Optimizing route...")
        locations = [
            {'lat': 52.5200, 'lon': 13.4050},
            {'lat': 52.5300, 'lon': 13.4150},
            {'lat': 52.5100, 'lon': 13.3950}
        ]
        route = crm_service.optimize_route(locations)
        print(f"   Optimized route: {route}")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_knowledge_base():
    """Demonstrate knowledge base functionality."""
    print("\n" + "="*60)
    print("KNOWLEDGE BASE DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    try:
        # Create article
        print("\n1. Creating KB article...")
        article_data = {
            'title': 'How to Install Solar Panels',
            'content': 'Step-by-step guide for solar panel installation...',
            'category': 'installation',
            'tags': ['solar', 'installation', 'guide', 'diy'],
            'author_id': 1
        }
        article_id = crm_service.create_kb_article(article_data)
        print(f"   Article created with ID: {article_id}")
        
        # Search KB
        print("\n2. Searching knowledge base...")
        results = crm_service.search_kb('solar panel installation')
        print(f"   Found {len(results) if isinstance(results, list) else 0} articles")
        
        # Get article
        print("\n3. Getting article details...")
        article = crm_service.get_kb_article(article_id)
        print(f"   Article: {article}")
        
        # Get popular articles
        print("\n4. Getting popular articles...")
        popular = crm_service.get_popular_kb_articles(limit=10)
        print(f"   Found {len(popular) if isinstance(popular, list) else 0} popular articles")
        
    except Exception as e:
        print(f"   Note: {e}")


def demo_health_check():
    """Demonstrate health check functionality."""
    print("\n" + "="*60)
    print("HEALTH CHECK DEMO")
    print("="*60)
    
    crm_service = CRMAdvancedService()
    
    print("\nChecking health of all CRM modules...")
    health = crm_service.health_check()
    
    print(f"\nOverall Status: {health['overall']}")
    print("\nModule Status:")
    for module_name, status in health['modules'].items():
        print(f"  - {module_name}: {status}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("CRM ADVANCED SERVICE DEMO")
    print("="*60)
    print("\nThis demo showcases all features of the CRM Advanced Service.")
    print("Note: Some features may not work if legacy modules are not available.")
    
    # Run all demos
    demo_lead_scoring()
    demo_pipeline_automation()
    demo_email_campaigns()
    demo_customer_segmentation()
    demo_forecasting()
    demo_contract_management()
    demo_warranty_tracking()
    demo_customer_feedback()
    demo_geo_mapping()
    demo_knowledge_base()
    demo_health_check()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nFor more information, see:")
    print("  - docs/CRM_ADVANCED_SERVICE_GUIDE.md")
    print("  - docs/CRM_ADVANCED_QUICK_REFERENCE.md")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
