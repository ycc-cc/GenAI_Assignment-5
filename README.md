# Multi-Agent Customer Service System with A2A and MCP

A sophisticated multi-agent system demonstrating **Agent-to-Agent (A2A) communication** and **Model Context Protocol (MCP) integration** for automated customer service operations.

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [A2A Coordination Patterns](#a2a-coordination-patterns)
- [MCP Tools](#mcp-tools)
- [Test Scenarios](#test-scenarios)
- [Assignment Deliverables](#assignment-deliverables)

## 🎯 Overview

This project implements a coordinated multi-agent customer service system where specialized agents work together using A2A communication patterns. The system demonstrates:

1. **Task Allocation** - Router delegates tasks to specialist agents
2. **Negotiation** - Agents request context and coordinate responses
3. **Multi-Step Coordination** - Complex queries decomposed into sequential tasks

### System Components

- **Router Agent (Orchestrator)** - Analyzes queries and coordinates responses
- **Customer Data Agent (Specialist)** - Manages customer data through MCP
- **Support Agent (Specialist)** - Handles customer support and tickets
- **MCP Server** - Provides standardized data access tools

## 🏗️ System Architecture

```
Customer Query
     ↓
Router Agent (Orchestrator)
     ↓
     ├─→ Customer Data Agent ←→ MCP Server ←→ SQLite Database
     │         ↓                                      ↓
     └─→ Support Agent                          [customers]
           ↓                                     [tickets]
    Final Response
```

### A2A Communication Flow

```
┌─────────────┐
│   Router    │  Receives query, analyzes intent
│    Agent    │  
└──────┬──────┘
       │ A2A Communication
       ├──→ ┌──────────────────┐
       │    │ Customer Data    │  Accesses database via MCP
       │    │     Agent        │  Returns customer information
       │    └──────────────────┘
       │
       └──→ ┌──────────────────┐
            │  Support Agent   │  Generates support response
            │                  │  Creates/manages tickets
            └──────────────────┘
```

## ✨ Features

### A2A Coordination Patterns

1. **Task Allocation (Scenario 1)**
   - Router analyzes query intent
   - Delegates to appropriate specialist agent
   - Single-agent, straightforward execution

2. **Negotiation/Escalation (Scenario 2)**
   - Multiple agents coordinate
   - Context sharing between agents
   - Dynamic escalation based on urgency

3. **Multi-Step Coordination (Scenario 3)**
   - Complex queries decomposed
   - Sequential task execution
   - Data synthesis from multiple agents

### MCP Integration

- Standardized data access protocol
- Five required tools implemented
- Additional helper tools for complex queries
- Proper error handling and logging

### Comprehensive Logging

- Timestamp for every agent action
- Clear visualization of A2A communication
- Tool call tracking
- Success/failure indicators

## 📦 Prerequisites

- Python 3.8 or higher
- No external dependencies (uses Python standard library only)

## 🚀 Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd multi-agent-customer-service
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies (Optional)

```bash
pip install -r requirements.txt
```

**Note:** The core system uses only Python standard library modules, so no external packages are required for basic functionality.

### 4. Initialize Database

```bash
python part1_database_setup.py
```

This creates `support.db` with:
- 15 sample customers
- 25 sample support tickets  
- Proper schema with foreign keys and indexes

## 💻 Usage

### Run All Test Scenarios

```bash
python part4_test_scenarios.py
```

This demonstrates all A2A coordination patterns with 5 comprehensive tests.

### Test Individual Components

#### Test Database Setup
```bash
python part1_database_setup.py
```

#### Test MCP Server
```bash
python part2_mcp_server.py
```

#### Initialize Agents Only
```bash
python part3_agents.py
```

### Interactive Testing

```python
from part3_agents import RouterAgent, CustomerDataAgent, SupportAgent
from part2_mcp_server import MCPServer

# Initialize system
mcp_server = MCPServer("support.db")
data_agent = CustomerDataAgent(mcp_server)
support_agent = SupportAgent(mcp_server)
router = RouterAgent(data_agent, support_agent)

# Process a query
result = router.process_query(
    "Get customer information for ID 5"
)
print(result['response'])

# With context
result = router.process_query(
    "I need help upgrading my account",
    context={'customer_id': 1}
)
print(result['response'])
```

## 📁 Project Structure

```
.
├── part1_database_setup.py    # Database initialization
├── part2_mcp_server.py         # MCP server with tools
├── part3_agents.py             # Multi-agent system
├── part4_test_scenarios.py     # Comprehensive tests
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── support.db                  # SQLite database (created by setup)
```

## 🔄 A2A Coordination Patterns

### Pattern 1: Task Allocation

**Query:** "Get customer information for ID 5"

**Flow:**
```
Router Agent
    ↓ (analyzes intent: simple query)
Customer Data Agent
    ↓ (calls MCP: get_customer)
Database
    ↓ (returns data)
Router Agent
    ↓ (formats response)
User
```

### Pattern 2: Negotiation

**Query:** "I'm customer 12345 and need help upgrading my account"

**Flow:**
```
Router Agent
    ↓ (detects: needs customer context + support)
Customer Data Agent
    ↓ (gets customer info)
Router Agent  
    ↓ (passes context)
Support Agent
    ↓ (generates personalized response)
Router Agent
    ↓ (returns final response)
User
```

### Pattern 3: Multi-Step Coordination

**Query:** "Show me all active customers who have open tickets"

**Flow:**
```
Router Agent
    ↓ (decompose: complex analysis)
Customer Data Agent
    ↓ (executes complex query)
Router Agent
    ↓ (synthesizes results)
User
```

## 🔧 MCP Tools

### Required Tools (Assignment Specification)

1. **get_customer(customer_id)**
   - Retrieves customer by ID
   - Uses: customers.id

2. **list_customers(status, limit)**
   - Lists customers with optional status filter
   - Uses: customers.status

3. **update_customer(customer_id, data)**
   - Updates customer information
   - Uses: customers fields (name, email, phone, status)

4. **create_ticket(customer_id, issue, priority)**
   - Creates new support ticket
   - Uses: tickets fields

5. **get_customer_history(customer_id)**
   - Retrieves all tickets for a customer
   - Uses: tickets.customer_id

### Additional Helper Tools

6. **get_tickets_by_priority(priority, customer_ids)**
   - Filters tickets by priority
   - Supports customer ID filtering

7. **get_customers_with_open_tickets()**
   - Finds active customers with open tickets
   - For complex coordination scenarios

## 🧪 Test Scenarios

### Test 1: Simple Query (Task Allocation)
```
Query: "Get customer information for ID 5"
Pattern: Single agent, straightforward MCP call
Expected: Customer details displayed
```

### Test 2: Coordinated Query (Negotiation)
```
Query: "I'm customer 1 and need help upgrading my account"
Pattern: Data fetch + Support response
Expected: Personalized support message
```

### Test 3: Complex Query (Multi-Step)
```
Query: "Show me all active customers who have open tickets"
Pattern: Complex database query + result synthesis
Expected: List of customers with open ticket counts
```

### Test 4: Escalation (High Priority)
```
Query: "I've been charged twice, please refund immediately!"
Pattern: Urgency assessment + Customer context + Escalation
Expected: Escalated ticket with priority handling
```

### Test 5: Multi-Intent (Parallel Tasks)
```
Query: "Update my email to new@email.com and show my ticket history"
Pattern: Parallel execution of update and retrieve
Expected: Combined response with both actions completed
```

## 🎓 Assignment Deliverables Checklist

- [x] **Part 1: System Architecture**
  - [x] Router Agent (Orchestrator)
  - [x] Customer Data Agent (Specialist)
  - [x] Support Agent (Specialist)

- [x] **Part 2: MCP Integration**
  - [x] get_customer(customer_id)
  - [x] list_customers(status, limit)
  - [x] update_customer(customer_id, data)
  - [x] create_ticket(customer_id, issue, priority)
  - [x] get_customer_history(customer_id)
  - [x] Proper database schema (customers, tickets)
  - [x] Foreign key constraints
  - [x] Sample data (15 customers, 25 tickets)

- [x] **Part 3: A2A Coordination**
  - [x] Task Allocation pattern (Scenario 1)
  - [x] Negotiation pattern (Scenario 2)
  - [x] Multi-Step Coordination pattern (Scenario 3)
  - [x] Explicit logging of agent communication
  - [x] Transfer control documentation

- [x] **Test Scenarios**
  - [x] Simple Query test
  - [x] Coordinated Query test
  - [x] Complex Query test
  - [x] Escalation test
  - [x] Multi-Intent test

- [x] **Deliverables**
  - [x] Code implementation (all parts)
  - [x] README with setup instructions
  - [x] requirements.txt with proper venv separation
  - [x] Comprehensive testing demonstration
  - [x] Query output captured

## 📊 Database Schema

### Customers Table
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
name            TEXT NOT NULL
email           TEXT
phone           TEXT
status          TEXT CHECK(status IN ('active', 'disabled'))
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### Tickets Table
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
customer_id     INTEGER NOT NULL
issue           TEXT NOT NULL
status          TEXT CHECK(status IN ('open', 'in_progress', 'resolved'))
priority        TEXT CHECK(priority IN ('low', 'medium', 'high'))
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
```

## 📈 Sample Output

```
🚀 MULTI-AGENT CUSTOMER SERVICE SYSTEM - TEST SCENARIOS
================================================================================

TEST 1: Simple Data Query (Task Allocation)
Query: 'Get customer information for ID 5'
================================================================================

[17:01:01.377] [RouterAgent] INFO: Received query: 'Get customer information for ID 5'
[17:01:01.377] [RouterAgent] INFO: Detected intent: simple_data_query
[17:01:01.377] [RouterAgent] INFO: Pattern: TASK ALLOCATION (Simple Query)
[17:01:01.377] [RouterAgent] INFO: → CustomerDataAgent: get_customer(5)
[17:01:01.377] [CustomerDataAgent] INFO: Processing task: get_customer
[MCP] get_customer called with customer_id=5
[MCP] ✓ Customer 5 found: Charlie Brown
[17:01:01.380] [CustomerDataAgent] INFO: ✓ Task completed: get_customer
[17:01:01.380] [RouterAgent] INFO: ← CustomerDataAgent: Data received
[17:01:01.380] [RouterAgent] INFO: ✓ Query completed successfully

📋 FINAL RESPONSE:
Customer Information:
  ID: 5
  Name: Charlie Brown
  Email: charlie.brown@email.com
  Phone: +1-555-0105
  Status: active
```

## 🛠️ Troubleshooting

### Database Not Found
```bash
# Run database setup
python part1_database_setup.py
```

### Import Errors
```bash
# Ensure files are in same directory
ls -la part*.py

# Check Python path
python -c "import sys; print(sys.path)"
```

### Permission Issues
```bash
# Make files executable (Unix/Linux/Mac)
chmod +x part*.py
```

## 🚀 Extension Ideas

1. **Add More Specialist Agents**
   - Billing Agent for payment processing
   - Analytics Agent for insights
   - Notification Agent for alerts

2. **Enhanced A2A Patterns**
   - Parallel agent execution
   - Agent voting/consensus
   - Dynamic agent discovery

3. **Real-time Features**
   - WebSocket support for live updates
   - Streaming responses
   - Real-time ticket status

4. **ML Integration**
   - Intent classification with ML
   - Sentiment analysis
   - Predictive ticket priority

5. **Production Features**
   - Authentication and authorization
   - Rate limiting
   - Caching layer
   - Metrics and monitoring

## 📝 Learning Outcomes

### What This Project Demonstrates

1. **A2A Communication**
   - Standardized agent interaction patterns
   - Context sharing between agents
   - Dynamic task routing

2. **MCP Integration**
   - External data access through standard protocol
   - Tool-based architecture
   - Clean separation of concerns

3. **Multi-Agent Coordination**
   - Task decomposition strategies
   - Agent specialization benefits
   - Orchestration patterns

4. **Software Engineering**
   - Clean code structure
   - Comprehensive logging
   - Error handling
   - Testability

## 📄 License

This project is created for educational purposes as part of a course assignment.

## 🙏 Acknowledgments

- Based on A2A coordination patterns from Google's ADK
- Assignment specifications from course materials
- Database schema from provided specification

## 📧 Support

For questions about this implementation:
- Review the code documentation
- Check the comprehensive logging output
- Refer to course materials
- Contact your course instructor

---

**Built with Python • SQLite • A2A Pattern • MCP Protocol**

*Assignment: Multi-Agent Customer Service System with A2A and MCP*
