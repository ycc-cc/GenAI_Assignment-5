"""
Part 2: MCP Server Implementation for Customer Service System
Implements Model Context Protocol (MCP) server with required tools:
- get_customer(customer_id)
- list_customers(status, limit)
- update_customer(customer_id, data)
- create_ticket(customer_id, issue, priority)
- get_customer_history(customer_id)
"""

import sqlite3
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


class MCPServer:
    """MCP Server for customer database operations"""
    
    def __init__(self, db_path: str = "support.db"):
        """Initialize MCP server with database path.
        
        Args:
            db_path: Path to SQLite database
        """
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
        """
        Get customer information by ID.
        
        Args:
            customer_id: Customer ID to retrieve (uses customers.id)
            
        Returns:
            Dictionary with customer information or error
        """
        print(f"[MCP] get_customer called with customer_id={customer_id}")
        
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, email, phone, status, created_at, updated_at
                FROM customers
                WHERE id = ?
            """, (customer_id,))
            
            result = cursor.fetchone()
            
            if result:
                print(f"[MCP] ✓ Customer {customer_id} found: {result['name']}")
                return {
                    'success': True,
                    'customer': result
                }
            else:
                print(f"[MCP] ✗ Customer {customer_id} not found")
                return {
                    'success': False,
                    'error': f'Customer {customer_id} not found'
                }
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def list_customers(self, status: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        List customers with optional status filter.
        
        Args:
            status: Filter by status ('active' or 'disabled') - uses customers.status
            limit: Maximum number of customers to return
            
        Returns:
            Dictionary with list of customers
        """
        print(f"[MCP] list_customers called with status={status}, limit={limit}")
        
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()
        
        try:
            if status:
                cursor.execute("""
                    SELECT id, name, email, phone, status, created_at, updated_at
                    FROM customers
                    WHERE status = ?
                    LIMIT ?
                """, (status, limit))
            else:
                cursor.execute("""
                    SELECT id, name, email, phone, status, created_at, updated_at
                    FROM customers
                    LIMIT ?
                """, (limit,))
            
            results = cursor.fetchall()
            print(f"[MCP] ✓ Found {len(results)} customers")
            
            return {
                'success': True,
                'customers': results,
                'count': len(results)
            }
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update customer information.
        
        Args:
            customer_id: Customer ID to update (uses customers.id)
            data: Dictionary with fields to update (uses customers fields: name, email, phone, status)
            
        Returns:
            Dictionary with update status
        """
        print(f"[MCP] update_customer called for customer_id={customer_id} with data={data}")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if customer exists
            cursor.execute('SELECT id FROM customers WHERE id = ?', (customer_id,))
            if not cursor.fetchone():
                print(f"[MCP] ✗ Customer {customer_id} not found")
                return {
                    'success': False,
                    'error': f'Customer {customer_id} not found'
                }
            
            # Build update query dynamically
            allowed_fields = ['name', 'email', 'phone', 'status']
            update_fields = []
            values = []
            
            for field, value in data.items():
                if field in allowed_fields:
                    update_fields.append(f'{field} = ?')
                    values.append(value)
            
            if not update_fields:
                print(f"[MCP] ✗ No valid fields to update")
                return {
                    'success': False,
                    'error': 'No valid fields to update'
                }
            
            # The trigger will automatically update updated_at
            values.append(customer_id)
            
            query = f"""
                UPDATE customers
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            
            cursor.execute(query, values)
            conn.commit()
            
            print(f"[MCP] ✓ Customer {customer_id} updated successfully")
            return {
                'success': True,
                'customer_id': customer_id,
                'updated_fields': list(data.keys())
            }
        except Exception as e:
            conn.rollback()
            print(f"[MCP] ✗ Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def create_ticket(self, customer_id: int, issue: str, priority: str = 'medium') -> Dict[str, Any]:
        """
        Create a new support ticket.
        
        Args:
            customer_id: Customer ID for the ticket (uses customers.id)
            issue: Description of the issue (uses tickets.issue)
            priority: Priority level - 'low', 'medium', or 'high' (uses tickets.priority)
            
        Returns:
            Dictionary with ticket creation status
        """
        print(f"[MCP] create_ticket called for customer_id={customer_id}, priority={priority}")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Validate customer exists
            cursor.execute('SELECT id FROM customers WHERE id = ?', (customer_id,))
            if not cursor.fetchone():
                print(f"[MCP] ✗ Customer {customer_id} not found")
                return {
                    'success': False,
                    'error': f'Customer {customer_id} not found'
                }
            
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
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_customer_history(self, customer_id: int) -> Dict[str, Any]:
        """
        Get all tickets for a customer (customer history).
        
        Args:
            customer_id: Customer ID to get history for (uses tickets.customer_id)
            
        Returns:
            Dictionary with customer ticket history
        """
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
                return {
                    'success': False,
                    'error': f'Customer {customer_id} not found'
                }
            
            # Get all tickets
            cursor.execute("""
                SELECT id, customer_id, issue, status, priority, created_at
                FROM tickets
                WHERE customer_id = ?
                ORDER BY created_at DESC
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
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    # ========================================================================
    # ADDITIONAL HELPER TOOLS FOR COMPLEX QUERIES
    # ========================================================================
    
    def get_tickets_by_priority(self, priority: str, customer_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Get tickets by priority, optionally filtered by customer IDs.
        Helper tool for complex coordination scenarios.
        
        Args:
            priority: Priority level to filter by
            customer_ids: Optional list of customer IDs to filter
            
        Returns:
            Dictionary with matching tickets
        """
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
            
            return {
                'success': True,
                'priority': priority,
                'tickets': tickets,
                'count': len(tickets)
            }
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_customers_with_open_tickets(self) -> Dict[str, Any]:
        """
        Get all active customers who have open tickets.
        Helper tool for complex coordination scenarios.
        
        Returns:
            Dictionary with customers and their open tickets
        """
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
            
            return {
                'success': True,
                'customers': results,
                'count': len(results)
            }
        except Exception as e:
            print(f"[MCP] ✗ Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()


def test_mcp_server():
    """Test all MCP server tools."""
    print("\n" + "="*70)
    print("TESTING MCP SERVER TOOLS")
    print("="*70 + "\n")
    
    server = MCPServer("support.db")
    
    # Test 1: get_customer
    print("TEST 1: get_customer(5)")
    print("-" * 70)
    result = server.get_customer(5)
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Test 2: list_customers
    print("TEST 2: list_customers(status='active', limit=3)")
    print("-" * 70)
    result = server.list_customers(status='active', limit=3)
    print(f"Result: Found {result['count']} customers")
    for customer in result['customers']:
        print(f"  - {customer['name']} ({customer['email']})")
    print()
    
    # Test 3: update_customer
    print("TEST 3: update_customer(1, {'email': 'newemail@example.com'})")
    print("-" * 70)
    result = server.update_customer(1, {'email': 'newemail@example.com'})
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Test 4: create_ticket
    print("TEST 4: create_ticket(1, 'Test issue', 'high')")
    print("-" * 70)
    result = server.create_ticket(1, 'Test issue from MCP tool', 'high')
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # Test 5: get_customer_history
    print("TEST 5: get_customer_history(1)")
    print("-" * 70)
    result = server.get_customer_history(1)
    print(f"Result: Found {result['ticket_count']} tickets for {result['customer_name']}")
    for ticket in result['tickets'][:3]:
        print(f"  - Ticket #{ticket['id']}: {ticket['issue']} [{ticket['status']}]")
    print()
    
    # Test 6: get_tickets_by_priority
    print("TEST 6: get_tickets_by_priority('high')")
    print("-" * 70)
    result = server.get_tickets_by_priority('high')
    print(f"Result: Found {result['count']} high-priority tickets")
    for ticket in result['tickets'][:3]:
        print(f"  - Ticket #{ticket['id']} ({ticket['customer_name']}): {ticket['issue']}")
    print()
    
    # Test 7: get_customers_with_open_tickets
    print("TEST 7: get_customers_with_open_tickets()")
    print("-" * 70)
    result = server.get_customers_with_open_tickets()
    print(f"Result: Found {result['count']} customers with open tickets")
    for customer in result['customers'][:3]:
        print(f"  - {customer['name']} ({customer['email']}): {customer['open_ticket_count']} open tickets")
    print()
    
    print("="*70)
    print("✓ ALL MCP SERVER TESTS COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_mcp_server()
