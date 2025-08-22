# 🚀 LifeAI Emergency Assistant - Setup Instructions

## 📋 **Quick Setup Guide**

### **Step 1: Install Required Packages**
```bash
pip install streamlit boto3 python-dotenv
```

### **Step 2: Configure Environment Variables**

1. **Copy the `.env` file** and update with your actual values:

```bash
# Required AWS Settings (UPDATE THESE!)
AWS_ACCESS_KEY_ID=your_actual_aws_access_key
AWS_SECRET_ACCESS_KEY=your_actual_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Required S3 Settings (UPDATE THESE!)
S3_BUCKET_NAME=your-actual-bucket-name
S3_AUDIO_BUCKET=your-actual-audio-bucket

# Required DynamoDB Settings (UPDATE THESE!)
DYNAMODB_TABLE_NAME=EmergencyIncidents
```

### **Step 3: Update Your Actual Values**

Replace these placeholders in `.env`:

```bash
# Replace this:
S3_BUCKET_NAME=your-emergency-protocols-bucket

# With your actual bucket name:
S3_BUCKET_NAME=emergency-protocols-anshita-2024
```

### **Step 4: Run the Application**
```bash
streamlit run main.py
```

---

## 🔧 **Configuration Management**

### **Environment Variables Loaded:**
- ✅ **AWS Credentials** - Secure authentication
- ✅ **S3 Bucket Names** - Document storage
- ✅ **DynamoDB Tables** - Incident tracking  
- ✅ **Bedrock Models** - AI configuration
- ✅ **Regional Settings** - Service locations

### **Configuration Files:**
- **`.env`** - Environment variables (NEVER commit!)
- **`config.py`** - Configuration management system
- **`.gitignore`** - Prevents sensitive files from being committed

### **Benefits:**
- 🔒 **Secure** - No hardcoded credentials
- 🔄 **Flexible** - Easy environment switching
- 📈 **Scalable** - Ready for production deployment
- 🛡️ **Safe** - Prevents accidental credential exposure

---

## 🎯 **What Each File Does:**

### **`.env`**
- Stores all sensitive configuration
- Never committed to version control
- Easy to update for different environments

### **`config.py`**
- Loads environment variables
- Provides centralized configuration access
- Validates configuration completeness
- Handles fallbacks and defaults

### **`.gitignore`**
- Prevents `.env` from being committed
- Protects AWS credentials
- Excludes temporary files

---

## ✅ **Verification Checklist:**

- [ ] `.env` file created with actual values
- [ ] AWS credentials configured
- [ ] S3 bucket name updated
- [ ] DynamoDB table name set
- [ ] Application runs without errors
- [ ] Configuration status shows green checkmarks

---

## 🚨 **Security Notes:**

### **NEVER commit these files:**
- `.env` (contains secrets)
- `aws-credentials.json`
- Any file with API keys

### **Always use:**
- Environment variables for secrets
- `.gitignore` to protect sensitive files
- Different `.env` files for different environments

---

## 🔄 **Environment Switching:**

### **Development:**
```bash
ENVIRONMENT=development
DEBUG_MODE=True
SIMULATE_EMERGENCY_CALLS=True
```

### **Production:**
```bash
ENVIRONMENT=production
DEBUG_MODE=False
SIMULATE_EMERGENCY_CALLS=False
```

---

**🎉 Your LifeAI Emergency Assistant is now securely configured and ready to save lives!**