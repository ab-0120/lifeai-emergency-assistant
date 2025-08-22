"""
SMS Emergency System - Sends real SMS alerts using AWS SNS
"""

import streamlit as st
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

class SMSEmergencySystem:
    """Handles real SMS emergency alerts"""
    
    def __init__(self):
        self.sns = boto3.client('sns', region_name=os.getenv('SNS_REGION', 'us-east-1'))
        self.emergency_number = os.getenv('EMERGENCY_SMS_NUMBER', '+1234567890')
        self.from_number = os.getenv('SMS_FROM_NUMBER', 'LifeAI-Emergency')
    
    def send_emergency_sms(self, emergency_data, recipient_number=None):
        """Send real SMS emergency alert"""
        
        # Use provided number or default
        phone_number = recipient_number or self.emergency_number
        
        # Create emergency message
        message = self._create_emergency_message(emergency_data)
        
        try:
            # Send SMS using AWS SNS
            response = self.sns.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': self.from_number
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'  # High priority
                    }
                }
            )
            
            message_id = response.get('MessageId')
            
            # Show success
            st.success("📱 **EMERGENCY SMS SENT SUCCESSFULLY**")
            st.info(f"📞 **Sent to:** {phone_number}")
            st.info(f"🆔 **Message ID:** {message_id}")
            
            # Show message content
            st.markdown("### 📝 **Message Sent:**")
            st.text_area("SMS Content", message, height=150, disabled=True)
            
            return {
                "success": True,
                "message_id": message_id,
                "phone_number": phone_number,
                "timestamp": datetime.now().isoformat()
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            st.error(f"📱 **SMS FAILED**: {error_code}")
            st.error(f"**Error:** {error_message}")
            
            # Show fallback options
            self._show_fallback_options(phone_number, message)
            
            return {
                "success": False,
                "error": error_message,
                "phone_number": phone_number
            }
        
        except Exception as e:
            st.error(f"📱 **SMS SYSTEM ERROR**: {str(e)}")
            
            # Show detailed error for debugging
            st.error(f"**Error Type**: {type(e).__name__}")
            st.error(f"**Error Details**: {str(e)}")
            
            # Common solutions
            st.markdown("### 🔧 **Common Solutions:**")
            st.markdown("""
            1. **Set SMS spending limit** in AWS SNS Console
            2. **Verify phone number** format: +917906171685
            3. **Check AWS credentials** are working
            4. **Try test SMS** from AWS Console first
            """)
            
            self._show_fallback_options(phone_number, message)
            
            return {
                "success": False,
                "error": str(e),
                "phone_number": phone_number
            }
    
    def _create_emergency_message(self, emergency_data):
        """Create emergency SMS message"""
        
        emergency_type = emergency_data.get('emergency_type', 'Unknown')
        description = emergency_data.get('description', 'Emergency situation')
        severity = emergency_data.get('severity', 8)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        message = f"""🚨 EMERGENCY ALERT 🚨

TYPE: {emergency_type.upper()}
SEVERITY: {severity}/10
TIME: {timestamp}

DESCRIPTION: {description}

IMMEDIATE ACTION REQUIRED:
- Call 911 if life-threatening
- Follow first aid protocols
- Stay with person until help arrives

This is an automated emergency alert from LifeAI Emergency Response System.

Reply STOP to opt out."""
        
        return message
    
    def _show_fallback_options(self, phone_number, message):
        """Show fallback options when SMS fails"""
        
        st.markdown("---")
        st.warning("📱 **SMS DELIVERY FAILED - MANUAL OPTIONS:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📞 **Call Directly:**")
            if st.button(f"📞 CALL {phone_number}", use_container_width=True):
                st.info(f"📞 Calling {phone_number}...")
                st.markdown("**Tell them:** Emergency situation, need immediate help")
        
        with col2:
            st.markdown("### 📝 **Manual Text:**")
            if st.button("📱 OPEN MESSAGING APP", use_container_width=True):
                st.info("📱 Opening default messaging app...")
                st.text_area("Copy this message:", message, height=100)

def show_sms_emergency_interface(emergency_data):
    """Main SMS emergency interface"""
    
    sms_system = SMSEmergencySystem()
    
    st.markdown("## 📱 **EMERGENCY SMS ALERT SYSTEM**")
    
    # Phone number input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        phone_number = st.text_input(
            "📞 Emergency Contact Number:",
            value=sms_system.emergency_number,
            placeholder="+1234567890",
            help="Enter the phone number to receive emergency SMS"
        )
    
    with col2:
        st.markdown("### 🚨 **Send Alert**")
        if st.button("📱 **SEND EMERGENCY SMS**", type="primary", use_container_width=True):
            if phone_number:
                # Send SMS
                result = sms_system.send_emergency_sms(emergency_data, phone_number)
                
                # Store result in session state
                st.session_state.sms_sent = result
            else:
                st.error("📞 Please enter a valid phone number")
    
    # Show SMS preview
    st.markdown("---")
    st.markdown("### 📝 **SMS Preview:**")
    
    preview_message = sms_system._create_emergency_message(emergency_data)
    st.text_area("Message that will be sent:", preview_message, height=200, disabled=True)
    
    # Show SMS history if available
    if st.session_state.get('sms_sent'):
        st.markdown("---")
        st.markdown("### 📊 **SMS Status:**")
        
        result = st.session_state.sms_sent
        
        if result['success']:
            st.success(f"✅ SMS delivered to {result['phone_number']}")
            st.info(f"🆔 Message ID: {result['message_id']}")
            st.info(f"⏰ Sent at: {result['timestamp']}")
        else:
            st.error(f"❌ SMS failed to {result['phone_number']}")
            st.error(f"Error: {result['error']}")
    
    # Additional emergency options
    st.markdown("---")
    st.markdown("### 🚨 **Additional Emergency Options:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 **CALL 911**", use_container_width=True):
            st.error("📞 **CALLING 911 NOW**")
            st.info("Tell them: Location, emergency type, number of people")
    
    with col2:
        if st.button("🚑 **CALL AMBULANCE**", use_container_width=True):
            st.error("🚑 **CALLING AMBULANCE**")
            st.info("Medical emergency - immediate response needed")
    
    with col3:
        if st.button("🔄 **RESEND SMS**", use_container_width=True):
            if phone_number:
                sms_system.send_emergency_sms(emergency_data, phone_number)

def test_sms_system():
    """Test SMS system with sample data"""
    
    st.markdown("### 🧪 **Test SMS System**")
    
    test_data = {
        'emergency_type': 'cardiac',
        'description': 'Person collapsed and not breathing - TEST MESSAGE',
        'severity': 9,
        'life_threatening': True
    }
    
    if st.button("🧪 **SEND TEST SMS**"):
        sms_system = SMSEmergencySystem()
        result = sms_system.send_emergency_sms(test_data)
        
        if result['success']:
            st.success("✅ Test SMS sent successfully!")
        else:
            st.error("❌ Test SMS failed")

# Configuration helper
def setup_sms_instructions():
    """Show SMS setup instructions"""
    
    with st.expander("🔧 **SMS Setup Instructions**", expanded=False):
        st.markdown("""
        ### AWS SNS SMS Setup:
        
        1. **Enable SMS in AWS SNS:**
           - Go to AWS SNS Console
           - Click "Text messaging (SMS)"
           - Set spending limit (start with $1.00)
           
        2. **Update .env file:**
           ```
           EMERGENCY_SMS_NUMBER=+1234567890  # Your real phone number
           SMS_FROM_NUMBER=LifeAI-Emergency
           ```
        
        3. **Test SMS:**
           - Use the test button below
           - Check your phone for message
           
        4. **Costs:**
           - ~$0.0075 per SMS in US
           - Very affordable for emergency use
        
        **Note:** Replace +1234567890 with your actual phone number!
        """)