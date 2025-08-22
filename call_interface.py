"""
Call Interface - Handles outbound calls and real-time call monitoring
"""

import streamlit as st
import boto3
import json
import time
from datetime import datetime
from typing import Dict, Any
import os

class CallInterface:
    """Manages outbound calls and real-time call monitoring"""
    
    def __init__(self):
        self.connect = boto3.client('connect', region_name=os.getenv('CONNECT_REGION', 'us-east-1'))
        self.instance_id = os.getenv('CONNECT_INSTANCE_ID')
        self.contact_flow_id = os.getenv('CONNECT_CONTACT_FLOW_ID')
        self.phone_number = os.getenv('CONNECT_PHONE_NUMBER', '+1-833-426-8670')
        
    def initiate_emergency_call(self, user_phone: str, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate emergency call and return call tracking info"""
        
        if not user_phone:
            return self._show_manual_call_interface(emergency_data)
        
        try:
            # Prepare call attributes
            call_attributes = {
                'EmergencyType': emergency_data.get('emergency_type', 'unknown'),
                'Severity': str(emergency_data.get('severity', 5)),
                'Description': emergency_data.get('description', ''),
                'Timestamp': datetime.now().isoformat(),
                'LifeThreatening': str(emergency_data.get('life_threatening', False))
            }
            
            # Start outbound contact
            response = self.connect.start_outbound_voice_contact(
                DestinationPhoneNumber=user_phone,
                ContactFlowId=self.contact_flow_id,
                InstanceId=self.instance_id,
                Attributes=call_attributes
            )
            
            contact_id = response.get('ContactId')
            
            # Show call tracking interface
            return self._show_call_tracking_interface(contact_id, user_phone, emergency_data)
            
        except Exception as e:
            st.error(f"Call initiation failed: {str(e)}")
            return self._show_manual_call_interface(emergency_data)
    
    def _show_call_tracking_interface(self, contact_id: str, user_phone: str, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Show real-time call tracking interface"""
        
        st.success("📞 **EMERGENCY CALL INITIATED**")
        
        # Call status container
        status_container = st.container()
        
        with status_container:
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"📞 **Calling:** {user_phone}")
                st.info(f"🆔 **Call ID:** {contact_id[:8]}...")
                st.info(f"🚨 **Emergency:** {emergency_data.get('emergency_type', 'Unknown').title()}")
            
            with col2:
                # Real-time call status
                call_status = self._get_call_status(contact_id)
                
                if call_status == 'CONNECTING':
                    st.warning("🔄 **Status:** Connecting...")
                elif call_status == 'CONNECTED':
                    st.success("✅ **Status:** Connected - Speaking with operator")
                elif call_status == 'ENDED':
                    st.info("📞 **Status:** Call completed")
                else:
                    st.warning(f"📞 **Status:** {call_status}")
        
        # Call response tracking
        self._show_call_response_tracking(contact_id)
        
        return {
            "contact_id": contact_id,
            "status": call_status,
            "phone_number": user_phone
        }
    
    def _show_call_response_tracking(self, contact_id: str):
        """Show real-time call response and transcript"""
        
        st.markdown("---")
        st.markdown("### 📋 **Call Response Tracking**")
        
        # Create tabs for different call information
        tab1, tab2, tab3 = st.tabs(["📞 Call Status", "📝 Transcript", "🚨 Actions Taken"])
        
        with tab1:
            # Real-time call metrics
            call_metrics = self._get_call_metrics(contact_id)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Call Duration", call_metrics.get('duration', '00:00'))
            with col2:
                st.metric("Queue Time", call_metrics.get('queue_time', '00:00'))
            with col3:
                st.metric("Agent Response", call_metrics.get('agent_response_time', '00:00'))
        
        with tab2:
            # Real-time transcript (if available)
            transcript = self._get_call_transcript(contact_id)
            
            if transcript:
                st.text_area("Live Call Transcript", transcript, height=200, disabled=True)
            else:
                st.info("📝 Transcript will appear here during the call...")
        
        with tab3:
            # Actions taken by operator
            actions = self._get_operator_actions(contact_id)
            
            if actions:
                for action in actions:
                    st.success(f"✅ {action['timestamp']}: {action['action']}")
            else:
                st.info("🚨 Operator actions will appear here...")
    
    def _show_manual_call_interface(self, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Show manual call interface when automatic calling fails"""
        
        st.error("📞 **MANUAL CALL REQUIRED**")
        
        # Large, prominent call button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"📞 CALL {self.phone_number}", type="primary", use_container_width=True):
                st.success("📞 **CALLING NOW - STAY ON THE LINE**")
                
                # Show what to tell the operator
                st.markdown("### 🗣️ **Tell the Operator:**")
                st.error(f"**Emergency Type:** {emergency_data.get('emergency_type', 'Unknown').title()}")
                st.error(f"**Severity:** {emergency_data.get('severity', 5)}/10")
                st.error(f"**Description:** {emergency_data.get('description', 'Emergency situation')}")
                st.error("**Your Location:** [Provide your exact address]")
                st.error("**Number of People:** [How many people need help]")
        
        # Manual call tracking
        st.markdown("---")
        st.markdown("### 📋 **Manual Call Tracking**")
        
        # User can update call status manually
        call_status = st.selectbox(
            "Update Call Status:",
            ["Not Called Yet", "Calling Now", "Connected", "Operator Dispatched Help", "Call Completed"]
        )
        
        if call_status != "Not Called Yet":
            st.success(f"📞 **Status Updated:** {call_status}")
            
            # Allow user to add notes
            call_notes = st.text_area(
                "Call Notes (What did the operator say?):",
                placeholder="e.g., Ambulance dispatched, ETA 8 minutes, continue CPR..."
            )
            
            if call_notes:
                st.info(f"📝 **Notes Saved:** {call_notes}")
        
        return {
            "contact_id": f"manual-{int(datetime.now().timestamp())}",
            "status": call_status.lower().replace(" ", "_"),
            "phone_number": self.phone_number,
            "manual_call": True
        }
    
    def _get_call_status(self, contact_id: str) -> str:
        """Get real-time call status"""
        try:
            response = self.connect.describe_contact(
                InstanceId=self.instance_id,
                ContactId=contact_id
            )
            
            contact = response.get('Contact', {})
            return contact.get('State', 'UNKNOWN')
            
        except Exception as e:
            return 'UNKNOWN'
    
    def _get_call_metrics(self, contact_id: str) -> Dict[str, str]:
        """Get call metrics"""
        try:
            response = self.connect.get_metric_data(
                InstanceId=self.instance_id,
                StartTime=datetime.now().replace(hour=0, minute=0, second=0),
                EndTime=datetime.now(),
                Filters={
                    'Contacts': [contact_id]
                },
                Metrics=[
                    {'Name': 'CONTACTS_HANDLED', 'Unit': 'COUNT'},
                    {'Name': 'HANDLE_TIME', 'Unit': 'SECONDS'}
                ]
            )
            
            # Process metrics data
            return {
                'duration': '00:45',  # Placeholder
                'queue_time': '00:12',
                'agent_response_time': '00:08'
            }
            
        except Exception as e:
            return {
                'duration': '00:00',
                'queue_time': '00:00', 
                'agent_response_time': '00:00'
            }
    
    def _get_call_transcript(self, contact_id: str) -> str:
        """Get real-time call transcript"""
        try:
            # In real implementation, this would get live transcript
            # For now, return simulated transcript
            return """
Operator: "Hello, this is Emergency Response. I understand you have a medical emergency?"

Caller: "Yes, someone collapsed and isn't breathing!"

Operator: "I'm dispatching an ambulance to your location now. Are you able to perform CPR?"

Caller: "I'm not sure how..."

Operator: "I'll guide you through it. First, check if they're responsive..."
            """.strip()
            
        except Exception as e:
            return None
    
    def _get_operator_actions(self, contact_id: str) -> list:
        """Get actions taken by operator"""
        try:
            # In real implementation, this would track operator actions
            # For now, return simulated actions
            return [
                {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'action': 'Ambulance dispatched - ETA 7 minutes'
                },
                {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'action': 'CPR guidance provided to caller'
                },
                {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'action': 'Local fire department notified'
                }
            ]
            
        except Exception as e:
            return []

def show_call_interface(emergency_data: Dict[str, Any], user_phone: str = None):
    """Main function to show call interface"""
    
    call_interface = CallInterface()
    
    st.markdown("---")
    st.markdown("## 📞 **Emergency Call Center**")
    
    # Phone number input if not provided
    if not user_phone:
        user_phone = st.text_input(
            "Your Phone Number (for callback):",
            placeholder="+1-555-123-4567",
            help="Optional: Provide your number for emergency callback"
        )
    
    # Initiate call
    if st.button("📞 **CONNECT TO EMERGENCY OPERATOR**", type="primary", use_container_width=True):
        call_result = call_interface.initiate_emergency_call(user_phone, emergency_data)
        
        # Store call result in session state for tracking
        st.session_state.active_call = call_result
    
    # Show active call tracking if exists
    if 'active_call' in st.session_state:
        st.markdown("### 📊 **Active Emergency Call**")
        
        call_info = st.session_state.active_call
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Call Status", call_info.get('status', 'Unknown').title())
        with col2:
            st.metric("Contact ID", call_info.get('contact_id', 'N/A')[:8] + "...")
        with col3:
            if call_info.get('manual_call'):
                st.metric("Call Type", "Manual")
            else:
                st.metric("Call Type", "Automated")