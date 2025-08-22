import streamlit as st
import boto3
import json
from datetime import datetime
import uuid
import io
from orchestrator import EmergencyOrchestrator
import os
try:
    # Try Streamlit secrets first (for deployment)
    import streamlit as st
    if hasattr(st, 'secrets'):
        os.environ.update(st.secrets.get('secrets', {}))
except:
    pass

from config import (
    get_aws_region, get_bucket_name, get_table_name, 
    get_bedrock_model, display_config_status, Config
)

# Configure Streamlit page
st.set_page_config(
    page_title="LifeAI - Emergency Assistant",
    page_icon="🚨",
    layout="wide"
)

# Initialize AWS clients
@st.cache_resource
def init_aws_clients():
    """Initialize AWS service clients"""
    try:
        # Initialize AWS clients using configuration
        region = get_aws_region()
        bedrock = boto3.client('bedrock-runtime', region_name=region)
        dynamodb = boto3.resource('dynamodb', region_name=region)
        s3 = boto3.client('s3', region_name=region)
        
        return bedrock, dynamodb, s3
    except Exception as e:
        st.error(f"AWS Connection Error: {e}")
        return None, None, None

# Test AWS connections
def test_aws_connections():
    """Test all AWS service connections"""
    bedrock, dynamodb, s3 = init_aws_clients()
    
    if not all([bedrock, dynamodb, s3]):
        return False
    
    try:
        # Test DynamoDB
        table = dynamodb.Table(get_table_name())
        table.load()
        
        # Test S3
        bucket_name = get_bucket_name()
        s3.head_bucket(Bucket=bucket_name)
        
        return True
    except Exception as e:
        st.error(f"Connection test failed: {e}")
        return False

# Main app
def main():
    # Title and header
    st.title("🚨 LifeAI - Emergency Response Assistant")
    st.markdown("**Intelligent AI-powered emergency response system**")
    
    # Sidebar for system status
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Display configuration status
        display_config_status()
        
        # Test AWS connections
        if st.button("Test AWS Connection"):
            with st.spinner("Testing connections..."):
                if test_aws_connections():
                    st.success("✅ All AWS services connected")
                else:
                    st.error("❌ Connection failed")
        
        # System info with dynamic values
        st.info(f"**Services:**\n- DynamoDB: {get_table_name()}\n- S3: {get_bucket_name()}\n- Bedrock: AI Analysis")
    
    # Main interface - always show emergency input
    st.session_state.emergency_active = True  # Always active for real emergencies
    
    # Emergency interface - always active
    if st.session_state.get('emergency_active', False):
        st.error("🚨 EMERGENCY RESPONSE SYSTEM - GET HELP NOW")
        
        # Main emergency input
        st.markdown("### 📝 **Describe the Emergency**")
        
        # Large text input for emergency description
        emergency_description = st.text_area(
            "What's happening?",
            placeholder="Type quickly: Person collapsed, choking, bleeding, chest pain, etc.",
            height=120,
            help="Describe the emergency in simple words - the AI will understand and provide specific help"
        )
        
        # Quick emergency buttons for faster input
        st.markdown("### ⚡ **Or Click for Common Emergencies:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💔 **NOT BREATHING**", use_container_width=True):
                st.session_state.emergency_processed = True
                st.session_state.emergency_description = "Person collapsed and is not breathing"
                st.rerun()
            
            if st.button("🩸 **CHOKING**", use_container_width=True):
                st.session_state.emergency_processed = True
                st.session_state.emergency_description = "Someone is choking on food"
                st.rerun()
        
        with col2:
            if st.button("🩸 **BLEEDING**", use_container_width=True):
                st.session_state.emergency_processed = True
                st.session_state.emergency_description = "Severe bleeding from deep cut"
                st.rerun()
            
            if st.button("💔 **CHEST PAIN**", use_container_width=True):
                st.session_state.emergency_processed = True
                st.session_state.emergency_description = "Person having chest pain"
                st.rerun()
        
        with col3:
            if st.button("🤕 **UNCONSCIOUS**", use_container_width=True):
                st.session_state.emergency_processed = True
                st.session_state.emergency_description = "Person fell and can't move"
                st.rerun()
            
            if st.button("😵 **ALLERGIC REACTION**", use_container_width=True):
                st.session_state.emergency_processed = True
                st.session_state.emergency_description = "Allergic reaction, difficulty breathing"
                st.rerun()
        
        # Main analyze button
        if emergency_description:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚨 **GET EMERGENCY HELP NOW**", type="primary", use_container_width=True):
                    st.session_state.emergency_processed = True
                    st.session_state.emergency_description = emergency_description
                    st.rerun()
        
        # Show emergency response if processed
        if st.session_state.get('emergency_processed', False):
            description = st.session_state.get('emergency_description', '')
            if description:
                handle_text_emergency(description)
    
    # Always show help information
    with st.expander("📞 **Emergency Hotline Information**", expanded=False):
        st.error("📱 **SMS EMERGENCY ALERTS:**")
        st.markdown("""
        - **Medical Emergencies** - CPR guidance, first aid
        - **Emergency Coordination** - Connect with local 911
        - **Real-time Support** - Stay on line during emergency
        - **Multi-language Support** - Available 24/7
        """)
        st.info("📱 **What to Say:** Location, emergency type, number of people, your phone number")
        st.success("✨ **AI-Powered:** Our system provides intelligent emergency response and coordinates with local services")



def handle_text_emergency(description):
    """Handle text input and provide immediate emergency response"""
    
    # Background processing in collapsible sidebar
    with st.sidebar:
        with st.expander("🔧 AI Brain Processing", expanded=False):
            orchestrator = EmergencyOrchestrator()
            
            try:
                response = orchestrator.process_emergency(description)
                st.success("✅ Emergency analysis complete")
                
                # Show brain decisions
                if response.get("decision_log"):
                    st.markdown("**Brain Decisions:**")
                    for decision in response["decision_log"][-3:]:  # Show last 3 decisions
                        st.text(f"• {decision['decision']}")
                        
            except Exception as e:
                st.error(f"⚠️ Brain processing error: {e}")
    
    # Main response - clean and actionable
    get_emergency_response(description)

def create_simulated_audio():
    """Create simulated audio data for demo purposes"""
    # In real implementation, this would capture actual microphone input
    # For demo, return empty bytes (orchestrator will use fallback transcript)
    return b"simulated_audio_data"

def analyze_emergency(description):
    """Analyze emergency using AWS Bedrock"""
    bedrock, dynamodb, s3 = init_aws_clients()
    
    if not bedrock:
        st.error("AWS Bedrock not available")
        return
    
    with st.spinner("🤖 AI analyzing emergency..."):
        try:
            # Create prompt for emergency analysis
            prompt = f"""
            Analyze this emergency situation and provide a JSON response with:
            1. emergency_type: (cardiac, choking, bleeding, burn, fracture, other)
            2. severity: (1-10 scale)
            3. immediate_action: (true/false)
            4. call_911: (true/false)
            5. summary: (brief description)
            
            Emergency: {description}
            
            Respond only with valid JSON.
            """
            
            # Call Bedrock using configured model
            response = bedrock.invoke_model(
                modelId=get_bedrock_model(),
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 300,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            # Parse response
            result = json.loads(response['body'].read())
            ai_response = result['content'][0]['text']
            
            # Try to parse JSON from AI response
            try:
                analysis = json.loads(ai_response)
            except:
                # Fallback if JSON parsing fails
                analysis = {
                    "emergency_type": "unknown",
                    "severity": 5,
                    "immediate_action": True,
                    "call_911": True,
                    "summary": "Emergency detected, seek immediate help"
                }
            
            # Display results
            display_analysis_results(analysis, description)
            
            # Store in DynamoDB
            store_incident(description, analysis)
            
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            # Show fallback emergency response
            st.warning("⚠️ AI analysis unavailable. Default emergency protocol activated.")
            st.markdown("**IMMEDIATE ACTIONS:**\n1. Call 911\n2. Check if person is responsive\n3. Check breathing\n4. Begin CPR if needed")

def display_analysis_results(analysis, description):
    """Display AI analysis results"""
    st.success("🤖 Emergency Analysis Complete")
    
    # Create columns for results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Emergency Type", analysis.get('emergency_type', 'Unknown').title())
    
    with col2:
        severity = analysis.get('severity', 5)
        st.metric("Severity Level", f"{severity}/10")
    
    with col3:
        if analysis.get('call_911', True):
            st.error("🚨 CALL 911 NOW")
        else:
            st.info("📞 Monitor Situation")
    
    # Summary
    st.markdown(f"**AI Summary:** {analysis.get('summary', 'Emergency situation detected')}")
    
    # Next actions
    if analysis.get('immediate_action', True):
        st.warning("⚡ IMMEDIATE ACTION REQUIRED")
        st.markdown("**Next Steps:**\n1. Ensure scene safety\n2. Check responsiveness\n3. Call for help\n4. Follow first aid protocols")

def store_incident(description, analysis):
    """Store incident in DynamoDB"""
    try:
        _, dynamodb, _ = init_aws_clients()
        table = dynamodb.Table('EmergencyIncidents')
        
        incident_id = str(uuid.uuid4())
        
        table.put_item(
            Item={
                'incident_id': incident_id,
                'timestamp': datetime.now().isoformat(),
                'description': description,
                'analysis': analysis,
                'status': 'active'
            }
        )
        
        st.success(f"✅ Incident logged: {incident_id[:8]}...")
        
    except Exception as e:
        st.warning(f"Logging failed: {e}")

def get_emergency_response(description):
    """Get clean, actionable emergency response"""
    
    # Determine emergency type
    emergency_type = classify_emergency(description.lower())
    
    # Emergency hotline button - prominent placement
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📱 SEND EMERGENCY SMS", type="primary", use_container_width=True):
            # Import and show SMS emergency interface
            from sms_emergency import show_sms_emergency_interface
            
            emergency_data = {
                'emergency_type': classify_emergency(description.lower()),
                'description': description,
                'severity': 8,
                'life_threatening': True
            }
            
            show_sms_emergency_interface(emergency_data)
    
    # Add reset button
    if st.button("🔄 Start Over", help="Clear emergency and start over"):
        st.session_state.emergency_processed = False
        st.session_state.emergency_description = ""
        st.rerun()
    
    st.markdown("---")
    
    # Emergency-specific instructions
    if "not breathing" in description.lower() or "collapsed" in description.lower():
        show_cpr_instructions()
    elif "choking" in description.lower():
        show_choking_instructions()
    elif "bleeding" in description.lower():
        show_bleeding_instructions()
    elif "chest pain" in description.lower():
        show_heart_attack_instructions()
    else:
        show_general_emergency_instructions()

def classify_emergency(description):
    """Simple emergency classification"""
    if any(word in description for word in ["not breathing", "collapsed", "unconscious"]):
        return "cardiac"
    elif "choking" in description:
        return "choking"
    elif "bleeding" in description:
        return "bleeding"
    elif "chest pain" in description:
        return "heart_attack"
    else:
        return "general"

def show_cpr_instructions():
    """Show detailed CPR steps"""
    st.error("🚨 **CARDIAC EMERGENCY - CPR REQUIRED**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⚡ IMMEDIATE STEPS:**")
        st.markdown("""
        1. **Check responsiveness**: Tap shoulders, shout "Are you okay?"
        2. **Check pulse**: 2 fingers on neck, 10 seconds max
        3. **If no pulse**: Start CPR immediately
        """)
    
    with col2:
        st.markdown("**💓 CPR TECHNIQUE:**")
        st.markdown("""
        1. **Hand position**: Center of chest, between nipples
        2. **Compressions**: Push hard, push fast, 2 inches deep
        3. **Rate**: 100-120 per minute (think "Stayin' Alive")
        4. **Ratio**: 30 compressions, 2 breaths, repeat
        """)
    
    st.warning("⚠️ **Don't stop CPR until help arrives or person starts breathing**")

def show_choking_instructions():
    """Show choking response steps"""
    st.error("🚨 **CHOKING EMERGENCY**")
    
    st.markdown("**⚡ IMMEDIATE STEPS:**")
    st.markdown("""
    1. **Ask**: "Are you choking?" If they can't speak/cough:
    2. **Back blows**: 5 sharp blows between shoulder blades
    3. **Abdominal thrusts**: 5 upward thrusts below ribcage
    4. **Repeat**: Back blows, then abdominal thrusts
    5. **If unconscious**: Start CPR
    """)
    
    st.info("📍 **Hand position for thrusts**: Just above navel, below ribcage")

def show_bleeding_instructions():
    """Show bleeding control steps"""
    st.error("🚨 **SEVERE BLEEDING**")
    
    st.markdown("**⚡ IMMEDIATE STEPS:**")
    st.markdown("""
    1. **Direct pressure**: Press firmly on wound with cloth/gauze
    2. **Elevate**: Raise injured area above heart if possible
    3. **Don't remove**: If object in wound, stabilize it, don't pull out
    4. **Pressure points**: If bleeding continues, press artery above wound
    """)
    
    st.warning("⚠️ **Watch for shock**: Pale, cold, weak pulse, rapid breathing")

def show_heart_attack_instructions():
    """Show heart attack response"""
    st.error("🚨 **POSSIBLE HEART ATTACK**")
    
    st.markdown("**⚡ IMMEDIATE STEPS:**")
    st.markdown("""
    1. **Sit them down**: Keep calm, loosen tight clothing
    2. **Aspirin**: Give 1 adult aspirin if not allergic (chew, don't swallow)
    3. **Monitor**: Watch breathing and consciousness
    4. **Be ready**: Prepare for CPR if they become unconscious
    """)
    
    st.info("📍 **Signs**: Chest pain, shortness of breath, nausea, sweating")

def show_general_emergency_instructions():
    """Show general emergency response"""
    st.warning("⚠️ **EMERGENCY RESPONSE**")
    
    st.markdown("**⚡ IMMEDIATE STEPS:**")
    st.markdown("""
    1. **Scene safety**: Make sure area is safe before helping
    2. **Check responsiveness**: Tap and shout to get response
    3. **Check breathing**: Look, listen, feel for 10 seconds
    4. **Recovery position**: If breathing but unconscious, turn on side
    """)

def record_audio():
    """Record audio from microphone (for future implementation)"""
    pass

if __name__ == "__main__":
    main()