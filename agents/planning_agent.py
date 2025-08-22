"""
Planning Agent - Emergency analysis and response planning
"""

import boto3
import json
import os
from .base_agent import BaseAgent
from config import get_bedrock_model

class PlanningAgent(BaseAgent):
    """AI-powered emergency planning agent"""
    
    def __init__(self):
        super().__init__("Planning Agent")
        self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
        self.use_bedrock = os.getenv('USE_BEDROCK', 'True').lower() == 'true'
    
    def execute(self, data: dict) -> dict:
        """Analyze emergency and create response plan"""
        emergency_description = data.get('emergency_description', '')
        
        if not emergency_description:
            return self._error_response("No emergency description provided")
        
        self.log_action("Analyzing emergency situation...")
        
        try:
            if self.use_bedrock:
                plan = self._bedrock_analysis(emergency_description)
            else:
                plan = self._local_analysis(emergency_description)
            
            self.log_action("Emergency analysis complete", "success")
            return {
                "success": True,
                "emergency_plan": plan,
                "agent": self.agent_name
            }
            
        except Exception as e:
            self.log_action(f"Analysis failed: {str(e)}", "error")
            return {
                "success": False,
                "emergency_plan": self._fallback_plan(emergency_description),
                "agent": self.agent_name,
                "error": str(e)
            }
    
    def _bedrock_analysis(self, description: str) -> dict:
        """Use Bedrock for AI analysis"""
        prompt = f"""
        You are an Emergency Response AI. Analyze this emergency and create a response plan.
        
        Emergency: {description}
        
        Respond with JSON only:
        {{
            "emergency_type": "cardiac|choking|bleeding|trauma|burn|other",
            "severity": 1-10,
            "life_threatening": true/false,
            "time_critical": true/false,
            "required_actions": {{
                "call_911": true/false,
                "cpr_needed": true/false,
                "first_aid": true/false,
                "aed_needed": true/false
            }},
            "next_agents": ["emergency_services", "medical_guidance", "communication"]
        }}
        """
        
        response = self.bedrock.invoke_model(
            modelId=get_bedrock_model(),
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 500,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        plan_text = result['content'][0]['text']
        
        try:
            return json.loads(plan_text)
        except json.JSONDecodeError:
            return self._fallback_plan(description)
    
    def _local_analysis(self, description: str) -> dict:
        """Local analysis without Bedrock"""
        desc_lower = description.lower()
        
        # Emergency type detection
        if any(word in desc_lower for word in ["not breathing", "collapsed", "unconscious"]):
            emergency_type = "cardiac"
            severity = 9
            cpr_needed = True
            aed_needed = True
        elif "choking" in desc_lower:
            emergency_type = "choking"
            severity = 8
            cpr_needed = False
            aed_needed = False
        elif any(word in desc_lower for word in ["bleeding", "cut", "wound"]):
            emergency_type = "bleeding"
            severity = 7
            cpr_needed = False
            aed_needed = False
        elif "chest pain" in desc_lower:
            emergency_type = "cardiac"
            severity = 8
            cpr_needed = False
            aed_needed = True
        else:
            emergency_type = "other"
            severity = 6
            cpr_needed = False
            aed_needed = False
        
        return {
            "emergency_type": emergency_type,
            "severity": severity,
            "life_threatening": severity >= 7,
            "time_critical": True,
            "required_actions": {
                "call_911": True,
                "cpr_needed": cpr_needed,
                "first_aid": True,
                "aed_needed": aed_needed
            },
            "next_agents": ["emergency_services", "medical_guidance", "communication"]
        }
    
    def _fallback_plan(self, description: str) -> dict:
        """Fallback plan when analysis fails"""
        return {
            "emergency_type": "unknown",
            "severity": 8,
            "life_threatening": True,
            "time_critical": True,
            "required_actions": {
                "call_911": True,
                "cpr_needed": True,
                "first_aid": True,
                "aed_needed": True
            },
            "next_agents": ["emergency_services", "medical_guidance", "communication"]
        }
    
    def _error_response(self, error_msg: str) -> dict:
        """Return error response"""
        self.log_action(error_msg, "error")
        return {
            "success": False,
            "error": error_msg,
            "agent": self.agent_name
        }