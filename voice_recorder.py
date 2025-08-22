"""
Simple Voice Recorder Component for Streamlit
Uses JavaScript MediaRecorder API for reliable microphone access
"""

import streamlit as st
import base64
from typing import Optional
import streamlit.components.v1 as components

def create_voice_recorder_js():
    """Create JavaScript-based voice recorder"""
    
    recorder_html = """
    <div id="voice-recorder">
        <style>
            .recorder-container {
                text-align: center;
                padding: 20px;
                border: 2px solid #ff4b4b;
                border-radius: 10px;
                background-color: #f0f2f6;
                margin: 10px 0;
            }
            .record-btn {
                background-color: #ff4b4b;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                border-radius: 50px;
                cursor: pointer;
                margin: 10px;
                transition: all 0.3s;
            }
            .record-btn:hover {
                background-color: #ff6b6b;
                transform: scale(1.05);
            }
            .record-btn:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
                transform: none;
            }
            .stop-btn {
                background-color: #28a745;
            }
            .stop-btn:hover {
                background-color: #34ce57;
            }
            .status {
                font-size: 16px;
                margin: 10px 0;
                font-weight: bold;
            }
            .recording {
                color: #ff4b4b;
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.3; }
            }
            .ready {
                color: #28a745;
            }
            .error {
                color: #dc3545;
            }
        </style>
        
        <div class="recorder-container">
            <div id="status" class="status ready">🎤 Ready to Record</div>
            <button id="startBtn" class="record-btn">🔴 START RECORDING</button>
            <button id="stopBtn" class="record-btn stop-btn" disabled>⏹️ STOP RECORDING</button>
            <div id="audioPlayback"></div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const status = document.getElementById('status');
        const audioPlayback = document.getElementById('audioPlayback');
        
        // Request microphone access
        async function initRecorder() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        sampleRate: 44100
                    } 
                });
                
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    
                    // Create audio player
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = audioUrl;
                    audio.style.marginTop = '10px';
                    
                    audioPlayback.innerHTML = '';
                    audioPlayback.appendChild(audio);
                    
                    // Convert to base64 and send to Streamlit
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        window.parent.postMessage({
                            type: 'audio_recorded',
                            data: base64Audio
                        }, '*');
                    };
                    reader.readAsDataURL(audioBlob);
                    
                    status.textContent = '✅ Recording Complete - Audio Ready!';
                    status.className = 'status ready';
                };
                
                status.textContent = '🎤 Microphone Ready - Click START to record';
                status.className = 'status ready';
                
            } catch (err) {
                console.error('Microphone access denied:', err);
                status.textContent = '❌ Microphone access denied. Please allow microphone access and refresh.';
                status.className = 'status error';
                startBtn.disabled = true;
            }
        }
        
        startBtn.addEventListener('click', () => {
            if (!mediaRecorder) {
                initRecorder().then(() => {
                    if (mediaRecorder) {
                        startRecording();
                    }
                });
            } else {
                startRecording();
            }
        });
        
        stopBtn.addEventListener('click', () => {
            if (isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                startBtn.disabled = false;
                stopBtn.disabled = true;
                status.textContent = '⏹️ Processing recording...';
                status.className = 'status';
            }
        });
        
        function startRecording() {
            audioChunks = [];
            audioPlayback.innerHTML = '';
            mediaRecorder.start();
            isRecording = true;
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = '🔴 RECORDING - Speak clearly about the emergency';
            status.className = 'status recording';
        }
        
        // Initialize on load
        initRecorder();
    </script>
    """
    
    return recorder_html

def create_microphone_recorder() -> Optional[bytes]:
    """Create JavaScript-based microphone recorder"""
    
    st.markdown("### 🎤 Direct Microphone Recording")
    st.info("🎙️ Click START to record directly from your microphone")
    
    # Simple file uploader as fallback for now
    st.markdown("**For now, please use file upload method:**")
    
    uploaded_file = st.file_uploader(
        "Upload recorded audio file",
        type=['wav', 'mp3', 'm4a', 'ogg', 'webm'],
        help="Record audio on your device, then upload it here"
    )
    
    if uploaded_file is not None:
        st.success("✅ Audio file uploaded successfully!")
        
        # Show audio player for confirmation
        st.audio(uploaded_file)
        
        # Get file bytes
        audio_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset for potential re-use
        
        return audio_bytes
    
    # Instructions for recording
    with st.expander("📝 How to record audio", expanded=False):
        st.markdown("""
        **Quick Recording Methods:**
        
        **Phone (Easiest):**
        1. Open Voice Recorder app
        2. Record: "Help! Person collapsed and not breathing!"
        3. Save and upload file
        
        **Windows Computer:**
        1. Search "Voice Recorder" in Start Menu
        2. Click record, speak emergency
        3. Save and upload
        
        **Online Recorder:**
        1. Go to: https://online-voice-recorder.com
        2. Allow microphone, record emergency
        3. Download and upload file
        """)
    
    return None

def create_enhanced_voice_tab():
    """Create enhanced voice input tab with direct microphone access"""
    
    st.markdown("### 🎤 Voice Emergency Report")
    
    # Create tabs within the voice section
    voice_tab1, voice_tab2 = st.tabs(["🎙️ Record Live", "⚡ Quick Select"])
    
    with voice_tab1:
        st.info("🎤 Record audio on your device, then upload it here")
        
        # Audio file upload
        audio_data = create_microphone_recorder()
        
        if audio_data:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🤖 PROCESS VOICE EMERGENCY", type="primary", use_container_width=True):
                    transcript = process_voice_input(audio_data)
                    if transcript:
                        return transcript
    
    with voice_tab2:
        st.info("⚡ Select a common emergency scenario for instant processing")
        
        # Quick selection options
        voice_scenario = st.selectbox(
            "Select Emergency Scenario:",
            [
                "Person collapsed and is not breathing",
                "Someone is choking on food", 
                "Severe bleeding from deep cut",
                "Person having chest pain",
                "Someone fell and can't move",
                "Allergic reaction - difficulty breathing",
                "Burn injury from fire/heat",
                "Possible stroke - slurred speech",
                "Diabetic emergency - unconscious"
            ]
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚨 PROCESS SELECTED EMERGENCY", type="primary", use_container_width=True):
                return voice_scenario
    
    return None

def process_voice_input(audio_data: bytes) -> str:
    """Process voice input through transcription agent"""
    
    with st.spinner("🎤 Converting voice to text..."):
        try:
            # Import here to avoid circular imports
            from agents.transcription_agent import TranscriptionAgent
            
            # Create transcription agent
            transcription_agent = TranscriptionAgent()
            
            # Process audio (WebM format from JavaScript)
            result = transcription_agent.execute({
                'audio_data': audio_data,
                'audio_format': 'webm',
                'language_code': 'en-US'
            })
            
            if result['success']:
                transcript = result['transcript']
                st.success(f"🎤 Voice converted: '{transcript}'")
                return transcript
            else:
                # Use fallback if transcription fails
                fallback = result.get('fallback_transcript', 'Emergency situation detected')
                st.warning(f"⚠️ Voice processing failed, using fallback: '{fallback}'")
                return fallback
                
        except Exception as e:
            st.error(f"❌ Voice processing error: {str(e)}")
            return "Emergency situation detected"

# Add JavaScript message listener
def add_message_listener():
    """Add JavaScript message listener for audio data"""
    
    listener_js = """
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'audio_recorded') {
                // Send audio data to Streamlit
                window.parent.postMessage({
                    type: 'streamlit_audio',
                    data: event.data.data
                }, '*');
            }
        });
    </script>
    """
    
    components.html(listener_js, height=0)