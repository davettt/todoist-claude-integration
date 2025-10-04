"""
Todoist API client for task management operations - UPDATED
Added complete_task functionality to properly mark tasks as done
"""

import uuid
from typing import Any, Dict, List, Optional

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

        project_map = {p["name"]: p["id"] for p in projects}

        section_map = {}
        for section in sections:
            project_id = section["project_id"]
            section_name = section["name"]
            if project_id not in section_map:
                section_map[project_id] = {}
            section_map[project_id][section_name] = section["id"]

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

    def find_task_by_content(
        self,
        tasks: List[Dict[str, Any]],
        content: str,
        project_id: str = None,
        section_id: str = None,
        task_id: str = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Find a task by its content with optional disambiguation using project/section/ID

        Args:
            tasks: List of tasks to search
            content: Task content/name to match
            project_id: Optional project ID for disambiguation
            section_id: Optional section ID for disambiguation
            task_id: Optional task ID for exact match (highest priority)

        Returns:
            Matching task or None if not found

        Notes:
            - If task_id is provided, it takes priority for exact matching
            - If multiple tasks have same content, project/section are used to disambiguate
            - Warns user if duplicates are found without sufficient disambiguation
        """
        # If task_id provided, use it for exact match (most reliable)
        if task_id:
            for task in tasks:
                if task.get("id") == task_id:
                    return task
            # Fall through to content matching if ID not found
            print(f"⚠️  Task ID '{task_id}' not found, trying content match...")

        # Find all tasks matching content
        matches = [task for task in tasks if task.get("content") == content]

        if len(matches) == 0:
            return None

        if len(matches) == 1:
            return matches[0]

        # Multiple matches found - try to disambiguate
        print(f"⚠️  Found {len(matches)} tasks with name '{content}'")

        # Try filtering by project_id
        if project_id:
            project_matches = [
                task for task in matches if task.get("project_id") == project_id
            ]
            if len(project_matches) == 1:
                print("✅ Disambiguated by project ID")
                return project_matches[0]
            elif len(project_matches) > 1:
                matches = project_matches  # Narrow down further

        # Try filtering by section_id
        if section_id:
            section_matches = [
                task for task in matches if task.get("section_id") == section_id
            ]
            if len(section_matches) == 1:
                print("✅ Disambiguated by section ID")
                return section_matches[0]
            elif len(section_matches) > 1:
                matches = section_matches

        # Still have duplicates - show details and use first match
        print("⚠️  Multiple tasks still match after filtering:")
        for i, task in enumerate(matches[:3], 1):  # Show first 3
            project = task.get("project_id", "unknown")
            section = task.get("section_id", "none")
            task_id_display = task.get("id", "unknown")
            print(
                f"   {i}. ID: {task_id_display}, Project: {project}, Section: {section}"
            )

        if len(matches) > 3:
            print(f"   ... and {len(matches) - 3} more")

        print("⚠️  Using first match. For better accuracy:")
        print("   • Ensure task names are unique, OR")
        print("   • Specify 'project_name' and 'section_name' in your task JSON")

        return matches[0]

    def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a single task in Todoist

        Args:
            task_data: Task data dictionary with content, description, etc.

        Returns:
            Created task data if successful, None if failed
        """
        if not self.validate_required_fields(task_data, ["content"]):
            return None

        url = f"{self.rest_url}/tasks"
        headers = self.get_headers()

        result = self.safe_request(
            "POST",
            url,
            f"creating task '{task_data['content']}'",
            headers=headers,
            json=task_data,
        )

        if result:
            print(f"✅ Created: {task_data['content']}")
            self.log_operation("Created task", task_data["content"])

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
        valid_fields = ["content", "description", "priority", "labels", "due_string"]

        for field in valid_fields:
            if field in task_data:
                update_data[field] = task_data[field]

        if not update_data:
            return True  # Nothing to update

        url = f"{self.rest_url}/tasks/{task_id}"
        headers = self.get_headers()

        result = self.safe_request(
            "POST", url, "updating task fields", headers=headers, json=update_data
        )

        return result is not None

    def move_task(
        self, task_id: str, project_id: str = None, section_id: str = None
    ) -> bool:
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
            commands.append(
                {
                    "type": "item_move",
                    "uuid": move_project_uuid,
                    "args": {"id": task_id, "project_id": int(project_id)},
                }
            )

        # Move to section if specified
        if section_id:
            move_section_uuid = str(uuid.uuid4())
            commands.append(
                {
                    "type": "item_move",
                    "uuid": move_section_uuid,
                    "args": {"id": task_id, "section_id": int(section_id)},
                }
            )

        if not commands:
            return True  # Nothing to move

        # Execute commands using Sync API
        headers = self.get_headers()
        sync_data = {"commands": commands}

        result = self.safe_request(
            "POST", self.sync_url, "moving task", headers=headers, json=sync_data
        )

        if result and "sync_status" in result:
            # Check for errors in sync_status
            for command_uuid, status in result["sync_status"].items():
                if "error" in status:
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

        result = self.safe_request("POST", url, "completing task", headers=headers)

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

        result = self.safe_request("DELETE", url, "deleting task", headers=headers)

        if result is not None:  # API returns 204 with no content on success
            display_content = task_content or task_id
            print(f"🗑️ Deleted: {display_content}")
            self.log_operation("Deleted task", display_content)
            return True

        return False

    # High-level operations

    def prepare_task_data(
        self,
        task_info: Dict[str, Any],
        project_map: Dict[str, str],
        section_map: Dict[str, Dict[str, str]],
    ) -> tuple:
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
            "priority": task_info.get("priority", 1),
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
                section_id = section_map[project_id_for_section].get(
                    task_info["section_name"]
                )

        return task_data, project_id, section_id

    def process_task_operation(
        self,
        task_info: Dict[str, Any],
        operation_type: str,
        existing_tasks: List[Dict[str, Any]],
        project_map: Dict[str, str],
        section_map: Dict[str, Dict[str, str]],
    ) -> bool:
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
        # Extract disambiguation parameters if provided
        task_id = task_info.get("task_id")  # Highest priority if provided
        project_name = task_info.get("project_name")
        section_name = task_info.get("section_name")

        # Convert project/section names to IDs for disambiguation
        lookup_project_id = None
        lookup_section_id = None

        if project_name and project_name in project_map:
            lookup_project_id = project_map[project_name]

        if section_name and project_name and lookup_project_id:
            if (
                lookup_project_id in section_map
                and section_name in section_map[lookup_project_id]
            ):
                lookup_section_id = section_map[lookup_project_id][section_name]

        if operation_type == "complete":
            existing_task = self.find_task_by_content(
                existing_tasks,
                task_info["content"],
                project_id=lookup_project_id,
                section_id=lookup_section_id,
                task_id=task_id,
            )
            if existing_task:
                return self.complete_task(existing_task["id"], task_info["content"])
            else:
                print(f"⚠️ Task not found for completion: {task_info['content']}")
                return False

        elif operation_type == "delete":
            existing_task = self.find_task_by_content(
                existing_tasks,
                task_info["content"],
                project_id=lookup_project_id,
                section_id=lookup_section_id,
                task_id=task_id,
            )
            if existing_task:
                return self.delete_task(existing_task["id"], task_info["content"])
            else:
                print(f"⚠️ Task not found for deletion: {task_info['content']}")
                return False

        elif operation_type == "update":
            existing_task = self.find_task_by_content(
                existing_tasks,
                task_info["content"],
                project_id=lookup_project_id,
                section_id=lookup_section_id,
                task_id=task_id,
            )
            if not existing_task:
                print(f"⚠️ Task not found for update: {task_info['content']}")
                return False

            task_data, project_id, section_id = self.prepare_task_data(
                task_info, project_map, section_map
            )

            # Update fields first
            field_success = self.update_task_fields(existing_task["id"], task_data)

            # Then move if needed
            move_success = True
            if project_id or section_id:
                move_success = self.move_task(
                    existing_task["id"], project_id, section_id
                )

            if field_success and move_success:
                print(f"✅ Updated: {task_info['content']}")
                return True
            else:
                print(f"⚠️ Partial update for: {task_info['content']}")
                return False

        elif operation_type == "create":
            task_data, project_id, section_id = self.prepare_task_data(
                task_info, project_map, section_map
            )

            # Create task first
            created_task = self.create_task(task_data)
            if not created_task:
                return False

            # Then move if needed
            if project_id or section_id:
                move_success = self.move_task(
                    created_task["id"], project_id, section_id
                )
                if not move_success:
                    print(f"⚠️ Task created but move failed: {task_info['content']}")

            return True

        return False
