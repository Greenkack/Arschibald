"""
Communication Service

Service for managing customer communications including email, SMS,
templates, scheduling, tracking, and analytics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging

from backend.models.communication_models import (
    Communication, CommunicationTemplate, CommunicationCampaign,
    CommunicationSchedule, CommunicationAnalytics,
    EmailConfiguration, SMSConfiguration,
    CommunicationType, CommunicationStatus, TemplateType
)
from backend.models.communication_schemas import (
    CommunicationCreate, CommunicationUpdate, CommunicationResponse,
    TemplateCreate, TemplateUpdate, TemplateResponse,
    CampaignCreate, CampaignUpdate, CampaignResponse,
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    EmailConfigCreate, EmailConfigUpdate,
    SMSConfigCreate, SMSConfigUpdate,
    BulkCommunicationCreate, CommunicationAnalyticsSummary
)

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for managing communications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Communication CRUD Operations
    
    def create_communication(
        self,
        user_id: int,
        communication: CommunicationCreate
    ) -> Communication:
        """Create a new communication"""
        db_communication = Communication(
            user_id=user_id,
            **communication.dict()
        )
        self.db.add(db_communication)
        self.db.commit()
        self.db.refresh(db_communication)
        
        # Create analytics record
        analytics = CommunicationAnalytics(communication_id=db_communication.id)
        self.db.add(analytics)
        self.db.commit()
        
        return db_communication

    
    def get_communication(self, communication_id: int) -> Optional[Communication]:
        """Get communication by ID"""
        return self.db.query(Communication).filter(
            Communication.id == communication_id
        ).first()
    
    def get_communications(
        self,
        user_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        type: Optional[CommunicationType] = None,
        status: Optional[CommunicationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Communication]:
        """Get communications with filters"""
        query = self.db.query(Communication)
        
        if user_id:
            query = query.filter(Communication.user_id == user_id)
        if customer_id:
            query = query.filter(Communication.customer_id == customer_id)
        if type:
            query = query.filter(Communication.type == type)
        if status:
            query = query.filter(Communication.status == status)
        
        return query.order_by(Communication.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_communication(
        self,
        communication_id: int,
        communication_update: CommunicationUpdate
    ) -> Optional[Communication]:
        """Update communication"""
        db_communication = self.get_communication(communication_id)
        if not db_communication:
            return None
        
        update_data = communication_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_communication, field, value)
        
        self.db.commit()
        self.db.refresh(db_communication)
        return db_communication
    
    def delete_communication(self, communication_id: int) -> bool:
        """Delete communication"""
        db_communication = self.get_communication(communication_id)
        if not db_communication:
            return False
        
        self.db.delete(db_communication)
        self.db.commit()
        return True

    
    # Email Integration
    
    def send_email(
        self,
        communication_id: int,
        email_config_id: Optional[int] = None
    ) -> bool:
        """Send email communication"""
        communication = self.get_communication(communication_id)
        if not communication or communication.type != CommunicationType.EMAIL:
            return False
        
        # Get email configuration
        if email_config_id:
            config = self.db.query(EmailConfiguration).filter(
                EmailConfiguration.id == email_config_id
            ).first()
        else:
            config = self.db.query(EmailConfiguration).filter(
                EmailConfiguration.is_default == True,
                EmailConfiguration.is_active == True
            ).first()
        
        if not config:
            communication.status = CommunicationStatus.FAILED
            communication.error_message = "No email configuration found"
            self.db.commit()
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{config.from_name} <{config.from_email}>" if config.from_name else config.from_email
            msg['To'] = ', '.join(communication.to_addresses)
            if communication.cc_addresses:
                msg['Cc'] = ', '.join(communication.cc_addresses)
            if communication.subject:
                msg['Subject'] = communication.subject
            if config.reply_to_email:
                msg['Reply-To'] = config.reply_to_email
            
            # Add body
            msg.attach(MIMEText(communication.body, 'html'))
            
            # Add attachments
            if communication.attachments:
                for attachment_path in communication.attachments:
                    try:
                        with open(attachment_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {attachment_path.split("/")[-1]}'
                            )
                            msg.attach(part)
                    except Exception as e:
                        logger.error(f"Failed to attach file {attachment_path}: {str(e)}")
            
            # Send email
            if config.use_ssl:
                server = smtplib.SMTP_SSL(config.smtp_host, config.smtp_port)
            else:
                server = smtplib.SMTP(config.smtp_host, config.smtp_port)
                if config.use_tls:
                    server.starttls()
            
            server.login(config.smtp_username, config.smtp_password)
            
            recipients = communication.to_addresses.copy()
            if communication.cc_addresses:
                recipients.extend(communication.cc_addresses)
            if communication.bcc_addresses:
                recipients.extend(communication.bcc_addresses)
            
            server.sendmail(config.from_email, recipients, msg.as_string())
            server.quit()
            
            # Update communication status
            communication.status = CommunicationStatus.SENT
            communication.sent_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Email sent successfully: {communication_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email {communication_id}: {str(e)}")
            communication.status = CommunicationStatus.FAILED
            communication.error_message = str(e)
            communication.retry_count += 1
            self.db.commit()
            return False

    
    # SMS Integration
    
    def send_sms(
        self,
        communication_id: int,
        sms_config_id: Optional[int] = None
    ) -> bool:
        """Send SMS communication"""
        communication = self.get_communication(communication_id)
        if not communication or communication.type != CommunicationType.SMS:
            return False
        
        # Get SMS configuration
        if sms_config_id:
            config = self.db.query(SMSConfiguration).filter(
                SMSConfiguration.id == sms_config_id
            ).first()
        else:
            config = self.db.query(SMSConfiguration).filter(
                SMSConfiguration.is_default == True,
                SMSConfiguration.is_active == True
            ).first()
        
        if not config:
            communication.status = CommunicationStatus.FAILED
            communication.error_message = "No SMS configuration found"
            self.db.commit()
            return False
        
        try:
            # Send SMS based on provider
            if config.provider.lower() == 'twilio':
                success = self._send_twilio_sms(communication, config)
            elif config.provider.lower() == 'nexmo':
                success = self._send_nexmo_sms(communication, config)
            else:
                raise ValueError(f"Unsupported SMS provider: {config.provider}")
            
            if success:
                communication.status = CommunicationStatus.SENT
                communication.sent_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"SMS sent successfully: {communication_id}")
                return True
            else:
                raise Exception("SMS sending failed")
                
        except Exception as e:
            logger.error(f"Failed to send SMS {communication_id}: {str(e)}")
            communication.status = CommunicationStatus.FAILED
            communication.error_message = str(e)
            communication.retry_count += 1
            self.db.commit()
            return False
    
    def _send_twilio_sms(self, communication: Communication, config: SMSConfiguration) -> bool:
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            client = Client(config.account_sid, config.api_key)
            
            for to_number in communication.to_addresses:
                message = client.messages.create(
                    body=communication.body,
                    from_=config.from_number,
                    to=to_number
                )
                logger.info(f"Twilio SMS sent: {message.sid}")
            
            return True
        except Exception as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            return False
    
    def _send_nexmo_sms(self, communication: Communication, config: SMSConfiguration) -> bool:
        """Send SMS via Nexmo/Vonage"""
        try:
            import nexmo
            client = nexmo.Client(key=config.api_key, secret=config.api_secret)
            
            for to_number in communication.to_addresses:
                response = client.send_message({
                    'from': config.from_number,
                    'to': to_number,
                    'text': communication.body
                })
                
                if response['messages'][0]['status'] != '0':
                    raise Exception(f"Nexmo error: {response['messages'][0]['error-text']}")
                
                logger.info(f"Nexmo SMS sent: {response['messages'][0]['message-id']}")
            
            return True
        except Exception as e:
            logger.error(f"Nexmo SMS error: {str(e)}")
            return False
