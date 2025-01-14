# LLM Evals

A framework for evaluating the performance of Large Language Model (LLM) pipelines for custom applications.

## Repo Build Progress
1. [x] Define a pipeline:
 - Select a model.
 - Select a system prompt.
 - Select few-shot examples.
 - Set up logging.
 - [x] Add support for Gemini and Claude pipelines.

2. [x] Set up a chatbot app.

3. [x] Create an Evaluation Dataset:
 - Create a task.
 - Select the evaluation method: ground truth or criteria-based scoring.
 - Enter the ground truth response OR criteria for scoring.
 - Select between a) llm as a judge b) human as a judge. (default to llm as a judge)
 - Save the evaluation dataset

4. [x] Run an evaluation on a pipeline and evaluation dataset.
 - Run the pipeline on the evaluation dataset.
 - Save the evaluation and pipeline metadata.

5. Coming later
 - Suupport for document-enabled pipelines.
 - Create evaluation datasets from logs.
 - Save customer feedback/comments.
 - Iterate on response quality using human feedback.

 ## Getting Started

 ```
 pip install uv
 uv venv
 source .venv/bin/activate
 uv pip install -r requirements.txt
 ```

 ## Pipeline Configuration
 The purpose of evaluations is to benchmark the quality of answers produced by AI.

 We'll use `pipeline` to refer to the means by which answers are produced. A pipeline can be used to power a chatbot assistant OR it can be called directly to run evaluations. It's important that there be consistency between the two.

 Pipelines are defined in YAML files under `app/configs/pipelines/`. For now, each pipeline config specifies:

 - Basic metadata (name, version, description)
 - API configuration
 - Model selection and version
 - Parameters (temperature, system message, etc.)

 Later, we can look at adding in tools or document retrieval to the configuration.

 ### Managing Pipelines and Running the Assistant
 ```bash
 # List available pipelines
 uv run -m app.main --list

 # Set active pipeline
 uv run -m app.main --set-active gpt-4o-mini-pipe

 # Show active pipeline details
 uv run -m app.main --show-active

 # Run the active pipeline
 uv run -m app.main --run
 ```

 ### Creating New Pipelines
 Create a new YAML file in `app/configs/pipelines/` following this structure:
 ```yaml
 name: "Pipeline Name"
 version: "1.0.0"
 created_at: "2024-01-08"
 last_modified: "2024-01-08"
 description: "Pipeline description"

 components:
    api: "openai"
    model: "model-name"

parameters:
    temperature: 0.7
    system_message: |
        System message for the model...
```

Supported API Types:
1. OpenAI (`api: "openai"`):
    - Requires `OPENAI_API_KEY` in .env
    - Models: gpt-4, gpt-4-turbo, gpt-3.5-turbo, etc.

2. Google (`api: "google"`):
    - Requires `GOOGLE_API_KEY` in .env
    - Models: gemini-pro, gemini-pro-vision, gemini-2.0-flash-exp

3. Anthropic (`api: "anthropic"`):
    - Requires `ANTHROPIC_API_KEY` in .env
    - Models: claude-3-opus, claude-3-sonnet, claude-3-haiku

For later:
    - Create few-shot examples from logs.
    - Store feedback.
    - Create hints from logs.


## Database Setup
```bash
# First backup existing .env if it exists
cp .env .env.backup 2>dev/null || true

# Append database config
cat << EOF >> .env

# Database Configuration
POSTGRES_DB=advanced_evals
POSTGRES_USER=eval_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# API Keys (uncomment and your key for the API you're using)
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_API_KEY=your_gemini_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
EOF

# Then edit the passwords and API keys in .env:
nano .env # or use your preferred editor

# Load the environment variables:
source .env
```

1. Install PostgreSQL if you haven't already:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOs with Homebrew
brew install postgresql # or latest version
brew services start postgresql
```

2. Create user and database:
```bash
source .env

# Ubuntu/Debian
sudo -u postgres psql -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE $POSTGRES_DB OWNER '$POSTGRES_USER';"

# macOs
psql postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
psql postgres -c "CREATE DATABASE $POSTGRES_DB OWNER '$POSTGRES_USER';"
```

### Database Management

To inspect the database tables:
```bash
source .env
# Connect to the database
psql $POSTGRES_DB -U $POSTGRES_USER

# In psql:
\dt               # List all tables
\d response_logs  # Show response_logs table structure
\d migrations     # Show migrations table structure

# Some useful queries (Count all responses, show 5 most recent responses):
SELECT COUNT(*) FROM response_logs;
SELECT * FROM response_logs ORDER BY timestamp DESC LIMIT 5;

# View most recent response:
SELECT * FROM response_logs ORDER BY timestamp DESC LIMIT 1;

# List all evaluation runs
SELECT r.id as run_id, 
       d.name as dataset,
       r.pipeline_name,
       r.total_tasks,
       r.passing_tasks,
       r.average_score,
       r.created_at
FROM evaluation_runs r
JOIN evaluation_datasets d ON r.dataset_id = d.id
ORDER BY r.created_at DESC

# View all runs for a specific dataset
SELECT r.id as run_id,
       r.pipeline_name,
       r.pipeline_version,
       r.judge_pipeline_name,
       r.total_tasks,
       r.passing_tasks,
       r.average_score,
       r.created_at,
       (EXTRACT(EPOCH FROM (r.completed_at - r.created_at))) as duration_seconds
FROM evaluation_runs r
JOIN evaluation_datasets d ON r.dataset_id = d.id
WHERE d.name = 'tricky-touch'
ORDER BY r.created_at DESC;

# Quit psql
\q
```

### Creating and Managing Evaluation Datasets
To work with evaluation datasets:
```bash
# Create a new evaluation dataset or append to existing
uv run -m app.main --create-eval-dataset

# Edit an existing task in a dataset
uv run -m app.main --edit-task
```

The CLI will guide you through:
1. Choosing to create new or append to existing dataset
2. Setting metadata (name, version, description)
3. Selecting judge type (LLM, human)
4. Adding tasks/questions with either:
    - Ground truth responses
    - Criteria-based scoring rules
5. Options to add more questions to the dataset

When editing a task (--edit-task):
1. Select the dataset from the list
2. Choose the task number to edit
3. View and modify the question and evaluation criteria
4. Review and confirm your changes

### Running Evaluations
To evaluate a pipeline's performance on a dataset:
```bash
# Run evaluation
uv run -m app.main --evaluate
```

The CLI will:
1. Show available datasets and prompt for selection
2. Show available pipelines and prompt for selection (or use active pipeline)
3. Run the evaluation using the appropriate judge

