"""
Medical Guidance Agent - Provides step-by-step medical instructions
"""

import boto3
import json
import os
from .base_agent import BaseAgent
from config import get_bedrock_model

class MedicalGuidanceAgent(BaseAgent):
    """Provides real-time medical guidance"""
    
    def __init__(self):
        super().__init__("Medical Guidance Agent")
        self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
        self.use_bedrock = os.getenv('USE_BEDROCK', 'True').lower() == 'true'
    
    def execute(self, data: dict) -> dict:
        """Provide medical guidance based on emergency type"""
        emergency_plan = data.get('emergency_plan', {})
        emergency_type = emergency_plan.get('emergency_type', 'unknown')
        
        self.log_action("Generating medical guidance...")
        
        try:
            if self.use_bedrock:
                instructions = self._bedrock_guidance(emergency_type, emergency_plan)
            else:
                instructions = self._local_guidance(emergency_type, emergency_plan)
            
            self.log_action("Medical guidance ready", "success")
            
            return {
                "success": True,
                "instructions": instructions,
                "emergency_type": emergency_type,
                "agent": self.agent_name
            }
            
        except Exception as e:
            self.log_action(f"Guidance generation failed: {str(e)}", "error")
            return {
                "success": False,
                "instructions": self._fallback_instructions(emergency_type),
                "agent": self.agent_name,
                "error": str(e)
            }
    
    def _bedrock_guidance(self, emergency_type: str, emergency_plan: dict) -> dict:
        """Get guidance from Bedrock AI"""
        cpr_needed = emergency_plan.get('required_actions', {}).get('cpr_needed', False)
        aed_needed = emergency_plan.get('required_actions', {}).get('aed_needed', False)
        
        prompt = f"""
        Provide step-by-step first aid instructions for: {emergency_type}
        
        Context:
        - CPR needed: {cpr_needed}
        - AED needed: {aed_needed}
        
        Provide JSON response:
        {{
            "immediate_steps": ["step1", "step2", "step3"],
            "detailed_instructions": {{
                "step1": "detailed description",
                "step2": "detailed description"
            }},
            "warnings": ["warning1", "warning2"],
            "when_to_stop": "condition to stop"
        }}
        
        Make instructions clear for non-medical person.
        """
        
        response = self.bedrock.invoke_model(
            modelId=get_bedrock_model(),
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 800,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        guidance_text = result['content'][0]['text']
        
        try:
            return json.loads(guidance_text)
        except json.JSONDecodeError:
            return self._local_guidance(emergency_type, emergency_plan)
    
    def _local_guidance(self, emergency_type: str, emergency_plan: dict) -> dict:
        """Local guidance without Bedrock"""
        guidance_map = {
            "cardiac": {
                "immediate_steps": [
                    "Check responsiveness - tap shoulders, shout 'Are you okay?'",
                    "Check pulse on neck for 10 seconds maximum",
                    "If no pulse, start CPR immediately",
                    "Push hard and fast on center of chest",
                    "30 compressions, 2 breaths, repeat"
                ],
                "detailed_instructions": {
                    "hand_position": "Center of chest, between nipples, heel of hand",
                    "compression_depth": "At least 2 inches deep",
                    "compression_rate": "100-120 per minute (think 'Stayin' Alive')",
                    "rescue_breaths": "Tilt head back, lift chin, seal mouth, 2 breaths"
                },
                "warnings": [
                    "Don't stop CPR until help arrives or person starts breathing",
                    "Switch with someone every 2 minutes if possible",
                    "Don't be afraid to break ribs - better than death"
                ],
                "when_to_stop": "Person starts breathing normally or help arrives"
            },
            "choking": {
                "immediate_steps": [
                    "Ask 'Are you choking?' - if they can't speak, act immediately",
                    "Stand behind person, lean them forward",
                    "Give 5 sharp back blows between shoulder blades",
                    "Give 5 abdominal thrusts below ribcage",
                    "Repeat back blows and thrusts until object clears"
                ],
                "detailed_instructions": {
                    "back_blows": "Use heel of hand, hit firmly between shoulder blades",
                    "abdominal_thrusts": "Hands just above navel, quick upward thrusts",
                    "if_unconscious": "Start CPR immediately, check mouth before breaths"
                },
                "warnings": [
                    "Don't do abdominal thrusts on pregnant women or small children",
                    "If person becomes unconscious, start CPR",
                    "Continue until object is expelled or help arrives"
                ],
                "when_to_stop": "Object is expelled and person can breathe normally"
            },
            "bleeding": {
                "immediate_steps": [
                    "Apply direct pressure to wound with clean cloth",
                    "Elevate injured area above heart if possible",
                    "Don't remove embedded objects - stabilize them",
                    "Apply pressure to pressure points if bleeding continues",
                    "Watch for signs of shock"
                ],
                "detailed_instructions": {
                    "direct_pressure": "Press firmly with palm, don't peek at wound",
                    "elevation": "Raise above heart level to reduce blood flow",
                    "pressure_points": "Press artery against bone above wound",
                    "shock_signs": "Pale, cold, weak pulse, rapid breathing"
                },
                "warnings": [
                    "Don't remove objects stuck in wound",
                    "Don't use tourniquet unless trained",
                    "Watch for shock - lay person down, elevate legs"
                ],
                "when_to_stop": "Bleeding is controlled and help has arrived"
            }
        }
        
        return guidance_map.get(emergency_type, self._fallback_instructions(emergency_type))
    
    def _fallback_instructions(self, emergency_type: str) -> dict:
        """Fallback instructions when all else fails"""
        return {
            "immediate_steps": [
                "Ensure scene safety",
                "Check if person is responsive",
                "Call 911 if not already done",
                "Monitor breathing and consciousness",
                "Provide comfort and reassurance"
            ],
            "detailed_instructions": {
                "scene_safety": "Make sure area is safe before approaching",
                "responsiveness": "Tap shoulders and shout to get response",
                "monitoring": "Watch for changes in breathing or consciousness"
            },
            "warnings": [
                "Don't move person unless in immediate danger",
                "Don't give food or water",
                "Stay with person until help arrives"
            ],
            "when_to_stop": "Professional help has arrived and taken over"
        }