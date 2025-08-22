"""
Transcription Agent - Converts voice to text using AWS Transcribe
"""

import boto3
import json
import time
import uuid
from .base_agent import BaseAgent
from config import get_bucket_name

class TranscriptionAgent(BaseAgent):
    """Converts audio to text using AWS Transcribe"""
    
    def __init__(self):
        super().__init__("Transcription Agent")
        self.transcribe = boto3.client('transcribe', region_name=self.region)
        self.s3 = boto3.client('s3', region_name=self.region)
        self.bucket_name = get_bucket_name()
        self.audio_folder = "audio/"
    
    def execute(self, data: dict) -> dict:
        """Convert audio to text"""
        audio_data = data.get('audio_data')
        audio_format = data.get('audio_format', 'wav')
        language_code = data.get('language_code', 'en-US')
        
        if not audio_data:
            return self._error_response("No audio data provided")
        
        self.log_action("Processing voice input...")
        
        try:
            # Upload audio to S3
            audio_key = self._upload_audio(audio_data, audio_format)
            
            # Convert WebM to WAV if needed
            if audio_format == 'webm':
                # For WebM files, AWS Transcribe expects them as-is
                audio_format = 'webm'
            
            # Start transcription job
            job_name = f"emergency-transcribe-{int(time.time())}"
            transcript = self._transcribe_audio(audio_key, job_name, language_code, audio_format)
            
            if transcript:
                self.log_action("Voice transcription complete", "success")
                return {
                    "success": True,
                    "transcript": transcript,
                    "language_detected": language_code,
                    "agent": self.agent_name
                }
            else:
                return self._error_response("Transcription failed")
                
        except Exception as e:
            self.log_action(f"Transcription error: {str(e)}", "error")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "fallback_transcript": "Emergency situation detected"
            }
    
    def _upload_audio(self, audio_data: bytes, audio_format: str) -> str:
        """Upload audio file to S3"""
        audio_key = f"{self.audio_folder}emergency-audio-{uuid.uuid4()}.{audio_format}"
        
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=audio_key,
            Body=audio_data,
            ContentType=f"audio/{audio_format}"
        )
        
        self.log_action(f"Audio uploaded to S3: {audio_key}")
        return audio_key
    
    def _transcribe_audio(self, audio_key: str, job_name: str, language_code: str, audio_format: str = 'wav') -> str:
        """Start transcription job and wait for completion"""
        
        # Start transcription job
        media_format = audio_format if audio_format in ['mp3', 'mp4', 'wav', 'flac'] else 'wav'
        
        self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{self.bucket_name}/{audio_key}'},
            MediaFormat=media_format,
            LanguageCode=language_code,
            Settings={
                'ShowSpeakerLabels': False,
                'MaxSpeakerLabels': 1,
                'ShowAlternatives': False
            }
        )
        
        self.log_action("Transcription job started, waiting for completion...")
        
        # Wait for completion
        max_wait = 60  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            response = self.transcribe.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            
            if status == 'COMPLETED':
                # Get transcript from results
                transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                return self._extract_transcript(transcript_uri)
                
            elif status == 'FAILED':
                failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown error')
                self.log_action(f"Transcription failed: {failure_reason}", "error")
                return None
            
            time.sleep(3)
            wait_time += 3
        
        self.log_action("Transcription timeout", "warning")
        return None
    
    def _extract_transcript(self, transcript_uri: str) -> str:
        """Extract transcript text from S3 results"""
        try:
            # Parse S3 URI to get bucket and key
            uri_parts = transcript_uri.replace('https://', '').split('/')
            result_bucket = uri_parts[0].split('.')[0]
            result_key = '/'.join(uri_parts[1:])
            
            # Get transcript file from S3
            response = self.s3.get_object(Bucket=result_bucket, Key=result_key)
            transcript_json = json.loads(response['Body'].read().decode('utf-8'))
            
            # Extract transcript text
            transcript_text = transcript_json['results']['transcripts'][0]['transcript']
            
            self.log_action(f"Transcript extracted: {transcript_text[:50]}...")
            return transcript_text
            
        except Exception as e:
            self.log_action(f"Failed to extract transcript: {str(e)}", "error")
            return None
    
    def _error_response(self, error_msg: str) -> dict:
        """Return error response"""
        self.log_action(error_msg, "error")
        return {
            "success": False,
            "error": error_msg,
            "agent": self.agent_name
        }