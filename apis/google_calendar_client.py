"""
Google Calendar API client for calendar management operations
Mirrors the TodoistClient architecture for consistency
FIXED VERSION - Corrects free time slot calculation
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
class GoogleCalendarClient:
    """Google Calendar API client with complete CRUD operations"""
    
    def __init__(self):
        self.service_name = "Google Calendar"
        self.calendar_service = None
        self._initialize_calendar_service()
    
    def _initialize_calendar_service(self):
        """Initialize Google Calendar service with authentication"""
        try:
            # Import Google Calendar API libraries
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            # Calendar API scopes
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            creds = None
            token_path = 'local_data/calendar_token.json'
            credentials_path = 'local_data/calendar_credentials.json'
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(credentials_path):
                        raise ValueError(
                            f"Google Calendar credentials not found at {credentials_path}\\n"
                            "Please download credentials from Google Cloud Console and save as calendar_credentials.json"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            
        except ImportError:
            raise ValueError(
                "Google Calendar API libraries not installed.\\n"
                "Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Calendar service: {str(e)}")
    
    def log_operation(self, operation: str, details: str = ""):
        """Log API operations with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {self.service_name}: {operation}"
        if details:
            log_message += f" - {details}"
        print(f"📝 {log_message}")
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> bool:
        """Validate that required fields are present in data"""
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        return True
    
    def get_calendars(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch all calendars"""
        try:
            result = self.calendar_service.calendarList().list().execute()
            calendars = result.get('items', [])
            
            self.log_operation("Fetched calendars", f"{len(calendars)} calendars")
            return calendars
            
        except Exception as e:
            print(f"❌ Error fetching calendars: {str(e)}")
            return None
    
    def get_events(self, calendar_id: str = 'primary', 
                   time_min: str = None, time_max: str = None,
                   max_results: int = 250) -> Optional[List[Dict[str, Any]]]:
        """Fetch events from a specific calendar"""
        try:
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            if not time_max:
                end_time = datetime.utcnow() + timedelta(days=30)
                time_max = end_time.isoformat() + 'Z'
            
            result = self.calendar_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = result.get('items', [])
            self.log_operation("Fetched events", f"{len(events)} events from {calendar_id}")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching events: {str(e)}")
            return None
    
    def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new calendar event"""
        try:
            if not self.validate_required_fields(event_data, ['summary', 'start', 'end']):
                return None
            
            result = self.calendar_service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            print(f"✅ Created event: {event_data.get('summary', 'Untitled')}")
            self.log_operation("Created event", event_data.get('summary', 'Untitled'))
            return result
            
        except Exception as e:
            print(f"❌ Error creating event: {str(e)}")
            return None
    
    def update_event(self, calendar_id: str, event_id: str, 
                     event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing calendar event"""
        try:
            result = self.calendar_service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            print(f"✅ Updated event: {event_data.get('summary', event_id)}")
            self.log_operation("Updated event", event_data.get('summary', event_id))
            return result
            
        except Exception as e:
            print(f"❌ Error updating event: {str(e)}")
            return None
    
    def delete_event(self, calendar_id: str, event_id: str, 
                     event_summary: str = "") -> bool:
        """Delete a calendar event"""
        try:
            self.calendar_service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            display_name = event_summary or event_id
            print(f"🗑️ Deleted event: {display_name}")
            self.log_operation("Deleted event", display_name)
            return True
            
        except Exception as e:
            print(f"❌ Error deleting event: {str(e)}")
            return False
    
    def find_free_time(self, calendar_id: str, time_min: str, time_max: str,
                       duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Find free time slots in the calendar - FIXED VERSION"""
        try:
            # Get events in the time range
            events = self.get_events(calendar_id, time_min, time_max)
            if events is None:
                return []
            
            # Parse time range
            start_time = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
            
            # For realistic analysis, constrain to working hours (7 AM - 8 PM)
            working_start = start_time.replace(hour=7, minute=0, second=0, microsecond=0)
            working_end = start_time.replace(hour=20, minute=0, second=0, microsecond=0)
            
            # Make sure we're within the requested time range
            working_start = max(working_start, start_time)
            working_end = min(working_end, end_time)
            
            # If working hours don't overlap with requested range, return empty
            if working_start >= working_end:
                return []
            
            # Create list of busy periods (only within working hours)
            busy_periods = []
            for event in events:
                if 'start' in event and 'end' in event:
                    event_start = event['start'].get('dateTime', event['start'].get('date'))
                    event_end = event['end'].get('dateTime', event['end'].get('date'))
                    
                    if event_start and event_end:
                        # Handle all-day events
                        if 'T' not in event_start:
                            continue  # Skip all-day events for now
                        
                        start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                        
                        # Only include events that overlap with working hours
                        if end_dt > working_start and start_dt < working_end:
                            # Clip to working hours
                            clipped_start = max(start_dt, working_start)
                            clipped_end = min(end_dt, working_end)
                            busy_periods.append((clipped_start, clipped_end))
            
            # Sort busy periods
            busy_periods.sort(key=lambda x: x[0])
            
            # Merge overlapping busy periods
            merged_busy = []
            for start, end in busy_periods:
                if merged_busy and start <= merged_busy[-1][1]:
                    # Overlapping or adjacent - merge
                    merged_busy[-1] = (merged_busy[-1][0], max(merged_busy[-1][1], end))
                else:
                    merged_busy.append((start, end))
            
            # Find free slots between busy periods
            free_slots = []
            current_time = working_start  # Start from working hours, not midnight
            
            for busy_start, busy_end in merged_busy:
                # Check if there's a gap before this busy period
                gap_duration = (busy_start - current_time).total_seconds() / 60
                if gap_duration >= duration_minutes:
                    free_slots.append({
                        'start': current_time.isoformat(),
                        'end': busy_start.isoformat(),
                        'duration_minutes': gap_duration
                    })
                
                current_time = max(current_time, busy_end)
            
            # Check for free time after last event (or entire day if no events)
            final_gap = (working_end - current_time).total_seconds() / 60
            if final_gap >= duration_minutes:
                free_slots.append({
                    'start': current_time.isoformat(),
                    'end': working_end.isoformat(),
                    'duration_minutes': final_gap
                })
            
            return free_slots
            
        except Exception as e:
            print(f"❌ Error finding free time: {str(e)}")
            return []
    
    def create_task_time_block(self, task_data: Dict[str, Any], 
                               start_time: str, duration_minutes: int,
                               calendar_id: str = 'primary') -> Optional[Dict[str, Any]]:
        """Create a time block for a Todoist task"""
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            event_data = {
                'summary': f"📋 {task_data['content']}",
                'description': f"Todoist Task: {task_data.get('description', '')}\\n\\nTask ID: {task_data.get('task_id', '')}",
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Australia/Brisbane'
                },
                'end': {
                    'dateTime': end_dt.isoformat(), 
                    'timeZone': 'Australia/Brisbane'
                },
                'colorId': '2',  # Green color for task blocks
                'extendedProperties': {
                    'private': {
                        'source': 'todoist',
                        'task_id': task_data.get('task_id', ''),
                        'priority': str(task_data.get('priority', 1))
                    }
                }
            }
            
            return self.create_event(calendar_id, event_data)
            
        except Exception as e:
            print(f"❌ Error creating task time block: {str(e)}")
            return None
