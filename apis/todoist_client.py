"""
Todoist API client for task management operations - UPDATED
Added complete_task functionality to properly mark tasks as done
"""

import uuid
from typing import Dict, Any, List, Optional
from .base_client import BaseAPIClient

class TodoistClient(BaseAPIClient):
    """Todoist API client with complete CRUD operations + task completion"""
    
    def __init__(self):
        super().__init__("Todoist", "TODOIST_API_TOKEN")
        self.rest_url = "https://api.todoist.com/rest/v2"
        self.sync_url = "https://api.todoist.com/sync/v9/sync"
    
    # Project and Section Management
    
    def get_projects(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all projects from Todoist"""
        url = f"{self.rest_url}/projects"
        headers = self.get_headers()
        
        result = self.safe_request("GET", url, "fetching projects", headers=headers)
        if result:
            self.log_operation("Fetched projects", f"{len(result)} projects")
        return result
    
    def get_sections(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all sections from Todoist"""
        url = f"{self.rest_url}/sections"
        headers = self.get_headers()
        
        result = self.safe_request("GET", url, "fetching sections", headers=headers)
        if result:
            self.log_operation("Fetched sections", f"{len(result)} sections")
        return result
    
    def get_labels(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all labels from Todoist"""
        url = f"{self.rest_url}/labels"
        headers = self.get_headers()
        
        result = self.safe_request("GET", url, "fetching labels", headers=headers)
        if result:
            self.log_operation("Fetched labels", f"{len(result)} labels")
        return result
    
    def build_project_mappings(self) -> tuple:
        """
        Build project and section mappings for easier lookup
        
        Returns:
            Tuple of (project_map, section_map) where:
            - project_map: {project_name: project_id}
            - section_map: {project_id: {section_name: section_id}}
        """
        projects = self.get_projects()
        sections = self.get_sections()
        
        if not projects or sections is None:
            return {}, {}
        
        project_map = {p['name']: p['id'] for p in projects}
        
        section_map = {}
        for section in sections:
            project_id = section['project_id']
            section_name = section['name']
            if project_id not in section_map:
                section_map[project_id] = {}
            section_map[project_id][section_name] = section['id']
        
        return project_map, section_map
    
    # Task Management
    
    def get_all_tasks(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all active tasks from Todoist"""
        url = f"{self.rest_url}/tasks"
        headers = self.get_headers()
        
        result = self.safe_request("GET", url, "fetching tasks", headers=headers)
        if result:
            self.log_operation("Fetched tasks", f"{len(result)} tasks")
        return result
    
    def find_task_by_content(self, tasks: List[Dict[str, Any]], content: str) -> Optional[Dict[str, Any]]:
        """Find a task by its content"""
        for task in tasks:
            if task.get('content') == content:
                return task
        return None
    
    def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a single task in Todoist
        
        Args:
            task_data: Task data dictionary with content, description, etc.
            
        Returns:
            Created task data if successful, None if failed
        """
        if not self.validate_required_fields(task_data, ['content']):
            return None
        
        url = f"{self.rest_url}/tasks"
        headers = self.get_headers()
        
        result = self.safe_request("POST", url, f"creating task '{task_data['content']}'", 
                                 headers=headers, json=task_data)
        
        if result:
            print(f"✅ Created: {task_data['content']}")
            self.log_operation("Created task", task_data['content'])
        
        return result
    
    def update_task_fields(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Update task fields that work with REST API (not project/section moves)
        
        Args:
            task_id: Todoist task ID
            task_data: Data to update
            
        Returns:
            True if successful, False if failed
        """
        # Only include fields that work with REST API
        update_data = {}
        valid_fields = ['content', 'description', 'priority', 'labels', 'due_string']
        
        for field in valid_fields:
            if field in task_data:
                update_data[field] = task_data[field]
        
        if not update_data:
            return True  # Nothing to update
        
        url = f"{self.rest_url}/tasks/{task_id}"
        headers = self.get_headers()
        
        result = self.safe_request("POST", url, f"updating task fields", 
                                 headers=headers, json=update_data)
        
        return result is not None
    
    def move_task(self, task_id: str, project_id: str = None, section_id: str = None) -> bool:
        """
        Move task using Sync API (supports project/section moves)
        
        Args:
            task_id: Todoist task ID
            project_id: Target project ID (optional)
            section_id: Target section ID (optional)
            
        Returns:
            True if successful, False if failed
        """
        commands = []
        
        # Move to project if specified
        if project_id:
            move_project_uuid = str(uuid.uuid4())
            commands.append({
                "type": "item_move",
                "uuid": move_project_uuid,
                "args": {
                    "id": task_id,
                    "project_id": int(project_id)
                }
            })
        
        # Move to section if specified
        if section_id:
            move_section_uuid = str(uuid.uuid4())
            commands.append({
                "type": "item_move",
                "uuid": move_section_uuid,
                "args": {
                    "id": task_id,
                    "section_id": int(section_id)
                }
            })
        
        if not commands:
            return True  # Nothing to move
        
        # Execute commands using Sync API
        headers = self.get_headers()
        sync_data = {"commands": commands}
        
        result = self.safe_request("POST", self.sync_url, "moving task", 
                                 headers=headers, json=sync_data)
        
        if result and 'sync_status' in result:
            # Check for errors in sync_status
            for command_uuid, status in result['sync_status'].items():
                if 'error' in status:
                    print(f"❌ Move command failed: {status['error']}")
                    return False
        
        return result is not None
    
    def complete_task(self, task_id: str, task_content: str = "") -> bool:
        """
        Complete a task in Todoist (marks as done, preserves history)
        This is different from delete_task - it properly completes the task
        and advances recurring tasks to their next instance.
        
        Args:
            task_id: Todoist task ID
            task_content: Task content for logging (optional)
            
        Returns:
            True if successful, False if failed
        """
        url = f"{self.rest_url}/tasks/{task_id}/close"
        headers = self.get_headers()
        
        result = self.safe_request("POST", url, f"completing task", headers=headers)
        
        if result is not None:  # API returns 204 with no content on success
            display_content = task_content or task_id
            print(f"✅ Completed: {display_content}")
            self.log_operation("Completed task", display_content)
            return True
        
        return False
    
    def delete_task(self, task_id: str, task_content: str = "") -> bool:
        """
        Delete a task from Todoist (permanently removes it)
        Use complete_task() instead if you want to mark as done
        
        Args:
            task_id: Todoist task ID
            task_content: Task content for logging (optional)
            
        Returns:
            True if successful, False if failed
        """
        url = f"{self.rest_url}/tasks/{task_id}"
        headers = self.get_headers()
        
        result = self.safe_request("DELETE", url, f"deleting task", headers=headers)
        
        if result is not None:  # API returns 204 with no content on success
            display_content = task_content or task_id
            print(f"🗑️ Deleted: {display_content}")
            self.log_operation("Deleted task", display_content)
            return True
        
        return False
    
    # High-level operations
    
    def prepare_task_data(self, task_info: Dict[str, Any], project_map: Dict[str, str], 
                         section_map: Dict[str, Dict[str, str]]) -> tuple:
        """
        Prepare task data for Todoist API from task info
        
        Args:
            task_info: Task information from JSON file
            project_map: Project name to ID mapping
            section_map: Section mappings by project
            
        Returns:
            Tuple of (task_data, project_id, section_id)
        """
        task_data = {
            "content": task_info["content"],
            "description": task_info.get("description", ""),
            "priority": task_info.get("priority", 1)
        }
        
        # Add due date if provided
        if task_info.get("due_date"):
            task_data["due_string"] = task_info["due_date"]
        
        # Add labels if specified
        if task_info.get("labels"):
            task_data["labels"] = task_info["labels"]
        
        # Get project and section IDs
        project_id = None
        section_id = None
        
        if task_info.get("project_name"):
            project_id = project_map.get(task_info["project_name"])
        
        if task_info.get("section_name") and task_info.get("project_name"):
            project_id_for_section = project_map.get(task_info["project_name"])
            if project_id_for_section and project_id_for_section in section_map:
                section_id = section_map[project_id_for_section].get(task_info["section_name"])
        
        return task_data, project_id, section_id
    
    def process_task_operation(self, task_info: Dict[str, Any], operation_type: str, 
                             existing_tasks: List[Dict[str, Any]], project_map: Dict[str, str], 
                             section_map: Dict[str, Dict[str, str]]) -> bool:
        """
        Process a single task operation (create, update, complete, or delete)
        
        Args:
            task_info: Task information
            operation_type: 'create', 'update', 'complete', or 'delete'
            existing_tasks: List of existing tasks for lookup
            project_map: Project mappings
            section_map: Section mappings
            
        Returns:
            True if successful, False if failed
        """
        if operation_type == "complete":
            existing_task = self.find_task_by_content(existing_tasks, task_info['content'])
            if existing_task:
                return self.complete_task(existing_task['id'], task_info['content'])
            else:
                print(f"⚠️ Task not found for completion: {task_info['content']}")
                return False
        
        elif operation_type == "delete":
            existing_task = self.find_task_by_content(existing_tasks, task_info['content'])
            if existing_task:
                return self.delete_task(existing_task['id'], task_info['content'])
            else:
                print(f"⚠️ Task not found for deletion: {task_info['content']}")
                return False
        
        elif operation_type == "update":
            existing_task = self.find_task_by_content(existing_tasks, task_info['content'])
            if not existing_task:
                print(f"⚠️ Task not found for update: {task_info['content']}")
                return False
            
            task_data, project_id, section_id = self.prepare_task_data(task_info, project_map, section_map)
            
            # Update fields first
            field_success = self.update_task_fields(existing_task['id'], task_data)
            
            # Then move if needed
            move_success = True
            if project_id or section_id:
                move_success = self.move_task(existing_task['id'], project_id, section_id)
            
            if field_success and move_success:
                print(f"✅ Updated: {task_info['content']}")
                return True
            else:
                print(f"⚠️ Partial update for: {task_info['content']}")
                return False
        
        elif operation_type == "create":
            task_data, project_id, section_id = self.prepare_task_data(task_info, project_map, section_map)
            
            # Create task first
            created_task = self.create_task(task_data)
            if not created_task:
                return False
            
            # Then move if needed
            if project_id or section_id:
                move_success = self.move_task(created_task['id'], project_id, section_id)
                if not move_success:
                    print(f"⚠️ Task created but move failed: {task_info['content']}")
            
            return True
        
        return False
