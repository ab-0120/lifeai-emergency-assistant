"""
Emergency Response Orchestrator - The Brain of the System

This orchestrator acts like a human brain, analyzing situations and deciding
which agents to activate, in what order, and how they should communicate.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
from agents.planning_agent import PlanningAgent
from agents.emergency_services_agent import EmergencyServicesAgent
from agents.medical_guidance_agent import MedicalGuidanceAgent
from agents.communication_agent import CommunicationAgent
from agents.transcription_agent import TranscriptionAgent
from agents.connect_agent import ConnectAgent

class EmergencyOrchestrator:
    """
    The central brain that coordinates all emergency response agents
    
    Like a human brain:
    - Receives input (emergency description)
    - Analyzes the situation (planning agent)
    - Makes decisions (which agents to activate)
    - Coordinates responses (manages data flow between agents)
    - Monitors progress (tracks all agent activities)
    """
    
    def __init__(self):
        self.session_id = f"emergency_{int(datetime.now().timestamp())}"
        self.active_agents = {}
        self.agent_results = {}
        self.decision_log = []
        
        # Initialize available agents
        self.available_agents = {
            "transcription": TranscriptionAgent(),
            "planning": PlanningAgent(),
            "emergency_services": EmergencyServicesAgent(),
            "connect_hotline": ConnectAgent(),
            "medical_guidance": MedicalGuidanceAgent(),
            "communication": CommunicationAgent()
        }
    
    def process_emergency(self, emergency_description: str) -> Dict[str, Any]:
        """
        Main brain function - processes emergency from start to finish
        
        Brain Process:
        1. Analyze situation (what's happening?)
        2. Make decisions (what needs to be done?)
        3. Coordinate response (activate agents in right order)
        4. Monitor and adapt (track progress, make adjustments)
        """
        
        self._log_decision(f"Emergency received: {emergency_description}")
        
        # PHASE 1: SITUATION ANALYSIS
        analysis_result = self._analyze_situation(emergency_description)
        
        if not analysis_result["success"]:
            return self._emergency_fallback(emergency_description)
        
        emergency_plan = analysis_result["emergency_plan"]
        
        # PHASE 2: DECISION MAKING
        agent_sequence = self._decide_agent_sequence(emergency_plan)
        
        # PHASE 3: COORDINATED RESPONSE
        response_results = self._coordinate_response(agent_sequence, emergency_plan)
        
        # PHASE 4: FINAL ASSESSMENT
        return self._compile_final_response(emergency_plan, response_results)
    
    def _analyze_situation(self, emergency_description: str) -> Dict[str, Any]:
        """
        Brain's analysis phase - understand what's happening
        """
        self._log_decision("Analyzing emergency situation...")
        
        planning_agent = self.available_agents["planning"]
        self.active_agents["planning"] = planning_agent
        
        analysis_data = {"emergency_description": emergency_description}
        result = planning_agent.execute(analysis_data)
        
        self.agent_results["planning"] = result
        
        if result["success"]:
            self._log_decision(f"Analysis complete: {result['emergency_plan']['emergency_type']} emergency, severity {result['emergency_plan']['severity']}")
        else:
            self._log_decision("Analysis failed, using fallback plan")
        
        return result
    
    def _decide_agent_sequence(self, emergency_plan: Dict[str, Any]) -> List[str]:
        """
        Brain's decision-making phase - decide which agents to activate and in what order
        
        Decision logic based on emergency characteristics:
        - Life-threatening: Emergency services first, then medical guidance
        - Non-life-threatening: Medical guidance first, then emergency services if needed
        - Always: Communication agent for notifications
        """
        
        emergency_type = emergency_plan.get("emergency_type", "unknown")
        severity = emergency_plan.get("severity", 5)
        life_threatening = emergency_plan.get("life_threatening", False)
        required_actions = emergency_plan.get("required_actions", {})
        
        sequence = []
        
        # Decision tree based on emergency characteristics
        if life_threatening or severity >= 8:
            self._log_decision("Life-threatening emergency detected - prioritizing emergency services")
            
            if required_actions.get("call_911", False):
                sequence.append("emergency_services")
            
            if required_actions.get("cpr_needed", False) or required_actions.get("first_aid", False):
                sequence.append("medical_guidance")
            
            sequence.append("communication")
            
        elif severity >= 6:
            self._log_decision("Serious emergency detected - medical guidance first")
            
            if required_actions.get("first_aid", False):
                sequence.append("medical_guidance")
            
            if required_actions.get("call_911", False):
                sequence.append("emergency_services")
            
            sequence.append("communication")
            
        else:
            self._log_decision("Standard emergency response")
            
            sequence.extend(["medical_guidance", "communication"])
            
            if required_actions.get("call_911", False):
                sequence.append("emergency_services")
        
        self._log_decision(f"Agent sequence decided: {' -> '.join(sequence)}")
        return sequence
    
    def _coordinate_response(self, agent_sequence: List[str], emergency_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Brain's coordination phase - activate agents in sequence and manage data flow
        """
        
        response_results = {}
        shared_data = {"emergency_plan": emergency_plan}
        
        for agent_name in agent_sequence:
            if agent_name not in self.available_agents:
                self._log_decision(f"Agent {agent_name} not available, skipping")
                continue
            
            self._log_decision(f"Activating {agent_name} agent...")
            
            agent = self.available_agents[agent_name]
            self.active_agents[agent_name] = agent
            
            # Execute agent with shared data
            result = agent.execute(shared_data)
            response_results[agent_name] = result
            
            # Update shared data with results for next agents
            if result["success"]:
                shared_data[f"{agent_name}_result"] = result
                self._log_decision(f"{agent_name} agent completed successfully")
            else:
                self._log_decision(f"{agent_name} agent failed: {result.get('error', 'Unknown error')}")
        
        return response_results
    
    def _compile_final_response(self, emergency_plan: Dict[str, Any], response_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Brain's final assessment - compile all results into coherent response
        """
        
        successful_agents = [name for name, result in response_results.items() if result.get("success", False)]
        failed_agents = [name for name, result in response_results.items() if not result.get("success", False)]
        
        self._log_decision(f"Response complete. Successful agents: {successful_agents}, Failed agents: {failed_agents}")
        
        return {
            "session_id": self.session_id,
            "emergency_plan": emergency_plan,
            "response_results": response_results,
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "decision_log": self.decision_log,
            "timestamp": datetime.now().isoformat(),
            "status": "COMPLETE" if not failed_agents else "PARTIAL_SUCCESS"
        }
    
    def _emergency_fallback(self, emergency_description: str) -> Dict[str, Any]:
        """
        Brain's emergency fallback when analysis fails
        """
        self._log_decision("Emergency fallback activated - critical system failure")
        
        return {
            "session_id": self.session_id,
            "emergency_plan": {
                "emergency_type": "unknown",
                "severity": 9,
                "life_threatening": True,
                "required_actions": {"call_911": True, "first_aid": True}
            },
            "response_results": {},
            "successful_agents": [],
            "failed_agents": ["planning"],
            "decision_log": self.decision_log,
            "timestamp": datetime.now().isoformat(),
            "status": "FALLBACK_ACTIVATED",
            "fallback_instructions": [
                "CALL 911 IMMEDIATELY",
                "Check if person is responsive",
                "Check breathing and pulse",
                "Begin CPR if needed",
                "Stay with person until help arrives"
            ]
        }
    
    def _log_decision(self, decision: str):
        """Log brain's decision-making process"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision
        }
        self.decision_log.append(log_entry)
        
        # Also log to Streamlit sidebar if available
        try:
            st.info(f"🧠 **Brain**: {decision}")
        except:
            pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current status of all system components"""
        return {
            "session_id": self.session_id,
            "active_agents": {name: agent.get_status() for name, agent in self.active_agents.items()},
            "available_agents": list(self.available_agents.keys()),
            "decision_count": len(self.decision_log),
            "last_decision": self.decision_log[-1] if self.decision_log else None
        }