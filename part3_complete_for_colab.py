"""
Complete Part 3: Multi-Agent System with A2A Coordination
All-in-One Version for Colab/Jupyter Notebook

This file contains:
1. MCP Server (from Part 2)
2. All Three Agents (Router, Customer Data, Support)
3. A2A Coordination Patterns
4. Test Scenarios

Run this after setting up the database with Part 1.
"""

import sqlite3
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime


# ============================================================================
# MCP SERVER (Part 2)
# ============================================================================

class MCPServer:
    """MCP Server for customer database operations"""
    
    def __init__(self, db_path: str = "support.db"):
        """Initialize MCP server with database path."""
        self.db_path = db_path
        print(f"✓ MCP Server initialized with database: {db_path}")
    
    def _get_connection(self):
        """Create database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def _dict_factory(self, cursor, row):
        """Convert database row to dictionary."""
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}
    
    # ========================================================================
    # REQUIRED MCP TOOLS
    # ========================================================================
    
    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get customer information by ID."""
        print(f"[MCP] get_customer called with customer_id={customer_id}")
        
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM customers WHERE id = ?
            """, (customer_id,))
            
            result = cursor.fetchone()
            
            if result:
                print(f"[MCP] ✓ Customer {customer_id} found: {result['name']}")
                return {'success': True, 'customer': result}
            else:
                print(f"[MCP] ✗ Customer {customer_id} not found")
                return {'success': False, 'error': f'Customer {customer_id} not found'}
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def list_customers(self, status: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """List customers with optional status filter."""
        print(f"[MCP] list_customers called with status={status}, limit={limit}")
        
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        
        try:
            if status:
                cursor.execute("""
                    SELECT id, name, email, phone, status, created_at, updated_at
                    FROM customers WHERE status = ? LIMIT ?
                """, (status, limit))
            else:
                cursor.execute("""
                    SELECT id, name, email, phone, status, created_at, updated_at
                    FROM customers LIMIT ?
                """, (limit,))
            
            results = cursor.fetchall()
            print(f"[MCP] ✓ Found {len(results)} customers")
            
            return {'success': True, 'customers': results, 'count': len(results)}
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information."""
        print(f"[MCP] update_customer called for customer_id={customer_id} with data={data}")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if customer exists
            cursor.execute('SELECT id FROM customers WHERE id = ?', (customer_id,))
            if not cursor.fetchone():
                print(f"[MCP] ✗ Customer {customer_id} not found")
                return {'success': False, 'error': f'Customer {customer_id} not found'}
            
            # Build update query
            allowed_fields = ['name', 'email', 'phone', 'status']
            update_fields = []
            values = []
            
            for field, value in data.items():
                if field in allowed_fields:
                    update_fields.append(f'{field} = ?')
                    values.append(value)
            
            if not update_fields:
                print(f"[MCP] ✗ No valid fields to update")
                return {'success': False, 'error': 'No valid fields to update'}
            
            values.append(customer_id)
            query = f"UPDATE customers SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            
            print(f"[MCP] ✓ Customer {customer_id} updated successfully")
            return {'success': True, 'customer_id': customer_id, 'updated_fields': list(data.keys())}
        except Exception as e:
            conn.rollback()
            print(f"[MCP] ✗ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def create_ticket(self, customer_id: int, issue: str, priority: str = 'medium') -> Dict[str, Any]:
        """Create a new support ticket."""
        print(f"[MCP] create_ticket called for customer_id={customer_id}, priority={priority}")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Validate customer exists
            cursor.execute('SELECT id FROM customers WHERE id = ?', (customer_id,))
            if not cursor.fetchone():
                print(f"[MCP] ✗ Customer {customer_id} not found")
                return {'success': False, 'error': f'Customer {customer_id} not found'}
            
            # Validate priority
            if priority not in ['low', 'medium', 'high']:
                print(f"[MCP] ⚠ Invalid priority '{priority}', defaulting to 'medium'")
                priority = 'medium'
            
            cursor.execute("""
                INSERT INTO tickets (customer_id, issue, status, priority)
                VALUES (?, ?, 'open', ?)
            """, (customer_id, issue, priority))
            
            ticket_id = cursor.lastrowid
            conn.commit()
            
            print(f"[MCP] ✓ Ticket #{ticket_id} created successfully")
            return {
                'success': True,
                'ticket_id': ticket_id,
                'customer_id': customer_id,
                'issue': issue,
                'priority': priority,
                'status': 'open'
            }
        except Exception as e:
            conn.rollback()
            print(f"[MCP] ✗ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        """Get all tickets for a customer."""
        print(f"[MCP] get_customer_history called for customer_id={customer_id}")
        
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        
        try:
            # Verify customer exists
            cursor.execute('SELECT id, name FROM customers WHERE id = ?', (customer_id,))
            customer = cursor.fetchone()
            
            if not customer:
                print(f"[MCP] ✗ Customer {customer_id} not found")
                return {'success': False, 'error': f'Customer {customer_id} not found'}
            
            # Get all tickets
            cursor.execute("""
                SELECT id, customer_id, issue, status, priority, created_at
                FROM tickets WHERE customer_id = ? ORDER BY created_at DESC
            """, (customer_id,))
            
            tickets = cursor.fetchall()
            print(f"[MCP] ✓ Found {len(tickets)} tickets for customer {customer_id}")
            
            return {
                'success': True,
                'customer_id': customer_id,
                'customer_name': customer['name'],
                'tickets': tickets,
                'ticket_count': len(tickets)
            }
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    # ========================================================================
    # HELPER TOOLS FOR COMPLEX QUERIES
    # ========================================================================
    
    def get_tickets_by_priority(self, priority: str, customer_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get tickets by priority, optionally filtered by customer IDs."""
        print(f"[MCP] get_tickets_by_priority called with priority={priority}")
        
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        
        try:
            if customer_ids:
                placeholders = ','.join('?' * len(customer_ids))
                query = f"""
                    SELECT t.id, t.customer_id, c.name as customer_name, 
                           t.issue, t.status, t.priority, t.created_at
                    FROM tickets t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE t.priority = ? AND t.customer_id IN ({placeholders})
                    ORDER BY t.created_at DESC
                """
                cursor.execute(query, [priority] + customer_ids)
            else:
                cursor.execute("""
                    SELECT t.id, t.customer_id, c.name as customer_name,
                           t.issue, t.status, t.priority, t.created_at
                    FROM tickets t
                    JOIN customers c ON t.customer_id = c.id
                    WHERE t.priority = ?
                    ORDER BY t.created_at DESC
                """, (priority,))
            
            tickets = cursor.fetchall()
            print(f"[MCP] ✓ Found {len(tickets)} {priority}-priority tickets")
            
            return {'success': True, 'priority': priority, 'tickets': tickets, 'count': len(tickets)}
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_customers_with_open_tickets(self) -> Dict[str, Any]:
        """Get all active customers who have open tickets."""
        print(f"[MCP] get_customers_with_open_tickets called")
        
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT DISTINCT c.id, c.name, c.email, c.status,
                       COUNT(t.id) as open_ticket_count
                FROM customers c
                JOIN tickets t ON c.id = t.customer_id
                WHERE c.status = 'active' AND t.status = 'open'
                GROUP BY c.id, c.name, c.email, c.status
                ORDER BY open_ticket_count DESC
            """)
            
            results = cursor.fetchall()
            print(f"[MCP] ✓ Found {len(results)} active customers with open tickets")
            
            return {'success': True, 'customers': results, 'count': len(results)}
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()


# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class Agent:
    """Base agent class with logging and coordination capabilities."""
    
    def __init__(self, name: str, role: str, description: str):
        """Initialize agent with name, role, and description."""
        self.name = name
        self.role = role
        self.description = description
        self.logs = []
        self.log(f"Initialized - Role: {role}")
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent activity with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{self.name}] {level}: {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def get_card(self) -> Dict[str, Any]:
        """Return agent card with capabilities (similar to A2A agent card)."""
        return {
            'name': self.name,
            'role': self.role,
            'description': self.description
        }


# ============================================================================
# CUSTOMER DATA AGENT (Specialist)
# ============================================================================

class CustomerDataAgent(Agent):
    """
    Agent responsible for customer data operations via MCP.
    Handles all database operations related to customers and their data.
    """
    
    def __init__(self, mcp_server: MCPServer):
        """Initialize Customer Data Agent."""
        super().__init__(
            name="CustomerDataAgent",
            role="Data Specialist",
            description="Manages customer data operations including retrieval, updates, and history tracking"
        )
        self.mcp_server = mcp_server
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process data-related tasks."""
        action = task.get('action')
        self.log(f"Processing task: {action}")
        
        try:
            # Route to appropriate MCP tool based on action
            if action == 'get_customer':
                result = self._get_customer(task)
            
            elif action == 'list_customers':
                result = self._list_customers(task)
            
            elif action == 'update_customer':
                result = self._update_customer(task)
            
            elif action == 'get_customer_history':
                result = self._get_history(task)
            
            elif action == 'get_customers_with_open_tickets':
                result = self._get_customers_with_open_tickets()
            
            else:
                result = {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
            
            # Log result
            if result.get('success'):
                self.log(f"✓ Task completed: {action}")
            else:
                self.log(f"✗ Task failed: {result.get('error')}", "ERROR")
            
            return result
            
        except Exception as e:
            self.log(f"✗ Exception: {str(e)}", "ERROR")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_customer(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer by ID using MCP."""
        customer_id = task.get('customer_id')
        return self.mcp_server.get_customer(customer_id)
    
    def _list_customers(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """List customers with optional filter using MCP."""
        status = task.get('status')
        limit = task.get('limit', 10)
        return self.mcp_server.list_customers(status, limit)
    
    def _update_customer(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information using MCP."""
        customer_id = task.get('customer_id')
        data = task.get('data', {})
        return self.mcp_server.update_customer(customer_id, data)
    
    def _get_history(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer ticket history using MCP."""
        customer_id = task.get('customer_id')
        return self.mcp_server.get_customer_history(customer_id)
    
    def _get_customers_with_open_tickets(self) -> Dict[str, Any]:
        """Get active customers with open tickets using MCP."""
        return self.mcp_server.get_customers_with_open_tickets()


# ============================================================================
# SUPPORT AGENT (Specialist)
# ============================================================================

class SupportAgent(Agent):
    """
    Agent responsible for customer support operations.
    Handles ticket creation, support responses, and issue escalation.
    """
    
    def __init__(self, mcp_server: MCPServer):
        """Initialize Support Agent."""
        super().__init__(
            name="SupportAgent",
            role="Support Specialist",
            description="Handles customer support queries, ticket management, and issue resolution"
        )
        self.mcp_server = mcp_server
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process support-related tasks."""
        action = task.get('action')
        self.log(f"Processing task: {action}")
        
        try:
            # Route to appropriate handler based on action
            if action == 'create_ticket':
                result = self._create_ticket(task)
            
            elif action == 'provide_support':
                result = self._provide_support(task)
            
            elif action == 'assess_urgency':
                result = self._assess_urgency(task)
            
            elif action == 'get_high_priority_tickets':
                result = self._get_high_priority_tickets(task)
            
            else:
                result = {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
            
            # Log result
            if result.get('success'):
                self.log(f"✓ Task completed: {action}")
            else:
                self.log(f"✗ Task failed: {result.get('error')}", "ERROR")
            
            return result
            
        except Exception as e:
            self.log(f"✗ Exception: {str(e)}", "ERROR")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_ticket(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new support ticket using MCP."""
        customer_id = task.get('customer_id')
        issue = task.get('issue')
        priority = task.get('priority', 'medium')
        return self.mcp_server.create_ticket(customer_id, issue, priority)
    
    def _provide_support(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate support response based on customer context and query."""
        query = task.get('query', '')
        customer_data = task.get('customer_data', {})
        
        customer = customer_data.get('customer', {})
        name = customer.get('name', 'Customer')
        status = customer.get('status', 'unknown')
        
        # Analyze query and generate appropriate response
        response = self._generate_response(query, name, status)
        
        return {
            'success': True,
            'response': response
        }
    
    def _assess_urgency(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Assess urgency of a support query."""
        query = task.get('query', '').lower()
        
        # High urgency keywords
        high_urgency = ['urgent', 'immediately', 'critical', 'emergency', 'down', 
                        'charged twice', 'refund', 'security', 'breach']
        
        # Medium urgency keywords
        medium_urgency = ['issue', 'problem', 'not working', 'broken', 'help']
        
        for keyword in high_urgency:
            if keyword in query:
                return {
                    'success': True,
                    'urgency': 'high',
                    'priority': 'high',
                    'reason': f'Contains high-urgency keyword: {keyword}'
                }
        
        for keyword in medium_urgency:
            if keyword in query:
                return {
                    'success': True,
                    'urgency': 'medium',
                    'priority': 'medium',
                    'reason': f'Contains medium-urgency keyword: {keyword}'
                }
        
        return {
            'success': True,
            'urgency': 'low',
            'priority': 'low',
            'reason': 'General inquiry'
        }
    
    def _get_high_priority_tickets(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Get high priority tickets, optionally filtered by customer IDs."""
        customer_ids = task.get('customer_ids')
        return self.mcp_server.get_tickets_by_priority('high', customer_ids)
    
    def _generate_response(self, query: str, name: str, status: str) -> str:
        """Generate appropriate support response."""
        query_lower = query.lower()
        
        if 'upgrade' in query_lower:
            return f"Hello {name}! I'd be happy to help you upgrade your account. Let me check your current status and available options."
        
        elif 'cancel' in query_lower:
            return f"Hello {name}, I understand you're considering cancellation. Before we proceed, I'd like to understand your concerns. What's prompting this decision?"
        
        elif 'refund' in query_lower or 'charge' in query_lower:
            return f"Hello {name}, I apologize for any billing issues. I'll escalate this to our billing team immediately. Can you provide more details?"
        
        elif 'help' in query_lower or 'support' in query_lower:
            return f"Hello {name}! I'm here to help with your inquiry. What can I assist you with today?"
        
        else:
            return f"Hello {name}! Thank you for reaching out. I'm reviewing your request and will provide assistance shortly."


# ============================================================================
# ROUTER AGENT (Orchestrator)
# ============================================================================

class RouterAgent(Agent):
    """
    Agent responsible for routing and coordinating tasks between specialist agents.
    Implements A2A coordination patterns: task allocation, negotiation, and multi-step workflows.
    """
    
    def __init__(self, data_agent: CustomerDataAgent, support_agent: SupportAgent):
        """Initialize Router Agent."""
        super().__init__(
            name="RouterAgent",
            role="Orchestrator",
            description="Coordinates tasks between specialized agents using A2A communication"
        )
        self.data_agent = data_agent
        self.support_agent = support_agent
        self.log("Connected to CustomerDataAgent and SupportAgent")
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process customer query using A2A coordination."""
        self.log(f"Received query: '{query}'")
        if context:
            self.log(f"Context: {context}")
        
        # Analyze query intent
        intent = self._analyze_intent(query)
        self.log(f"Detected intent: {intent}")
        
        # Route to appropriate coordination pattern
        if intent == 'simple_data_query':
            return self._handle_simple_query(query, context)
        
        elif intent == 'coordinated_support':
            return self._handle_coordinated_support(query, context)
        
        elif intent == 'complex_analysis':
            return self._handle_complex_analysis(query, context)
        
        elif intent == 'escalation':
            return self._handle_escalation(query, context)
        
        elif intent == 'multi_intent':
            return self._handle_multi_intent(query, context)
        
        else:
            return {
                'success': False,
                'error': 'Unable to determine query intent'
            }
    
    def _analyze_intent(self, query: str) -> str:
        """Analyze query to determine coordination intent."""
        query_lower = query.lower()
        
        # Simple data queries
        if any(phrase in query_lower for phrase in ['get customer', 'customer information', 'show customer']):
            if not any(word in query_lower for word in ['help', 'support', 'upgrade', 'issue']):
                return 'simple_data_query'
        
        # Escalation (urgent issues)
        if any(word in query_lower for word in ['charged twice', 'refund immediately', 'urgent', 'emergency']):
            return 'escalation'
        
        # Multi-intent (multiple actions)
        actions = ['update', 'show', 'get', 'create', 'list']
        action_count = sum(1 for action in actions if action in query_lower)
        if action_count >= 2:
            return 'multi_intent'
        
        # Complex analysis
        if any(phrase in query_lower for phrase in ['all customers', 'high-priority tickets', 'open tickets', 'active customers']):
            return 'complex_analysis'
        
        # Coordinated support (needs both data and support)
        if any(word in query_lower for word in ['help', 'support', 'upgrade', 'cancel', 'issue']):
            return 'coordinated_support'
        
        return 'general'
    
    def _extract_customer_id(self, query: str, context: Optional[Dict]) -> Optional[int]:
        """Extract customer ID from query or context."""
        if context and 'customer_id' in context:
            return context['customer_id']
        
        # Try to extract from query
        match = re.search(r'(?:id|customer)\s*(\d+)', query.lower())
        if match:
            return int(match.group(1))
        
        return None
    
    # ========================================================================
    # COORDINATION PATTERN: Task Allocation (Scenario 1)
    # ========================================================================
    
    def _handle_simple_query(self, query: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Handle simple data retrieval queries using Task Allocation pattern.
        Router → Data Agent → Response
        """
        self.log("Pattern: TASK ALLOCATION (Simple Query)")
        
        customer_id = self._extract_customer_id(query, context)
        
        if not customer_id:
            return {
                'success': False,
                'error': 'Customer ID required but not found in query or context'
            }
        
        # A2A Communication: Router → Data Agent
        self.log(f"→ CustomerDataAgent: get_customer({customer_id})")
        result = self.data_agent.process({
            'action': 'get_customer',
            'customer_id': customer_id
        })
        
        if not result.get('success'):
            return result
        
        self.log("← CustomerDataAgent: Data received")
        
        # Format response
        customer = result['customer']
        response = f"Customer Information:\n"
        response += f"  ID: {customer['id']}\n"
        response += f"  Name: {customer['name']}\n"
        response += f"  Email: {customer['email']}\n"
        response += f"  Phone: {customer['phone']}\n"
        response += f"  Status: {customer['status']}\n"
        
        self.log("✓ Query completed successfully")
        return {
            'success': True,
            'response': response,
            'data': result
        }
    
    # ========================================================================
    # COORDINATION PATTERN: Negotiation/Escalation (Scenario 2)
    # ========================================================================
    
    def _handle_coordinated_support(self, query: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Handle queries requiring coordination between agents using Negotiation pattern.
        Router → Data Agent → Support Agent → Response
        """
        self.log("Pattern: NEGOTIATION (Coordinated Support)")
        
        customer_id = self._extract_customer_id(query, context)
        
        if not customer_id:
            return {
                'success': False,
                'error': 'Customer ID required for support queries'
            }
        
        # Step 1: A2A Communication - Get customer context
        self.log(f"→ CustomerDataAgent: get_customer({customer_id})")
        customer_result = self.data_agent.process({
            'action': 'get_customer',
            'customer_id': customer_id
        })
        
        if not customer_result.get('success'):
            return customer_result
        
        self.log("← CustomerDataAgent: Customer data received")
        
        # Step 2: A2A Communication - Get support response
        self.log("→ SupportAgent: provide_support()")
        support_result = self.support_agent.process({
            'action': 'provide_support',
            'customer_data': customer_result,
            'query': query
        })
        
        if not support_result.get('success'):
            return support_result
        
        self.log("← SupportAgent: Support response generated")
        self.log("✓ Coordinated query completed successfully")
        
        return {
            'success': True,
            'response': support_result['response'],
            'customer_data': customer_result
        }
    
    # ========================================================================
    # COORDINATION PATTERN: Multi-Step Coordination (Scenario 3)
    # ========================================================================
    
    def _handle_complex_analysis(self, query: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Handle complex queries requiring multi-step coordination.
        Router → Data Agent → Support Agent → Data Agent → Response
        """
        self.log("Pattern: MULTI-STEP COORDINATION (Complex Analysis)")
        query_lower = query.lower()
        
        # Check for "active customers with open tickets"
        if 'active customers' in query_lower and 'open tickets' in query_lower:
            self.log("Sub-task: Get active customers with open tickets")
            
            # A2A Communication: Router → Data Agent
            self.log("→ CustomerDataAgent: get_customers_with_open_tickets()")
            result = self.data_agent.process({
                'action': 'get_customers_with_open_tickets'
            })
            
            if not result.get('success'):
                return result
            
            self.log(f"← CustomerDataAgent: Found {result['count']} customers")
            
            # Format response
            customers = result['customers']
            response = f"Active Customers with Open Tickets:\n\n"
            response += f"Total: {len(customers)} customers\n\n"
            
            for customer in customers:
                response += f"  • {customer['name']} (ID: {customer['id']})\n"
                response += f"    Email: {customer['email']}\n"
                response += f"    Open Tickets: {customer['open_ticket_count']}\n\n"
            
            self.log("✓ Complex analysis completed successfully")
            return {
                'success': True,
                'response': response,
                'customers': customers
            }
        
        return {
            'success': False,
            'error': 'Complex query pattern not recognized'
        }
    
    # ========================================================================
    # COORDINATION PATTERN: Escalation (Scenario 2 variant)
    # ========================================================================
    
    def _handle_escalation(self, query: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Handle urgent/escalation queries with priority handling.
        Router → Support Agent (assess) → Data Agent → Response
        """
        self.log("Pattern: ESCALATION (High Priority)")
        
        # Step 1: Assess urgency
        self.log("→ SupportAgent: assess_urgency()")
        urgency_result = self.support_agent.process({
            'action': 'assess_urgency',
            'query': query
        })
        
        self.log(f"← SupportAgent: Urgency = {urgency_result.get('urgency', 'unknown')}")
        
        # Step 2: Get customer context if available
        customer_id = self._extract_customer_id(query, context)
        customer_data = None
        
        if customer_id:
            self.log(f"→ CustomerDataAgent: get_customer({customer_id})")
            customer_result = self.data_agent.process({
                'action': 'get_customer',
                'customer_id': customer_id
            })
            if customer_result.get('success'):
                customer_data = customer_result
                self.log("← CustomerDataAgent: Customer data received")
        
        # Generate escalated response
        response = "🚨 ESCALATED TICKET - Priority Support\n\n"
        if customer_data:
            customer = customer_data['customer']
            response += f"Customer: {customer['name']} (ID: {customer['id']})\n"
            response += f"Contact: {customer['email']}\n\n"
        
        response += f"Urgency: {urgency_result.get('urgency', 'unknown').upper()}\n"
        response += f"Priority: {urgency_result.get('priority', 'medium')}\n"
        response += f"Reason: {urgency_result.get('reason', 'Escalated by system')}\n\n"
        response += "This issue has been flagged for immediate attention.\n"
        response += "Expected response time: Within 1 hour\n"
        
        self.log("✓ Escalation handled successfully")
        return {
            'success': True,
            'response': response,
            'urgency': urgency_result,
            'customer_data': customer_data
        }
    
    # ========================================================================
    # COORDINATION PATTERN: Multi-Intent (Complex Scenario 2)
    # ========================================================================
    
    def _handle_multi_intent(self, query: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Handle queries with multiple intents requiring parallel coordination.
        Router → [Data Agent + Support Agent] → Response
        """
        self.log("Pattern: MULTI-INTENT (Parallel Tasks)")
        query_lower = query.lower()
        
        customer_id = self._extract_customer_id(query, context)
        if not customer_id:
            return {
                'success': False,
                'error': 'Customer ID required for multi-intent queries'
            }
        
        results = []
        
        # Check for update email intent
        if 'update' in query_lower and 'email' in query_lower:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
            if email_match:
                new_email = email_match.group(0)
                self.log(f"→ CustomerDataAgent: update_customer(email={new_email})")
                update_result = self.data_agent.process({
                    'action': 'update_customer',
                    'customer_id': customer_id,
                    'data': {'email': new_email}
                })
                results.append(('update_email', update_result))
                self.log("← CustomerDataAgent: Email update complete")
        
        # Check for show history intent
        if 'show' in query_lower and ('history' in query_lower or 'tickets' in query_lower):
            self.log(f"→ CustomerDataAgent: get_customer_history({customer_id})")
            history_result = self.data_agent.process({
                'action': 'get_customer_history',
                'customer_id': customer_id
            })
            results.append(('get_history', history_result))
            self.log(f"← CustomerDataAgent: Found {history_result.get('ticket_count', 0)} tickets")
        
        # Format combined response
        response = "Multi-Action Request Processed:\n\n"
        
        for action_type, result in results:
            if result.get('success'):
                if action_type == 'update_email':
                    response += "✓ Email updated successfully\n\n"
                elif action_type == 'get_history':
                    response += f"✓ Ticket History Retrieved:\n"
                    response += f"  Total Tickets: {result['ticket_count']}\n"
                    for ticket in result.get('tickets', [])[:5]:
                        response += f"  • Ticket #{ticket['id']}: {ticket['issue']} [{ticket['status']}]\n"
                    response += "\n"
        
        self.log("✓ Multi-intent query completed successfully")
        return {
            'success': True,
            'response': response,
            'results': results
        }


# ============================================================================
# TEST SCENARIOS
# ============================================================================

def print_separator():
    """Print visual separator."""
    print("\n" + "="*80 + "\n")


def print_test_header(test_num: int, title: str, query: str):
    """Print formatted test header."""
    print_separator()
    print(f"TEST {test_num}: {title}")
    print(f"Query: '{query}'")
    print_separator()


def run_test_scenarios(router: RouterAgent):
    """Run comprehensive test scenarios."""
    
    print("\n🚀 MULTI-AGENT CUSTOMER SERVICE SYSTEM - TEST SCENARIOS")
    print("="*80)
    print("Demonstrating A2A Coordination Patterns")
    print("="*80 + "\n")
    
    # ========================================================================
    # TEST 1: Simple Query (Task Allocation)
    # ========================================================================
    
    print_test_header(1, "Simple Data Query (Task Allocation)", 
                     "Get customer information for ID 5")
    
    result = router.process_query("Get customer information for ID 5")
    
    print("\n📋 FINAL RESPONSE:")
    print(result['response'] if result.get('success') else f"Error: {result.get('error')}")
    
    # ========================================================================
    # TEST 2: Coordinated Query (Negotiation)
    # ========================================================================
    
    print_test_header(2, "Coordinated Support Query (Negotiation)",
                     "I'm customer 1 and need help upgrading my account")
    
    result = router.process_query(
        "I'm customer 1 and need help upgrading my account",
        context={'customer_id': 1}
    )
    
    print("\n📋 FINAL RESPONSE:")
    print(result['response'] if result.get('success') else f"Error: {result.get('error')}")
    
    # ========================================================================
    # TEST 3: Complex Query (Multi-Step Coordination)
    # ========================================================================
    
    print_test_header(3, "Complex Analysis Query (Multi-Step Coordination)",
                     "Show me all active customers who have open tickets")
    
    result = router.process_query("Show me all active customers who have open tickets")
    
    print("\n📋 FINAL RESPONSE:")
    print(result['response'] if result.get('success') else f"Error: {result.get('error')}")
    
    # ========================================================================
    # TEST 4: Escalation Query
    # ========================================================================
    
    print_test_header(4, "Escalation Query (High Priority)",
                     "I've been charged twice, please refund immediately!")
    
    result = router.process_query(
        "I've been charged twice, please refund immediately!",
        context={'customer_id': 2}
    )
    
    print("\n📋 FINAL RESPONSE:")
    print(result['response'] if result.get('success') else f"Error: {result.get('error')}")
    
    # ========================================================================
    # TEST 5: Multi-Intent Query
    # ========================================================================
    
    print_test_header(5, "Multi-Intent Query (Parallel Tasks)",
                     "Update my email to newemail@test.com and show my ticket history")
    
    result = router.process_query(
        "Update my email to newemail@test.com and show my ticket history",
        context={'customer_id': 4}
    )
    
    print("\n📋 FINAL RESPONSE:")
    print(result['response'] if result.get('success') else f"Error: {result.get('error')}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    
    print_separator()
    print("✅ ALL TEST SCENARIOS COMPLETED")
    print_separator()
    
    print("\nA2A Coordination Patterns Demonstrated:")
    print("  1. ✓ Task Allocation - Simple query routing")
    print("  2. ✓ Negotiation - Multi-agent coordination")
    print("  3. ✓ Multi-Step Coordination - Complex queries")
    print("  4. ✓ Escalation - Priority handling")
    print("  5. ✓ Parallel Tasks - Multi-intent processing")
    print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MULTI-AGENT SYSTEM - COMPLETE INITIALIZATION")
    print("="*80 + "\n")
    
    # Initialize MCP Server
    mcp_server = MCPServer("support.db")
    
    # Initialize Agents
    data_agent = CustomerDataAgent(mcp_server)
    support_agent = SupportAgent(mcp_server)
    router = RouterAgent(data_agent, support_agent)
    
    print("\n" + "="*80)
    print("✓ ALL COMPONENTS INITIALIZED")
    print("="*80 + "\n")
    
    # Run test scenarios
    run_test_scenarios(router)
