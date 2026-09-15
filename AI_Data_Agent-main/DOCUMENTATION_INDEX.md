# Documentation Index & Quick Reference

## 📚 Complete Documentation Overview

This project includes comprehensive documentation across multiple files. Here's a guide to find what you need:

### 📖 Main Documentation Files

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System Architecture & Design
   - Executive summary and project overview
   - High-level system architecture with diagrams
   - Component overview and responsibilities
   - Complete data flow diagrams
   - Technology stack details
   - Module breakdown with detailed descriptions
   - Configuration and setup instructions
   - Performance considerations and scalability
   - **Best for**: Understanding how the system works as a whole

2. **[AGENT_WORKFLOWS.md](AGENT_WORKFLOWS.md)** - Agent Detailed Workflows
   - SQL Analyst Agent deep dive (6-stage pipeline)
   - ETL Analyst Agent details
   - Complete agent state management
   - Error handling strategies
   - Real-world use cases
   - **Best for**: Understanding how agents process requests step-by-step

3. **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - API Reference & Usage
   - Quick start guide with installation steps
   - Complete API reference for all modules
   - Utility functions documentation
   - Schema definitions
   - Common usage patterns
   - Advanced usage examples
   - Error handling examples
   - Debugging techniques
   - **Best for**: Building applications on top of the system

4. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production Deployment
   - Local development setup
   - Docker and container deployment
   - Kubernetes deployment
   - Cloud provider deployment (AWS, GCP, Azure)
   - Production architecture
   - Best practices and security
   - Performance optimization techniques
   - Comprehensive troubleshooting guide
   - Monitoring and logging setup
   - **Best for**: Deploying to production and troubleshooting issues

---

## 🚀 Quick Start

### Installation (5 minutes)
```bash
git clone <repo-url> && cd AI_Data_Agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env  # Set your API keys
python feed_db.py
python main.py
```

### Basic Usage
```python
from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

response = data_agent.invoke({
    "messages": [HumanMessage(content="Show top 5 users by rides")],
    "route_response": ""
})
print(response)
```

---

## 🎯 Quick Reference by Use Case

### I want to...

#### Understand the System
- **Project Overview** → [ARCHITECTURE.md - Executive Summary](ARCHITECTURE.md#executive-summary)
- **How Components Work** → [ARCHITECTURE.md - Component Overview](ARCHITECTURE.md#component-overview)
- **System Diagrams** → [ARCHITECTURE.md - System Architecture](ARCHITECTURE.md#system-architecture)

#### Write SQL Queries
- **SQL Agent Workflow** → [AGENT_WORKFLOWS.md - SQL Agent Deep Dive](AGENT_WORKFLOWS.md#sql-analyst-agent-deep-dive)
- **Usage Examples** → [IMPLEMENTATION_GUIDE.md - Pattern 1: Simple SQL Query](IMPLEMENTATION_GUIDE.md#pattern-1-simple-sql-query)
- **Safety Validation** → [AGENT_WORKFLOWS.md - Stage 4: Safety Validation](AGENT_WORKFLOWS.md#stage-4-safety-validation)

#### Extract/Transform Data
- **ETL Agent Workflow** → [AGENT_WORKFLOWS.md - ETL Agent Deep Dive](AGENT_WORKFLOWS.md#etl-analyst-agent-deep-dive)
- **Use Cases** → [AGENT_WORKFLOWS.md - ETL Use Cases](AGENT_WORKFLOWS.md#etl-use-cases)
- **API Reference** → [IMPLEMENTATION_GUIDE.md - ETL Tools Class](IMPLEMENTATION_GUIDE.md#etltools-class)

#### Deploy to Production
- **Docker Setup** → [DEPLOYMENT_GUIDE.md - Docker Deployment](DEPLOYMENT_GUIDE.md#docker-deployment)
- **Kubernetes** → [DEPLOYMENT_GUIDE.md - Kubernetes Deployment](DEPLOYMENT_GUIDE.md#kubernetes-deployment)
- **Cloud Services** → [DEPLOYMENT_GUIDE.md - Cloud Deployment Options](DEPLOYMENT_GUIDE.md#cloud-deployment-options)

#### Debug Issues
- **Troubleshooting** → [DEPLOYMENT_GUIDE.md - Troubleshooting Guide](DEPLOYMENT_GUIDE.md#troubleshooting-guide)
- **Error Handling** → [IMPLEMENTATION_GUIDE.md - Error Handling Examples](IMPLEMENTATION_GUIDE.md#error-handling-examples)
- **Logging Setup** → [DEPLOYMENT_GUIDE.md - Monitoring & Logging](DEPLOYMENT_GUIDE.md#monitoring--logging)

#### Optimize Performance
- **Performance Tips** → [ARCHITECTURE.md - Performance Considerations](ARCHITECTURE.md#performance-considerations)
- **Optimization Strategies** → [DEPLOYMENT_GUIDE.md - Performance Optimization](DEPLOYMENT_GUIDE.md#performance-optimization)
- **Caching** → [DEPLOYMENT_GUIDE.md - Caching Strategy](DEPLOYMENT_GUIDE.md#2-caching-strategy)

#### Extend the System
- **Custom Tools** → [IMPLEMENTATION_GUIDE.md - Custom Tool Integration](IMPLEMENTATION_GUIDE.md#custom-tool-integration)
- **Future Enhancements** → [ARCHITECTURE.md - Future Enhancements](ARCHITECTURE.md#future-enhancements)
- **Best Practices** → [DEPLOYMENT_GUIDE.md - Best Practices](DEPLOYMENT_GUIDE.md#best-practices)

---

## 📊 Architecture Quick Reference

### System Components

```
┌─────────────────────────────────────────┐
│        Main Data Agent (Router)         │
│  - Classifies query type (SQL / ETL)   │
│  - Routes to appropriate agent          │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   ┌───▼────────┐ ┌────▼──────┐
   │ SQL Agent  │ │ ETL Agent  │
   │ (6 stages) │ │ (3 stages) │
   └────────────┘ └────────────┘
```

### Data Flow Summary

**SQL Path**: Question → Curate → Schema → Generate SQL → Validate → Execute → Format Answer

**ETL Path**: Request → Parse → Extract/Transform → Generate Code → Execute → Save

### Key Technologies

| Component | Technology |
|-----------|-----------|
| **Orchestration** | LangGraph |
| **LLM Integration** | LangChain |
| **Databases** | PostgreSQL |
| **Models** | Pydantic |
| **LLMs** | OpenAI (GPT-5.6) + Anthropic (Claude) |

---

## 🔧 API Quick Reference

### Main Entry Point
```python
data_agent.invoke({
    "messages": [HumanMessage(content="your query")],
    "route_response": ""
})
```

### Database Utility
```python
from utils.database import DatabaseUtil

db = DatabaseUtil(conn_details)
schema_info = db.schema_details("public")
results = db.execute_query("SELECT * FROM users")
```

### ETL Tools
```python
from utils.etl_tools import ETLTools

etl = ETLTools()
etl.extract_load(url, output_folder, format)
etl.transform_load_context(file_path)
etl.execute_code(pandas_code)
```

### LLM Selection
```python
from utils.llm_pick import pick_llm

llm = pick_llm("low")      # Fast, cheap
llm = pick_llm("medium")   # Balanced
llm = pick_llm("high")     # Premium
llm = pick_llm("claude")   # Multi-step tasks
```

---

## 📋 Common Tasks Checklist

### Getting Started
- [ ] Read [ARCHITECTURE.md - Overview](ARCHITECTURE.md#executive-summary)
- [ ] Follow [IMPLEMENTATION_GUIDE.md - Quick Start](IMPLEMENTATION_GUIDE.md#quick-start-guide)
- [ ] Run first query: [IMPLEMENTATION_GUIDE.md - Pattern 1](IMPLEMENTATION_GUIDE.md#pattern-1-simple-sql-query)

### SQL Operations
- [ ] Understand query stages: [AGENT_WORKFLOWS.md - SQL Stages](AGENT_WORKFLOWS.md#workflow-stages)
- [ ] Learn safety validation: [AGENT_WORKFLOWS.md - Stage 4](AGENT_WORKFLOWS.md#stage-4-safety-validation)
- [ ] Try example queries: [IMPLEMENTATION_GUIDE.md - Patterns 1-2](IMPLEMENTATION_GUIDE.md#common-usage-patterns)

### ETL Operations
- [ ] Understand ETL workflow: [AGENT_WORKFLOWS.md - ETL Workflow](AGENT_WORKFLOWS.md#etl-analyst-agent-deep-dive)
- [ ] Learn tools: [AGENT_WORKFLOWS.md - Core Components](AGENT_WORKFLOWS.md#core-components)
- [ ] Try ETL example: [IMPLEMENTATION_GUIDE.md - Pattern 3-4](IMPLEMENTATION_GUIDE.md#pattern-3-data-extraction)

### Production Deployment
- [ ] Review architecture: [DEPLOYMENT_GUIDE.md - Production Architecture](DEPLOYMENT_GUIDE.md#production-architecture)
- [ ] Choose deployment method: [DEPLOYMENT_GUIDE.md - Deployment Options](DEPLOYMENT_GUIDE.md#deployment-guide)
- [ ] Set up monitoring: [DEPLOYMENT_GUIDE.md - Monitoring](DEPLOYMENT_GUIDE.md#monitoring--logging)

### Troubleshooting
- [ ] Check [DEPLOYMENT_GUIDE.md - Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting-guide)
- [ ] Review [IMPLEMENTATION_GUIDE.md - Error Handling](IMPLEMENTATION_GUIDE.md#error-handling-examples)
- [ ] Check logs: [DEPLOYMENT_GUIDE.md - Structured Logging](DEPLOYMENT_GUIDE.md#structured-logging)

---

## 🔗 Navigation Guide

### By Document

**ARCHITECTURE.md**
- System overview and high-level design
- Technology stack and dependencies
- Module organization
- Scalability considerations

**AGENT_WORKFLOWS.md**
- Detailed step-by-step agent processing
- State management and data flow
- Error scenarios and handling
- Real-world examples

**IMPLEMENTATION_GUIDE.md**
- API reference documentation
- Code examples and patterns
- Debugging techniques
- Advanced usage scenarios

**DEPLOYMENT_GUIDE.md**
- Installation and setup
- Production deployment options
- Best practices and security
- Performance optimization
- Troubleshooting guide

### By Topic

**Architecture & Design**
- [ARCHITECTURE.md - System Architecture](ARCHITECTURE.md#system-architecture)
- [ARCHITECTURE.md - Component Overview](ARCHITECTURE.md#component-overview)
- [ARCHITECTURE.md - Module Breakdown](ARCHITECTURE.md#module-breakdown)

**Workflows & Processing**
- [AGENT_WORKFLOWS.md - SQL Agent](AGENT_WORKFLOWS.md#sql-analyst-agent-deep-dive)
- [AGENT_WORKFLOWS.md - ETL Agent](AGENT_WORKFLOWS.md#etl-analyst-agent-deep-dive)
- [AGENT_WORKFLOWS.md - State Management](AGENT_WORKFLOWS.md#state-management)

**Development & Integration**
- [IMPLEMENTATION_GUIDE.md - API Reference](IMPLEMENTATION_GUIDE.md#api-reference)
- [IMPLEMENTATION_GUIDE.md - Usage Patterns](IMPLEMENTATION_GUIDE.md#common-usage-patterns)
- [IMPLEMENTATION_GUIDE.md - Code Examples](IMPLEMENTATION_GUIDE.md#advanced-usage)

**Operations & Production**
- [DEPLOYMENT_GUIDE.md - Deployment](DEPLOYMENT_GUIDE.md#deployment-guide)
- [DEPLOYMENT_GUIDE.md - Best Practices](DEPLOYMENT_GUIDE.md#best-practices)
- [DEPLOYMENT_GUIDE.md - Monitoring](DEPLOYMENT_GUIDE.md#monitoring--logging)

---

## 📞 Support & Help

### Frequently Asked Questions

**Q: How do I write a good query for the SQL agent?**
A: → See [DEPLOYMENT_GUIDE.md - Query Design](DEPLOYMENT_GUIDE.md#1-query-design)

**Q: Why did my SQL query get blocked?**
A: → See [AGENT_WORKFLOWS.md - Safety Validation](AGENT_WORKFLOWS.md#stage-4-safety-validation)

**Q: How do I extract data from an API?**
A: → See [AGENT_WORKFLOWS.md - ETL Use Case 1](AGENT_WORKFLOWS.md#use-case-1-simple-data-extraction)

**Q: How do I deploy to production?**
A: → See [DEPLOYMENT_GUIDE.md - Deployment Guide](DEPLOYMENT_GUIDE.md#deployment-guide)

**Q: My database connection is failing, what should I do?**
A: → See [DEPLOYMENT_GUIDE.md - Database Issues](DEPLOYMENT_GUIDE.md#database-issues)

**Q: How do I improve performance?**
A: → See [DEPLOYMENT_GUIDE.md - Performance Optimization](DEPLOYMENT_GUIDE.md#performance-optimization)

---

## 📈 Learning Path

### Beginner Path (Estimated: 2-3 hours)
1. Read [ARCHITECTURE.md - Executive Summary](ARCHITECTURE.md#executive-summary)
2. Follow [IMPLEMENTATION_GUIDE.md - Quick Start](IMPLEMENTATION_GUIDE.md#quick-start-guide)
3. Try basic queries with [IMPLEMENTATION_GUIDE.md - Pattern 1](IMPLEMENTATION_GUIDE.md#pattern-1-simple-sql-query)
4. Explore ETL with [AGENT_WORKFLOWS.md - ETL Use Cases](AGENT_WORKFLOWS.md#etl-use-cases)

### Intermediate Path (Estimated: 1-2 hours)
1. Study [AGENT_WORKFLOWS.md - SQL Workflow](AGENT_WORKFLOWS.md#workflow-stages)
2. Learn [AGENT_WORKFLOWS.md - Safety Validation](AGENT_WORKFLOWS.md#stage-4-safety-validation)
3. Try [IMPLEMENTATION_GUIDE.md - Advanced Usage](IMPLEMENTATION_GUIDE.md#advanced-usage)
4. Review [DEPLOYMENT_GUIDE.md - Best Practices](DEPLOYMENT_GUIDE.md#best-practices)

### Advanced Path (Estimated: 2-3 hours)
1. Deep dive [DEPLOYMENT_GUIDE.md - Production Architecture](DEPLOYMENT_GUIDE.md#production-architecture)
2. Set up [DEPLOYMENT_GUIDE.md - Monitoring](DEPLOYMENT_GUIDE.md#monitoring--logging)
3. Implement [DEPLOYMENT_GUIDE.md - Performance Optimization](DEPLOYMENT_GUIDE.md#performance-optimization)
4. Study [IMPLEMENTATION_GUIDE.md - Custom Integration](IMPLEMENTATION_GUIDE.md#custom-tool-integration)

---

## 🎓 Key Concepts

### Query Routing
The main agent classifies incoming queries as either:
- **SQL**: Database queries, aggregations, analysis
- **ETL**: Data extraction, transformation, loading

### Agent Stages
Each agent has processing stages:
- **SQL Agent**: Curate → Context → Generate → Validate → Execute → Answer (6 stages)
- **ETL Agent**: Parse → Extract/Transform → Execute → Save (3-4 stages)

### LLM Selection
Different models used based on complexity:
- Simple tasks → Faster, cheaper model
- Complex reasoning → Premium model
- Multi-step workflows → Claude for consistency

### Safety First
All SQL queries validated before execution:
- Read-only operations only
- No INSERT, UPDATE, DELETE, DROP
- Protection against SQL injection

### Scalability
Designed for production scale:
- Connection pooling
- Response caching
- Async processing
- Load balancing

---

## 📝 Notes

- All documentation uses Mermaid diagrams for visual representation
- Code examples are production-ready
- Configuration uses environment variables
- Security best practices are throughout
- Error handling patterns are documented

---

## Version Information

- **Project Version**: 0.1.0
- **Python Version**: 3.12+
- **LangGraph**: 1.2.11+
- **LangChain**: 1.3.14+
- **Documentation Date**: 2024

---

**Last Updated**: 2024-08-30
**Total Documentation Pages**: 4 comprehensive guides
**Total Diagrams**: 15+ Mermaid diagrams
**Code Examples**: 50+ production-ready examples

