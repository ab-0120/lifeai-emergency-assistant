"""
Emergency Services Agent - 911 coordination and dispatch
"""

from datetime import datetime
from .base_agent import BaseAgent

class EmergencyServicesAgent(BaseAgent):
    """Handles emergency services coordination"""
    
    def __init__(self):
        super().__init__("Emergency Services Agent")
    
    def execute(self, data: dict) -> dict:
        """Coordinate with emergency services"""
        emergency_plan = data.get('emergency_plan', {})
        
        if not emergency_plan.get('required_actions', {}).get('call_911', False):
            return {
                "success": True,
                "action": "911_not_required",
                "agent": self.agent_name
            }
        
        self.log_action("Coordinating with 911 dispatch...")
        
        try:
            # Simulate 911 coordination
            dispatch_info = self._coordinate_911(emergency_plan)
            
            self.log_action(f"911 dispatched - ETA: {dispatch_info['eta']}", "success")
            
            return {
                "success": True,
                "dispatch_info": dispatch_info,
                "agent": self.agent_name
            }
            
        except Exception as e:
            self.log_action(f"911 coordination failed: {str(e)}", "error")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "fallback": "Manual 911 call required"
            }
    
    def _coordinate_911(self, emergency_plan: dict) -> dict:
        """Coordinate with 911 services"""
        emergency_type = emergency_plan.get('emergency_type', 'unknown')
        severity = emergency_plan.get('severity', 5)
        
        # Determine response type and ETA based on emergency
        if emergency_type == "cardiac":
            response_type = "ALS_Ambulance"  # Advanced Life Support
            eta = "6-8 minutes"
            units_dispatched = ["Ambulance", "Fire_Rescue", "AED_Unit"]
        elif emergency_type == "choking":
            response_type = "BLS_Ambulance"  # Basic Life Support
            eta = "8-10 minutes"
            units_dispatched = ["Ambulance", "Fire_Rescue"]
        elif emergency_type == "bleeding":
            response_type = "Trauma_Response"
            eta = "7-9 minutes"
            units_dispatched = ["Ambulance", "Trauma_Unit"]
        else:
            response_type = "Standard_Response"
            eta = "8-12 minutes"
            units_dispatched = ["Ambulance"]
        
        return {
            "call_id": f"911-{int(datetime.now().timestamp())}",
            "response_type": response_type,
            "eta": eta,
            "units_dispatched": units_dispatched,
            "priority": "HIGH" if severity >= 8 else "MEDIUM",
            "status": "DISPATCHED",
            "timestamp": datetime.now().isoformat()
        }