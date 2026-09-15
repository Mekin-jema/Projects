# Implementation Guide & API Reference

## Quick Start Guide

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- OpenAI API key
- Anthropic API key

### Installation Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd AI_Data_Agent

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
# PostgreSQL Configuration
host=localhost
port=5432
user=postgres
password=your_password
database=data_db

# LLM API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
EOF

# 5. Set up database
python feed_db.py

# 6. Run the agent
python main.py
```

---

## API Reference

### Core Agent Interface

#### `data_agent.invoke()`

Main entry point for the multi-agent system.

**Signature**:
```python
def invoke(state: dict) -> dict
```

**Parameters**:
```python
{
    "messages": List[BaseMessage],  # LangChain message objects
    "route_response": str           # Will be filled by router
}
```

**Returns**:
```python
{
    "messages": List[BaseMessage],  # Updated message history
    "route_response": "sql" | "etl",
    # ... agent-specific fields
}
```

**Basic Usage**:
```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

# SQL query
response = data_agent.invoke({
    "messages": [HumanMessage(content="Show me total rides per user")],
    "route_response": ""
})

print(response)
```

---

### SQL Agent Interface

#### `sql_analyst.invoke()`

Direct invocation of SQL agent.

**Signature**:
```python
def invoke(state: dict) -> dict
```

**Full State Schema**:
```python
{
    "messages": [],
    "user_question": str,
    "curated_question": "",
    "curated_question_with_prompt_context": "",
    "generated_sql_query": "",
    "is_safe": "No",
    "comments": "",
    "sql_query_execution_result": "",
    "final_answer": ""
}
```

**Example**:
```python
from agents.sql_analyst import sql_analyst
from langchain_core.messages import HumanMessage

input_state = {
    "messages": [],
    "user_question": "What is the average ride cost?",
    "curated_question": "",
    "curated_question_with_prompt_context": "",
    "generated_sql_query": "",
    "is_safe": "No",
    "comments": "",
    "sql_query_execution_result": "",
    "final_answer": ""
}

result = sql_analyst.invoke(input_state)

print("Generated SQL:", result["generated_sql_query"])
print("Is Safe:", result["is_safe"])
print("Results:", result["sql_query_execution_result"])
print("Answer:", result["final_answer"])
```

---

### ETL Agent Interface

#### `etl_analyst.invoke()`

Direct invocation of ETL agent.

**Signature**:
```python
def invoke(state: dict) -> dict
```

**State Schema**:
```python
{
    "messages": List[BaseMessage]
}
```

**Example**:
```python
from agents.etl_analyst import etl_analyst
from langchain_core.messages import HumanMessage

response = etl_analyst.invoke({
    "messages": [
        HumanMessage(content="""
        Extract data from https://pokeapi.co/api/v2/pokemon
        and save to data/extract in CSV format
        """)
    ]
})

print(response)
```

---

## Utility Functions API

### DatabaseUtil Class

**Location**: `utils/database.py`

#### Constructor

```python
from utils.database import DatabaseUtil

conn_details = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "dbname": "data_db"
}

db = DatabaseUtil(conn_details)
```

#### Methods

##### `schema_details(schema_name: str) -> str`

Retrieves comprehensive schema information.

```python
schema_info = db.schema_details("public")
print(schema_info)
```

**Output Format**:
```
Table: users (1000 rows)
├── Column: id
│   ├── Type: INTEGER
│   ├── Constraints: PRIMARY KEY
│   └── Sample: [1, 2, 3, 4, 5]
├── Column: name
│   ├── Type: VARCHAR
│   └── Sample: ['John', 'Jane', 'Bob']
└── Column: email
    ├── Type: VARCHAR
    └── Sample: ['john@example.com', 'jane@example.com']

Table: rides (5000 rows)
├── Column: id
│   ├── Type: INTEGER
│   └── Constraints: PRIMARY KEY
├── Column: user_id
│   ├── Type: INTEGER
│   └── Constraints: FOREIGN KEY → users.id
└── ...
```

##### `execute_query(query: str) -> dict`

Executes SQL query and returns results.

```python
result = db.execute_query("SELECT * FROM users LIMIT 5")

# Result structure:
# {
#     "rows": [{"id": 1, "name": "John", ...}, ...],
#     "columns": ["id", "name", "email", ...],
#     "row_count": 5,
#     "execution_time_ms": 234
# }
```

---

### ETLTools Class

**Location**: `utils/etl_tools.py`

#### Constructor

```python
from utils.etl_tools import ETLTools

etl = ETLTools()
```

#### Methods

##### `extract_load(url: str, output_folder: str, format: str) -> str`

Extracts data from API and saves locally.

```python
result = etl.extract_load(
    url="https://pokeapi.co/api/v2/pokemon",
    output_folder="data/extract",
    format="csv"
)

print(result)
# Output: "Data successfully extracted and saved to data/extract/extracted_data.csv"
```

**Supported Formats**:
- `"csv"`: Comma-separated values
- `"json"`: JSON lines format
- `"parquet"`: Apache Parquet binary format

**Error Handling**:
```python
try:
    result = etl.extract_load(url, output_folder, format)
    if "Error" in result:
        print(f"Failed: {result}")
    else:
        print(f"Success: {result}")
except Exception as e:
    print(f"Exception: {e}")
```

##### `transform_load_context(file_path: str) -> str`

Returns data preview for context.

```python
context = etl.transform_load_context("data/extract/extracted_data.csv")
print(context)
# Output: First 3-5 rows of the file for context
```

##### `execute_code(pandas_code: str) -> str`

Executes Python/Pandas code in sandboxed environment.

```python
code = """
import pandas as pd
df = pd.read_csv('data/extract/extracted_data.csv')
summary = df.describe()
print(summary)
"""

result = etl.execute_code(code)
print(result)
```

---

### LLM Selection API

**Location**: `utils/llm_pick.py`

#### Function: `pick_llm(level: str) -> BaseChatModel`

Returns appropriate LLM based on complexity level.

```python
from utils.llm_pick import pick_llm

# For simple tasks
llm = pick_llm("low")
response = llm.invoke("Curate this question: ...").content

# For moderate tasks
llm = pick_llm("medium")
response = llm.invoke("Generate SQL query: ...").content

# For complex reasoning
llm = pick_llm("high")
response = llm.invoke("Complex analysis: ...").content

# For multi-step workflows
llm = pick_llm("claude")
response = llm.invoke("Multi-step data transformation: ...").content
```

**Model Mapping**:
| Level | Model | Provider | Speed | Cost |
|-------|-------|----------|-------|------|
| low | GPT-5.6-Luna | OpenAI | ⚡⚡⚡⚡⚡ | $ |
| medium | GPT-5.6-Terra | OpenAI | ⚡⚡⚡ | $$ |
| high | GPT-5.6-Sol | OpenAI | ⚡⚡ | $$$ |
| claude | Claude Sonnet 5 | Anthropic | ⚡⚡⚡ | $$ |

---

## Schema Definitions

**Location**: `Models/schema.py`

### DataAgentSchema

Main router state schema.

```python
from Models.schema import DataAgentSchema
from typing import Annotated
from operator import add

class DataAgentSchema(BaseModel):
    messages: Annotated[list, add] = Field(
        ..., 
        description="List of messages to be processed by the Data agent"
    )
    route_response: str = Field(
        ..., 
        description="The response from the router indicating SQL or ETL"
    )
```

### AgentSchema

SQL agent state schema.

```python
from Models.schema import AgentSchema
from typing import Literal

class AgentSchema(BaseModel):
    messages: Annotated[list, add] = Field(...)
    user_question: str = Field(...)
    curated_question: str = Field(...)
    curated_question_with_prompt_context: str = Field(...)
    generated_sql_query: str = Field(...)
    is_safe: Literal["Yes", "No"] = Field(...)
    comments: str = Field(...)
    sql_query_execution_result: str = Field(...)
    final_answer: str = Field(...)
```

### RouterSchema

Query classification output.

```python
from Models.schema import RouterSchema
from typing import Literal

class RouterSchema(BaseModel):
    answer: Literal["sql", "etl"] = Field(
        ..., 
        description="Whether query is SQL or ETL"
    )
    comments: str = Field(
        ..., 
        description="Reasoning for classification"
    )
```

---

## Common Usage Patterns

### Pattern 1: Simple SQL Query

```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

# User wants to query the database
question = "Show me users who made more than 5 rides"

response = data_agent.invoke({
    "messages": [HumanMessage(content=question)],
    "route_response": ""
})

# Access results
if "sql_node" in response:
    print("SQL Query:", response.get("generated_sql_query"))
    print("Results:", response.get("sql_query_execution_result"))
    print("Answer:", response.get("final_answer"))
```

### Pattern 2: Complex Aggregation

```python
question = """
Calculate the total revenue per vehicle type in the last quarter,
group by type, and show top 5
"""

response = data_agent.invoke({
    "messages": [HumanMessage(content=question)],
    "route_response": ""
})

# Results include aggregation data
print("Analysis Results:", response["final_answer"])
```

### Pattern 3: Data Extraction

```python
question = """
Extract Pokemon data from https://pokeapi.co/api/v2/pokemon
and save to data/extract in CSV format
"""

response = data_agent.invoke({
    "messages": [HumanMessage(content=question)],
    "route_response": ""
})

# Check if extraction successful
print("Operation Status:", response["messages"][-1].content)
```

### Pattern 4: Data Transformation

```python
question = """
Read the Pokemon data from data/extract/extracted_data.csv,
calculate average height per type, 
and save to data/transform in JSON format
"""

response = data_agent.invoke({
    "messages": [HumanMessage(content=question)],
    "route_response": ""
})

print("Transformation Results:", response["messages"][-1].content)
```

### Pattern 5: Multi-turn Conversation

```python
from langchain_core.messages import HumanMessage, AIMessage

messages = []

# First turn
question1 = "How many rides were taken last month?"
messages.append(HumanMessage(content=question1))

response1 = data_agent.invoke({
    "messages": messages,
    "route_response": ""
})

messages.extend(response1["messages"])

# Second turn
question2 = "What's the average cost per ride?"
messages.append(HumanMessage(content=question2))

response2 = data_agent.invoke({
    "messages": messages,
    "route_response": ""
})

print("Conversation history:", response2["messages"])
```

---

## Error Handling Examples

### Example 1: Handling Unsafe Queries

```python
from agents.sql_analyst import sql_analyst
from langchain_core.messages import HumanMessage

result = sql_analyst.invoke({
    "messages": [],
    "user_question": "Delete all users",
    "curated_question": "",
    "curated_question_with_prompt_context": "",
    "generated_sql_query": "",
    "is_safe": "No",
    "comments": "",
    "sql_query_execution_result": "",
    "final_answer": ""
})

if result["is_safe"] == "No":
    print(f"Query blocked: {result['comments']}")
else:
    print(f"Results: {result['sql_query_execution_result']}")
```

### Example 2: Handling API Errors

```python
from utils.etl_tools import ETLTools

etl = ETLTools()

result = etl.extract_load(
    url="https://invalid-api.example.com/data",
    output_folder="data/extract",
    format="csv"
)

if "Failed" in result or "Error" in result:
    print(f"Error occurred: {result}")
    # Handle error appropriately
else:
    print(f"Success: {result}")
```

### Example 3: Connection Error Handling

```python
from utils.database import DatabaseUtil

try:
    db = DatabaseUtil({
        "host": "localhost",
        "port": 5432,
        "user": "wrong_user",
        "password": "wrong_password",
        "dbname": "data_db"
    })
    
    results = db.execute_query("SELECT * FROM users")
    
except ConnectionError as e:
    print(f"Database connection failed: {e}")
    # Retry logic or fallback
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Advanced Usage

### Custom LLM Configuration

```python
# Override LLM selection for specific tasks
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Use custom model directly
custom_llm = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=0,
    max_tokens=2000
)

# Use in agent
response = custom_llm.invoke("Your prompt here")
```

### Custom Tool Integration

```python
from langchain.tools import tool
from agents.etl_analyst import tools

@tool
def custom_data_tool(input_path: str, operation: str) -> str:
    """Custom data processing tool"""
    # Implementation
    return "Result"

# Add to ETL agent tools
custom_tools = tools + [custom_data_tool]
```

### Batch Processing

```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

queries = [
    "Total rides per user",
    "Average cost per ride",
    "Most active users",
    "Revenue by vehicle type"
]

results = []

for query in queries:
    response = data_agent.invoke({
        "messages": [HumanMessage(content=query)],
        "route_response": ""
    })
    results.append({
        "query": query,
        "answer": response.get("final_answer", "No answer generated")
    })

# Process results
for result in results:
    print(f"\nQ: {result['query']}")
    print(f"A: {result['answer']}")
```

---

## Performance Tips

1. **Use appropriate LLM levels** to optimize cost and speed
2. **Batch database queries** when possible
3. **Cache schema information** for repeated queries
4. **Use LIMIT in SQL** to restrict large result sets
5. **Implement pagination** for large datasets
6. **Monitor API rate limits** for external services
7. **Profile slow operations** and optimize query patterns

---

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("langchain")
logger.setLevel(logging.DEBUG)

# Now run your agent
response = data_agent.invoke({...})
```

### Inspect Agent State

```python
import json

def print_state(state):
    for key, value in state.items():
        if isinstance(value, str):
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {type(value)}")

print_state(response)
```

### Test Individual Components

```python
from utils.llm_pick import pick_llm

# Test LLM
llm = pick_llm("low")
result = llm.invoke("Test prompt")
print(result.content)

# Test database
from utils.database import DatabaseUtil
db = DatabaseUtil({...})
schema = db.schema_details("public")
print(schema)

# Test ETL
from utils.etl_tools import ETLTools
etl = ETLTools()
context = etl.transform_load_context("path/to/file.csv")
print(context)
```

---

