# 🚨 LifeAI Emergency Response Assistant

An AI-powered emergency response system that provides real-time medical guidance and coordinates emergency services using AWS technologies.

## 🚀 Features

- **🤖 AI-Powered Analysis** - Uses Amazon Bedrock for intelligent emergency assessment
- **📱 SMS Emergency Alerts** - Real SMS notifications via AWS SNS
- **🫁 Medical Guidance** - Step-by-step CPR, choking, and first aid instructions
- **🧠 Agentic AI System** - Multiple AI agents coordinate emergency response
- **📊 Real-time Monitoring** - Live incident tracking with DynamoDB

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Amazon Bedrock (Claude 3)
- **Database**: Amazon DynamoDB
- **Storage**: Amazon S3
- **Messaging**: Amazon SNS
- **Voice**: Amazon Transcribe (planned)

## 🚨 Emergency Response Types

- **💔 Cardiac Emergencies** - CPR guidance with proper technique
- **🫁 Choking** - Heimlich maneuver instructions
- **🩸 Bleeding Control** - Pressure techniques and wound care
- **💊 Heart Attack** - Recognition and response protocols
- **🤕 General Emergencies** - Safety and first aid basics

## 🎯 How It Works

1. **Emergency Detection** - User describes emergency via text or voice
2. **AI Analysis** - Bedrock analyzes situation and determines response
3. **Agent Coordination** - Multiple AI agents execute response plan
4. **Real-time Guidance** - Provides step-by-step medical instructions
5. **Emergency Alerts** - Sends SMS notifications to emergency contacts

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials

# Run the application
streamlit run main.py
```

## 📱 Demo

Try the live demo: [LifeAI Emergency Assistant](https://your-app-url.streamlit.app)

## ⚠️ Important Notice

This is a demonstration system. In real emergencies:
- **Call 911 immediately** for life-threatening situations
- Use this system as **supplementary guidance only**
- Always follow professional medical advice

## 🏗️ Architecture

```
User Input → Streamlit UI → Emergency Orchestrator → AI Agents
                                    ↓
AWS Bedrock ← Planning Agent ← Emergency Analysis
                                    ↓
SMS Alerts ← Communication Agent ← Response Coordination
                                    ↓
DynamoDB ← Monitoring Agent ← Incident Logging
```

## 📄 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ for emergency response and public safety**