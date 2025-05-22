"""
Intelligence alert system for the Project Intelligence System.

This module provides intelligent alert functionality for monitoring
project status, task blockers, and other critical issues.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple

from ..models.project import Project, Task, ProjectUpdate, ResourceStatus

logger = logging.getLogger(__name__)


class AlertGenerator:
    """
    Generates intelligent alerts based on project data.
    
    This class analyzes project data to identify potential issues
    and generate appropriate alerts.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the alert generator.
        
        Args:
            config: Configuration dictionary with the following keys:
                - blocked_task_threshold: Days a task can be blocked before alerting (default: 2)
                - approaching_deadline_threshold: Days before alerting about approaching deadlines (default: 7)
                - overdue_threshold: Days a task can be overdue before escalating (default: 3)
                - resource_low_threshold: Percentage below which resources are considered low (default: 25)
                - high_risk_threshold: Risk score threshold for high-risk alerts (default: 0.7)
                - risk_factors: Weights for different risk factors (default: balanced)
        """
        self.config = config or {}
        
        # Configure thresholds
        self.blocked_task_threshold = self.config.get("blocked_task_threshold", 2)
        self.approaching_deadline_threshold = self.config.get("approaching_deadline_threshold", 7)
        self.overdue_threshold = self.config.get("overdue_threshold", 3)
        self.resource_low_threshold = self.config.get("resource_low_threshold", 25)
        self.high_risk_threshold = self.config.get("high_risk_threshold", 0.7)
        
        # Configure risk factor weights
        self.risk_factors = self.config.get("risk_factors", {
            "blocked_days": 0.4,
            "overdue_days": 0.3,
            "completion_percentage": 0.2,
            "resource_availability": 0.1
        })
    
    async def generate_alerts(self, projects: Dict[str, Project]) -> List[Dict[str, Any]]:
        """
        Generate alerts for all projects.
        
        Args:
            projects: Dictionary of projects
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Generate alerts for each project
        for project_name, project in projects.items():
            project_alerts = await self._analyze_project(project_name, project)
            alerts.extend(project_alerts)
        
        # Sort alerts by severity (critical first)
        alerts.sort(key=lambda x: self._get_severity_sort_order(x.get("severity")))
        
        return alerts
    
    def _get_severity_sort_order(self, severity: str) -> int:
        """Get sort order value for severity level."""
        severity_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
            "info": 4
        }
        return severity_order.get(severity.lower(), 99)
    
    async def _analyze_project(self, project_name: str, project: Project) -> List[Dict[str, Any]]:
        """
        Analyze a project for potential issues.
        
        Args:
            project_name: Name of the project
            project: Project object to analyze
            
        Returns:
            List of alert dictionaries for the project
        """
        alerts = []
        
        # Check project status
        if project.status == "on_hold":
            alerts.append(self._create_alert(
                project_name=project_name,
                alert_type="project_on_hold",
                severity="high",
                title=f"Project '{project_name}' is on hold",
                description=f"The project has been placed on hold and may require attention.",
                metadata={
                    "project_status": project.status,
                    "owner": project.owner
                }
            ))
        
        # Analyze blocked tasks
        blocked_alerts = self._analyze_blocked_tasks(project_name, project)
        alerts.extend(blocked_alerts)
        
        # Analyze approaching and overdue deadlines
        deadline_alerts = self._analyze_deadlines(project_name, project)
        alerts.extend(deadline_alerts)
        
        # Analyze resource status
        resource_alerts = self._analyze_resources(project_name, project)
        alerts.extend(resource_alerts)
        
        # Analyze project progress
        progress_alerts = self._analyze_progress(project_name, project)
        alerts.extend(progress_alerts)
        
        # Analyze staffing allocation
        staffing_alerts = self._analyze_staffing(project_name, project)
        alerts.extend(staffing_alerts)
        
        return alerts
    
    def _analyze_blocked_tasks(self, project_name: str, project: Project) -> List[Dict[str, Any]]:
        """
        Analyze blocked tasks in a project.
        
        Args:
            project_name: Name of the project
            project: Project object to analyze
            
        Returns:
            List of alert dictionaries for blocked tasks
        """
        alerts = []
        now = datetime.now()
        
        # Find tasks that are marked as blocked
        blocked_tasks = [
            task for task in project.tasks.values()
            if task.status == "blocked" or len(task.blockers) > 0
        ]
        
        for task in blocked_tasks:
            # If the task has been updated recently, check how long it's been blocked
            blocked_duration = None
            if task.updated_at:
                blocked_duration = (now - task.updated_at).days
            
            # Create appropriate alert based on blocked duration
            if blocked_duration is not None and blocked_duration >= self.blocked_task_threshold:
                severity = "medium"
                if blocked_duration >= self.blocked_task_threshold * 2:
                    severity = "high"
                if blocked_duration >= self.blocked_task_threshold * 3:
                    severity = "critical"
                
                alerts.append(self._create_alert(
                    project_name=project_name,
                    alert_type="blocked_task",
                    severity=severity,
                    title=f"Task '{task.name}' has been blocked for {blocked_duration} days",
                    description=f"The task has blockers: {', '.join(task.blockers)}",
                    metadata={
                        "task_id": task.id,
                        "task_name": task.name,
                        "owner": task.owner,
                        "blocked_days": blocked_duration,
                        "blockers": task.blockers
                    },
                    suggested_actions=[
                        f"Contact {task.owner or 'the task owner'} to discuss blockers",
                        "Schedule a meeting to resolve blockers",
                        "Reassign task if the current owner cannot proceed"
                    ]
                ))
        
        return alerts
    
    def _analyze_deadlines(self, project_name: str, project: Project) -> List[Dict[str, Any]]:
        """
        Analyze approaching and overdue deadlines in a project.
        
        Args:
            project_name: Name of the project
            project: Project object to analyze
            
        Returns:
            List of alert dictionaries for deadline issues
        """
        alerts = []
        now = datetime.now()
        
        # Analyze all tasks with due dates
        for task in project.tasks.values():
            if not task.due_date or task.status == "completed":
                continue
            
            # Calculate days until deadline or days overdue
            days_diff = (task.due_date - now).days
            
            if days_diff < 0:
                # Task is overdue
                overdue_days = abs(days_diff)
                severity = "medium"
                if overdue_days >= self.overdue_threshold:
                    severity = "high"
                if overdue_days >= self.overdue_threshold * 2:
                    severity = "critical"
                
                alerts.append(self._create_alert(
                    project_name=project_name,
                    alert_type="overdue_task",
                    severity=severity,
                    title=f"Task '{task.name}' is overdue by {overdue_days} days",
                    description=f"The task was due on {task.due_date.strftime('%Y-%m-%d')} and has not been completed.",
                    metadata={
                        "task_id": task.id,
                        "task_name": task.name,
                        "owner": task.owner,
                        "due_date": task.due_date.isoformat(),
                        "overdue_days": overdue_days
                    },
                    suggested_actions=[
                        f"Contact {task.owner or 'the task owner'} for status update",
                        "Reassess the timeline and update the due date if necessary",
                        "Provide additional resources to complete the task"
                    ]
                ))
            elif days_diff <= self.approaching_deadline_threshold:
                # Task deadline is approaching
                completion_pct = task.completion_percentage or 0
                
                # Calculate expected completion based on time elapsed
                expected_completion = None
                if task.start_date:
                    total_duration = (task.due_date - task.start_date).total_seconds()
                    if total_duration > 0:
                        elapsed = (now - task.start_date).total_seconds()
                        expected_completion = min(100, (elapsed / total_duration) * 100)
                
                # Alert if task is behind schedule
                if expected_completion is not None and completion_pct < expected_completion * 0.8:
                    alerts.append(self._create_alert(
                        project_name=project_name,
                        alert_type="behind_schedule",
                        severity="medium",
                        title=f"Task '{task.name}' is behind schedule with deadline in {days_diff} days",
                        description=f"The task is {completion_pct:.1f}% complete but should be at {expected_completion:.1f}% based on timeline.",
                        metadata={
                            "task_id": task.id,
                            "task_name": task.name,
                            "owner": task.owner,
                            "due_date": task.due_date.isoformat(),
                            "days_remaining": days_diff,
                            "completion": completion_pct,
                            "expected_completion": expected_completion
                        },
                        suggested_actions=[
                            f"Contact {task.owner or 'the task owner'} to verify progress",
                            "Allocate additional resources to accelerate completion",
                            "Adjust the timeline or scope if necessary"
                        ]
                    ))
                elif days_diff <= 3:
                    # Deadline is very close
                    alerts.append(self._create_alert(
                        project_name=project_name,
                        alert_type="approaching_deadline",
                        severity="medium",
                        title=f"Task '{task.name}' deadline is in {days_diff} days",
                        description=f"The task is due on {task.due_date.strftime('%Y-%m-%d')} and is {completion_pct:.1f}% complete.",
                        metadata={
                            "task_id": task.id,
                            "task_name": task.name,
                            "owner": task.owner,
                            "due_date": task.due_date.isoformat(),
                            "days_remaining": days_diff,
                            "completion": completion_pct
                        }
                    ))
        
        # Check overall project deadline
        if project.end_date:
            days_to_project_deadline = (project.end_date - now).days
            completion_pct = project.get_completion_percentage()
            
            if days_to_project_deadline < 0:
                # Project is overdue
                overdue_days = abs(days_to_project_deadline)
                alerts.append(self._create_alert(
                    project_name=project_name,
                    alert_type="overdue_project",
                    severity="high",
                    title=f"Project '{project_name}' is overdue by {overdue_days} days",
                    description=f"The project was scheduled to complete on {project.end_date.strftime('%Y-%m-%d')} and is {completion_pct:.1f}% complete.",
                    metadata={
                        "project_name": project_name,
                        "end_date": project.end_date.isoformat(),
                        "overdue_days": overdue_days,
                        "completion": completion_pct
                    }
                ))
            elif days_to_project_deadline <= 14 and completion_pct < 80:
                # Project may not complete on time
                alerts.append(self._create_alert(
                    project_name=project_name,
                    alert_type="at_risk_project",
                    severity="high",
                    title=f"Project '{project_name}' may not complete on time",
                    description=f"The project is due in {days_to_project_deadline} days but is only {completion_pct:.1f}% complete.",
                    metadata={
                        "project_name": project_name,
                        "end_date": project.end_date.isoformat(),
                        "days_remaining": days_to_project_deadline,
                        "completion": completion_pct
                    }
                ))
        
        return alerts
    
    def _analyze_resources(self, project_name: str, project: Project) -> List[Dict[str, Any]]:
        """
        Analyze resource status in a project.
        
        Args:
            project_name: Name of the project
            project: Project object to analyze
            
        Returns:
            List of alert dictionaries for resource issues
        """
        alerts = []
        
        # Check each resource
        for resource_type, resource in project.resources.items():
            if resource.status in ["depleted", "low"]:
                severity = "medium" if resource.status == "low" else "high"
                
                alerts.append(self._create_alert(
                    project_name=project_name,
                    alert_type="resource_issue",
                    severity=severity,
                    title=f"{resource_type.capitalize()} resource is {resource.status}",
                    description=f"The {resource_type} resource for project '{project_name}' is {resource.status}.",
                    metadata={
                        "resource_type": resource_type,
                        "status": resource.status,
                        "quantity": resource.quantity,
                        "last_updated": resource.last_updated.isoformat() if resource.last_updated else None
                    },
                    suggested_actions=[
                        f"Allocate additional {resource_type} resources to the project",
                        "Reassess resource requirements and adjust planning",
                        "Prioritize tasks to make optimal use of limited resources"
                    ]
                ))
        
        return alerts
    
    def _analyze_progress(self, project_name: str, project: Project) -> List[Dict[str, Any]]:
        """
        Analyze project progress.
        
        Args:
            project_name: Name of the project
            project: Project object to analyze
            
        Returns:
            List of alert dictionaries for progress issues
        """
        alerts = []
        
        # Check for stalled progress
        completion_pct = project.get_completion_percentage()
        
        # Get recent updates
        updates = sorted(project.updates, key=lambda u: u.timestamp, reverse=True)
        latest_update = updates[0] if updates else None
        
        # Check for recent activity
        if latest_update:
            days_since_update = (datetime.now() - latest_update.timestamp).days
            
            if days_since_update >= 7 and project.status == "active":
                alerts.append(self._create_alert(
                    project_name=project_name,
                    alert_type="no_recent_activity",
                    severity="medium",
                    title=f"No updates for project '{project_name}' in {days_since_update} days",
                    description=f"The project is active but has not had any updates recorded in {days_since_update} days.",
                    metadata={
                        "days_since_update": days_since_update,
                        "last_update": latest_update.timestamp.isoformat(),
                        "last_update_author": latest_update.author
                    }
                ))
        
        # Check for stalled completion percentage
        stalled_threshold = 14  # Two weeks
        if len(updates) >= 2:
            # Check if completion percentage hasn't changed significantly
            recent_updates = [u for u in updates if (datetime.now() - u.timestamp).days <= stalled_threshold]
            
            if recent_updates and completion_pct < 90:
                # Get completion percentage from earlier update if available
                has_stalled = False
                for update in recent_updates:
                    if "completion_percentage" in update.metadata:
                        old_completion = update.metadata["completion_percentage"]
                        if abs(completion_pct - old_completion) < 5:  # Less than 5% change
                            has_stalled = True
                            break
                
                if has_stalled:
                    alerts.append(self._create_alert(
                        project_name=project_name,
                        alert_type="stalled_progress",
                        severity="medium",
                        title=f"Progress on project '{project_name}' has stalled",
                        description=f"The project completion percentage has not changed significantly in the past {stalled_threshold} days.",
                        metadata={
                            "completion": completion_pct,
                            "days_stalled": stalled_threshold
                        }
                    ))
        
        return alerts
    
    def _analyze_staffing(self, project_name: str, project: Project) -> List[Dict[str, Any]]:
        """
        Analyze staffing allocation in a project.
        
        Args:
            project_name: Name of the project
            project: Project object to analyze
            
        Returns:
            List of alert dictionaries for staffing issues
        """
        alerts = []
        
        # Collect tasks by owner
        tasks_by_owner = {}
        for task in project.tasks.values():
            if task.status != "completed" and task.owner:
                if task.owner not in tasks_by_owner:
                    tasks_by_owner[task.owner] = []
                tasks_by_owner[task.owner].append(task)
        
        # Check for overloaded team members
        for owner, tasks in tasks_by_owner.items():
            if len(tasks) >= 5:
                # Count tasks with approaching/overdue deadlines
                now = datetime.now()
                urgent_tasks = []
                
                for task in tasks:
                    if task.due_date and (task.due_date - now).days <= self.approaching_deadline_threshold:
                        urgent_tasks.append(task)
                
                if len(urgent_tasks) >= 3:
                    alerts.append(self._create_alert(
                        project_name=project_name,
                        alert_type="resource_overload",
                        severity="high",
                        title=f"Team member {owner} is overloaded with {len(urgent_tasks)} urgent tasks",
                        description=f"{owner} has {len(tasks)} active tasks, with {len(urgent_tasks)} due within {self.approaching_deadline_threshold} days.",
                        metadata={
                            "owner": owner,
                            "total_tasks": len(tasks),
                            "urgent_tasks": len(urgent_tasks),
                            "task_ids": [task.id for task in urgent_tasks]
                        },
                        suggested_actions=[
                            f"Reassign some tasks from {owner} to other team members",
                            "Prioritize tasks to focus on the most critical ones",
                            "Extend deadlines for less critical tasks"
                        ]
                    ))
                elif len(tasks) >= 8:
                    # Many tasks but not all urgent
                    alerts.append(self._create_alert(
                        project_name=project_name,
                        alert_type="high_workload",
                        severity="medium",
                        title=f"Team member {owner} has a high workload with {len(tasks)} tasks",
                        description=f"{owner} is assigned to {len(tasks)} active tasks, which may impact productivity.",
                        metadata={
                            "owner": owner,
                            "total_tasks": len(tasks),
                            "task_ids": [task.id for task in tasks]
                        }
                    ))
        
        return alerts
    
    def _create_alert(self,
                     project_name: str,
                     alert_type: str,
                     severity: str,
                     title: str,
                     description: str,
                     metadata: Optional[Dict[str, Any]] = None,
                     suggested_actions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create an alert dictionary.
        
        Args:
            project_name: Name of the project
            alert_type: Type of alert
            severity: Alert severity (critical, high, medium, low, info)
            title: Alert title
            description: Alert description
            metadata: Additional metadata for the alert
            suggested_actions: List of suggested actions to resolve the alert
            
        Returns:
            Alert dictionary
        """
        return {
            "project_name": project_name,
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "suggested_actions": suggested_actions or [],
            "id": f"{alert_type}_{project_name}_{datetime.now().timestamp()}"
        }


class ReschedulingRecommender:
    """
    Recommends task rescheduling based on team workload and dependencies.
    
    This class analyzes task assignments, deadlines, and dependencies to
    recommend optimal rescheduling of tasks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the rescheduling recommender.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    async def generate_recommendations(self, projects: Dict[str, Project]) -> List[Dict[str, Any]]:
        """
        Generate rescheduling recommendations.
        
        Args:
            projects: Dictionary of projects
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Collect all active tasks across projects
        all_tasks = []
        for project_name, project in projects.items():
            for task in project.tasks.values():
                if task.status not in ["completed", "cancelled"]:
                    task_info = {
                        "project_name": project_name,
                        "task": task
                    }
                    all_tasks.append(task_info)
        
        # Group tasks by owner
        tasks_by_owner = {}
        for task_info in all_tasks:
            owner = task_info["task"].owner
            if owner:
                if owner not in tasks_by_owner:
                    tasks_by_owner[owner] = []
                tasks_by_owner[owner].append(task_info)
        
        # Analyze workload and generate rescheduling recommendations
        for owner, owner_tasks in tasks_by_owner.items():
            # Sort tasks by due date
            owner_tasks.sort(key=lambda x: x["task"].due_date or datetime.max)
            
            # Look for overloaded periods
            overloaded_periods = self._identify_overloaded_periods(owner_tasks)
            
            for period in overloaded_periods:
                # Find tasks that could be rescheduled
                reschedulable_tasks = self._identify_reschedulable_tasks(period["tasks"], projects)
                
                if reschedulable_tasks:
                    # Generate recommendation
                    recommendations.append({
                        "type": "reschedule_recommendation",
                        "owner": owner,
                        "period_start": period["start"].isoformat(),
                        "period_end": period["end"].isoformat(),
                        "task_count": len(period["tasks"]),
                        "reschedulable_tasks": [
                            {
                                "project_name": task["project_name"],
                                "task_id": task["task"].id,
                                "task_name": task["task"].name,
                                "current_due_date": task["task"].due_date.isoformat() if task["task"].due_date else None,
                                "suggested_due_date": suggested_date.isoformat() if suggested_date else None,
                                "priority": task["task"].priority
                            }
                            for task, suggested_date in reschedulable_tasks
                        ],
                        "reason": f"Workload for {owner} is high during this period with {len(period['tasks'])} tasks due",
                        "timestamp": datetime.now().isoformat()
                    })
        
        return recommendations
    
    def _identify_overloaded_periods(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify periods where a team member is overloaded.
        
        Args:
            tasks: List of task info dictionaries for an owner
            
        Returns:
            List of overloaded period dictionaries
        """
        # This is a simplified implementation - a real version would use a more
        # sophisticated algorithm to identify overlapping due dates and workload
        
        overloaded_periods = []
        
        # Group tasks by week
        tasks_by_week = {}
        for task_info in tasks:
            task = task_info["task"]
            if task.due_date:
                # Get the start of the week
                week_start = task.due_date - timedelta(days=task.due_date.weekday())
                week_key = week_start.strftime("%Y-%m-%d")
                
                if week_key not in tasks_by_week:
                    tasks_by_week[week_key] = {
                        "start": week_start,
                        "end": week_start + timedelta(days=6),
                        "tasks": []
                    }
                
                tasks_by_week[week_key]["tasks"].append(task_info)
        
        # Identify weeks with too many tasks
        for week_key, week_data in tasks_by_week.items():
            if len(week_data["tasks"]) >= 3:
                overloaded_periods.append(week_data)
        
        return overloaded_periods
    
    def _identify_reschedulable_tasks(self, tasks: List[Dict[str, Any]], projects: Dict[str, Project]) -> List[Tuple[Dict[str, Any], Optional[datetime]]]:
        """
        Identify tasks that could be rescheduled and suggest new dates.
        
        Args:
            tasks: List of task info dictionaries
            projects: Dictionary of projects
            
        Returns:
            List of tuples with task info and suggested new due date
        """
        # Sort tasks by priority (higher priority first)
        priority_order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
        sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x["task"].priority, 3))
        
        # Find lower priority tasks that could be rescheduled
        reschedulable = []
        
        for task_info in sorted_tasks:
            task = task_info["task"]
            project = projects.get(task_info["project_name"])
            
            # Skip high priority tasks
            if task.priority == "high":
                continue
            
            # Check if this task has dependents
            has_dependents = False
            if project:
                for other_task in project.tasks.values():
                    if task.id in other_task.dependencies:
                        has_dependents = True
                        break
            
            # If no dependents and not high priority, consider reschedulable
            if not has_dependents:
                # Suggest a new due date (+7 days as a simple heuristic)
                suggested_date = task.due_date + timedelta(days=7) if task.due_date else None
                reschedulable.append((task_info, suggested_date))
                
                # Only reschedule a few tasks
                if len(reschedulable) >= 2:
                    break
        
        return reschedulable


class AssignmentRecommender:
    """
    Recommends task assignments based on team expertise and workload.
    
    This class analyzes team member workloads, skills, and task requirements
    to recommend optimal task assignments.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the assignment recommender.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Create LLM client for determining task assignments
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o")
    
    async def recommend_assignment(self, projects: Dict[str, Project], task: Task, project_name: str) -> List[Dict[str, Any]]:
        """
        Recommend team members for task assignment.
        
        Args:
            projects: Dictionary of projects
            task: Task to assign
            project_name: Name of the project
            
        Returns:
            List of recommendation dictionaries
        """
        # Get team members and their workloads
        team_workloads = self._get_team_workloads(projects)
        
        # Get team members on this project
        project = projects.get(project_name)
        project_team = project.team_members if project else []
        
        # Create a prompt for the LLM to determine the best assignment
        prompt = self._create_assignment_prompt(task, project_name, team_workloads, project_team)
        
        # Get recommendations from LLM
        from langchain_core.messages import HumanMessage
        result = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        # Parse the LLM response
        recommendations = self._parse_llm_response(result.content, team_workloads)
        
        return recommendations
    
    def _get_team_workloads(self, projects: Dict[str, Project]) -> Dict[str, Dict[str, Any]]:
        """
        Get workload information for all team members.
        
        Args:
            projects: Dictionary of projects
            
        Returns:
            Dictionary mapping team members to their workload info
        """
        workloads = {}
        
        # Collect all team members
        for project in projects.values():
            for member in project.team_members:
                if member not in workloads:
                    workloads[member] = {
                        "active_tasks": 0,
                        "upcoming_deadlines": 0,
                        "projects": set(),
                        "skills": set()
                    }
            
            # Collect task assignments
            for task in project.tasks.values():
                if task.status != "completed" and task.owner:
                    if task.owner not in workloads:
                        workloads[task.owner] = {
                            "active_tasks": 0,
                            "upcoming_deadlines": 0,
                            "projects": set(),
                            "skills": set()
                        }
                    
                    workloads[task.owner]["active_tasks"] += 1
                    workloads[task.owner]["projects"].add(project.name)
                    
                    # Check for upcoming deadlines
                    if task.due_date and (task.due_date - datetime.now()).days <= 7:
                        workloads[task.owner]["upcoming_deadlines"] += 1
                    
                    # Infer skills from task names and descriptions
                    if task.name:
                        self._extract_skills(task.name, workloads[task.owner]["skills"])
                    if task.description:
                        self._extract_skills(task.description, workloads[task.owner]["skills"])
        
        # Convert sets to lists for easier serialization
        for member, info in workloads.items():
            info["projects"] = list(info["projects"])
            info["skills"] = list(info["skills"])
        
        return workloads
    
    def _extract_skills(self, text: str, skills_set: set) -> None:
        """
        Extract potential skills from text.
        
        Args:
            text: Text to analyze
            skills_set: Set to add extracted skills to
        """
        # This is a simplified implementation - a real version would use
        # a more sophisticated NLP approach or a predefined skills taxonomy
        
        # Common technical skills to look for
        skill_keywords = [
            "python", "java", "javascript", "react", "angular", "vue", "node",
            "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "devops",
            "machine learning", "ai", "data science", "analytics", "bi",
            "frontend", "backend", "fullstack", "mobile", "android", "ios",
            "database", "sql", "nosql", "mongodb", "postgresql", "mysql",
            "design", "ui", "ux", "product", "project management", "agile", "scrum",
            "testing", "qa", "security", "networking", "infrastructure", "architecture",
            "research", "analysis", "documentation", "support", "training"
        ]
        
        # Check for skills in the text
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills_set.add(skill)
    
    def _create_assignment_prompt(self, task: Task, project_name: str, team_workloads: Dict[str, Dict[str, Any]], project_team: List[str]) -> str:
        """
        Create a prompt for the LLM to determine the best assignment.
        
        Args:
            task: Task to assign
            project_name: Name of the project
            team_workloads: Dictionary of team member workloads
            project_team: List of team members on this project
            
        Returns:
            Prompt string for the LLM
        """
        # Build task information
        task_info = f"""
Task Information:
- Project: {project_name}
- Task Name: {task.name}
- Description: {task.description}
- Priority: {task.priority}
- Due Date: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'Not set'}
- Status: {task.status}
- Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}
- Blockers: {', '.join(task.blockers) if task.blockers else 'None'}
"""
        
        # Build team information
        team_info = "Team Information:\n"
        for member, info in team_workloads.items():
            # Indicate if the member is part of the project team
            is_project_member = member in project_team
            team_info += f"""
- Name: {member} {'(Project Team Member)' if is_project_member else ''}
  * Active Tasks: {info['active_tasks']}
  * Upcoming Deadlines: {info['upcoming_deadlines']}
  * Projects: {', '.join(info['projects'])}
  * Skills: {', '.join(info['skills'])}
"""
        
        # Build the full prompt
        prompt = f"""You are an AI assistant that specializes in project management and task assignment. 
Given the following information about a task and potential team members, recommend who should be assigned to this task.

{task_info}

{team_info}

Please provide 1-3 recommendations for who should be assigned to this task. For each recommendation, explain your reasoning and provide a confidence score (0-100%).

Your response should be in the following format:

Recommendation 1: [Name] (Confidence: X%)
Reason: [Brief explanation why this person is a good fit]

Recommendation 2: [Name] (Confidence: Y%)
Reason: [Brief explanation why this person is a good fit]

Recommendation 3: [Name] (Confidence: Z%)
Reason: [Brief explanation why this person is a good fit]

If there are fewer than 3 good candidates, you may provide fewer recommendations.
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, team_workloads: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse the LLM response to extract recommendations.
        
        Args:
            response: Response string from the LLM
            team_workloads: Dictionary of team member workloads
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Use a simple regex-based approach to extract recommendations
        import re
        recommendation_pattern = r"Recommendation\s+\d+:\s+([^\(]+)\s+\(Confidence:\s+(\d+)%\)\s+Reason:\s+([^\n]+)"
        
        matches = re.findall(recommendation_pattern, response)
        
        for match in matches:
            name = match[0].strip()
            confidence = int(match[1])
            reason = match[2].strip()
            
            # Get workload info if available
            workload = team_workloads.get(name, {
                "active_tasks": 0,
                "upcoming_deadlines": 0,
                "projects": [],
                "skills": []
            })
            
            recommendations.append({
                "name": name,
                "confidence": confidence,
                "reason": reason,
                "active_tasks": workload["active_tasks"],
                "upcoming_deadlines": workload["upcoming_deadlines"],
                "projects": workload["projects"],
                "skills": workload["skills"]
            })
        
        # Sort by confidence (highest first)
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return recommendations


class PerformanceAnalyzer:
    """
    Analyzes project performance trends over time.
    
    This class calculates velocity, burn-down rates, and other
    performance metrics to identify trends and potential issues.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the performance analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.history = {}  # Store historical performance data
    
    async def update_history(self, projects: Dict[str, Project]) -> None:
        """
        Update the performance history with current project data.
        
        Args:
            projects: Dictionary of projects
        """
        current_time = datetime.now()
        
        for project_name, project in projects.items():
            if project_name not in self.history:
                self.history[project_name] = []
            
            # Calculate current metrics
            metrics = {
                "timestamp": current_time,
                "completion_percentage": project.get_completion_percentage(),
                "total_tasks": len(project.tasks),
                "completed_tasks": sum(1 for task in project.tasks.values() if task.status == "completed"),
                "active_tasks": sum(1 for task in project.tasks.values() if task.status not in ["completed", "cancelled"]),
                "blocked_tasks": sum(1 for task in project.tasks.values() if task.status == "blocked" or len(task.blockers) > 0),
                "overdue_tasks": sum(1 for task in project.tasks.values() 
                                    if task.due_date and task.due_date < current_time and task.status != "completed")
            }
            
            # Add historical point
            self.history[project_name].append(metrics)
            
            # Limit history size (keep last 30 points)
            if len(self.history[project_name]) > 30:
                self.history[project_name] = self.history[project_name][-30:]
    
    async def analyze_trends(self, project_name: str) -> Dict[str, Any]:
        """
        Analyze performance trends for a project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary of trend analysis results
        """
        if project_name not in self.history or len(self.history[project_name]) < 2:
            return {
                "project_name": project_name,
                "status": "insufficient_data",
                "message": "Not enough historical data to analyze trends"
            }
        
        # Get historical data
        history = self.history[project_name]
        
        # Calculate velocity (tasks completed per day)
        velocity = self._calculate_velocity(history)
        
        # Calculate burn-down rate
        burn_down_rate = self._calculate_burn_down_rate(history)
        
        # Calculate blocking trend
        blocking_trend = self._calculate_blocking_trend(history)
        
        # Calculate estimated completion
        estimated_completion = self._estimate_completion(history, velocity, burn_down_rate)
        
        # Determine overall trend
        overall_trend = self._determine_overall_trend(velocity, burn_down_rate, blocking_trend)
        
        return {
            "project_name": project_name,
            "status": "analyzed",
            "velocity": velocity,
            "burn_down_rate": burn_down_rate,
            "blocking_trend": blocking_trend,
            "estimated_completion": estimated_completion,
            "overall_trend": overall_trend,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_velocity(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate project velocity from history.
        
        Args:
            history: List of historical metrics
            
        Returns:
            Velocity metrics
        """
        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x["timestamp"])
        
        # Calculate tasks completed between each point
        velocities = []
        for i in range(1, len(sorted_history)):
            prev = sorted_history[i-1]
            curr = sorted_history[i]
            
            # Calculate days between measurements
            days_diff = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 86400
            if days_diff < 0.1:  # Avoid division by very small numbers
                continue
            
            # Calculate tasks completed in this period
            completed_diff = curr["completed_tasks"] - prev["completed_tasks"]
            
            # Calculate velocity (tasks per day)
            if completed_diff >= 0:  # Ignore negative differences (data errors)
                velocity = completed_diff / days_diff
                velocities.append(velocity)
        
        # Calculate statistics
        if velocities:
            current = velocities[-1] if velocities else 0
            average = sum(velocities) / len(velocities)
            
            # Calculate trend
            trend = 0
            if len(velocities) >= 3:
                recent = velocities[-3:]
                recent_avg = sum(recent) / len(recent)
                trend = recent_avg - average
            
            return {
                "current": current,
                "average": average,
                "trend": trend,
                "trend_label": "improving" if trend > 0 else "declining" if trend < 0 else "stable",
                "raw": velocities
            }
        else:
            return {
                "current": 0,
                "average": 0,
                "trend": 0,
                "trend_label": "unknown",
                "raw": []
            }
    
    def _calculate_burn_down_rate(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate project burn-down rate from history.
        
        Args:
            history: List of historical metrics
            
        Returns:
            Burn-down metrics
        """
        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x["timestamp"])
        
        # Calculate remaining work at each point
        burn_down = []
        for i in range(1, len(sorted_history)):
            prev = sorted_history[i-1]
            curr = sorted_history[i]
            
            # Calculate days between measurements
            days_diff = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 86400
            if days_diff < 0.1:  # Avoid division by very small numbers
                continue
            
            # Calculate remaining work (100% - completion%)
            prev_remaining = 100 - prev["completion_percentage"]
            curr_remaining = 100 - curr["completion_percentage"]
            
            # Calculate burn-down rate (percentage points per day)
            if prev_remaining >= curr_remaining:  # Ignore increases in remaining work
                rate = (prev_remaining - curr_remaining) / days_diff
                burn_down.append(rate)
        
        # Calculate statistics
        if burn_down:
            current = burn_down[-1] if burn_down else 0
            average = sum(burn_down) / len(burn_down)
            
            # Calculate trend
            trend = 0
            if len(burn_down) >= 3:
                recent = burn_down[-3:]
                recent_avg = sum(recent) / len(recent)
                trend = recent_avg - average
            
            return {
                "current": current,
                "average": average,
                "trend": trend,
                "trend_label": "improving" if trend > 0 else "declining" if trend < 0 else "stable",
                "raw": burn_down
            }
        else:
            return {
                "current": 0,
                "average": 0,
                "trend": 0,
                "trend_label": "unknown",
                "raw": []
            }
    
    def _calculate_blocking_trend(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate trend in blocked tasks from history.
        
        Args:
            history: List of historical metrics
            
        Returns:
            Blocking trend metrics
        """
        # Sort by timestamp
        sorted_history = sorted(history, key=lambda x: x["timestamp"])
        
        # Calculate blocked percentage at each point
        blocked_percentages = []
        for point in sorted_history:
            if point["active_tasks"] > 0:
                blocked_pct = (point["blocked_tasks"] / point["active_tasks"]) * 100
                blocked_percentages.append(blocked_pct)
            else:
                blocked_percentages.append(0)
        
        # Calculate statistics
        if blocked_percentages:
            current = blocked_percentages[-1]
            
            # Calculate trend
            trend = 0
            if len(blocked_percentages) >= 3:
                early = sum(blocked_percentages[:3]) / 3
                late = sum(blocked_percentages[-3:]) / 3
                trend = late - early
            
            return {
                "current": current,
                "trend": trend,
                "trend_label": "worsening" if trend > 0 else "improving" if trend < 0 else "stable",
                "raw": blocked_percentages
            }
        else:
            return {
                "current": 0,
                "trend": 0,
                "trend_label": "unknown",
                "raw": []
            }
    
    def _estimate_completion(self, history: List[Dict[str, Any]], velocity: Dict[str, Any], burn_down: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate project completion date based on current trends.
        
        Args:
            history: List of historical metrics
            velocity: Velocity metrics
            burn_down: Burn-down metrics
            
        Returns:
            Completion estimate metrics
        """
        # Get latest metrics
        latest = history[-1]
        remaining_percentage = 100 - latest["completion_percentage"]
        
        # Estimate based on burn-down rate
        burn_down_estimate = None
        if burn_down["current"] > 0:
            days_to_completion = remaining_percentage / burn_down["current"]
            burn_down_estimate = latest["timestamp"] + timedelta(days=days_to_completion)
        
        # Estimate based on velocity
        velocity_estimate = None
        if velocity["current"] > 0:
            remaining_tasks = latest["total_tasks"] - latest["completed_tasks"]
            days_to_completion = remaining_tasks / velocity["current"]
            velocity_estimate = latest["timestamp"] + timedelta(days=days_to_completion)
        
        # Combine estimates (simple average if both available)
        if burn_down_estimate and velocity_estimate:
            avg_days = ((burn_down_estimate - latest["timestamp"]).days + 
                        (velocity_estimate - latest["timestamp"]).days) / 2
            combined_estimate = latest["timestamp"] + timedelta(days=avg_days)
        else:
            combined_estimate = burn_down_estimate or velocity_estimate
        
        return {
            "burn_down_estimate": burn_down_estimate.isoformat() if burn_down_estimate else None,
            "velocity_estimate": velocity_estimate.isoformat() if velocity_estimate else None,
            "combined_estimate": combined_estimate.isoformat() if combined_estimate else None,
            "confidence": "high" if burn_down["trend"] >= 0 and velocity["trend"] >= 0 else
                         "medium" if burn_down["current"] > 0 or velocity["current"] > 0 else
                         "low"
        }
    
    def _determine_overall_trend(self, velocity: Dict[str, Any], burn_down: Dict[str, Any], blocking: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine overall project performance trend.
        
        Args:
            velocity: Velocity metrics
            burn_down: Burn-down metrics
            blocking: Blocking trend metrics
            
        Returns:
            Overall trend assessment
        """
        # Calculate a combined trend score
        trend_score = 0
        
        # Velocity trend contributes positively
        trend_score += velocity["trend"] * 5  # Scale for comparison
        
        # Burn-down trend contributes positively
        trend_score += burn_down["trend"] * 5  # Scale for comparison
        
        # Blocking trend contributes negatively
        trend_score -= blocking["trend"] * 0.2  # Scale for comparison
        
        # Determine trend label
        if trend_score > 0.5:
            trend_label = "improving"
        elif trend_score < -0.5:
            trend_label = "declining"
        else:
            trend_label = "stable"
        
        # Determine overall status
        if velocity["current"] > 0 and burn_down["current"] > 0 and blocking["current"] < 20:
            status = "healthy"
        elif velocity["current"] == 0 or burn_down["current"] == 0 or blocking["current"] > 50:
            status = "at_risk"
        else:
            status = "needs_attention"
        
        return {
            "trend_score": trend_score,
            "trend_label": trend_label,
            "status": status,
            "contributing_factors": {
                "velocity": velocity["trend_label"],
                "burn_down": burn_down["trend_label"],
                "blocking": blocking["trend_label"]
            }
        }