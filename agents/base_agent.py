"""
Base Agent - Foundation for all emergency response agents
"""

import streamlit as st
from abc import ABC, abstractmethod
from datetime import datetime
from config import get_aws_region

class BaseAgent(ABC):
    """Abstract base class for all emergency agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.region = get_aws_region()
        self.status = "inactive"
        self.last_action = None
        self.created_at = datetime.now()
    
    @abstractmethod
    def execute(self, data: dict) -> dict:
        """Execute agent's primary function"""
        pass
    
    def log_action(self, message: str, action_type: str = "info"):
        """Log agent actions"""
        self.last_action = {
            "message": message,
            "type": action_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log to sidebar if in Streamlit context
        try:
            if action_type == "success":
                st.success(f"✅ **{self.agent_name}**: {message}")
            elif action_type == "error":
                st.error(f"❌ **{self.agent_name}**: {message}")
            elif action_type == "warning":
                st.warning(f"⚠️ **{self.agent_name}**: {message}")
            else:
                st.info(f"🤖 **{self.agent_name}**: {message}")
        except:
            # Not in Streamlit context, just store the action
            pass
    
    def get_status(self) -> dict:
        """Get current agent status"""
        return {
            "name": self.agent_name,
            "status": self.status,
            "last_action": self.last_action,
            "uptime": (datetime.now() - self.created_at).total_seconds()
        }