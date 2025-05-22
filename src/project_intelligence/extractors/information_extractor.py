"""
Information extractor for the Project Intelligence System.

This module provides a class for extracting structured project information
from unstructured data sources (emails, messages, spreadsheets).
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

logger = logging.getLogger(__name__)


class InformationExtractor:
    """
    Extracts structured project information from unstructured data.
    
    This class uses NLP techniques and pattern matching to identify
    project-related information in text from various sources.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the information extractor.
        
        Args:
            config: Configuration dictionary for the extractor
        """
        self.config = config or {}
        
        # Initialize NLP components if needed
        self.nlp = None
        if self.config.get("use_spacy", True):
            try:
                self._initialize_nlp()
            except Exception as e:
                logger.warning(f"Failed to initialize NLP components: {str(e)}")
                logger.warning("Falling back to pattern matching only")
    
    def _initialize_nlp(self) -> None:
        """Initialize NLP components (spaCy)."""
        try:
            import spacy
            
            # Load English language model
            model_name = self.config.get("spacy_model", "en_core_web_sm")
            self.nlp = spacy.load(model_name)
            
            logger.info(f"Initialized spaCy NLP with model: {model_name}")
        except ImportError:
            logger.warning("spaCy not installed. Please install with: pip install spacy")
            logger.warning("Then download a model with: python -m spacy download en_core_web_sm")
            raise
    
    async def extract_information(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract project information from raw data.
        
        Args:
            data: List of raw data items from connectors
            
        Returns:
            List of extracted information items
        """
        extracted_items = []
        
        for item in data:
            source_type = item.get("source_type")
            
            if source_type == "email":
                extracted = await self._process_email(item)
            elif source_type == "slack":
                extracted = await self._process_slack_message(item)
            elif source_type == "teams":
                extracted = await self._process_teams_message(item)
            elif source_type == "spreadsheet":
                extracted = await self._process_spreadsheet(item)
            else:
                logger.warning(f"Unknown source type: {source_type}")
                continue
            
            extracted_items.extend(extracted)
        
        return extracted_items
    
    async def _process_email(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract information from an email.
        
        Args:
            email_data: Email data from connector
            
        Returns:
            List of extracted information items
        """
        items = []
        
        try:
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            sender = email_data.get("sender", "")
            date = email_data.get("date", datetime.now())
            
            # Combine subject and body for text analysis
            text = f"{subject}\n\n{body}"
            
            # Extract project information
            project_info = await self._extract_project_from_text(text)
            if project_info:
                for project_name in project_info:
                    # Extract tasks
                    tasks = await self._extract_tasks_from_text(text, project_name)
                    items.extend(tasks)
                    
                    # Extract updates
                    updates = await self._extract_updates_from_text(text, project_name, sender)
                    items.extend(updates)
                    
                    # Extract resource information
                    resources = await self._extract_resources_from_text(text, project_name)
                    items.extend(resources)
            
            # If no project was identified but email looks project-related,
            # try to infer project from context
            if not project_info and self._is_likely_project_related(text):
                inferred_project = self._infer_project_from_context(text, subject)
                if inferred_project:
                    tasks = await self._extract_tasks_from_text(text, inferred_project)
                    items.extend(tasks)
                    
                    updates = await self._extract_updates_from_text(text, inferred_project, sender)
                    items.extend(updates)
                    
                    resources = await self._extract_resources_from_text(text, inferred_project)
                    items.extend(resources)
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
        
        return items
    
    async def _process_slack_message(self, message_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract information from a Slack message.
        
        Args:
            message_data: Slack message data from connector
            
        Returns:
            List of extracted information items
        """
        items = []
        
        try:
            text = message_data.get("text", "")
            user_name = message_data.get("user_real_name") or message_data.get("user_name", "Unknown")
            channel_name = message_data.get("channel_name", "")
            date = message_data.get("date", datetime.now())
            
            # Extract project information
            project_info = await self._extract_project_from_text(text)
            
            # If no project found, try to infer from channel name
            if not project_info:
                inferred_project = self._infer_project_from_channel(channel_name)
                if inferred_project:
                    project_info = [inferred_project]
            
            if project_info:
                for project_name in project_info:
                    # Extract tasks
                    tasks = await self._extract_tasks_from_text(text, project_name)
                    items.extend(tasks)
                    
                    # Extract updates
                    updates = await self._extract_updates_from_text(text, project_name, user_name)
                    items.extend(updates)
                    
                    # Extract resource information
                    resources = await self._extract_resources_from_text(text, project_name)
                    items.extend(resources)
        except Exception as e:
            logger.error(f"Error processing Slack message: {str(e)}")
        
        return items
    
    async def _process_teams_message(self, message_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract information from a Teams message.
        
        Args:
            message_data: Teams message data from connector
            
        Returns:
            List of extracted information items
        """
        # Similar to Slack message processing
        return await self._process_slack_message(message_data)
    
    async def _process_spreadsheet(self, spreadsheet_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract information from spreadsheet data.
        
        Args:
            spreadsheet_data: Spreadsheet data from connector
            
        Returns:
            List of extracted information items
        """
        items = []
        
        try:
            data = spreadsheet_data.get("data", {})
            
            # Check if this is a structured project spreadsheet
            if self._is_project_spreadsheet(data):
                items.extend(await self._extract_from_structured_spreadsheet(data))
            else:
                # Try to extract from unstructured spreadsheet
                if "project" in data or "Project" in data:
                    project_name = data.get("project") or data.get("Project")
                    
                    # Extract task information if available
                    if any(key in data for key in ["task", "Task", "description", "Description"]):
                        task = {
                            "type": "task",
                            "project_name": project_name,
                            "name": data.get("task") or data.get("Task") or "",
                            "description": data.get("description") or data.get("Description") or "",
                            "status": data.get("status") or data.get("Status") or "pending",
                            "owner": data.get("owner") or data.get("Owner") or data.get("assignee") or data.get("Assignee"),
                            "due_date": self._parse_date(data.get("due_date") or data.get("Due date") or data.get("deadline") or data.get("Deadline")),
                            "blockers": self._parse_list(data.get("blockers") or data.get("Blockers") or data.get("blocking") or data.get("Blocking"))
                        }
                        items.append(task)
                    
                    # Extract resource information if available
                    if any(key in data for key in ["resource", "Resource", "inventory", "Inventory"]):
                        resource = {
                            "type": "resource",
                            "project_name": project_name,
                            "resource_type": data.get("resource") or data.get("Resource") or data.get("resource_type") or data.get("Resource type") or "unknown",
                            "status": data.get("status") or data.get("Status") or "unknown",
                            "quantity": self._parse_number(data.get("quantity") or data.get("Quantity") or data.get("amount") or data.get("Amount"))
                        }
                        items.append(resource)
        except Exception as e:
            logger.error(f"Error processing spreadsheet data: {str(e)}")
        
        return items
    
    async def _extract_project_from_text(self, text: str) -> List[str]:
        """
        Extract project names from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of project names
        """
        projects = []
        
        # Use NLP if available
        if self.nlp:
            doc = await asyncio.to_thread(self.nlp, text)
            
            # Look for noun phrases that might be project names
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:
                    projects.append(ent.text)
            
            # Look for capitalized noun phrases (potential project names)
            for chunk in doc.noun_chunks:
                if chunk.text[0].isupper() and len(chunk.text.split()) <= 5:
                    projects.append(chunk.text)
        
        # Use regex patterns as fallback or supplement
        project_patterns = [
            r"[Pp]roject\s+([A-Z][a-zA-Z0-9\s\-_]+)",
            r"[Pp]roject[\s:]*([A-Z][a-zA-Z0-9\s\-_]+)",
            r"([A-Z][a-zA-Z0-9\-_]+)\s+[Pp]roject",
            r"[Ww]ork(?:ing)?\s+on\s+([A-Z][a-zA-Z0-9\s\-_]+)"
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text)
            projects.extend([match.strip() for match in matches if match.strip()])
        
        # Deduplicate and filter out common false positives
        unique_projects = []
        false_positives = ["project", "Project", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Weekend"]
        
        for project in projects:
            clean_project = project.strip()
            if (clean_project and 
                clean_project not in unique_projects and 
                clean_project not in false_positives and
                len(clean_project) > 2):
                unique_projects.append(clean_project)
        
        return unique_projects
    
    async def _extract_tasks_from_text(self, text: str, project_name: str) -> List[Dict[str, Any]]:
        """
        Extract tasks from text.
        
        Args:
            text: Text to analyze
            project_name: Name of the project
            
        Returns:
            List of task dictionaries
        """
        tasks = []
        
        # Look for task descriptions
        task_patterns = [
            r"[Tt]ask[:\s]+([^\n\.]+)",
            r"[Tt]odo[:\s]+([^\n\.]+)",
            r"[Nn]eed(?:s)?\s+to\s+([^\n\.]+)",
            r"[Hh]ave\s+to\s+([^\n\.]+)",
            r"[Mm]ust\s+([^\n\.]+)",
            r"[Ss]hould\s+([^\n\.]+)",
            r"- ([^\n\.]+)",
            r"\d+\.\s+([^\n\.]+)"
        ]
        
        task_matches = []
        for pattern in task_patterns:
            matches = re.findall(pattern, text)
            task_matches.extend([match.strip() for match in matches if match.strip()])
        
        # Look for task details
        for task_description in task_matches:
            # Skip if too short
            if len(task_description) < 5:
                continue
                
            task = {
                "type": "task",
                "project_name": project_name,
                "name": task_description,
                "description": task_description,
            }
            
            # Try to extract owner
            owner_match = re.search(r"(?:assigned to|owner|responsible)[:\s]+([^\n\.,]+)", text, re.IGNORECASE)
            if owner_match:
                task["owner"] = owner_match.group(1).strip()
            
            # Try to extract due date
            due_date_patterns = [
                r"(?:due|deadline|by)[:\s]+([^\n\.]+)",
                r"(?:due|deadline|by)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}(?:[\/\-\.]\d{2,4})?)"
            ]
            
            for pattern in due_date_patterns:
                due_match = re.search(pattern, text, re.IGNORECASE)
                if due_match:
                    raw_date = due_match.group(1).strip()
                    task["due_date"] = self._parse_date(raw_date)
                    break
            
            # Try to extract status
            status_pattern = r"(?:status|state)[:\s]+([^\n\.]+)"
            status_match = re.search(status_pattern, text, re.IGNORECASE)
            if status_match:
                status = status_match.group(1).strip().lower()
                if status in ["done", "completed", "finished"]:
                    task["status"] = "completed"
                elif status in ["in progress", "ongoing", "started", "working on"]:
                    task["status"] = "in_progress"
                elif status in ["blocked", "on hold", "waiting"]:
                    task["status"] = "blocked"
                elif status in ["not started", "todo", "to do", "planned"]:
                    task["status"] = "not_started"
                else:
                    task["status"] = "pending"
            
            # Try to extract blockers
            blocker_pattern = r"(?:blocked by|blocker|blocking)[:\s]+([^\n\.]+)"
            blocker_match = re.search(blocker_pattern, text, re.IGNORECASE)
            if blocker_match:
                task["blockers"] = [blocker_match.group(1).strip()]
            
            tasks.append(task)
        
        return tasks
    
    async def _extract_updates_from_text(self, text: str, project_name: str, author: str) -> List[Dict[str, Any]]:
        """
        Extract project updates from text.
        
        Args:
            text: Text to analyze
            project_name: Name of the project
            author: Author of the update
            
        Returns:
            List of update dictionaries
        """
        updates = []
        
        # Look for update indicators
        update_patterns = [
            r"[Uu]pdate[:\s]+([^\n]+)",
            r"[Ss]tatus[:\s]+([^\n]+)",
            r"[Pp]rogress[:\s]+([^\n]+)",
            r"[Cc]ompleted[:\s]+([^\n]+)",
            r"[Ff]inished[:\s]+([^\n]+)"
        ]
        
        for pattern in update_patterns:
            update_match = re.search(pattern, text, re.IGNORECASE)
            if update_match:
                update = {
                    "type": "update",
                    "project_name": project_name,
                    "content": update_match.group(1).strip(),
                    "author": author,
                }
                
                # Try to determine update type
                content = update["content"].lower()
                if any(word in content for word in ["complete", "finished", "done"]):
                    update["update_type"] = "completion"
                elif any(word in content for word in ["start", "began", "kick", "off"]):
                    update["update_type"] = "initiation"
                elif any(word in content for word in ["block", "issue", "problem", "challenge"]):
                    update["update_type"] = "blocker"
                elif any(word in content for word in ["milestone", "goal", "target"]):
                    update["update_type"] = "milestone"
                else:
                    update["update_type"] = "progress"
                
                updates.append(update)
        
        # If no specific updates found but text is project-related,
        # consider the whole text as a general update
        if not updates and self._is_likely_project_related(text):
            updates.append({
                "type": "update",
                "project_name": project_name,
                "content": text[:200] + ("..." if len(text) > 200 else ""),  # Truncate if too long
                "author": author,
                "update_type": "general"
            })
        
        return updates
    
    async def _extract_resources_from_text(self, text: str, project_name: str) -> List[Dict[str, Any]]:
        """
        Extract resource information from text.
        
        Args:
            text: Text to analyze
            project_name: Name of the project
            
        Returns:
            List of resource dictionaries
        """
        resources = []
        
        # Look for inventory/resource mentions
        resource_patterns = [
            r"(?:inventory|stock|resource)[:\s]+([^\n\.]+)",
            r"([0-9]+)\s+(?:units|pieces|items)\s+of\s+([^\n\.]+)",
            r"([^\n\.]+)\s+(?:inventory|stock|level)[:\s]+([0-9]+)",
            r"(?:need|require)\s+([0-9]+)\s+([^\n\.]+)"
        ]
        
        for pattern in resource_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 1:
                    resource_info = match.group(1).strip()
                    parts = resource_info.split()
                    
                    # Try to extract quantity and type
                    quantity = None
                    resource_type = resource_info
                    
                    for part in parts:
                        if part.isdigit():
                            quantity = int(part)
                            resource_type = resource_info.replace(part, "").strip()
                            break
                    
                    resources.append({
                        "type": "resource",
                        "project_name": project_name,
                        "resource_type": resource_type,
                        "status": "available",
                        "quantity": quantity
                    })
                elif len(match.groups()) == 2:
                    # Pattern captures quantity and resource type
                    try:
                        quantity = int(match.group(1))
                        resource_type = match.group(2).strip()
                    except ValueError:
                        quantity = None
                        resource_type = match.group(1).strip()
                    
                    resources.append({
                        "type": "resource",
                        "project_name": project_name,
                        "resource_type": resource_type,
                        "status": "available",
                        "quantity": quantity
                    })
        
        # Look for staffing information
        staffing_patterns = [
            r"([0-9]+)\s+(?:staff|employees|workers|people|resources|engineers|developers)",
            r"(?:team|staff|headcount)[:\s]+([0-9]+)",
            r"(?:assign|allocate)\s+([0-9]+)\s+(?:people|staff|employees|workers|resources)"
        ]
        
        for pattern in staffing_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    quantity = int(match.group(1))
                    resources.append({
                        "type": "resource",
                        "project_name": project_name,
                        "resource_type": "staff",
                        "status": "allocated",
                        "quantity": quantity
                    })
                except ValueError:
                    pass
        
        return resources
    
    def _is_likely_project_related(self, text: str) -> bool:
        """
        Check if text is likely project-related.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if the text is likely related to a project
        """
        project_indicators = [
            "task", "deadline", "milestone", "project", "status", "update",
            "progress", "timeline", "schedule", "deliverable", "sprint",
            "backlog", "priority", "goal", "objective", "blocker", "resource",
            "budget", "assigned", "owner", "due date"
        ]
        
        text_lower = text.lower()
        matches = sum(1 for indicator in project_indicators if indicator in text_lower)
        
        # If at least 2 indicators are present, likely project-related
        return matches >= 2
    
    def _infer_project_from_context(self, text: str, subject: str = "") -> Optional[str]:
        """
        Infer project name from context.
        
        Args:
            text: Text to analyze
            subject: Subject line (for emails)
            
        Returns:
            Inferred project name or None
        """
        # First check subject line for project-like names
        if subject:
            subject_words = subject.split()
            for word in subject_words:
                if word[0].isupper() and len(word) > 2 and word.lower() not in ["the", "and", "for", "from", "with"]:
                    return word
        
        # Look for capitalized words in text
        words = text.split()
        for word in words:
            clean_word = word.strip(".,;:()[]{}")
            if (clean_word and clean_word[0].isupper() and 
                len(clean_word) > 2 and 
                clean_word.lower() not in ["the", "and", "for", "from", "with", "monday", "tuesday", "wednesday", "thursday", "friday"]):
                return clean_word
        
        return None
    
    def _infer_project_from_channel(self, channel_name: str) -> Optional[str]:
        """
        Infer project name from channel name.
        
        Args:
            channel_name: Channel name
            
        Returns:
            Inferred project name or None
        """
        if not channel_name:
            return None
        
        # Remove common prefixes
        prefixes = ["team-", "project-", "proj-", "prj-", "channel-", "ch-"]
        name = channel_name
        for prefix in prefixes:
            if name.lower().startswith(prefix):
                name = name[len(prefix):]
                break
        
        # Capitalize first letter of each word
        parts = name.split("-")
        name = " ".join(part.capitalize() for part in parts)
        
        # Return if seems like a reasonable project name
        if len(name) > 2:
            return name
        
        return None
    
    def _is_project_spreadsheet(self, data: Dict[str, Any]) -> bool:
        """
        Check if a spreadsheet appears to be project-related.
        
        Args:
            data: Spreadsheet data
            
        Returns:
            True if the spreadsheet is likely project-related
        """
        project_indicators = [
            "project", "task", "milestone", "status", "owner", "assignee",
            "due date", "deadline", "priority", "progress", "description"
        ]
        
        # Check if at least 2 indicators are in the keys
        matches = 0
        for key in data.keys():
            if any(indicator.lower() in key.lower() for indicator in project_indicators):
                matches += 1
        
        return matches >= 2
    
    async def _extract_from_structured_spreadsheet(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract information from a structured project spreadsheet.
        
        Args:
            data: Spreadsheet data
            
        Returns:
            List of extracted information items
        """
        # This is a placeholder - in a real implementation, this would
        # handle various common spreadsheet formats
        return []
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse a date string.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed datetime or None
        """
        if not date_str:
            return None
        
        try:
            # Try various date formats
            from dateutil import parser
            return parser.parse(date_str)
        except Exception:
            try:
                # Try common formats manually
                import re
                
                # MM/DD/YYYY or DD/MM/YYYY
                match = re.match(r"(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})", date_str)
                if match:
                    month, day, year = map(int, match.groups())
                    if year < 100:
                        year += 2000
                    return datetime(year, month, day)
                
                # Month name formats
                months = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
                }
                
                match = re.match(r"(\d{1,2})\s+([a-zA-Z]{3,9})(?:\s+(\d{2,4}))?", date_str)
                if match:
                    day, month_name, year = match.groups()
                    month = months.get(month_name.lower()[:3])
                    year = int(year) if year else datetime.now().year
                    if year < 100:
                        year += 2000
                    return datetime(year, month, int(day))
            except Exception:
                pass
        
        return None
    
    def _parse_number(self, number_str: Optional[str]) -> Optional[int]:
        """
        Parse a number string.
        
        Args:
            number_str: Number string to parse
            
        Returns:
            Parsed integer or None
        """
        if not number_str:
            return None
        
        try:
            return int(number_str)
        except ValueError:
            try:
                return int(float(number_str))
            except ValueError:
                return None
    
    def _parse_list(self, list_str: Optional[str]) -> List[str]:
        """
        Parse a comma-separated list string.
        
        Args:
            list_str: List string to parse
            
        Returns:
            List of strings
        """
        if not list_str:
            return []
        
        return [item.strip() for item in list_str.split(",") if item.strip()]