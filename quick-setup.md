# 🚀 **LifeAI - Quick Setup Guide (Single Bucket)**

## ⚡ **1-Minute Setup**

### **Step 1: Install Packages**
```bash
pip install streamlit boto3 python-dotenv
```

### **Step 2: Update .env File**
Replace these values in `.env`:

```bash
# Your actual S3 bucket name (SAME bucket for everything)
S3_BUCKET_NAME=emergency-lifeai-anshita-2024

# Your DynamoDB table name  
DYNAMODB_TABLE_NAME=EmergencyIncidents
```

### **Step 3: Create S3 Bucket Structure**
Create **ONE bucket** with these folders:

```
emergency-lifeai-anshita-2024/
├── documents/          # Upload your protocol files here
├── audio/             # Auto-created for voice processing  
└── logs/              # Auto-created for system logs
```

### **Step 4: Upload Documents**
Upload your emergency protocol files to `documents/` folder:
- `cardiac-emergency-protocols.txt`
- `trauma-bleeding-protocols.txt` 
- `medical-emergency-protocols.txt`
- `neurological-emergency-protocols.txt`

### **Step 5: Run Application**
```bash
streamlit run main.py
```

---

## ✅ **Single Bucket Benefits**

### **Simplified Architecture:**
```
ONE BUCKET = emergency-lifeai-anshita-2024
├── documents/    → First-aid protocols (AI reads these)
├── audio/        → Voice recordings (temporary)
└── logs/         → System logs (monitoring)
```

### **Easy Management:**
- ✅ **One bucket to create**
- ✅ **One bucket to manage** 
- ✅ **One bucket to secure**
- ✅ **One bucket to monitor**

### **Cost Effective:**
- ✅ **No cross-bucket charges**
- ✅ **Unified storage pricing**
- ✅ **Single backup strategy**

---

## 🎯 **Verification Checklist**

- [ ] `.env` updated with actual bucket name
- [ ] S3 bucket created: `emergency-lifeai-anshita-2024`
- [ ] Documents uploaded to `documents/` folder
- [ ] DynamoDB table created: `EmergencyIncidents`
- [ ] App runs: `streamlit run main.py`
- [ ] Configuration status shows ✅ green checkmarks

---

## 🔧 **Folder Structure Explained**

### **documents/** 
- **Purpose**: AI knowledge base
- **Content**: Emergency protocol text files
- **Access**: Read-only by AI agents

### **audio/**
- **Purpose**: Voice processing
- **Content**: Temporary audio files (.wav)
- **Access**: Read-write for transcription
- **Cleanup**: Auto-delete after processing

### **logs/**
- **Purpose**: System monitoring  
- **Content**: Incident logs, system events
- **Access**: Write-only for logging
- **Retention**: Configurable cleanup

---

**🎉 Your LifeAI Emergency Assistant is ready with simplified single-bucket architecture!**