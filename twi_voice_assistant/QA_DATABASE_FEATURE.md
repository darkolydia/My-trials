# Q&A Database Feature

## Overview

The voice assistant uses **PostgreSQL and SQLite** as the database for questions and answers. When a caller asks a question, the system looks up the answer from the database (PostgreSQL first, then SQLite). This allows for:

- **Faster responses** - No need to process if answer exists
- **Consistent answers** - Same question gets same answer
- **Learning system** - Automatically stores new Q&A pairs
- **Usage tracking** - Tracks how often each Q&A is used

## How It Works

### Dual backend: PostgreSQL + SQLite

- **Lookup**: PostgreSQL first; if not found, SQLite. The caller gets the answer from the database.
- **Storage**: New or updated Q&A pairs are written to **both** PostgreSQL and SQLite (when Postgres is configured).
- **SQLite only**: If `DATABASE_URL` / `POSTGRES_URI` is not set, only SQLite is used.
- **Optional**: Install `psycopg2-binary` and set `DATABASE_URL` or `POSTGRES_URI` in `.env` to enable PostgreSQL.

### Automatic Flow

1. **User asks a question** → Transcribed to text
2. **System checks database** → Searches PostgreSQL, then SQLite
3. **If found** → Returns stored answer from the database
4. **If not found** → Uses keyword matching, then stores Q&A in both databases
5. **Future calls** → Same question uses stored answer from the database

### Database Schema

The `qa_pairs` table stores:
- `qa_id` - Unique identifier
- `question_text` - The question (normalized)
- `answer_text` - The answer
- `language` - Language code (default: 'tw')
- `usage_count` - How many times it's been used
- `last_used` - Timestamp of last usage
- `created_at` - When it was first created
- `updated_at` - When it was last updated

## Usage

### Automatic (During Calls)

The system automatically:
- Checks database when processing questions
- Stores new Q&A pairs after keyword matching
- Updates usage counts when Q&A pairs are used

### Manual Management

#### Add Q&A Pair
```bash
python manage_qa.py add "wo ho te sen" "Me ho ye. Meda wo ase sɛ wobu me. Wo ho te sɛn?" --language tw
```

#### List All Q&A Pairs
```bash
python manage_qa.py list
python manage_qa.py list --language tw --limit 50
```

#### View Specific Q&A
```bash
python manage_qa.py view 1
```

#### Update Q&A Pair
```bash
python manage_qa.py update 1 --answer "New answer text"
python manage_qa.py update 1 --question "New question" --answer "New answer"
```

#### Delete Q&A Pair
```bash
python manage_qa.py delete 1
```

#### Search Q&A Pairs
```bash
python manage_qa.py search "wo ho"
python manage_qa.py search "help" --language tw
```

#### View via Database Viewer
```bash
python view_database.py --qa
python view_database.py --qa --language tw --qa-limit 20
```

## Matching Algorithm

The system uses intelligent matching:

1. **Exact Match** (case-insensitive, trimmed)
   - "wo ho te sen" matches "wo ho te sen"

2. **Fuzzy Match** (substring matching)
   - "wo ho te sen" matches "wo ho te sen na wo?"
   - "how are you" matches "how are you doing today"

3. **Usage Tracking**
   - Each match increments usage count
   - Updates last_used timestamp

## Example Flow

### First Time Asking a Question

```
User: "wo ho te sen"
  ↓
System: Checks database → Not found
  ↓
System: Uses keyword matching → Finds answer
  ↓
System: Stores Q&A in database (qa_id=1, usage_count=0)
  ↓
System: Returns answer to user
```

### Second Time Asking Same Question

```
User: "wo ho te sen"
  ↓
System: Checks database → Found! (qa_id=1)
  ↓
System: Updates usage_count to 1, updates last_used
  ↓
System: Returns stored answer immediately
  ↓
(No keyword matching needed - faster!)
```

## Benefits

1. **Performance** - Faster responses for repeated questions
2. **Consistency** - Same question always gets same answer
3. **Learning** - System builds knowledge base automatically
4. **Analytics** - Track popular questions via usage_count
5. **Customization** - Admins can add/edit Q&A pairs manually

## Integration with Existing System

The Q&A database integrates seamlessly:

- **Backward Compatible** - Still uses keyword matching as fallback
- **Automatic Storage** - All processed Q&A pairs are stored
- **No Breaking Changes** - Existing functionality unchanged
- **Optional** - Works even if database is unavailable

## Database Location

Q&A pairs are stored in **both** PostgreSQL and SQLite:

- **SQLite**: `voice_assistant.db` (table `qa_pairs`), same file as calls/conversations
- **PostgreSQL**: When configured via `DATABASE_URL` or `POSTGRES_URI`, table `qa_pairs` is created automatically
- **Indexes**: Optimized for fast lookups in both backends

## PostgreSQL setup (optional)

1. Install the driver: `pip install psycopg2-binary`
2. In `.env`, set either:
   - `DATABASE_URL=postgresql://user:password@host:5432/dbname`
   - or `POSTGRES_URI=postgresql://user:password@host:5432/dbname`
3. The `qa_pairs` table is created automatically on first use.
4. Q&A is stored and read from both PostgreSQL and SQLite; callers receive answers from the database.

## Best Practices

1. **Review stored Q&A pairs** periodically
   ```bash
   python manage_qa.py list
   ```

2. **Update incorrect answers**
   ```bash
   python manage_qa.py update <qa_id> --answer "Correct answer"
   ```

3. **Delete outdated Q&A pairs**
   ```bash
   python manage_qa.py delete <qa_id>
   ```

4. **Search before adding** to avoid duplicates
   ```bash
   python manage_qa.py search "question text"
   ```

5. **Monitor usage** to identify popular questions
   ```bash
   python view_database.py --qa
   ```

## Future Enhancements

Potential improvements:
- **LLM Integration** - Generate answers using AI models
- **Confidence Scoring** - Rate answer quality
- **Multi-language Support** - Better language detection
- **Answer Variations** - Multiple answers per question
- **Context Awareness** - Consider conversation history
- **Export/Import** - Backup and share Q&A databases
