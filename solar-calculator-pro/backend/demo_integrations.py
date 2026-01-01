"""
Third-Party Integrations Demo

Demonstrates how to use all third-party service integrations.

Requirements: 6.1
"""

import asyncio
from services.third_party_integration_service import ThirdPartyIntegrationService
from datetime import datetime, timedelta


async def demo_weather_integration(service: ThirdPartyIntegrationService):
    """Demo weather API integration"""
    print("\n=== Weather API Integration Demo ===\n")
    
    # Berlin coordinates
    lat, lon = 52.52, 13.405
    
    # Get current weather
    print("1. Getting current weather for Berlin...")
    weather = await service.weather.get_current_weather(lat, lon)
    if weather:
        print(f"   Temperature: {weather['temperature']}°C")
        print(f"   Cloud Cover: {weather['cloud_cover']}%")
        print(f"   Humidity: {weather['humidity']}%")
        print(f"   Wind Speed: {weather['wind_speed']} m/s")
    
    # Get forecast
    print("\n2. Getting 7-day forecast...")
    forecast = await service.weather.get_forecast(lat, lon, days=7)
    if forecast:
        print(f"   Forecast for {len(forecast)} days:")
        for day in forecast[:3]:  # Show first 3 days
            print(f"   - {day['date']}: {day['temperature_max']}°C / {day['temperature_min']}°C")
    
    # Get historical data
    print("\n3. Getting historical weather data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    historical = await service.weather.get_historical_data(lat, lon, start_date, end_date)
    if historical is not None:
        print(f"   Retrieved {len(historical)} historical data points")


async def demo_mapping_integration(service: ThirdPartyIntegrationService):
    """Demo mapping API integration"""
    print("\n=== Mapping API Integration Demo ===\n")
    
    # Geocode address
    print("1. Geocoding address...")
    location = await service.mapping.geocode("Berlin, Germany")
    if location:
        print(f"   Address: {location['formatted_address']}")
        print(f"   Coordinates: {location['lat']}, {location['lon']}")
        print(f"   City: {location['city']}")
        print(f"   Country: {location['country']}")
    
    # Reverse geocode
    print("\n2. Reverse geocoding coordinates...")
    address = await service.mapping.reverse_geocode(52.52, 13.405)
    if address:
        print(f"   Address: {address['formatted_address']}")
        print(f"   Postal Code: {address['postal_code']}")
    
    # Calculate distance
    print("\n3. Calculating distance...")
    distance = await service.mapping.get_distance(
        origin={'lat': 52.52, 'lon': 13.405},  # Berlin
        destination={'lat': 48.137, 'lon': 11.576}  # Munich
    )
    if distance:
        print(f"   Distance: {distance['distance_km']} km")
        print(f"   Duration: {distance['duration_minutes']} minutes")


async def demo_payment_integration(service: ThirdPartyIntegrationService):
    """Demo payment gateway integration"""
    print("\n=== Payment Gateway Integration Demo ===\n")
    
    # Create payment intent
    print("1. Creating payment intent...")
    intent = await service.payment.create_payment_intent(
        amount=16999.00,
        currency='EUR',
        metadata={'project_id': 'proj_123', 'customer_id': 'cust_456'}
    )
    if intent:
        print(f"   Payment Intent ID: {intent['id']}")
        print(f"   Amount: {intent['amount']} {intent['currency']}")
        print(f"   Status: {intent['status']}")
        print(f"   Client Secret: {intent['client_secret'][:20]}...")
        
        # Confirm payment
        print("\n2. Confirming payment...")
        confirmation = await service.payment.confirm_payment(intent['id'])
        if confirmation:
            print(f"   Payment Status: {confirmation['status']}")
            print(f"   Amount Received: {confirmation['amount_received']} {confirmation['currency']}")
        
        # Refund payment
        print("\n3. Processing refund...")
        refund = await service.payment.refund_payment(intent['id'], amount=5000.00)
        if refund:
            print(f"   Refund ID: {refund['id']}")
            print(f"   Refund Amount: {refund['amount']}")
            print(f"   Refund Status: {refund['status']}")


async def demo_email_integration(service: ThirdPartyIntegrationService):
    """Demo email service integration"""
    print("\n=== Email Service Integration Demo ===\n")
    
    # Send email
    print("1. Sending email...")
    result = await service.email.send_email(
        to_email='customer@example.com',
        subject='Your Solar Quote',
        html_content='<h1>Solar Quote</h1><p>Your quote is ready!</p>',
        text_content='Solar Quote\n\nYour quote is ready!'
    )
    if result:
        print(f"   Message ID: {result['message_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Sent to: {result['to']}")
        print(f"   Timestamp: {result['timestamp']}")
    
    # Send template email
    print("\n2. Sending template email...")
    template_result = await service.email.send_template_email(
        to_email='customer@example.com',
        template_id='quote_template',
        template_data={
            'customer_name': 'John Doe',
            'quote_amount': '16.999,00 €',
            'system_size': '10 kWp',
            'annual_production': '12.500 kWh'
        }
    )
    if template_result:
        print(f"   Message ID: {template_result['message_id']}")
        print(f"   Template ID: {template_result['template_id']}")
        print(f"   Status: {template_result['status']}")


async def demo_cloud_storage_integration(service: ThirdPartyIntegrationService):
    """Demo cloud storage integration"""
    print("\n=== Cloud Storage Integration Demo ===\n")
    
    # Upload file
    print("1. Uploading file...")
    file_data = b"Sample PDF content for testing"
    upload_result = await service.cloud_storage.upload_file(
        file_path='projects/proj_123/quote.pdf',
        file_data=file_data,
        content_type='application/pdf',
        metadata={'project_id': 'proj_123', 'uploaded_by': 'user_456'}
    )
    if upload_result:
        print(f"   File Path: {upload_result['file_path']}")
        print(f"   URL: {upload_result['url']}")
        print(f"   Size: {upload_result['size']} bytes")
        print(f"   Uploaded: {upload_result['uploaded_at']}")
    
    # List files
    print("\n2. Listing files...")
    files = await service.cloud_storage.list_files(prefix='projects/proj_123/')
    if files is not None:
        print(f"   Found {len(files)} files")
    
    # Download file
    print("\n3. Downloading file...")
    downloaded = await service.cloud_storage.download_file('projects/proj_123/quote.pdf')
    if downloaded is not None:
        print(f"   Downloaded {len(downloaded)} bytes")
    
    # Delete file
    print("\n4. Deleting file...")
    deleted = await service.cloud_storage.delete_file('projects/proj_123/quote.pdf')
    print(f"   Deletion successful: {deleted}")


async def demo_analytics_integration(service: ThirdPartyIntegrationService):
    """Demo analytics integration"""
    print("\n=== Analytics Integration Demo ===\n")
    
    # Track event
    print("1. Tracking event...")
    event_result = await service.analytics.track_event(
        category='Solar Calculator',
        action='Calculate',
        label='10kWp System',
        value=16999,
        user_id='user_123'
    )
    print(f"   Event tracked: {event_result}")
    
    # Track page view
    print("\n2. Tracking page view...")
    pageview_result = await service.analytics.track_page_view(
        page_path='/solar-calculator',
        page_title='Solar Calculator',
        user_id='user_123'
    )
    print(f"   Page view tracked: {pageview_result}")
    
    # Track user
    print("\n3. Tracking user properties...")
    user_result = await service.analytics.track_user(
        user_id='user_123',
        properties={
            'plan': 'premium',
            'signup_date': '2024-01-01',
            'projects_count': 5,
            'total_revenue': 84995.00
        }
    )
    print(f"   User tracked: {user_result}")


async def demo_integration_status(service: ThirdPartyIntegrationService):
    """Demo integration status and health checks"""
    print("\n=== Integration Status & Health Checks ===\n")
    
    # Get all status
    print("1. Getting status of all integrations...")
    status = await service.get_all_status()
    for integration, info in status.items():
        print(f"\n   {integration.upper()}:")
        print(f"   - Provider: {info['provider']}")
        print(f"   - Enabled: {info['enabled']}")
        print(f"   - Connected: {info['connected']}")
        print(f"   - Last Check: {info['last_check']}")
    
    # Test all connections
    print("\n2. Testing all integration connections...")
    test_results = await service.test_all_connections()
    print("\n   Connection Test Results:")
    for integration, success in test_results.items():
        status_ if success else ""
        print(f"   {status_icon} {integration}: {'Connected' if success else 'Failed'}")


async def main():
    """Main demo function"""
    print("=" * 60)
    print("Third-Party Integrations Demo")
    print("=" * 60)
    
    # Initialize service with configuration
    config = {
        'weather': {
            'enabled': True,
            'provider': 'openweathermap',
            'api_key': 'demo_key'
        },
        'mapping': {
            'enabled': True,
            'provider': 'google_maps',
            'api_key': 'demo_key'
        },
        'payment': {
            'enabled': True,
            'provider': 'stripe',
            'secret_key': 'sk_test_demo',
            'publishable_key': 'pk_test_demo'
        },
        'email': {
            'enabled': True,
            'provider': 'sendgrid',
            'api_key': 'demo_key',
            'from_email': 'noreply@example.com',
            'from_name': 'Solar Calculator Pro'
        },
        'cloud_storage': {
            'enabled': True,
            'provider': 's3',
            'bucket': 'solar-calculator-demo',
            'region': 'eu-central-1'
        },
        'analytics': {
            'enabled': True,
            'provider': 'google_analytics',
            'tracking_id': 'UA-DEMO-1'
        }
    }
    
    service = ThirdPartyIntegrationService(config)
    
    # Run all demos
    await demo_integration_status(service)
    await demo_weather_integration(service)
    await demo_mapping_integration(service)
    await demo_payment_integration(service)
    await demo_email_integration(service)
    await demo_cloud_storage_integration(service)
    await demo_analytics_integration(service)
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nFor more information, see:")
    print("- docs/THIRD_PARTY_INTEGRATIONS_GUIDE.md")
    print("- docs/INTEGRATIONS_QUICK_REFERENCE.md")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
