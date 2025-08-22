"""
Amazon Connect Agent - Handles emergency calls through Amazon Connect
"""

import boto3
import os
from datetime import datetime
from .base_agent import BaseAgent

class ConnectAgent(BaseAgent):
    """Handles emergency calls through Amazon Connect toll-free number"""
    
    def __init__(self):
        super().__init__("Connect Agent")
        self.connect = boto3.client('connect', region_name=self.region)
        self.instance_id = os.getenv('CONNECT_INSTANCE_ID')
        self.contact_flow_id = os.getenv('CONNECT_CONTACT_FLOW_ID')
        self.phone_number = os.getenv('CONNECT_PHONE_NUMBER', '+1-833-426-8670')
    
    def execute(self, data: dict) -> dict:
        """Initiate emergency call through Amazon Connect"""
        emergency_plan = data.get('emergency_plan', {})
        user_phone = data.get('user_phone', '')
        
        if not emergency_plan.get('required_actions', {}).get('call_911', False):
            return {
                "success": True,
                "action": "emergency_call_not_required",
                "agent": self.agent_name
            }
        
        self.log_action("Initiating emergency call through Amazon Connect...")
        
        try:
            # Initiate outbound call to user
            call_result = self._initiate_emergency_call(emergency_plan, user_phone)
            
            self.log_action(f"Emergency call initiated - Contact ID: {call_result.get('contact_id', 'N/A')}", "success")
            
            return {
                "success": True,
                "call_result": call_result,
                "hotline_number": self.phone_number,
                "agent": self.agent_name
            }
            
        except Exception as e:
            self.log_action(f"Emergency call failed: {str(e)}", "error")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "fallback": f"Manual call required to {self.phone_number}"
            }
    
    def _initiate_emergency_call(self, emergency_plan: dict, user_phone: str) -> dict:
        """Initiate emergency call through Amazon Connect"""
        
        emergency_type = emergency_plan.get('emergency_type', 'unknown')
        severity = emergency_plan.get('severity', 5)
        
        # Prepare call attributes
        call_attributes = {
            'EmergencyType': emergency_type,
            'Severity': str(severity),
            'Timestamp': datetime.now().isoformat(),
            'LifeThreatening': str(emergency_plan.get('life_threatening', False)),
            'TimeCritical': str(emergency_plan.get('time_critical', False))
        }
        
        if user_phone and self.instance_id and self.contact_flow_id:
            try:
                # Start outbound contact
                response = self.connect.start_outbound_voice_contact(
                    DestinationPhoneNumber=user_phone,
                    ContactFlowId=self.contact_flow_id,
                    InstanceId=self.instance_id,
                    Attributes=call_attributes
                )
                
                return {
                    "contact_id": response.get('ContactId'),
                    "call_type": "outbound_to_user",
                    "status": "initiated",
                    "phone_number": user_phone,
                    "emergency_hotline": self.phone_number
                }
                
            except Exception as e:
                # Fallback to providing hotline number
                self.log_action(f"Outbound call failed: {e}, providing hotline number", "warning")
                return self._provide_hotline_info(emergency_plan)
        else:
            # Provide hotline number for manual calling
            return self._provide_hotline_info(emergency_plan)
    
    def _provide_hotline_info(self, emergency_plan: dict) -> dict:
        """Provide emergency hotline information"""
        
        emergency_type = emergency_plan.get('emergency_type', 'unknown')
        severity = emergency_plan.get('severity', 5)
        
        # Determine priority level
        if severity >= 8:
            priority = "CRITICAL"
            message = f"CRITICAL {emergency_type.upper()} EMERGENCY"
        elif severity >= 6:
            priority = "HIGH"
            message = f"HIGH PRIORITY {emergency_type.upper()} EMERGENCY"
        else:
            priority = "MEDIUM"
            message = f"{emergency_type.upper()} EMERGENCY"
        
        return {
            "contact_id": f"manual-{int(datetime.now().timestamp())}",
            "call_type": "manual_hotline",
            "status": "hotline_provided",
            "phone_number": self.phone_number,
            "priority": priority,
            "message": message,
            "instructions": [
                f"Call {self.phone_number} immediately",
                f"Tell them: {message}",
                "Provide your location",
                "Stay on the line for guidance"
            ]
        }
    
    def get_hotline_number(self) -> str:
        """Get the emergency hotline number"""
        return self.phone_number
    
    def create_contact_flow_config(self) -> dict:
        """Provide configuration for Amazon Connect contact flow"""
        return {
            "contact_flow_name": "LifeAI Emergency Response",
            "description": "Emergency response contact flow for LifeAI system",
            "type": "CONTACT_FLOW",
            "content": {
                "Version": "2019-10-30",
                "StartAction": "greeting",
                "Actions": [
                    {
                        "Identifier": "greeting",
                        "Type": "MessageParticipant",
                        "Parameters": {
                            "Text": "Hello, this is LifeAI Emergency Response. We detected an emergency situation. Are you safe and able to speak?"
                        },
                        "Transitions": {
                            "NextAction": "get_emergency_details"
                        }
                    },
                    {
                        "Identifier": "get_emergency_details",
                        "Type": "GetParticipantInput",
                        "Parameters": {
                            "Text": "Please describe your emergency situation. Press 1 for medical emergency, 2 for fire, 3 for police, or stay on the line to speak with an agent.",
                            "MaxDigits": 1,
                            "Timeout": "PT10S"
                        },
                        "Transitions": {
                            "NextAction": "route_emergency",
                            "Conditions": [
                                {
                                    "NextAction": "medical_emergency",
                                    "Condition": {
                                        "Option": "1"
                                    }
                                },
                                {
                                    "NextAction": "fire_emergency", 
                                    "Condition": {
                                        "Option": "2"
                                    }
                                },
                                {
                                    "NextAction": "police_emergency",
                                    "Condition": {
                                        "Option": "3"
                    }
                                }
                            ],
                            "DefaultNextAction": "connect_agent"
                        }
                    }
                ]
            }
        }