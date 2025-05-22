"""
Metrics calculator for Project Intelligence.

This module provides functions for calculating project metrics including
burndown charts and velocity trends.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from project_intelligence.models.project import Project
from project_intelligence.models.task import Task

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """
    Calculates metrics for projects including burndown and velocity.
    """
    
    def __init__(self):
        """Initialize the metrics calculator."""
        self.default_sprint_length = 14  # Default sprint length in days
    
    def calculate_all_metrics(self, projects: Dict[str, Project]) -> Dict[str, Any]:
        """
        Calculate metrics for all projects.
        
        Args:
            projects: Dictionary of project objects
            
        Returns:
            Dictionary containing all metrics
        """
        metrics = {
            "current_date": datetime.now().isoformat(),
            "projects": {}
        }
        
        for project_name, project in projects.items():
            project_metrics = self.calculate_project_metrics(project)
            metrics["projects"][project_name] = project_metrics
        
        # Add summary metrics across all projects
        metrics.update(self.calculate_summary_metrics(projects, metrics["projects"]))
        
        return metrics
    
    def calculate_project_metrics(self, project: Project) -> Dict[str, Any]:
        """
        Calculate metrics for a single project.
        
        Args:
            project: Project object
            
        Returns:
            Dictionary containing project metrics
        """
        metrics = {}
        
        # Basic project metrics
        metrics["completion_percentage"] = project.get_completion_percentage()
        metrics["task_count"] = len(project.tasks)
        
        # Task status breakdown
        status_counts = self._count_tasks_by_status(project.tasks)
        metrics["task_status"] = status_counts
        
        # Calculate velocity metrics
        metrics["velocity"] = self.calculate_velocity_metrics(project)
        
        # Calculate burndown metrics
        metrics["burndown"] = self.calculate_burndown_metrics(project)
        
        # Calculate overdue and blocked tasks
        metrics["overdue_tasks"] = self._count_overdue_tasks(project.tasks)
        metrics["blocked_tasks"] = status_counts.get("blocked", 0)
        
        # Calculate days ahead/behind schedule
        metrics["days_behind"] = self._calculate_days_behind(project, metrics["burndown"])
        
        return metrics
    
    def calculate_velocity_metrics(self, project: Project) -> Dict[str, Any]:
        """
        Calculate velocity metrics for a project.
        
        Args:
            project: Project object
            
        Returns:
            Dictionary containing velocity metrics
        """
        velocity_metrics = {
            "average": 0.0,
            "trend": [],
            "completed_points": [],
            "prediction_accuracy": None
        }
        
        # Get project updates and extract velocity data
        updates = sorted(project.updates, key=lambda u: u.timestamp)
        
        if not updates:
            return self._generate_placeholder_velocity(project)
        
        # Extract velocity data from updates
        sprint_points = []
        
        for update in updates:
            if "completed_points" in update.metadata:
                sprint_points.append({
                    "date": update.timestamp.isoformat()[:10],
                    "value": update.metadata["completed_points"]
                })
        
        if not sprint_points:
            return self._generate_placeholder_velocity(project)
        
        # Calculate average velocity
        total_points = sum(point["value"] for point in sprint_points)
        average_velocity = total_points / len(sprint_points)
        
        # Calculate velocity trend (rolling average)
        window_size = min(3, len(sprint_points))
        trend = []
        
        for i in range(len(sprint_points)):
            if i < window_size - 1:
                # Not enough data for window yet
                continue
                
            window = sprint_points[i - window_size + 1 : i + 1]
            window_avg = sum(point["value"] for point in window) / window_size
            
            trend.append({
                "date": sprint_points[i]["date"],
                "value": window_avg
            })
        
        # Calculate prediction accuracy if available
        prediction_accuracy = None
        predicted_points = [u.metadata.get("predicted_points") for u in updates if "predicted_points" in u.metadata]
        actual_points = [u.metadata.get("completed_points") for u in updates if "completed_points" in u.metadata]
        
        if predicted_points and actual_points and len(predicted_points) == len(actual_points):
            # Calculate how close predictions were to actuals
            accuracy_sum = 0
            count = 0
            
            for predicted, actual in zip(predicted_points, actual_points):
                if predicted > 0:  # Avoid division by zero
                    accuracy = min(actual / predicted, predicted / actual)
                    accuracy_sum += accuracy
                    count += 1
            
            if count > 0:
                prediction_accuracy = accuracy_sum / count
        
        velocity_metrics["average"] = average_velocity
        velocity_metrics["trend"] = trend
        velocity_metrics["completed_points"] = sprint_points
        velocity_metrics["prediction_accuracy"] = prediction_accuracy
        
        return velocity_metrics
    
    def calculate_burndown_metrics(self, project: Project) -> Dict[str, Any]:
        """
        Calculate burndown metrics for a project.
        
        Args:
            project: Project object
            
        Returns:
            Dictionary containing burndown metrics
        """
        burndown_metrics = {
            "remaining_work": [],
            "ideal_burndown": [],
            "completion_date_projection": None,
            "is_on_track": False
        }
        
        # Get start and end dates
        start_date = project.start_date or datetime.now() - timedelta(days=30)
        end_date = project.end_date
        
        if not end_date:
            if project.updates:
                # Estimate end date based on velocity and remaining work
                velocity_data = self.calculate_velocity_metrics(project)
                avg_velocity = velocity_data["average"]
                
                if avg_velocity > 0:
                    remaining_points = self._calculate_remaining_points(project)
                    days_needed = (remaining_points / avg_velocity) * self.default_sprint_length
                    end_date = datetime.now() + timedelta(days=days_needed)
                else:
                    # Default to 3 months from start if no velocity data
                    end_date = start_date + timedelta(days=90)
            else:
                # Default to 3 months from start if no updates
                end_date = start_date + timedelta(days=90)
        
        # Calculate total work points
        total_points = self._calculate_total_points(project)
        
        # Generate ideal burndown
        days_total = (end_date - start_date).days
        ideal_burndown = []
        
        for day in range(days_total + 1):
            date = (start_date + timedelta(days=day)).isoformat()[:10]
            ideal_value = total_points * (1 - day / days_total)
            ideal_burndown.append({"date": date, "value": ideal_value})
        
        # Generate actual burndown from updates
        updates = sorted(project.updates, key=lambda u: u.timestamp)
        remaining_work = []
        
        if updates:
            for update in updates:
                if "remaining_points" in update.metadata:
                    remaining_work.append({
                        "date": update.timestamp.isoformat()[:10],
                        "value": update.metadata["remaining_points"]
                    })
        
        # If no updates with remaining_points, calculate based on task completion
        if not remaining_work:
            remaining_work = self._calculate_remaining_work_from_tasks(project, start_date, days_total)
        
        # Determine if on track
        is_on_track = True
        completion_date_projection = end_date.isoformat()[:10]
        
        if remaining_work:
            latest_value = remaining_work[-1]["value"]
            
            # Find where we should be on the ideal burndown
            days_elapsed = (datetime.now() - start_date).days
            ideal_value_now = None
            
            if 0 <= days_elapsed < len(ideal_burndown):
                ideal_value_now = ideal_burndown[days_elapsed]["value"]
                
                # On track if within 10% of ideal or better
                is_on_track = latest_value <= ideal_value_now * 1.1
                
                # Project completion date based on current progress
                if latest_value > 0 and len(remaining_work) >= 2:
                    # Calculate velocity from actual burndown
                    first_point = remaining_work[0]
                    last_point = remaining_work[-1]
                    
                    first_date = datetime.fromisoformat(first_point["date"])
                    last_date = datetime.fromisoformat(last_point["date"])
                    
                    days_diff = max(1, (last_date - first_date).days)  # Avoid division by zero
                    points_per_day = (first_point["value"] - last_point["value"]) / days_diff
                    
                    if points_per_day > 0:
                        days_to_completion = latest_value / points_per_day
                        projected_date = datetime.now() + timedelta(days=days_to_completion)
                        completion_date_projection = projected_date.isoformat()[:10]
        
        burndown_metrics["remaining_work"] = remaining_work
        burndown_metrics["ideal_burndown"] = ideal_burndown
        burndown_metrics["completion_date_projection"] = completion_date_projection
        burndown_metrics["is_on_track"] = is_on_track
        
        return burndown_metrics
    
    def calculate_summary_metrics(self, projects: Dict[str, Project], project_metrics: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calculate summary metrics across all projects.
        
        Args:
            projects: Dictionary of project objects
            project_metrics: Dictionary of project metrics
            
        Returns:
            Dictionary containing summary metrics
        """
        summary = {
            "total_projects": len(projects),
            "projects_on_track": 0,
            "projects_at_risk": 0,
            "projects_behind": 0,
            "average_completion": 0.0,
            "average_velocity": 0.0
        }
        
        if not projects:
            return summary
        
        # Calculate summary metrics
        total_completion = 0.0
        total_velocity = 0.0
        
        for project_name, metrics in project_metrics.items():
            # Determine project status
            is_on_track = metrics.get("burndown", {}).get("is_on_track", True)
            days_behind = metrics.get("days_behind", 0)
            
            if is_on_track:
                summary["projects_on_track"] += 1
            elif days_behind <= 7:
                summary["projects_at_risk"] += 1
            else:
                summary["projects_behind"] += 1
            
            # Add to totals
            total_completion += metrics.get("completion_percentage", 0.0)
            total_velocity += metrics.get("velocity", {}).get("average", 0.0)
        
        # Calculate averages
        summary["average_completion"] = total_completion / len(projects)
        summary["average_velocity"] = total_velocity / len(projects)
        
        return summary
    
    def _count_tasks_by_status(self, tasks: Dict[str, Task]) -> Dict[str, int]:
        """
        Count tasks by status.
        
        Args:
            tasks: Dictionary of task objects
            
        Returns:
            Dictionary with counts by status
        """
        status_counts = {}
        
        for task in tasks.values():
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def _count_overdue_tasks(self, tasks: Dict[str, Task]) -> int:
        """
        Count overdue tasks.
        
        Args:
            tasks: Dictionary of task objects
            
        Returns:
            Number of overdue tasks
        """
        now = datetime.now()
        return sum(1 for task in tasks.values() 
                  if task.due_date and task.due_date < now and task.status != "completed")
    
    def _calculate_total_points(self, project: Project) -> float:
        """
        Calculate total story points for a project.
        
        Args:
            project: Project object
            
        Returns:
            Total story points
        """
        total = 0.0
        
        for task in project.tasks.values():
            points = getattr(task, "story_points", None)
            if points is not None:
                total += points
        
        # Default to task count if no story points
        if total == 0:
            total = len(project.tasks)
        
        return total
    
    def _calculate_remaining_points(self, project: Project) -> float:
        """
        Calculate remaining story points for a project.
        
        Args:
            project: Project object
            
        Returns:
            Remaining story points
        """
        remaining = 0.0
        
        for task in project.tasks.values():
            if task.status != "completed":
                points = getattr(task, "story_points", None)
                if points is not None:
                    remaining += points
                else:
                    # Default to 1 point per task if no story points
                    remaining += 1
        
        return remaining
    
    def _calculate_days_behind(self, project: Project, burndown_data: Dict[str, Any]) -> int:
        """
        Calculate days behind schedule.
        
        Args:
            project: Project object
            burndown_data: Burndown metrics
            
        Returns:
            Days behind schedule (negative if ahead)
        """
        if not burndown_data.get("remaining_work") or not burndown_data.get("ideal_burndown"):
            return 0
        
        remaining_work = burndown_data["remaining_work"]
        ideal_burndown = burndown_data["ideal_burndown"]
        
        if not remaining_work:
            return 0
        
        # Get latest actual remaining work
        latest_actual = remaining_work[-1]["value"]
        
        # Find where this value would be on the ideal burndown
        days_behind = 0
        now = datetime.now()
        
        for i, point in enumerate(ideal_burndown):
            if point["value"] <= latest_actual:
                ideal_date = datetime.fromisoformat(point["date"])
                days_behind = (now - ideal_date).days
                break
        
        return days_behind
    
    def _calculate_remaining_work_from_tasks(
        self, project: Project, start_date: datetime, days_total: int
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Calculate remaining work points based on task completion.
        
        Args:
            project: Project object
            start_date: Project start date
            days_total: Total project duration in days
            
        Returns:
            List of remaining work data points
        """
        remaining_work = []
        total_points = self._calculate_total_points(project)
        
        # Get completion percentage over time from updates
        updates = sorted(project.updates, key=lambda u: u.timestamp)
        
        if not updates:
            # Only include current status if no updates
            remaining = self._calculate_remaining_points(project)
            remaining_work.append({
                "date": datetime.now().isoformat()[:10],
                "value": remaining
            })
            return remaining_work
        
        # Generate remaining work points from updates
        for update in updates:
            if "completion_percentage" in update.metadata:
                completion_pct = update.metadata["completion_percentage"]
                remaining = total_points * (1 - completion_pct / 100)
                
                remaining_work.append({
                    "date": update.timestamp.isoformat()[:10],
                    "value": remaining
                })
        
        # Add current remaining work if not included in updates
        current_completion = project.get_completion_percentage()
        current_remaining = total_points * (1 - current_completion / 100)
        
        latest_date = updates[-1].timestamp.isoformat()[:10] if updates else None
        today = datetime.now().isoformat()[:10]
        
        if latest_date != today:
            remaining_work.append({
                "date": today,
                "value": current_remaining
            })
        
        return remaining_work
    
    def _generate_placeholder_velocity(self, project: Project) -> Dict[str, Any]:
        """
        Generate placeholder velocity data when no real data exists.
        
        Args:
            project: Project object
            
        Returns:
            Dictionary containing placeholder velocity metrics
        """
        # Create placeholder velocity data with realistic values
        velocity_metrics = {
            "average": 0.0,
            "trend": [],
            "completed_points": [],
            "prediction_accuracy": None
        }
        
        # Estimate a reasonable velocity based on project size
        task_count = len(project.tasks)
        estimated_velocity = max(5, min(task_count / 5, 15))  # Between 5-15 points per sprint
        
        # Generate some historical data
        sprint_count = 4
        today = datetime.now()
        sprint_points = []
        
        for i in range(sprint_count):
            # Generate sprint data with some variation
            sprint_date = (today - timedelta(days=(sprint_count - i) * self.default_sprint_length)).isoformat()[:10]
            points = estimated_velocity * (0.8 + 0.4 * (i / sprint_count))  # Increasing trend
            variation = (i % 3 - 1) * 2  # Small random variation
            
            sprint_points.append({
                "date": sprint_date,
                "value": max(0, points + variation)
            })
        
        # Calculate average velocity
        total_points = sum(point["value"] for point in sprint_points)
        average_velocity = total_points / len(sprint_points) if sprint_points else estimated_velocity
        
        # Calculate velocity trend (rolling average)
        window_size = min(3, len(sprint_points))
        trend = []
        
        for i in range(len(sprint_points)):
            if i < window_size - 1:
                # Not enough data for window yet
                continue
                
            window = sprint_points[i - window_size + 1 : i + 1]
            window_avg = sum(point["value"] for point in window) / window_size
            
            trend.append({
                "date": sprint_points[i]["date"],
                "value": window_avg
            })
        
        velocity_metrics["average"] = average_velocity
        velocity_metrics["trend"] = trend
        velocity_metrics["completed_points"] = sprint_points
        
        return velocity_metrics