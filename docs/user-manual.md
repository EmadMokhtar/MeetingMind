# MeetingMind User Manual

Welcome to MeetingMind! This manual will help you get the most out of your AI-powered meeting transcript analyzer.

---

## 1. Introduction

### 1.1 What is MeetingMind?

MeetingMind is an intelligent tool that automatically transforms your meeting transcripts into actionable insights using advanced AI technology. Instead of spending hours reviewing meeting notes and extracting important information manually, MeetingMind does it for you in minutes.

Whether you're a busy manager juggling multiple teams, a project coordinator tracking action items across projects, or a professional who attends many meetings each week, MeetingMind helps you stay organized and never miss important follow-ups. Simply provide your meeting transcripts, and MeetingMind generates comprehensive analyses including summaries, action items, decisions made, and strategic insights.

MeetingMind runs continuously on your computer, watching a folder for new transcript files. When you drop a transcript into the folder, it's automatically processed and a beautifully formatted analysis document appears in your output folder—no manual intervention needed.

### 1.2 What You Get

Every transcript you process with MeetingMind generates a comprehensive analysis with these seven sections:

1. **📋 Summary** - A concise overview of the meeting with key topics discussed
2. **✅ Action Points** - Prioritized tasks with assigned owners, deadlines, and priority levels
3. **📝 Todo List** - Additional tasks and follow-up items that need attention
4. **👥 Important Mentions** - Key people, companies, or entities mentioned with context about why they're significant
5. **🔄 Recap** - Meeting highlights, decisions made, and next steps in an easy-to-scan format
6. **🎭 Meeting Tone** - Analysis of sentiment, energy level, and collaboration quality
7. **💡 Key Insights** - Strategic insights, patterns observed, and actionable recommendations

Each section is formatted in beautiful markdown, making it easy to read, share with your team, or import into your project management tools.

### 1.3 What You Need

To use MeetingMind, you'll need:

- **Python 3.11 or newer** - The programming language MeetingMind is built with (free download from python.org)
- **An OpenAI or Anthropic API key** - This gives MeetingMind access to AI models that analyze your transcripts (costs around $0.10-$0.50 per typical meeting)
- **Meeting transcripts** - Text files (`.txt` or `.md`) containing your meeting conversations

That's it! No complicated setup, no server infrastructure, and no monthly subscription fees—just pay for the AI usage as you go.

---

## 2. Quick Start

Get your first transcript analyzed in under 5 minutes:

### Step 1: Check Your Python Version

Open your terminal (or Command Prompt on Windows) and run:

```bash
python3 --version
```

**Expected output:**
```
Python 3.11.5
```

If you see version 3.11 or higher, you're good to go! If not, download and install Python 3.11+ from [python.org](https://www.python.org/downloads/).

### Step 2: Install MeetingMind

Clone or download MeetingMind and install dependencies:

```bash
# Navigate to where you want MeetingMind
cd ~/Projects

# Clone the repository
git clone https://github.com/your-org/MeetingMind.git
cd MeetingMind

# Install using Make (recommended)
make install
```

**Expected output:**
```
uv sync
Resolved 45 packages in 1.2s
Installed 45 packages in 850ms
```

### Step 3: Get Your API Key

1. Go to [OpenAI's platform](https://platform.openai.com/api-keys) (or [Anthropic](https://console.anthropic.com/) if using Claude)
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (it looks like `sk-proj-abc123...`)

⚠️ **Important:** Keep this key secret! Never share it or commit it to version control.

### Step 4: Configure MeetingMind

Create a `.env` file in the MeetingMind folder:

```bash
# Copy the example file
cp .env.example .env

# Edit it with your favorite text editor
nano .env
```

Update the API key line:

```env
MEETINGMIND_API_KEY=sk-proj-your-actual-key-here
```

Save and close the file.

### Step 5: Process Your First Transcript

Create a transcripts folder and add a sample file:

```bash
# Create the input folder
mkdir transcripts

# Create a sample transcript
cat > transcripts/team-meeting.txt << 'EOF'
Alice: Good morning everyone! Let's review the Q4 roadmap.

Bob: We need to prioritize the mobile app redesign. Customer feedback shows our current UI is confusing for new users.

Alice: Agreed. Bob, can you lead that effort? Let's target end of November.

Bob: Yes, I'll put together a project plan by Friday.

Carol: What about the API documentation? We've had several support tickets about missing examples.

Alice: Good point. Carol, can you work with the dev team to update the docs? This should be high priority.

Carol: Absolutely. I'll have it done by October 15th.

Alice: Perfect. Any other urgent items?

Bob: Just a heads up—TechCorp mentioned they might want a custom integration. Could be a big deal.

Alice: Interesting. Let's schedule a follow-up meeting with TechCorp next week to discuss.
EOF

# Process it!
meetingmind process
```

**Expected output:**
```
Processing file: team-meeting.txt
✓ Analysis complete: outputs/team-meeting_20240315_143022.md

Processed 1 file(s)
```

### Step 6: View Your Results

Open the output file:

```bash
cat outputs/team-meeting_20240315_143022.md
```

You'll see a beautifully formatted analysis with action points for Bob and Carol, important mentions of TechCorp, meeting highlights, and more!

🎉 **Congratulations!** You've successfully processed your first transcript with MeetingMind.

---

## 3. Installation

### 3.1 Prerequisites

**Python 3.11 or Newer**

Check your version:

```bash
python3 --version
```

If you need to install or upgrade Python:
- **macOS**: Download from [python.org](https://www.python.org/downloads/) or use Homebrew: `brew install python@3.11`
- **Linux**: Use your package manager: `sudo apt install python3.11` (Ubuntu/Debian) or `sudo yum install python311` (RedHat/CentOS)
- **Windows**: Download the installer from [python.org](https://www.python.org/downloads/windows/)

**API Key**

You need an API key from either:
- **OpenAI** (for GPT-4, GPT-3.5-turbo, etc.): [Sign up here](https://platform.openai.com/signup)
- **Anthropic** (for Claude models): [Sign up here](https://console.anthropic.com/)

API keys cost money based on usage. A typical 30-minute meeting transcript costs $0.10-$0.50 to process depending on the model you choose.

**UV Package Manager (Optional)**

MeetingMind uses UV for fast dependency management. It's automatically installed when you run `make install`, but you can install it manually:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3.2 Install Steps

**Option 1: Using Make (Recommended)**

```bash
# Clone the repository
git clone https://github.com/your-org/MeetingMind.git
cd MeetingMind

# Install dependencies
make install
```

**Option 2: Using UV Directly**

```bash
# Clone the repository
git clone https://github.com/your-org/MeetingMind.git
cd MeetingMind

# Sync dependencies
uv sync
```

**Option 3: Using pip**

```bash
# Clone the repository
git clone https://github.com/your-org/MeetingMind.git
cd MeetingMind

# Install in development mode
pip install -e ".[dev]"
```

The installation creates a virtual environment and installs all required dependencies including Pydantic AI, Click (for the CLI), and other necessary libraries.

### 3.3 Verify Installation

Check that MeetingMind is installed correctly:

```bash
# Check version
meetingmind --version
```

**Expected output:**
```
meetingmind, version 0.1.0
```

View available commands:

```bash
# Show help
meetingmind --help
```

**Expected output:**
```
Usage: meetingmind [OPTIONS] COMMAND [ARGS]...

  MeetingMind - Intelligent transcript processor with AI-powered insights.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  process  Process all unprocessed transcript files once and exit.
  reset    Reset processing state (clear all history).
  status   Show processing status and statistics.
  watch    Watch a folder for new transcript files and process them...
```

If you see this, you're ready to go!

### 3.4 Common Installation Issues

**Issue 1: "Command not found: meetingmind"**

**Cause:** The virtual environment isn't activated, or the package wasn't installed correctly.

**Solution:**
```bash
# If using UV
uv sync

# Then run with uv prefix
uv run meetingmind --version

# Or activate the virtual environment
source .venv/bin/activate  # macOS/Linux
# or on Windows:
.venv\Scripts\activate.bat

# Now you can run directly
meetingmind --version
```

**Issue 2: "Python 3.11 or higher is required"**

**Cause:** Your system's default Python version is too old.

**Solution:**
- Install Python 3.11+ from python.org
- Use `python3.11` explicitly: `python3.11 -m pip install -e .`
- Or use UV which handles Python versions automatically

**Issue 3: "Permission denied" during installation**

**Cause:** You're trying to install to system Python without administrator privileges.

**Solution:**
```bash
# Don't use sudo! Use a virtual environment instead
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Or use `make install` which creates a virtual environment automatically.

**Issue 4: "No module named 'pydantic_ai'"**

**Cause:** Dependencies weren't installed properly.

**Solution:**
```bash
# Reinstall dependencies
make install

# Or manually
uv sync --all-extras
```

**Issue 5: "uv: command not found" when running make install**

**Cause:** UV isn't installed on your system.

**Solution:**
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload your shell
source ~/.bashrc  # or ~/.zshrc

# Try again
make install
```

---

## 4. Configuration

### 4.1 Your API Key (Most Important Step)

MeetingMind needs an API key to access AI models. Without it, processing will fail.

**Create Your .env File**

In the MeetingMind folder, create a file named `.env`:

```bash
# Copy the example file
cp .env.example .env

# Edit it
nano .env
```

**Add Your API Key**

The minimal `.env` file needs just one line:

```env
MEETINGMIND_API_KEY=sk-proj-your-actual-api-key-here
```

Replace `sk-proj-your-actual-api-key-here` with your real OpenAI API key (starts with `sk-`).

**For Anthropic/Claude Users:**

```env
MEETINGMIND_MODEL_PROVIDER=anthropic
MEETINGMIND_MODEL_NAME=claude-3-5-sonnet-latest
MEETINGMIND_API_KEY=sk-ant-your-anthropic-key-here
```

⚠️ **Security Warning**

Your API key is like a password—never:
- Commit the `.env` file to Git (it's already in `.gitignore`)
- Share it in Slack, email, or other communication tools
- Hard-code it in source files
- Upload it to public repositories

If you accidentally expose your key, delete it immediately from your API provider's dashboard and create a new one.

### 4.2 Configuration Options

All settings can be configured via environment variables in your `.env` file. Here's what each one does:

| What It Does | Setting | Default | Example |
|-------------|---------|---------|---------|
| Folder where transcripts are placed | `MEETINGMIND_INPUT_FOLDER` | `./transcripts` | `./my-meetings` |
| Folder where analyses are saved | `MEETINGMIND_OUTPUT_FOLDER` | `./outputs` | `./results` |
| Which file types to process | `MEETINGMIND_FILE_EXTENSIONS` | `.txt,.md` | `.txt` (text only) |
| How many files to process at once | `MEETINGMIND_MAX_CONCURRENT_FILES` | `3` | `5` (for faster processing) |
| Seconds between folder checks (watch mode) | `MEETINGMIND_POLL_INTERVAL_SECONDS` | `5.0` | `10.0` (check less often) |
| Seconds to wait before processing a file | `MEETINGMIND_STABILITY_CHECK_SECONDS` | `2.0` | `5.0` (for slow network drives) |
| Template for output filenames | `MEETINGMIND_FILENAME_TEMPLATE` | `{source_stem}_{timestamp}.md` | `analysis_{source_stem}.md` |
| Where processing history is stored | `MEETINGMIND_STATE_FILE` | `.meetingmind_state.json` | `.state/history.json` |
| Which AI provider to use | `MEETINGMIND_MODEL_PROVIDER` | `openai` | `anthropic` |
| Which AI model to use | `MEETINGMIND_MODEL_NAME` | `gpt-4` | `gpt-4-turbo-preview` or `claude-3-5-sonnet-latest` |
| Your API key | `MEETINGMIND_API_KEY` | *(none)* | `sk-proj-abc123...` |

**About Filename Templates**

The `MEETINGMIND_FILENAME_TEMPLATE` supports these placeholders:
- `{source_stem}` - Original filename without extension (e.g., `team-meeting`)
- `{timestamp}` - Current time in format `YYYYMMDD_HHMMSS` (e.g., `20240315_143022`)

Examples:
- `{source_stem}_{timestamp}.md` → `team-meeting_20240315_143022.md`
- `analysis-{source_stem}.md` → `analysis-team-meeting.md`
- `{timestamp}-{source_stem}.md` → `20240315_143022-team-meeting.md`

### 4.3 Complete .env Example

Here's a fully commented `.env` file you can copy and customize:

```env
# ================================================================
# MeetingMind Configuration
# ================================================================

# ------------------
# Folders
# ------------------

# Where to look for transcript files
MEETINGMIND_INPUT_FOLDER=./transcripts

# Where to save analysis markdown files
MEETINGMIND_OUTPUT_FOLDER=./outputs


# ------------------
# File Processing
# ------------------

# Which file extensions to process (comma-separated, include the dot)
MEETINGMIND_FILE_EXTENSIONS=.txt,.md

# Maximum number of files to process simultaneously (1-10)
# Higher = faster but uses more API quota and memory
MEETINGMIND_MAX_CONCURRENT_FILES=3

# How often to check for new files in watch mode (seconds)
# Lower = more responsive but uses more CPU
MEETINGMIND_POLL_INTERVAL_SECONDS=5.0

# How long to wait before processing a file to ensure it's fully written
# Increase this if files are on a slow network drive
MEETINGMIND_STABILITY_CHECK_SECONDS=2.0


# ------------------
# Output Settings
# ------------------

# Template for output filenames
# Placeholders: {source_stem} (original filename), {timestamp} (YYYYMMDD_HHMMSS)
MEETINGMIND_FILENAME_TEMPLATE={source_stem}_{timestamp}.md

# Where to store processing history (relative or absolute path)
MEETINGMIND_STATE_FILE=.meetingmind_state.json


# ------------------
# AI Model Settings
# ------------------

# Which AI provider to use: "openai" or "anthropic"
MEETINGMIND_MODEL_PROVIDER=openai

# Which model to use
# OpenAI options: gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo
# Anthropic options: claude-3-5-sonnet-latest, claude-3-opus-latest
MEETINGMIND_MODEL_NAME=gpt-4

# Your API key (keep this secret!)
# Get OpenAI keys at: https://platform.openai.com/api-keys
# Get Anthropic keys at: https://console.anthropic.com/
MEETINGMIND_API_KEY=sk-proj-your-actual-key-here
```

**Pro Tip:** Keep multiple `.env` files for different scenarios:
- `.env.openai` - Using OpenAI/GPT-4
- `.env.anthropic` - Using Anthropic/Claude
- `.env.production` - High concurrency for batch processing

Then copy the one you need: `cp .env.openai .env`

### 4.4 When to Change Defaults

**Increase `MAX_CONCURRENT_FILES` (to 5-8) when:**
- You have many transcripts to process at once
- You don't mind higher API costs
- Your computer has plenty of RAM (8GB+)
- You want faster batch processing

**Change `MODEL_NAME` when:**
- `gpt-4` → `gpt-4-turbo-preview` - You want faster, cheaper processing with similar quality
- `gpt-4` → `claude-3-5-sonnet-latest` - You want to try Anthropic's models
- `gpt-4` → `gpt-3.5-turbo` - You want much cheaper processing (but lower quality)

**Increase `POLL_INTERVAL_SECONDS` (to 10-30) when:**
- Running watch mode on a laptop to save battery
- Processing large files that take several minutes each
- You don't need immediate processing

**Increase `STABILITY_CHECK_SECONDS` (to 5-10) when:**
- Transcripts are saved to a network drive
- Your transcription tool writes files slowly
- You see "file not stable" warnings in the logs

**Customize `INPUT_FOLDER` and `OUTPUT_FOLDER` when:**
- Integrating with existing workflows
- Processing transcripts for different projects
- You want outputs in a shared drive for team access

---

## 5. Preparing Your Transcripts

### 5.1 Supported Formats

MeetingMind processes plain text files with these extensions:

✅ **Supported by default:**
- `.txt` - Plain text files
- `.md` - Markdown files

**What's inside doesn't matter** as long as it's readable text. MeetingMind handles:
- Speaker labels (Alice: Hello everyone)
- Timestamps (00:12:34)
- Paragraphs and line breaks
- Simple formatting

**Adding other extensions:**

Edit your `.env` file:

```env
# Process Word exports (plain text) and transcripts
MEETINGMIND_FILE_EXTENSIONS=.txt,.md,.transcript
```

**What MeetingMind cannot process:**
- ❌ Audio files (.mp3, .wav, .m4a)
- ❌ Video files (.mp4, .mov, .avi)
- ❌ Binary Word documents (.docx) - export to .txt first
- ❌ PDFs - convert to text first
- ❌ Spreadsheets (.xlsx, .csv)

### 5.2 Exporting from Meeting Platforms

**Zoom**

1. Go to [zoom.us](https://zoom.us) and sign in
2. Click **Recordings** in the left sidebar
3. Find your meeting and click on it
4. Under the recording, look for **Audio Transcript**
5. Click **Download** - you'll get a `.vtt` file
6. Rename it to `.txt` and move to your transcripts folder

**Tip:** Enable cloud recording in your Zoom settings to get automatic transcripts.

**Google Meet**

1. During the meeting, click the three dots (⋮) at the bottom
2. Click **Turn on captions**
3. After the meeting ends, check your Google Drive
4. Look in **Meet Recordings** folder
5. Find the transcript document (automatically created)
6. Download as `.txt`: **File → Download → Plain Text (.txt)**

**Microsoft Teams**

1. During the meeting, click **More actions** (•••)
2. Select **Start transcription**
3. After the meeting, go to the meeting chat
4. Click on the transcript attachment
5. Click **•••** (More options) → **Download**
6. Save as `.txt` file

**Otter.ai**

1. Go to your [Otter.ai](https://otter.ai) dashboard
2. Click on the conversation you want to export
3. Click **Export** at the top right
4. Choose **Text (.txt)** or **Word (.docx)**
5. If you chose Word, open it and save as plain text
6. Move to your transcripts folder

**Fireflies.ai**

1. Open your meeting in Fireflies dashboard
2. Click **Download** button
3. Select **Transcript** → **TXT format**
4. Save to your transcripts folder

**Rev.com**

1. Log into your Rev account
2. Go to your orders
3. Click the order you want
4. Click **Download** → **TXT**
5. Save to your transcripts folder

### 5.3 Tips for Better Results

**Include Speaker Labels**

✅ **Good:**
```
Alice: We need to finalize the budget by Friday.
Bob: I'll have the numbers ready by Thursday.
Carol: Should we schedule a review meeting?
```

❌ **Less ideal:**
```
We need to finalize the budget by Friday. I'll have the numbers ready by Thursday. Should we schedule a review meeting?
```

Speaker labels help MeetingMind identify who's responsible for action items and who made key points.

**Ensure Proper Punctuation**

Most transcription services add punctuation automatically. If yours doesn't, add basic punctuation:
- Periods at the end of sentences
- Question marks for questions
- Capitalize names and the beginning of sentences

**Remove Filler Content**

Clean up your transcripts by removing:
- Audio quality warnings ("Poor connection detected")
- System messages ("User joined the meeting")
- Excessive filler words ("um", "uh", "like" repeated many times)
- Personal/sensitive information you don't want in the analysis

**Use Descriptive Filenames**

✅ **Good filenames:**
- `2024-03-15-product-roadmap-meeting.txt`
- `Q1-marketing-review-team-alpha.txt`
- `client-kickoff-acme-corp.txt`

❌ **Less helpful:**
- `transcript.txt`
- `meeting1.txt`
- `audio123.txt`

Good filenames make it easier to find analyses later.

**Keep File Sizes Reasonable**

While MeetingMind can handle large transcripts, aim for:
- ✅ Under 50,000 words (typical: 30-60 minute meeting)
- ⚠️ 50,000-100,000 words (may be slower and more expensive)
- ❌ Over 100,000 words (consider splitting into multiple files)

### 5.4 What MeetingMind Cannot Do

**MeetingMind is an analysis tool, not a transcription tool.** It cannot:

❌ **Transcribe audio or video files directly**
- You need to use Zoom, Google Meet, Otter.ai, Rev.com, or similar services to create text transcripts first
- Then feed those transcripts to MeetingMind

❌ **Join your meetings automatically**
- MeetingMind doesn't attend meetings or record them
- It only analyzes transcripts you provide

❌ **Identify speakers from audio**
- If your transcript doesn't have speaker labels, MeetingMind can't add them
- Use a transcription service that includes speaker diarization (speaker identification)

❌ **Translate languages**
- Provide transcripts in English for best results
- If your transcript is in another language, translate it first using a translation service

❌ **Access your meeting recordings**
- MeetingMind doesn't connect to Zoom, Teams, or other platforms
- You must manually download transcripts

**What it CAN do:**
✅ Analyze text transcripts
✅ Extract action items and insights
✅ Identify key topics and decisions
✅ Assess meeting tone and sentiment
✅ Generate structured summaries

---

## 6. Using MeetingMind

### 6.1 Process Mode — One-Time Processing

**When to use Process Mode:**
- You have a batch of transcripts from last week's meetings
- You want to process files once and be done
- You're testing MeetingMind with sample transcripts
- You don't need continuous monitoring

**Basic usage:**

```bash
meetingmind process
```

This processes all unprocessed transcript files in your `INPUT_FOLDER` (default: `./transcripts`) and exits when done.

**Example session:**

```bash
$ meetingmind process
Processing file: team-standup-monday.txt
✓ Analysis complete: outputs/team-standup-monday_20240315_093022.md

Processing file: client-review-acme.txt
✓ Analysis complete: outputs/client-review-acme_20240315_093145.md

Processing file: planning-session.txt
✓ Analysis complete: outputs/planning-session_20240315_093312.md

Processed 3 file(s)
```

**With custom input folder:**

```bash
meetingmind process --input-folder ./march-meetings
```

**With custom output folder:**

```bash
meetingmind process --input-folder ./transcripts --output-folder ./analyses
```

**Process faster with more concurrency:**

```bash
meetingmind process --max-concurrent 5
```

This processes up to 5 files simultaneously instead of the default 3. Useful for batch processing many files quickly (but costs more in API usage).

**What happens:**
1. MeetingMind scans the input folder for eligible files (.txt, .md)
2. Checks which files have been processed before (skips them)
3. Processes all new files concurrently (up to `max_concurrent` limit)
4. Saves analysis markdown files to the output folder
5. Updates processing history
6. Exits when all files are done

### 6.2 Process a Single File

**When to use:**
- You want to analyze one specific transcript
- You're testing with different models or settings
- The transcript isn't in your usual input folder

**Usage:**

```bash
meetingmind process --transcript /path/to/meeting.txt
```

**Example:**

```bash
$ meetingmind process --transcript ~/Downloads/important-client-call.txt
Processing file: important-client-call.txt
✓ Analysis complete: outputs/important-client-call_20240315_143022.md

Processed 1 file(s)
```

**With custom output folder:**

```bash
meetingmind process --transcript ./meeting.txt --output-folder ./urgent-analyses
```

**Note:** When processing a single file, the `--transcript` path can be anywhere on your system—it doesn't need to be in your configured input folder.

**Difference from folder processing:**
- Folder mode: Processes all files in a directory
- Single file mode: Processes exactly one file regardless of location
- Both modes: Skip files already processed unless you reset state

### 6.3 Watch Mode — Continuous Monitoring

**When to use Watch Mode:**
- You have an ongoing workflow with regular meetings
- Your transcription service auto-saves files to a folder
- You want "set it and forget it" automated processing
- You're integrating MeetingMind into a production pipeline

**Basic usage:**

```bash
meetingmind watch
```

MeetingMind now runs continuously, checking for new files every 5 seconds (by default).

**Example session:**

```bash
$ meetingmind watch
Starting MeetingMind watcher...
Input folder: ./transcripts
Output folder: ./outputs
Poll interval: 5.0 seconds
Max concurrent: 3 files

Watching for new transcripts... (Press Ctrl+C to stop)

[2024-03-15 14:30:00] Checking for new files...
[2024-03-15 14:30:00] No new files to process

[2024-03-15 14:30:05] Checking for new files...
[2024-03-15 14:30:05] Found new file: standup-tuesday.txt
[2024-03-15 14:30:05] Processing standup-tuesday.txt...
[2024-03-15 14:30:23] ✓ Analysis complete: outputs/standup-tuesday_20240315_143023.md

[2024-03-15 14:30:28] Checking for new files...
[2024-03-15 14:30:28] No new files to process

^C
[2024-03-15 14:30:32] Interrupted by user
Shutting down gracefully...
```

**With custom options:**

```bash
# Watch a different folder
meetingmind watch --input-folder ./team-transcripts

# Check every 10 seconds instead of 5
meetingmind watch --poll-interval 10

# Process up to 5 files at once
meetingmind watch --max-concurrent 5

# Combine options
meetingmind watch --input-folder ./transcripts --output-folder ./results --poll-interval 15
```

**How to stop Watch Mode:**

Press `Ctrl+C` (or `Cmd+C` on Mac) in the terminal. MeetingMind will:
1. Finish processing any files currently being analyzed
2. Save all state changes
3. Exit gracefully

This is called a "graceful shutdown" — no files or state data are lost.

**Running in the background:**

To keep watch mode running even when you close the terminal:

```bash
# Using nohup (macOS/Linux)
nohup meetingmind watch > meetingmind.log 2>&1 &

# Check if it's running
ps aux | grep meetingmind

# Stop it later
pkill -f meetingmind
```

Or use a terminal multiplexer like `screen` or `tmux`:

```bash
# Start a screen session
screen -S meetingmind

# Run watch mode
meetingmind watch

# Detach: Press Ctrl+A, then D
# Reattach later: screen -r meetingmind
```

**What happens in watch mode:**
1. Every `poll_interval` seconds, scan the input folder
2. Find files with matching extensions (.txt, .md)
3. Wait `stability_check_seconds` to ensure the file is fully written
4. Skip files already processed (checked against state file)
5. Process new files concurrently (up to `max_concurrent`)
6. Save analyses to output folder
7. Update state file
8. Repeat forever until interrupted

### 6.4 Checking What's Been Processed

**View your processing history:**

```bash
meetingmind status
```

**Example output:**

```bash
$ meetingmind status
Total files processed: 12

Recent files:
  • standup-tuesday.txt
    Processed: 2024-03-15 14:30:23
    Output: standup-tuesday_20240315_143023.md

  • client-review-acme.txt
    Processed: 2024-03-15 09:31:45
    Output: client-review-acme_20240315_093145.md

  • team-standup-monday.txt
    Processed: 2024-03-15 09:30:22
    Output: team-standup-monday_20240315_093022.md

  • planning-session.txt
    Processed: 2024-03-15 09:33:12
    Output: planning-session_20240315_093312.md

  • weekly-review.txt
    Processed: 2024-03-14 16:22:08
    Output: weekly-review_20240314_162208.md

  [... up to 10 most recent files shown]
```

**Understanding the output:**

- **Total files processed** - How many transcripts have been analyzed since you started using MeetingMind (or last reset)
- **Recent files** - The 10 most recently processed files with timestamps
- **Processed** - When the file was analyzed
- **Output** - Name of the generated analysis file

**Why this is useful:**
- See what's already been processed so you don't duplicate work
- Verify that a file was successfully analyzed
- Check timestamps to find recent analyses
- Troubleshoot if a file wasn't processed when expected

### 6.5 Reprocessing a File

**The Problem:**

MeetingMind automatically skips files it has already processed. This is efficient, but what if:
- You updated your transcript with corrections
- You want to use a different AI model
- The first analysis failed or was incomplete
- You changed configuration settings and want a fresh analysis

**Solution 1: Reset All History (Nuclear Option)**

```bash
meetingmind reset
```

You'll be prompted to confirm:

```bash
$ meetingmind reset
This will clear all processing history. Continue? [y/N]: y
Processing state has been reset
```

⚠️ **Warning:** This clears the entire processing history. All previously processed files will be reprocessed next time you run `process` or `watch`.

**Solution 2: Manually Delete State File (Surgical Option)**

If you only want to reprocess specific files:

1. Open the state file (default: `.meetingmind_state.json`)
2. Find and delete the entry for the file you want to reprocess
3. Save the file

**Example state file:**

```json
{
  "processed_files": {
    "transcripts/team-meeting.txt": {
      "path": "transcripts/team-meeting.txt",
      "processed_at": "2024-03-15T14:30:23",
      "output_path": "outputs/team-meeting_20240315_143023.md"
    },
    "transcripts/client-call.txt": {
      "path": "transcripts/client-call.txt",
      "processed_at": "2024-03-15T09:31:45",
      "output_path": "outputs/client-call_20240315_093145.md"
    }
  }
}
```

To reprocess `team-meeting.txt`, delete its entire entry (the block with `"transcripts/team-meeting.txt": {...}`).

**Solution 3: Rename the File**

The simplest approach:

```bash
# Copy and rename
cp transcripts/team-meeting.txt transcripts/team-meeting-v2.txt

# Or move
mv transcripts/team-meeting.txt transcripts/team-meeting-updated.txt
```

Since the filename changed, MeetingMind treats it as a new file.

**Solution 4: Delete the State File Entirely**

```bash
rm .meetingmind_state.json
```

Next time you run MeetingMind, it starts fresh—all files will be reprocessed.

---

## 7. Understanding Your Output

Every analysis MeetingMind generates contains seven sections. Let's explore each one with examples.

### 7.1 📋 Summary

**What it contains:**
- A concise 2-4 paragraph overview of the entire meeting
- The main purpose and outcomes
- A bulleted list of key topics discussed

**When it's useful:**
- Quick refresher before a follow-up meeting
- Sharing with people who missed the meeting
- Executive summaries for leadership
- Meeting minutes for documentation

**Example output:**

```markdown
## 📋 Summary

This sprint planning meeting focused on prioritizing Q4 deliverables for the mobile app redesign project. The team reviewed customer feedback highlighting UI confusion for new users and agreed to make the mobile app redesign the top priority for the quarter.

Key decisions included assigning Bob as project lead for the redesign effort with a target completion date of November 30th. Carol will lead the API documentation update project to address support ticket issues, with a deadline of October 15th. The team also discussed a potential custom integration opportunity with TechCorp and scheduled a follow-up meeting.

**Key Topics:**
- Q4 roadmap and priorities
- Mobile app redesign project
- API documentation updates
- Customer feedback analysis
- TechCorp integration opportunity
- Resource allocation and deadlines
```

**How to use it:**
- Read this first to get the big picture
- Copy to your project management tool as meeting notes
- Forward to stakeholders who need a quick update
- Use as reference for status reports

### 7.2 ✅ Action Points

**What it contains:**
- Specific tasks that someone needs to complete
- Who's responsible (owner)
- When it's due (deadline)
- Priority level (high, medium, low) with color coding

**Priority color coding:**
- 🔴 **High** - Urgent, blocking other work, or time-sensitive
- 🟡 **Medium** - Important but not urgent
- 🟢 **Low** - Nice to have, background tasks

**When it's useful:**
- Immediately after a meeting to assign tasks
- Daily standups to check progress
- Weekly reviews to track completion
- Import into task management tools (Jira, Asana, Trello)

**Example output:**

```markdown
## ✅ Action Points

### 1. 🔴 Lead mobile app redesign project
- **Owner:** Bob
- **Deadline:** November 30th
- **Priority:** High

### 2. 🔴 Update API documentation with examples
- **Owner:** Carol
- **Deadline:** October 15th
- **Priority:** High

### 3. 🟡 Prepare redesign project plan
- **Owner:** Bob
- **Deadline:** Friday (this week)
- **Priority:** Medium

### 4. 🟡 Schedule follow-up meeting with TechCorp
- **Owner:** Alice
- **Deadline:** Next week
- **Priority:** Medium
```

**How to use it:**
- Send each person their assigned action items
- Set calendar reminders for deadlines
- Create tickets in your project management system
- Review in your next meeting to check progress

**Pro tip:** Copy the action points section and paste directly into Slack or email. The formatting is preserved and easy to read.

### 7.3 📝 Todo List

**What it contains:**
- Tasks and follow-up items mentioned in the meeting
- More informal than Action Points
- May not have specific owners or deadlines
- Includes context about why the task matters

**Difference from Action Points:**
- **Action Points** = Explicit commitments made during the meeting ("Bob will...")
- **Todo List** = Implied tasks, suggestions, or things to consider ("We should...")

**When it's useful:**
- Personal task tracking
- Backlog grooming for product teams
- Ideas to discuss in future meetings
- Context for future planning

**Example output:**

```markdown
## 📝 Todo List

- [ ] Analyze customer feedback data for UI pain points
  - *Context: Need to prioritize which UI elements to redesign first*

- [ ] Research best practices for mobile onboarding flows
  - *Context: Mentioned as part of addressing new user confusion*

- [ ] Coordinate with dev team for documentation review
  - *Context: Carol needs developer input on API examples*

- [ ] Prepare TechCorp integration proposal
  - *Context: Custom integration could be significant revenue opportunity*

- [ ] Review Q4 resource allocation
  - *Context: Ensure team has capacity for prioritized projects*
```

**How to use it:**
- Add items to your personal todo list
- Create backlog items for later sprints
- Identify tasks that need more definition
- Flag items to discuss in next planning meeting

### 7.4 👥 Important Mentions

**What gets flagged:**
- Key people who were discussed (but may not have been present)
- Important clients or partners mentioned
- Companies or organizations referenced
- Projects or initiatives called out
- Specific tools or technologies mentioned

**Each mention includes:**
- **Context** - How and why they were mentioned
- **Significance** - Why this mention matters

**When it's useful:**
- Identifying stakeholders to loop in
- Tracking client relationships
- Following up on partner opportunities
- Connecting dots between meetings and projects

**Example output:**

```markdown
## 👥 Important Mentions

### TechCorp
- **Context:** Bob mentioned they're interested in a custom integration
- **Significance:** Potential major client opportunity that requires immediate follow-up and scoping

### Customer Support Team
- **Context:** Multiple support tickets cited as reason for API documentation priority
- **Significance:** Direct user feedback driving product decisions and resource allocation

### Q4 Roadmap
- **Context:** Central focus of the meeting, used to prioritize upcoming work
- **Significance:** Strategic planning artifact guiding team priorities for the next quarter
```

**How to use it:**
- Email stakeholders mentioned to update them
- Follow up on client mentions with sales/account teams
- Track project dependencies
- Identify people to invite to future meetings

### 7.5 🔄 Recap

**What it contains:**

Three focused sub-sections:

1. **Highlights** - Most important moments or discussion points
2. **Decisions Made** - Concrete decisions that were finalized
3. **Next Steps** - Immediate actions to take after the meeting

**When it's useful:**
- End-of-meeting summaries
- Status updates to management
- Starting point for next meeting agenda
- Quick reference for "what did we decide?"

**Example output:**

```markdown
## 🔄 Recap

**Highlights:**
- Mobile app redesign identified as top Q4 priority based on customer feedback
- Strong consensus on addressing UI confusion for new users
- TechCorp integration opportunity could be significant for revenue growth
- Team has clear ownership and deadlines for priority projects

**Decisions Made:**
- Bob will lead mobile app redesign with November 30th target
- Carol will update API documentation with October 15th deadline
- API documentation elevated to high priority due to support volume
- Follow-up meeting with TechCorp to be scheduled next week

**Next Steps:**
- Bob: Prepare detailed project plan by end of week
- Carol: Coordinate with developers for documentation review
- Alice: Schedule TechCorp integration scoping meeting
- Team: Begin Q4 execution on prioritized roadmap items
```

**How to use it:**
- Post in your team Slack channel immediately after meeting
- Include in weekly status reports
- Reference at start of next meeting
- Share with stakeholders who need quick updates

**Pro tip:** The Recap section is designed to be copy-pasted directly into meeting minutes or status reports. No editing needed!

### 7.6 🎭 Meeting Tone

**What it analyzes:**

Four dimensions of meeting dynamics:

1. **Overall Sentiment** - positive, neutral, negative, or mixed
2. **Energy Level** - high, medium, or low
3. **Collaboration Quality** - excellent, good, fair, or poor
4. **Notes** - Additional observations about tone or dynamics

**When it's useful:**
- Assessing team morale and engagement
- Identifying meetings that may need follow-up
- Tracking meeting effectiveness over time
- Recognizing when a meeting went particularly well or poorly
- Management insights on team dynamics

**Example output (Positive meeting):**

```markdown
## 🎭 Meeting Tone

- **Overall Sentiment:** Positive
- **Energy Level:** High
- **Collaboration Quality:** Excellent

**Notes:** The meeting was highly productive with clear decision-making and strong team alignment. All participants actively contributed ideas and there was constructive dialogue about priorities. Team members expressed enthusiasm about the roadmap and confidence in their ability to deliver.
```

**Example output (Challenging meeting):**

```markdown
## 🎭 Meeting Tone

- **Overall Sentiment:** Mixed
- **Energy Level:** Medium
- **Collaboration Quality:** Fair

**Notes:** Some tension surfaced around resource allocation and competing priorities. While decisions were made, not all participants seemed fully bought in. Consider a follow-up discussion to address concerns and ensure team alignment before proceeding.
```

**How to interpret the fields:**

**Overall Sentiment:**
- **Positive** - Optimistic, constructive, productive atmosphere
- **Neutral** - Professional, matter-of-fact, informational
- **Negative** - Frustration, conflict, or low morale evident
- **Mixed** - Combination of positive and negative tones

**Energy Level:**
- **High** - Enthusiastic, animated, lots of back-and-forth
- **Medium** - Engaged but measured, professional
- **Low** - Quiet, passive, or exhausted

**Collaboration Quality:**
- **Excellent** - Active listening, building on ideas, consensus-building
- **Good** - Respectful dialogue, some collaboration
- **Fair** - Minimal interaction, mostly one-directional
- **Poor** - Conflict, talking past each other, or disengagement

**How to use it:**
- If sentiment is negative, schedule a retro or 1-on-1s
- If energy is consistently low, consider meeting format changes
- If collaboration is poor, address team dynamics
- If everything is excellent, recognize what made it work and repeat it

### 7.7 💡 Key Insights

**What it contains:**

Three types of strategic analysis:

1. **Insights** - Important patterns or observations about the meeting content
2. **Patterns** - Recurring themes across topics or decisions
3. **Recommendations** - Suggested actions or considerations based on the meeting

**Insights vs. Patterns vs. Recommendations:**

- **Insight** = "Here's something important I noticed"
- **Pattern** = "Here's something that keeps coming up"
- **Recommendation** = "Here's what you should consider doing"

**When to read this section:**
- Strategic planning sessions
- After important client or stakeholder meetings
- When making decisions about future direction
- Looking for process improvements
- Identifying systemic issues or opportunities

**Example output:**

```markdown
## 💡 Key Insights

**Insights:**
- Customer feedback is driving product strategy, indicating strong product-market fit but highlighting UX gaps
- Team has clear capacity and commitment for Q4 deliverables with realistic timelines
- TechCorp mention suggests growing demand for enterprise customization features
- Support ticket volume correlating with documentation gaps indicates documentation is a significant user pain point

**Patterns:**
- Strong emphasis on user experience and customer feedback throughout discussion
- Recurring theme of balancing feature development with documentation and support
- Consistent prioritization based on customer impact rather than technical preferences
- Team ownership model working well with clear assignments and deadlines

**Recommendations:**
- Consider establishing a regular customer feedback review process if not already in place
- Monitor TechCorp opportunity closely and allocate pre-sales support if needed
- Evaluate if documentation updates should be ongoing rather than project-based
- Track completion of action items in next meeting to maintain accountability
- Consider creating a product roadmap dashboard visible to all stakeholders
```

**How to use it:**
- Discuss recommendations in leadership meetings
- Add insights to quarterly planning documents
- Use patterns to identify process improvements
- Share with product team for roadmap planning
- Reference in retrospectives

**Pro tip:** The Key Insights section often surfaces things that weren't explicitly discussed but are implied by the meeting content. It's like having a strategic advisor in the room.

---

## 8. Common Workflows

### Workflow 1: Process Last Week's Meetings (Batch)

**Scenario:** You have 10 meeting transcripts from last week and want to analyze them all at once.

**Steps:**

1. **Create your transcripts folder (if you haven't already):**

```bash
mkdir transcripts
```

2. **Copy all your transcript files into the folder:**

```bash
# If they're in your Downloads folder
cp ~/Downloads/*.txt transcripts/

# Or if they're scattered in different places
cp ~/Documents/meeting-*.txt transcripts/
cp ~/Desktop/client-call.txt transcripts/
```

3. **Verify files are there:**

```bash
ls transcripts/
```

You should see:
```
client-review-monday.txt
standup-tuesday.txt
planning-wednesday.txt
...
```

4. **Run process mode:**

```bash
meetingmind process
```

5. **Wait for completion:**

```bash
Processing file: client-review-monday.txt
✓ Analysis complete: outputs/client-review-monday_20240315_143022.md

Processing file: standup-tuesday.txt
✓ Analysis complete: outputs/standup-tuesday_20240315_143145.md

[... continues for all files]

Processed 10 file(s)
```

6. **Review your analyses:**

```bash
# List all outputs
ls outputs/

# Open one
open outputs/client-review-monday_20240315_143022.md
# or on Linux: xdg-open outputs/client-review-monday_20240315_143022.md
```

**Tips for batch processing:**
- Process large batches during off-hours to avoid waiting
- Increase concurrency for faster processing: `meetingmind process --max-concurrent 5`
- Check status after completion: `meetingmind status`
- Files are only processed once—safe to run again without duplicating work

### Workflow 2: Set Up Ongoing Monitoring

**Scenario:** You want MeetingMind to automatically process transcripts as your transcription service saves them.

**Steps:**

1. **Configure your transcription service to save to a specific folder:**

For example, if using Otter.ai:
- Settings → Integrations → Dropbox
- Set export folder to `/path/to/MeetingMind/transcripts`

Or manually:
- Create a rule: "When new Otter transcript arrives in email, save to Dropbox/MeetingMind/transcripts"

2. **Verify the folder path in your .env:**

```env
MEETINGMIND_INPUT_FOLDER=./transcripts
```

Or set it to your Dropbox/cloud folder:

```env
MEETINGMIND_INPUT_FOLDER=/Users/yourname/Dropbox/MeetingMind/transcripts
```

3. **Start watch mode:**

```bash
meetingmind watch
```

4. **Keep it running in the background:**

Option A - Using screen:

```bash
screen -S meetingmind
meetingmind watch
# Press Ctrl+A, then D to detach
```

Reattach later:
```bash
screen -r meetingmind
```

Option B - Using nohup:

```bash
nohup meetingmind watch > meetingmind.log 2>&1 &
```

Check logs:
```bash
tail -f meetingmind.log
```

Stop it:
```bash
pkill -f meetingmind
```

5. **Test it:**

Drop a test transcript in the transcripts folder:

```bash
cp ~/Downloads/test-meeting.txt transcripts/
```

Within 5 seconds (or your configured poll interval), you should see it processed.

6. **Check results:**

```bash
ls outputs/
meetingmind status
```

**Pro tips:**
- Set up outputs folder to sync to cloud storage for team access
- Use a longer poll interval (30-60 seconds) if running on a laptop to save battery
- Monitor the log file occasionally to catch any errors
- Run `meetingmind status` daily to verify files are being processed

### Workflow 3: Use Claude Instead of GPT-4

**Scenario:** You want to try Anthropic's Claude models instead of OpenAI's GPT-4.

**Steps:**

1. **Get an Anthropic API key:**

Go to [console.anthropic.com](https://console.anthropic.com/), sign up, and create an API key.

2. **Update your .env file:**

```env
# Change these three lines
MEETINGMIND_MODEL_PROVIDER=anthropic
MEETINGMIND_MODEL_NAME=claude-3-5-sonnet-latest
MEETINGMIND_API_KEY=sk-ant-your-anthropic-key-here
```

3. **Process a test file:**

```bash
meetingmind process --transcript transcripts/test-meeting.txt
```

4. **Compare results:**

Run the same transcript with both models and compare:

```bash
# First with Claude (current .env)
meetingmind process --transcript test.txt

# Switch to OpenAI
cp .env .env.claude
cp .env.openai .env

# Process again (after resetting so it reprocesses)
meetingmind reset
meetingmind process --transcript test.txt
```

**Model recommendations:**

**OpenAI models:**
- `gpt-4` - Best quality, slower, ~$0.03 per 1K tokens
- `gpt-4-turbo-preview` - Faster, cheaper, similar quality
- `gpt-3.5-turbo` - Much cheaper (~$0.002 per 1K tokens), lower quality

**Anthropic models:**
- `claude-3-5-sonnet-latest` - Excellent quality, good speed (recommended)
- `claude-3-opus-latest` - Highest quality, more expensive
- `claude-3-sonnet-20240229` - Specific version (for consistency)

**Comparison:**

| Model | Quality | Speed | Cost | Best For |
|-------|---------|-------|------|----------|
| GPT-4 | Excellent | Slower | Higher | Critical meetings, detailed analysis |
| GPT-4 Turbo | Excellent | Fast | Medium | Best balance for most users |
| Claude 3.5 Sonnet | Excellent | Fast | Medium | Great alternative to GPT-4 |
| GPT-3.5 Turbo | Good | Very fast | Low | High volume, budget-conscious |

### Workflow 4: Organize by Project

**Scenario:** You manage multiple projects and want separate output folders for each.

**Setup:**

Create project-specific configuration files:

```bash
# Project Alpha config
cat > .env.alpha << 'EOF'
MEETINGMIND_INPUT_FOLDER=./transcripts/alpha
MEETINGMIND_OUTPUT_FOLDER=./outputs/alpha
MEETINGMIND_API_KEY=your-key-here
EOF

# Project Beta config
cat > .env.beta << 'EOF'
MEETINGMIND_INPUT_FOLDER=./transcripts/beta
MEETINGMIND_OUTPUT_FOLDER=./outputs/beta
MEETINGMIND_API_KEY=your-key-here
EOF
```

Create the folders:

```bash
mkdir -p transcripts/alpha transcripts/beta
mkdir -p outputs/alpha outputs/beta
```

**Usage:**

Process Project Alpha meetings:

```bash
# Copy the config
cp .env.alpha .env

# Process
meetingmind process

# Or in one command
MEETINGMIND_INPUT_FOLDER=./transcripts/alpha \
MEETINGMIND_OUTPUT_FOLDER=./outputs/alpha \
meetingmind process
```

Process Project Beta meetings:

```bash
cp .env.beta .env
meetingmind process
```

**Alternative approach - Multiple state files:**

Keep separate processing history for each project:

```bash
# Project Alpha
MEETINGMIND_STATE_FILE=.state-alpha.json \
MEETINGMIND_INPUT_FOLDER=./transcripts/alpha \
meetingmind process

# Project Beta
MEETINGMIND_STATE_FILE=.state-beta.json \
MEETINGMIND_INPUT_FOLDER=./transcripts/beta \
meetingmind process
```

**Shell aliases for convenience:**

Add to your `.bashrc` or `.zshrc`:

```bash
alias mm-alpha='MEETINGMIND_INPUT_FOLDER=./transcripts/alpha MEETINGMIND_OUTPUT_FOLDER=./outputs/alpha meetingmind'
alias mm-beta='MEETINGMIND_INPUT_FOLDER=./transcripts/beta MEETINGMIND_OUTPUT_FOLDER=./outputs/beta meetingmind'
```

Then use:

```bash
mm-alpha process
mm-beta watch
```

### Workflow 5: Process Only Specific File Types

**Scenario:** You have both `.txt` transcripts and `.md` notes files in the same folder, but only want to process transcripts.

**Solution - Update .env:**

```env
# Only process .txt files (not .md)
MEETINGMIND_FILE_EXTENSIONS=.txt
```

Or process only markdown:

```env
# Only process .md files
MEETINGMIND_FILE_EXTENSIONS=.md
```

Or add custom extensions:

```env
# Process .txt, .md, and .transcript files
MEETINGMIND_FILE_EXTENSIONS=.txt,.md,.transcript
```

**Usage:**

```bash
# With .env configured for .txt only
meetingmind process

# Or override via environment variable
MEETINGMIND_FILE_EXTENSIONS=.md meetingmind process
```

**Pro tip:** Use subdirectories instead:

```
transcripts/
├── text/           # .txt files
├── markdown/       # .md files
└── processed/      # Move here after processing
```

Then process specific folders:

```bash
meetingmind process --input-folder transcripts/text
meetingmind process --input-folder transcripts/markdown
```

---

## 9. Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| **"No new files to process" when files are in folder** | Files already processed, or wrong file extension | Check `meetingmind status` to see if files were processed before. Verify file extensions match `MEETINGMIND_FILE_EXTENSIONS` setting. Try `meetingmind reset` to reprocess. |
| **`AuthenticationError` or API key error** | Invalid API key, or key not set | Verify your `.env` file exists and contains `MEETINGMIND_API_KEY=sk-...`. Check the key is valid at your provider's dashboard. Make sure there are no spaces or quotes around the key. |
| **Files detected but not processed (not stable warning)** | File is being written slowly or on network drive | Increase `MEETINGMIND_STABILITY_CHECK_SECONDS=5.0` in `.env`. Wait longer before checking. Ensure file is fully written before processing. |
| **Slow processing / timeouts** | Large transcript, slow API response, or model overloaded | Use a faster model: `gpt-4-turbo-preview` or `gpt-3.5-turbo`. Split large transcripts into smaller chunks. Reduce `MAX_CONCURRENT_FILES` to 1 to avoid rate limits. |
| **"Corrupted state file, starting fresh" warning** | State file JSON was manually edited incorrectly | Let MeetingMind recreate it automatically. If persistent, delete `.meetingmind_state.json` and restart. Avoid editing state file directly. |
| **Output file is empty or has placeholder text** | API call failed during processing | Check API quota and rate limits at your provider's dashboard. Verify internet connection. Look for error messages in console output. Try reprocessing after resetting state. |
| **`meetingmind` command not found** | Package not installed or venv not activated | Run `make install` or `uv sync`. Then use `uv run meetingmind` or activate venv: `source .venv/bin/activate`. Check installation: `which meetingmind`. |
| **Wrong Python version error** | System Python is too old (< 3.11) | Install Python 3.11+ from python.org. Use `python3.11` explicitly. Or use UV which manages Python versions: `uv python install 3.11`. |
| **Files being processed twice after reset** | Normal behavior—reset clears history | This is expected. `meetingmind reset` makes all files eligible for reprocessing. To process only specific files, edit state file manually instead. |
| **Watch mode exits immediately** | Error in configuration or missing API key | Check for error messages when starting watch mode. Verify `.env` file has valid `API_KEY`. Try running `meetingmind process` first to test config. Check logs for specific error. |
| **"Rate limit exceeded" error** | Too many API requests too quickly | Reduce `MAX_CONCURRENT_FILES` to 1 or 2. Add delays between batches. Upgrade your API plan for higher rate limits. Wait a few minutes and try again. |
| **Output folder not created** | Folder doesn't exist and MeetingMind can't create it | Manually create the output folder: `mkdir -p outputs`. Check folder permissions: `ls -ld outputs`. Verify `OUTPUT_FOLDER` path in `.env` is correct. |

**General debugging steps:**

1. **Check your configuration:**
   ```bash
   cat .env
   ```

2. **Verify API key is set:**
   ```bash
   echo $MEETINGMIND_API_KEY
   # or
   grep API_KEY .env
   ```

3. **Test with a small file first:**
   ```bash
   # Create a minimal test file
   echo "Alice: Hello\nBob: Hi" > transcripts/test.txt
   meetingmind process
   ```

4. **Check status and logs:**
   ```bash
   meetingmind status
   # If using watch mode with nohup:
   tail -f meetingmind.log
   ```

5. **Reset and try again:**
   ```bash
   meetingmind reset
   meetingmind process --transcript transcripts/test.txt
   ```

6. **Verify file permissions:**
   ```bash
   ls -lh transcripts/
   ls -lh outputs/
   ```

7. **Check API provider status:**
   - OpenAI: [status.openai.com](https://status.openai.com)
   - Anthropic: [status.anthropic.com](https://status.anthropic.com)

---

## 10. FAQ

### 1. Can I use Anthropic/Claude instead of OpenAI?

**Yes!** MeetingMind supports both OpenAI and Anthropic models.

Update your `.env` file:

```env
MEETINGMIND_MODEL_PROVIDER=anthropic
MEETINGMIND_MODEL_NAME=claude-3-5-sonnet-latest
MEETINGMIND_API_KEY=sk-ant-your-anthropic-key-here
```

Claude models often produce excellent analyses with strong reasoning capabilities, and some users prefer Claude's communication style.

### 2. How much does it cost per transcript?

**Typical costs:**

| Transcript Length | Model | Approximate Cost |
|------------------|-------|------------------|
| 15-min meeting (~3,000 words) | GPT-4 | $0.10 - $0.20 |
| 30-min meeting (~6,000 words) | GPT-4 | $0.20 - $0.40 |
| 60-min meeting (~12,000 words) | GPT-4 | $0.40 - $0.80 |
| 15-min meeting | GPT-3.5 Turbo | $0.02 - $0.05 |
| 30-min meeting | GPT-3.5 Turbo | $0.04 - $0.10 |
| 30-min meeting | Claude 3.5 Sonnet | $0.15 - $0.35 |

**Factors affecting cost:**
- Transcript length (longer = more expensive)
- Model choice (GPT-4 > Claude > GPT-3.5 in cost)
- Analysis complexity (more nuanced meetings may use more tokens)

**Cost-saving tips:**
- Use `gpt-3.5-turbo` for routine meetings (80% cheaper)
- Reserve `gpt-4` for critical client meetings or complex discussions
- Clean up transcripts to remove unnecessary content before processing
- Process in batches during off-peak hours (some providers offer discounts)

### 3. Can I reprocess a file I've already processed?

**Yes, several ways:**

**Option 1:** Reset all processing history
```bash
meetingmind reset
```

**Option 2:** Edit the state file to remove specific entries
```bash
nano .meetingmind_state.json
# Delete the entry for the file you want to reprocess
```

**Option 3:** Rename the file
```bash
mv transcripts/meeting.txt transcripts/meeting-v2.txt
```

**Option 4:** Delete the state file entirely
```bash
rm .meetingmind_state.json
```

After using any of these methods, run `meetingmind process` again.

### 4. What happens if the AI call fails during processing?

**MeetingMind handles failures gracefully:**

1. The file is **not** marked as processed in the state file
2. Error is logged to console/log file
3. Processing continues for other files (in batch mode)
4. You can retry later without any issues

**Common failures:**
- Network timeout → Retry after checking internet connection
- Rate limit exceeded → Wait a few minutes, reduce concurrency
- Invalid API key → Fix `.env` file and retry
- Model overload → Try again in a few minutes

The file will be automatically picked up next time you run `meetingmind process` or `watch`.

### 5. Is my meeting content sent to OpenAI/Anthropic?

**Yes, here's how it works:**

1. Your transcript text is sent to OpenAI or Anthropic's API
2. Their AI model analyzes it and returns structured results
3. MeetingMind saves the results to your local disk
4. The transcript itself remains on your computer

**Privacy considerations:**

✅ **What's sent:**
- The transcript text content
- Your API requests and usage data

❌ **What's NOT sent:**
- Your original transcript files (only content, not files)
- Your output analysis files
- Your processing history/state

**For sensitive meetings:**
- Use models from providers with strong privacy policies
- Check OpenAI's [privacy policy](https://openai.com/privacy/) and data retention
- Check Anthropic's [privacy policy](https://www.anthropic.com/privacy)
- Consider self-hosted models for highly confidential content (see FAQ #12)
- Redact sensitive information before processing

**Important:** Both OpenAI and Anthropic state they don't use API data to train models (as of 2024), but always check current terms of service.

### 6. Can I process audio or video files directly?

**No, MeetingMind only processes text transcripts.** It's an analysis tool, not a transcription tool.

**To process audio/video:**

1. **First**, transcribe using one of these services:
   - **Otter.ai** - Automatic transcription with speaker labels
   - **Rev.com** - Professional human transcription
   - **Zoom** - Automatic cloud transcription
   - **Google Meet** - Automatic caption transcription
   - **Whisper (OpenAI)** - Self-hosted transcription API

2. **Then**, feed the transcript to MeetingMind:
   ```bash
   meetingmind process --transcript transcript.txt
   ```

**Why this limitation?**

Transcription and analysis are separate skills. MeetingMind focuses on doing analysis exceptionally well. There are many excellent transcription tools—use the best tool for each job.

### 7. How long does processing take?

**Typical processing times:**

| Transcript Length | Model | Time |
|------------------|-------|------|
| 15-min meeting (~3,000 words) | GPT-4 | 20-45 seconds |
| 30-min meeting (~6,000 words) | GPT-4 | 45-90 seconds |
| 60-min meeting (~12,000 words) | GPT-4 | 90-180 seconds |
| 30-min meeting | GPT-3.5 Turbo | 15-30 seconds |
| 30-min meeting | Claude 3.5 | 30-60 seconds |

**Factors affecting speed:**
- Transcript length (longer = slower)
- Model choice (GPT-3.5 is fastest, GPT-4 is slower)
- API response time (varies by provider load)
- Number of concurrent files (more = individual files take longer)
- Network latency

**Speed tips:**
- Use `gpt-4-turbo-preview` for faster GPT-4 processing
- Use `gpt-3.5-turbo` for quickest results
- Process during off-peak hours for better API response times
- Reduce `MAX_CONCURRENT_FILES` if individual files are slow

### 8. Can I customize the output format?

**Partially.** The markdown structure is fixed (7 sections), but you can:

**Customize the filename:**
```env
MEETINGMIND_FILENAME_TEMPLATE=analysis-{source_stem}.md
# or
MEETINGMIND_FILENAME_TEMPLATE={timestamp}-{source_stem}.md
```

**Post-process the markdown:**

Use a script to convert to other formats:

```bash
# Convert to HTML
pandoc outputs/meeting.md -o outputs/meeting.html

# Convert to PDF
pandoc outputs/meeting.md -o outputs/meeting.pdf

# Convert to Word
pandoc outputs/meeting.md -o outputs/meeting.docx
```

**Modify the source code:**

For advanced users, edit `src/meetingmind/markdown.py` to customize:
- Section order
- Formatting
- Additional sections
- Emoji choices

**Future feature:** Custom templates are planned for a future version.

### 9. Can I run multiple instances of MeetingMind?

**Yes, but carefully.**

**Safe scenarios:**

✅ **Different folders:**
```bash
# Terminal 1
MEETINGMIND_INPUT_FOLDER=./project-a/transcripts meetingmind watch

# Terminal 2
MEETINGMIND_INPUT_FOLDER=./project-b/transcripts meetingmind watch
```

✅ **Different state files:**
```bash
# Terminal 1
MEETINGMIND_STATE_FILE=.state-alpha.json meetingmind watch

# Terminal 2
MEETINGMIND_STATE_FILE=.state-beta.json meetingmind watch
```

**Unsafe scenarios:**

❌ **Same input folder + same state file:**
- Files may be processed twice
- State file may be corrupted by concurrent writes
- Undefined behavior

**Best practice:**
- Use separate folders for each instance
- Use separate state files for each instance
- Or simply use one instance with higher `MAX_CONCURRENT_FILES`

### 10. How do I back up my processing history?

**The state file contains all processing history:**

```bash
# Back up the state file
cp .meetingmind_state.json .meetingmind_state.backup.json

# Or with timestamp
cp .meetingmind_state.json .meetingmind_state.$(date +%Y%m%d).json
```

**Automated backups:**

Create a daily backup cron job:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 3 AM)
0 3 * * * cd /path/to/MeetingMind && cp .meetingmind_state.json .meetingmind_state.backup.json
```

**Restore from backup:**

```bash
cp .meetingmind_state.backup.json .meetingmind_state.json
```

**What's in the state file:**
- List of all processed files with paths
- Processing timestamps
- Output file locations

**Pro tip:** Back up your entire MeetingMind folder periodically:

```bash
# Create archive
tar -czf meetingmind-backup-$(date +%Y%m%d).tar.gz \
    transcripts/ outputs/ .env .meetingmind_state.json

# Restore later
tar -xzf meetingmind-backup-20240315.tar.gz
```

### 11. What's the maximum transcript length?

**Technical limits:**

| Model | Token Limit | Approximate Words |
|-------|-------------|-------------------|
| GPT-4 | 8,192 tokens | ~6,000 words |
| GPT-4 Turbo | 128,000 tokens | ~96,000 words |
| GPT-3.5 Turbo | 16,385 tokens | ~12,000 words |
| Claude 3.5 Sonnet | 200,000 tokens | ~150,000 words |

**Practical limits:**

- ✅ **Under 10,000 words** - No issues
- ⚠️ **10,000-30,000 words** - Works but slower and more expensive
- ❌ **Over 30,000 words** - May hit context limits or timeout

**For very long transcripts:**

1. **Split into multiple files:**
   ```bash
   # Split by speaker or topic
   split-transcript.sh long-meeting.txt
   ```

2. **Use a model with larger context:**
   ```env
   MEETINGMIND_MODEL_NAME=gpt-4-turbo-preview  # 128K tokens
   # or
   MEETINGMIND_MODEL_NAME=claude-3-5-sonnet-latest  # 200K tokens
   ```

3. **Edit the transcript to remove:**
   - Redundant content
   - Off-topic discussions
   - Excessive filler words

**Typical meeting lengths:**
- 30-minute meeting: 5,000-7,000 words ✅
- 1-hour meeting: 10,000-15,000 words ✅
- 2-hour meeting: 20,000-30,000 words ⚠️
- 4-hour workshop: 40,000-60,000 words ❌ (split recommended)

### 12. Can I use a local/offline AI model?

**Not currently supported in the main release**, but possible with modifications.

**Why local models aren't included:**
- MeetingMind uses Pydantic AI which is optimized for API-based models
- Local models (Llama, Mistral, etc.) typically require different infrastructure
- Quality of analysis varies significantly with smaller models

**Workarounds for advanced users:**

1. **Use LM Studio or Ollama** with OpenAI-compatible API:
   ```bash
   # Start LM Studio with OpenAI-compatible server
   # or use Ollama with OpenAI compatibility
   
   # Point MeetingMind to local endpoint
   MEETINGMIND_API_BASE=http://localhost:1234/v1
   MEETINGMIND_API_KEY=not-needed
   meetingmind process
   ```

2. **Modify the agent code** to use local models directly
   - Edit `src/meetingmind/agents.py`
   - Replace Pydantic AI clients with local model calls
   - Handle structured output extraction manually

3. **Use Azure OpenAI** for on-premises deployment:
   ```env
   MEETINGMIND_MODEL_PROVIDER=azure
   MEETINGMIND_API_BASE=https://your-resource.openai.azure.com/
   MEETINGMIND_API_KEY=your-azure-key
   ```

**Future plans:**
- Local model support is on the roadmap
- Contributions welcome if you'd like to add this feature!

**For maximum privacy:**
- Use Azure OpenAI with private endpoints
- Deploy in your own Azure tenant
- Or wait for official local model support

---

## 11. Quick Reference Card

### Commands

| Command | What It Does |
|---------|-------------|
| `meetingmind watch` | Monitor folder and process files continuously |
| `meetingmind process` | Process all new files once and exit |
| `meetingmind process --transcript FILE` | Process one specific file |
| `meetingmind status` | Show processing history and statistics |
| `meetingmind reset` | Clear all processing history (reprocess everything) |
| `meetingmind --version` | Show version number |
| `meetingmind --help` | Show help and available commands |
| `make install` | Install dependencies |
| `make run` | Start watch mode (shortcut for `meetingmind watch`) |
| `make test` | Run test suite |

**Command options:**

| Option | Available On | What It Does | Example |
|--------|-------------|-------------|---------|
| `--input-folder PATH` | watch, process | Override input folder | `--input-folder ./my-transcripts` |
| `--output-folder PATH` | watch, process | Override output folder | `--output-folder ./analyses` |
| `--poll-interval N` | watch | Override poll interval (seconds) | `--poll-interval 10` |
| `--max-concurrent N` | watch, process | Override max concurrent files | `--max-concurrent 5` |
| `--transcript PATH` | process | Process single file | `--transcript ./meeting.txt` |

### Key Settings

| Setting | Default | Change When... |
|---------|---------|---------------|
| `INPUT_FOLDER` | `./transcripts` | Using different folder structure |
| `OUTPUT_FOLDER` | `./outputs` | Want outputs elsewhere |
| `FILE_EXTENSIONS` | `.txt,.md` | Processing other file types |
| `MAX_CONCURRENT_FILES` | `3` | Want faster/slower processing |
| `POLL_INTERVAL_SECONDS` | `5.0` | Running on battery, or want faster response |
| `MODEL_PROVIDER` | `openai` | Using Anthropic/Claude instead |
| `MODEL_NAME` | `gpt-4` | Want faster/cheaper/different model |
| `API_KEY` | *(none)* | **Required** - Your OpenAI/Anthropic key |

**Quick .env template:**

```env
MEETINGMIND_API_KEY=sk-proj-your-key-here
MEETINGMIND_INPUT_FOLDER=./transcripts
MEETINGMIND_OUTPUT_FOLDER=./outputs
MEETINGMIND_MODEL_NAME=gpt-4
```

### Shortcuts & Tips

**Useful shell aliases (add to ~/.bashrc or ~/.zshrc):**

```bash
# Quick commands
alias mm='meetingmind'
alias mmw='meetingmind watch'
alias mmp='meetingmind process'
alias mms='meetingmind status'
alias mmr='meetingmind reset'

# Project-specific
alias mm-work='cd ~/MeetingMind/work && meetingmind watch'
alias mm-personal='cd ~/MeetingMind/personal && meetingmind watch'

# With UV
alias mm='uv run meetingmind'
```

**Check if watch mode is running:**

```bash
# macOS/Linux
ps aux | grep meetingmind

# Count running instances
ps aux | grep meetingmind | wc -l

# Kill all instances
pkill -f meetingmind
```

**Quick file count:**

```bash
# How many transcripts?
ls transcripts/*.txt | wc -l

# How many outputs?
ls outputs/*.md | wc -l

# What's not processed yet?
comm -23 <(ls transcripts/*.txt | sort) <(meetingmind status | grep "• " | sort)
```

**Monitor processing in real-time:**

```bash
# Watch the output folder
watch -n 2 ls -lht outputs/ | head

# Tail logs if using nohup
tail -f meetingmind.log

# Follow state file changes
watch -n 5 cat .meetingmind_state.json
```

**Batch operations:**

```bash
# Process last week's meetings
find transcripts/ -type f -mtime -7 -exec meetingmind process --transcript {} \;

# Archive processed transcripts
mkdir -p archive/$(date +%Y-%m)
mv transcripts/*.txt archive/$(date +%Y-%m)/

# Clean old outputs (older than 90 days)
find outputs/ -name "*.md" -mtime +90 -delete
```

**Quick test:**

```bash
# Create test file
echo "Alice: Hello\nBob: Hi Alice, how are you?\nAlice: Great! Let's discuss the project." > transcripts/test.txt

# Process it
meetingmind process

# View output
cat outputs/test_*.md
```

**Environment variable shortcuts:**

```bash
# One-time override
MEETINGMIND_MODEL_NAME=gpt-3.5-turbo meetingmind process

# Chain multiple
MEETINGMIND_INPUT_FOLDER=./urgent \
MEETINGMIND_MAX_CONCURRENT_FILES=1 \
meetingmind process
```

**Check API usage:**

```bash
# OpenAI
open https://platform.openai.com/usage

# Anthropic
open https://console.anthropic.com/usage

# Or use curl
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $MEETINGMIND_API_KEY"
```

---

## Support & Community

### Getting Help

**Documentation:**
- This user manual (you're reading it!)
- README.md in the project root
- Inline code documentation

**Troubleshooting:**
- See Section 9 (Troubleshooting) above
- Check FAQ (Section 10)
- Review error messages carefully—they often indicate the exact problem

**Community:**
- GitHub Issues: Report bugs or request features
- GitHub Discussions: Ask questions, share tips
- Contributing: See CONTRIBUTING.md for how to contribute

### Reporting Issues

When reporting a bug, include:
1. MeetingMind version: `meetingmind --version`
2. Python version: `python3 --version`
3. Operating system: macOS, Linux, Windows
4. Error message (full text)
5. Steps to reproduce
6. Configuration (sanitize your API key!)

**Example issue:**

```
**Bug:** Watch mode exits immediately after starting

**Environment:**
- MeetingMind: 0.1.0
- Python: 3.11.5
- OS: macOS 14.0

**Error:**
```
AuthenticationError: Invalid API key
```

**Steps:**
1. Run `meetingmind watch`
2. See error immediately

**Config:**
```env
MEETINGMIND_API_KEY=sk-proj-... (redacted)
MEETINGMIND_MODEL_PROVIDER=openai
```
```

### Feature Requests

Have an idea? Open a GitHub issue with:
- Clear description of the feature
- Use case: What problem does it solve?
- Example: How would you use it?

We especially welcome contributions! See the development section in README.md.

---

## Appendix: Example Scenarios

### Scenario A: Weekly Team Standup

**Meeting:** 15-minute daily standup, 5 people

**Transcript excerpt:**
```
Alice: Good morning team. Let's do quick updates.

Bob: I finished the login page redesign yesterday. Moving to the dashboard today.

Carol: Working on API integration. Hit a blocker with authentication tokens. Need help from the backend team.

David: I can help Carol this afternoon. My task from yesterday is done.

Alice: Great. Bob, can you demo the login page at Friday's review?

Bob: Yes, I'll prepare a walkthrough.
```

**MeetingMind output highlights:**
- **Action Point:** Bob - Prepare login page demo for Friday review (High priority)
- **Action Point:** David - Help Carol with authentication token issue this afternoon (High priority)
- **Todo:** Schedule Friday review meeting
- **Important Mention:** Backend team - needed for authentication support
- **Tone:** Positive, high energy, excellent collaboration

**Time saved:** 10 minutes of manual note-taking and action item extraction

### Scenario B: Client Discovery Call

**Meeting:** 45-minute initial client call, 3 people (1 prospect)

**MeetingMind output highlights:**
- **Summary:** Prospect seeking to integrate our API into their e-commerce platform
- **Action Points:** 
  - Prepare technical integration proposal (You, by next Tuesday)
  - Schedule technical deep-dive with their engineering team (You, next week)
  - Send pricing for enterprise tier (Sales, by Friday)
- **Important Mentions:** 
  - Shopify - Their current platform
  - Q4 launch - Their aggressive timeline
  - $100K ARR potential - Mentioned revenue opportunity
- **Key Insights:**
  - Client is technically sophisticated, knows what they need
  - Timeline is aggressive—will need priority support
  - Competitor XYZ was mentioned negatively (integration issues)
  - Recommendation: Fast-track this opportunity with dedicated resources

**Time saved:** 20 minutes writing follow-up notes, plus ensured no action items were missed

### Scenario C: Quarterly Planning Session

**Meeting:** 2-hour strategic planning, 8 people

**MeetingMind output highlights:**
- **Summary:** Set Q4 priorities across three product areas
- **Action Points:** 12 action items assigned with clear owners and deadlines
- **Decisions Made:**
  - Mobile app redesign is top priority
  - API v3 delayed to Q1 next year
  - Hiring freeze except for critical positions
  - Budget reallocation: 60% product, 30% marketing, 10% ops
- **Meeting Tone:** Mixed—constructive but some tension around resource allocation
- **Key Insights:**
  - Pattern: Recurring concern about engineering capacity
  - Recommendation: Consider bringing in contractors for Q4 sprint
  - Pattern: Marketing and product teams not fully aligned on roadmap
  - Recommendation: Schedule biweekly sync between product and marketing leads

**Time saved:** 45+ minutes of meeting minutes compilation, plus strategic insights that might have been missed

---

**End of User Manual**

---

*MeetingMind Version 0.1.0 | Last Updated: March 2024*

*For the latest documentation, visit: https://github.com/your-org/MeetingMind*
