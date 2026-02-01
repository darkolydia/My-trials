# Database Integration Guide

## Overview

The voice assistant system now includes SQLite database integration for logging calls, conversations, and tracking statistics.

## Database Schema

### Tables

1. **calls** - Stores call session information
   - `call_id` (PRIMARY KEY)
   - `caller_id` - SIP caller ID
   - `extension` - Extension number called
   - `start_time` - Call start timestamp
   - `end_time` - Call end timestamp
   - `status` - Call status (active, completed, failed)
   - `duration_seconds` - Call duration
   - `audio_file_path` - Path to recorded question audio
   - `response_file_path` - Path to generated response audio
   - `created_at` - Record creation timestamp

2. **conversations** - Stores question-answer pairs
   - `conversation_id` (PRIMARY KEY)
   - `call_id` (FOREIGN KEY) - Links to calls table
   - `question_text` - Transcribed question
   - `answer_text` - Generated answer
   - `question_audio_path` - Path to question audio file
   - `answer_audio_path` - Path to answer audio file
   - `stt_processing_time` - STT processing time (seconds)
   - `tts_processing_time` - TTS processing time (seconds)
   - `total_processing_time` - Total processing time (seconds)
   - `language` - Language code (default: 'tw')
   - `created_at` - Record creation timestamp

3. **statistics** - Daily statistics (for future use)
   - `stat_id` (PRIMARY KEY)
   - `date` - Date of statistics
   - `total_calls` - Total calls for the date
   - `total_conversations` - Total conversations
   - `avg_processing_time` - Average processing time
   - `successful_calls` - Number of successful calls
   - `failed_calls` - Number of failed calls

## Usage

### Automatic Logging

The database is automatically used when `voice_assistant.py` is called. Each call creates:
1. A call record when processing starts
2. A conversation record when processing completes
3. Updates to call record when processing finishes

### Manual Database Operations

#### View Recent Calls
```bash
python view_database.py --list 10
```

#### View Specific Call
```bash
python view_database.py --call 1
```

#### View Statistics
```bash
python view_database.py --stats
python view_database.py --stats --date 2024-01-15
```

### Database Location

By default, the database is created as `voice_assistant.db` in the current working directory. You can specify a different path:

```python
from database import VoiceAssistantDB

db = VoiceAssistantDB("path/to/voice_assistant.db")
```

## Integration with FreeSWITCH

The database integration is transparent to FreeSWITCH. The existing dialplan configuration continues to work:

```xml
<action application="system" 
        data="python &quot;C:\Users\User\Desktop\FreeSWITCH-to-linphone\voice_assistant.py&quot; 
              &quot;C:\freeswitch_recordings\user_question.wav&quot; 
              -o &quot;C:\Program Files\FreeSWITCH\sounds\custom\response.wav&quot;"/>
```

The script automatically:
- Creates a call record
- Processes the audio
- Logs the conversation
- Updates the call status

### Optional: Pass Call Information

If you want to pass caller ID or call ID from FreeSWITCH, you can modify the dialplan:

```xml
<action application="set" data="caller_id=${caller_id_number}"/>
<action application="system" 
        data="python voice_assistant.py ${record_file} -o response.wav --caller-id ${caller_id}"/>
```

## Database Module API

### Creating a Call
```python
from database import VoiceAssistantDB

db = VoiceAssistantDB("voice_assistant.db")
call_id = db.create_call(
    caller_id="1000",
    extension="1002",
    audio_file_path="user_question.wav"
)
```

### Adding a Conversation
```python
conv_id = db.add_conversation(
    call_id=call_id,
    question_text="wo ho te sen",
    answer_text="Me ho ye. Meda wo ase.",
    question_audio_path="user_question.wav",
    answer_audio_path="response.wav",
    stt_processing_time=3.5,
    tts_processing_time=2.8,
    total_processing_time=6.3
)
```

### Updating a Call
```python
db.update_call(
    call_id=call_id,
    status="completed",
    duration_seconds=15,
    response_file_path="response.wav"
)
```

### Querying Data
```python
# Get call details
call = db.get_call(call_id)

# Get conversations for a call
conversations = db.get_call_conversations(call_id)

# Get recent calls
recent_calls = db.get_recent_calls(limit=10)

# Get statistics
stats = db.get_statistics(date="2024-01-15")
```

## Error Handling

The database integration is designed to be non-blocking:
- If database is unavailable, processing continues normally
- Database errors are logged as warnings
- The voice assistant continues to function even if database fails

## Backup and Maintenance

### Backup Database
```bash
# Simple copy
cp voice_assistant.db voice_assistant_backup.db

# Or use SQLite backup command
sqlite3 voice_assistant.db ".backup voice_assistant_backup.db"
```

### Database Size

The database will grow over time. Consider:
- Archiving old records periodically
- Implementing data retention policies
- Exporting data to CSV/JSON for analysis

### Example: Export to CSV
```python
import csv
from database import VoiceAssistantDB

db = VoiceAssistantDB("voice_assistant.db")
calls = db.get_recent_calls(limit=1000)

with open('calls_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=calls[0].keys())
    writer.writeheader()
    writer.writerows(calls)
```

## Performance Considerations

- SQLite is suitable for single-server deployments
- For high-volume systems, consider PostgreSQL or MySQL
- Indexes are created automatically for common queries
- Database operations are fast (<10ms typically)

## Future Enhancements

Potential improvements:
- User tracking and analytics
- Conversation history search
- Performance metrics dashboard
- Automated reporting
- Integration with external analytics tools
