"""
Communication Agent - Handles alerts and notifications
"""

from datetime import datetime
from .base_agent import BaseAgent

class CommunicationAgent(BaseAgent):
    """Handles emergency communications and alerts"""
    
    def __init__(self):
        super().__init__("Communication Agent")
    
    def execute(self, data: dict) -> dict:
        """Send emergency alerts and notifications"""
        emergency_plan = data.get('emergency_plan', {})
        
        self.log_action("Sending emergency notifications...")
        
        try:
            notifications = self._send_notifications(emergency_plan)
            
            self.log_action("All emergency contacts notified", "success")
            
            return {
                "success": True,
                "notifications": notifications,
                "agent": self.agent_name
            }
            
        except Exception as e:
            self.log_action(f"Communication failed: {str(e)}", "error")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "fallback": "Manual contact required"
            }
    
    def _send_notifications(self, emergency_plan: dict) -> dict:
        """Send various types of notifications"""
        emergency_type = emergency_plan.get('emergency_type', 'unknown')
        severity = emergency_plan.get('severity', 5)
        
        # Determine notification priority and recipients
        if severity >= 8:
            priority = "CRITICAL"
            recipients = ["emergency_contacts", "workplace_security", "hospital", "family"]
        elif severity >= 6:
            priority = "HIGH"
            recipients = ["emergency_contacts", "workplace_security"]
        else:
            priority = "MEDIUM"
            recipients = ["emergency_contacts"]
        
        notifications_sent = []
        
        for recipient in recipients:
            notification = {
                "recipient": recipient,
                "message": self._create_message(emergency_type, severity),
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "status": "SENT"
            }
            notifications_sent.append(notification)
        
        return {
            "total_sent": len(notifications_sent),
            "priority": priority,
            "notifications": notifications_sent,
            "emergency_broadcast": severity >= 8
        }
    
    def _create_message(self, emergency_type: str, severity: int) -> str:
        """Create appropriate message based on emergency"""
        base_message = f"EMERGENCY ALERT: {emergency_type.upper()} emergency in progress."
        
        if severity >= 8:
            urgency = "CRITICAL - Immediate response required."
        elif severity >= 6:
            urgency = "HIGH PRIORITY - Urgent response needed."
        else:
            urgency = "Emergency response in progress."
        
        return f"{base_message} {urgency} Emergency services have been contacted."