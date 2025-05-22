"""
Dashboard manager for the Project Intelligence System.

This module provides the DashboardManager class for creating and updating
the project intelligence dashboard.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from ..models.project import Project

logger = logging.getLogger(__name__)


class DashboardManager:
    """
    Manages the project intelligence dashboard.
    
    This class is responsible for creating and updating the dashboard with
    current project information.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the dashboard manager.
        
        Args:
            config: Configuration dictionary with the following keys:
                - dashboard_type: Type of dashboard to use (default: "web")
                - dashboard_path: Path to save dashboard files (for file-based dashboards)
                - dashboard_url: URL of dashboard API (for API-based dashboards)
                - refresh_interval: How often to refresh the dashboard in seconds (default: 300)
                - theme: Dashboard theme (default: "light")
        """
        self.config = config or {}
        self.dashboard_type = self.config.get("dashboard_type", "web")
        self.dashboard_path = self.config.get("dashboard_path", "dashboard")
        self.dashboard_url = self.config.get("dashboard_url")
        self.refresh_interval = self.config.get("refresh_interval", 300)
        self.theme = self.config.get("theme", "light")
        self.last_update = None
        
        # Initialize metrics calculator
        from project_intelligence.intelligence.metrics_calculator import MetricsCalculator
        self.metrics_calculator = MetricsCalculator()
        
    async def initialize(self) -> None:
        """Initialize the dashboard."""
        if self.dashboard_type == "web":
            await self._initialize_web_dashboard()
        elif self.dashboard_type == "file":
            await self._initialize_file_dashboard()
        elif self.dashboard_type == "api":
            await self._initialize_api_dashboard()
        else:
            logger.warning(f"Unknown dashboard type: {self.dashboard_type}")
        
        logger.info(f"Dashboard manager initialized with type: {self.dashboard_type}")
    
    async def _initialize_web_dashboard(self) -> None:
        """Initialize web-based dashboard."""
        try:
            # Ensure dashboard directory exists
            os.makedirs(self.dashboard_path, exist_ok=True)
            
            # Create initial HTML, CSS, and JS files
            html_path = os.path.join(self.dashboard_path, "index.html")
            css_path = os.path.join(self.dashboard_path, "styles.css")
            js_path = os.path.join(self.dashboard_path, "dashboard.js")
            
            # Create basic HTML template if it doesn't exist
            if not os.path.exists(html_path):
                with open(html_path, "w") as f:
                    f.write(self._get_html_template())
            
            # Create basic CSS if it doesn't exist
            if not os.path.exists(css_path):
                with open(css_path, "w") as f:
                    f.write(self._get_css_template())
            
            # Create basic JS if it doesn't exist
            if not os.path.exists(js_path):
                with open(js_path, "w") as f:
                    f.write(self._get_js_template())
            
            logger.info("Web dashboard initialized")
        except Exception as e:
            logger.error(f"Error initializing web dashboard: {str(e)}")
    
    async def _initialize_file_dashboard(self) -> None:
        """Initialize file-based dashboard."""
        try:
            # Ensure dashboard directory exists
            os.makedirs(self.dashboard_path, exist_ok=True)
            logger.info("File dashboard initialized")
        except Exception as e:
            logger.error(f"Error initializing file dashboard: {str(e)}")
    
    async def _initialize_api_dashboard(self) -> None:
        """Initialize API-based dashboard."""
        if not self.dashboard_url:
            logger.error("Missing dashboard_url for API dashboard")
            return
        
        try:
            # Test API connection
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.dashboard_url}/status") as response:
                    if response.status == 200:
                        logger.info("API dashboard initialized successfully")
                    else:
                        logger.warning(f"API dashboard returned status {response.status}")
            
            # Initialize API manager if using local API
            if self.dashboard_url.startswith("http://localhost") or self.dashboard_url.startswith("http://127.0.0.1"):
                from project_intelligence.api.api_manager import APIManager
                self.api_manager = APIManager(
                    host=self.dashboard_url.split("//")[1].split(":")[0],
                    port=int(self.dashboard_url.split(":")[-1].split("/")[0]),
                    enable_cors=True
                )
                logger.info("Local API manager initialized")
        except Exception as e:
            logger.error(f"Error initializing API dashboard: {str(e)}")
    
    async def update(self, projects: Dict[str, Project]) -> None:
        """
        Update the dashboard with current project information.
        
        Args:
            projects: Dictionary of project objects
        """
        try:
            if self.dashboard_type == "web":
                await self._update_web_dashboard(projects)
            elif self.dashboard_type == "file":
                await self._update_file_dashboard(projects)
            elif self.dashboard_type == "api":
                await self._update_api_dashboard(projects)
            else:
                logger.warning(f"Unknown dashboard type: {self.dashboard_type}")
            
            self.last_update = datetime.now()
            logger.info("Dashboard updated successfully")
        except Exception as e:
            logger.error(f"Error updating dashboard: {str(e)}")
    
    async def _update_web_dashboard(self, projects: Dict[str, Project]) -> None:
        """
        Update web-based dashboard.
        
        Args:
            projects: Dictionary of project objects
        """
        try:
            # Convert projects to JSON
            import json
            
            # Create data directory if it doesn't exist
            data_dir = os.path.join(self.dashboard_path, "data")
            os.makedirs(data_dir, exist_ok=True)
            
            # Write projects data
            projects_data = {name: project.to_dict() for name, project in projects.items()}
            with open(os.path.join(data_dir, "projects.json"), "w") as f:
                json.dump(projects_data, f, indent=2)
            
            # Write summary data
            summary_data = self._generate_summary_data(projects)
            with open(os.path.join(data_dir, "summary.json"), "w") as f:
                json.dump(summary_data, f, indent=2)
            
            # Write last update time
            with open(os.path.join(data_dir, "last_update.json"), "w") as f:
                json.dump({"last_update": datetime.now().isoformat()}, f, indent=2)
            
            logger.info("Web dashboard data updated")
        except Exception as e:
            logger.error(f"Error updating web dashboard: {str(e)}")
    
    async def _update_file_dashboard(self, projects: Dict[str, Project]) -> None:
        """
        Update file-based dashboard.
        
        Args:
            projects: Dictionary of project objects
        """
        try:
            # Generate dashboard report
            report = self._generate_text_report(projects)
            
            # Write report to file
            report_path = os.path.join(self.dashboard_path, "dashboard_report.txt")
            with open(report_path, "w") as f:
                f.write(report)
            
            # Generate CSV exports
            self._generate_csv_exports(projects)
            
            logger.info("File dashboard updated")
        except Exception as e:
            logger.error(f"Error updating file dashboard: {str(e)}")
    
    async def _update_api_dashboard(self, projects: Dict[str, Project]) -> None:
        """
        Update API-based dashboard.
        
        Args:
            projects: Dictionary of project objects
        """
        if not self.dashboard_url:
            logger.error("Missing dashboard_url for API dashboard")
            return
        
        try:
            # Generate intelligent data
            alerts = []
            recommendations = []
            assignments = []
            metrics = self.metrics_calculator.calculate_all_metrics(projects)
            
            # Generate alerts using AlertGenerator
            if hasattr(self, 'alert_generator'):
                alerts = await self.alert_generator.generate_alerts(projects)
            else:
                # Initialize alert generator if needed
                from project_intelligence.intelligence.alerts import AlertGenerator
                self.alert_generator = AlertGenerator()
                alerts = await self.alert_generator.generate_alerts(projects)
            
            # Generate rescheduling recommendations
            if hasattr(self, 'rescheduling_recommender'):
                recommendations = await self.rescheduling_recommender.generate_recommendations(projects)
            else:
                # Initialize rescheduling recommender if needed
                from project_intelligence.intelligence.alerts import ReschedulingRecommender
                self.rescheduling_recommender = ReschedulingRecommender()
                recommendations = await self.rescheduling_recommender.generate_recommendations(projects)
            
            # If using local API manager, update directly
            if hasattr(self, 'api_manager'):
                await self.api_manager.update(
                    projects=projects,
                    alerts=alerts,
                    recommendations=recommendations,
                    assignments=assignments,
                    metrics=metrics
                )
                logger.info("Local API dashboard updated successfully")
                return
                
            # Otherwise, use HTTP API
            import json
            import aiohttp
            
            projects_data = {name: project.to_dict() for name, project in projects.items()}
            
            # Send data to API
            async with aiohttp.ClientSession() as session:
                # Update projects
                async with session.post(
                    f"{self.dashboard_url}/api/projects/update",
                    json={"projects": projects_data}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"API projects update returned status {response.status}")
                
                # Update alerts
                if alerts:
                    async with session.post(
                        f"{self.dashboard_url}/api/alerts/update",
                        json={"alerts": alerts}
                    ) as response:
                        if response.status != 200:
                            logger.warning(f"API alerts update returned status {response.status}")
                
                # Update recommendations
                if recommendations:
                    async with session.post(
                        f"{self.dashboard_url}/api/recommendations/update",
                        json={"recommendations": recommendations}
                    ) as response:
                        if response.status != 200:
                            logger.warning(f"API recommendations update returned status {response.status}")
                
                # Update metrics
                async with session.post(
                    f"{self.dashboard_url}/api/metrics/update",
                    json={"metrics": metrics}
                ) as response:
                    if response.status != 200:
                        logger.warning(f"API metrics update returned status {response.status}")
                
                logger.info("API dashboard updated successfully")
        except Exception as e:
            logger.error(f"Error updating API dashboard: {str(e)}")
    
    def _generate_summary_data(self, projects: Dict[str, Project]) -> Dict[str, Any]:
        """
        Generate summary data for dashboard.
        
        Args:
            projects: Dictionary of project objects
            
        Returns:
            Summary data dictionary
        """
        # Count projects by status
        status_counts = {}
        for project in projects.values():
            status = project.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count tasks by status
        task_status_counts = {}
        for project in projects.values():
            for task in project.tasks.values():
                status = task.status
                task_status_counts[status] = task_status_counts.get(status, 0) + 1
        
        # Get overdue tasks
        overdue_tasks = []
        for project in projects.values():
            for task in project.get_overdue_tasks():
                overdue_tasks.append({
                    "project_name": project.name,
                    "task_id": task.id,
                    "task_name": task.name,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "owner": task.owner
                })
        
        # Get recent updates
        recent_updates = []
        for project in projects.values():
            for update in sorted(project.updates, key=lambda u: u.timestamp, reverse=True)[:5]:
                recent_updates.append({
                    "project_name": project.name,
                    "timestamp": update.timestamp.isoformat(),
                    "content": update.content,
                    "author": update.author,
                    "update_type": update.update_type
                })
        
        # Get resource allocation
        resource_allocation = {}
        for project in projects.values():
            for resource_type, resource in project.resources.items():
                if resource_type not in resource_allocation:
                    resource_allocation[resource_type] = []
                
                resource_allocation[resource_type].append({
                    "project_name": project.name,
                    "status": resource.status,
                    "quantity": resource.quantity,
                    "last_updated": resource.last_updated.isoformat() if resource.last_updated else None
                })
        
        return {
            "project_count": len(projects),
            "project_status_counts": status_counts,
            "task_status_counts": task_status_counts,
            "overdue_tasks": overdue_tasks,
            "recent_updates": recent_updates,
            "resource_allocation": resource_allocation,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_text_report(self, projects: Dict[str, Project]) -> str:
        """
        Generate a text report of projects.
        
        Args:
            projects: Dictionary of project objects
            
        Returns:
            Text report
        """
        lines = [
            "PROJECT INTELLIGENCE DASHBOARD",
            "=" * 30,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Projects: {len(projects)}",
            "\n",
        ]
        
        # Add project summaries
        for name, project in sorted(projects.items()):
            completion = project.get_completion_percentage()
            lines.append(f"PROJECT: {name}")
            lines.append("-" * 20)
            lines.append(f"Status: {project.status}")
            lines.append(f"Completion: {completion:.1f}%")
            lines.append(f"Owner: {project.owner or 'Unassigned'}")
            
            # Add task summary
            total_tasks = len(project.tasks)
            if total_tasks > 0:
                lines.append(f"\nTasks: {total_tasks}")
                
                # Group tasks by status
                tasks_by_status = {}
                for task in project.tasks.values():
                    if task.status not in tasks_by_status:
                        tasks_by_status[task.status] = []
                    tasks_by_status[task.status].append(task)
                
                for status, tasks in tasks_by_status.items():
                    lines.append(f"  {status}: {len(tasks)}")
                
                # List overdue tasks
                overdue = project.get_overdue_tasks()
                if overdue:
                    lines.append("\nOverdue Tasks:")
                    for task in overdue:
                        due_date = task.due_date.strftime("%Y-%m-%d") if task.due_date else "Unknown"
                        lines.append(f"  - {task.name} (Due: {due_date})")
            
            # Add recent updates
            if project.updates:
                recent = sorted(project.updates, key=lambda u: u.timestamp, reverse=True)[:3]
                if recent:
                    lines.append("\nRecent Updates:")
                    for update in recent:
                        date = update.timestamp.strftime("%Y-%m-%d")
                        lines.append(f"  - {date} by {update.author}: {update.content[:50]}...")
            
            # Add resource information
            if project.resources:
                lines.append("\nResources:")
                for resource_type, resource in project.resources.items():
                    quantity = resource.quantity if resource.quantity is not None else "N/A"
                    lines.append(f"  - {resource_type}: {quantity} ({resource.status})")
            
            lines.append("\n")
        
        return "\n".join(lines)
    
    def _generate_csv_exports(self, projects: Dict[str, Project]) -> None:
        """
        Generate CSV exports of project data.
        
        Args:
            projects: Dictionary of project objects
        """
        import csv
        
        # Create exports directory
        exports_dir = os.path.join(self.dashboard_path, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        # Export projects
        with open(os.path.join(exports_dir, "projects.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Project Name", "Status", "Completion %", "Owner", 
                "Start Date", "End Date", "Task Count"
            ])
            
            for name, project in projects.items():
                writer.writerow([
                    name,
                    project.status,
                    f"{project.get_completion_percentage():.1f}",
                    project.owner or "Unassigned",
                    project.start_date.strftime("%Y-%m-%d") if project.start_date else "N/A",
                    project.end_date.strftime("%Y-%m-%d") if project.end_date else "N/A",
                    len(project.tasks)
                ])
        
        # Export tasks
        with open(os.path.join(exports_dir, "tasks.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Project Name", "Task ID", "Task Name", "Status", 
                "Owner", "Due Date", "Priority", "Completion %"
            ])
            
            for name, project in projects.items():
                for task_id, task in project.tasks.items():
                    writer.writerow([
                        name,
                        task_id,
                        task.name,
                        task.status,
                        task.owner or "Unassigned",
                        task.due_date.strftime("%Y-%m-%d") if task.due_date else "N/A",
                        task.priority,
                        f"{task.completion_percentage or 0:.1f}"
                    ])
        
        # Export updates
        with open(os.path.join(exports_dir, "updates.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Project Name", "Timestamp", "Author", "Update Type", "Content"
            ])
            
            for name, project in projects.items():
                for update in project.updates:
                    writer.writerow([
                        name,
                        update.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        update.author,
                        update.update_type,
                        update.content
                    ])
    
    def _get_html_template(self) -> str:
        """
        Get HTML template for web dashboard.
        
        Returns:
            HTML template string
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Intelligence Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Project Intelligence Dashboard</h1>
        <div id="last-update">Last updated: <span id="update-time">Loading...</span></div>
    </header>
    
    <div class="dashboard-container">
        <div class="summary-section">
            <h2>Summary</h2>
            <div class="summary-cards">
                <div class="card">
                    <h3>Projects</h3>
                    <div class="card-content" id="project-summary"></div>
                </div>
                <div class="card">
                    <h3>Tasks</h3>
                    <div class="card-content" id="task-summary"></div>
                </div>
                <div class="card">
                    <h3>Resources</h3>
                    <div class="card-content" id="resource-summary"></div>
                </div>
            </div>
        </div>
        
        <div class="alerts-section">
            <h2>Alerts</h2>
            <div id="alerts-container"></div>
        </div>
        
        <div class="projects-section">
            <h2>Projects</h2>
            <div id="projects-container"></div>
        </div>
    </div>
    
    <script src="dashboard.js"></script>
</body>
</html>"""
    
    def _get_css_template(self) -> str:
        """
        Get CSS template for web dashboard.
        
        Returns:
            CSS template string
        """
        return """/* Dashboard Styles */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f7fa;
}

header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

h1, h2, h3 {
    margin-bottom: 0.5rem;
}

.dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.card {
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1rem;
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
}

.card h3 {
    color: #2c3e50;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.alerts-section {
    margin-bottom: 2rem;
}

#alerts-container {
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1rem;
}

.alert {
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    border-radius: 4px;
}

.alert.overdue {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
}

.alert.warning {
    background-color: #fff8e1;
    border-left: 4px solid #ffc107;
}

.alert.info {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
}

.projects-section {
    margin-bottom: 2rem;
}

#projects-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
}

.project-card {
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1rem;
}

.project-card h3 {
    color: #2c3e50;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.project-stats {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.project-progress {
    height: 8px;
    background-color: #e0e0e0;
    border-radius: 4px;
    margin-bottom: 1rem;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background-color: #4caf50;
}

.task-list {
    margin-top: 1rem;
}

.task-item {
    padding: 0.5rem;
    border-bottom: 1px solid #eee;
}

.task-item:last-child {
    border-bottom: none;
}

@media (max-width: 768px) {
    .summary-cards, #projects-container {
        grid-template-columns: 1fr;
    }
}"""
    
    def _get_js_template(self) -> str:
        """
        Get JavaScript template for web dashboard.
        
        Returns:
            JavaScript template string
        """
        return """// Dashboard JavaScript

// Fetch data from JSON files
async function fetchData() {
    try {
        const [projectsResponse, summaryResponse, lastUpdateResponse] = await Promise.all([
            fetch('data/projects.json'),
            fetch('data/summary.json'),
            fetch('data/last_update.json')
        ]);
        
        if (!projectsResponse.ok || !summaryResponse.ok || !lastUpdateResponse.ok) {
            throw new Error('Failed to fetch data');
        }
        
        const projects = await projectsResponse.json();
        const summary = await summaryResponse.json();
        const lastUpdate = await lastUpdateResponse.json();
        
        return { projects, summary, lastUpdate };
    } catch (error) {
        console.error('Error fetching data:', error);
        document.body.innerHTML = `<div class="error">Error loading dashboard data: ${error.message}</div>`;
        return null;
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Render the dashboard
async function renderDashboard() {
    const data = await fetchData();
    if (!data) return;
    
    const { projects, summary, lastUpdate } = data;
    
    // Update last update time
    document.getElementById('update-time').textContent = formatDate(lastUpdate.last_update);
    
    // Render summary
    renderProjectSummary(summary);
    renderTaskSummary(summary);
    renderResourceSummary(summary);
    
    // Render alerts
    renderAlerts(summary);
    
    // Render projects
    renderProjects(projects);
    
    // Set up auto-refresh
    setTimeout(renderDashboard, 300000); // Refresh every 5 minutes
}

// Render project summary
function renderProjectSummary(summary) {
    const container = document.getElementById('project-summary');
    
    const projectCount = summary.project_count;
    const statusCounts = summary.project_status_counts;
    
    let html = `<p>Total: ${projectCount}</p><ul>`;
    
    for (const status in statusCounts) {
        html += `<li>${status}: ${statusCounts[status]}</li>`;
    }
    
    html += '</ul>';
    container.innerHTML = html;
}

// Render task summary
function renderTaskSummary(summary) {
    const container = document.getElementById('task-summary');
    
    const taskCounts = summary.task_status_counts;
    let totalTasks = 0;
    
    for (const status in taskCounts) {
        totalTasks += taskCounts[status];
    }
    
    let html = `<p>Total: ${totalTasks}</p><ul>`;
    
    for (const status in taskCounts) {
        html += `<li>${status}: ${taskCounts[status]}</li>`;
    }
    
    html += '</ul>';
    container.innerHTML = html;
}

// Render resource summary
function renderResourceSummary(summary) {
    const container = document.getElementById('resource-summary');
    
    const resources = summary.resource_allocation;
    
    let html = '<ul>';
    
    for (const resourceType in resources) {
        let totalQuantity = 0;
        
        for (const allocation of resources[resourceType]) {
            if (allocation.quantity) {
                totalQuantity += allocation.quantity;
            }
        }
        
        html += `<li>${resourceType}: ${totalQuantity}</li>`;
    }
    
    html += '</ul>';
    container.innerHTML = html;
}

// Render alerts
function renderAlerts(summary) {
    const container = document.getElementById('alerts-container');
    
    const overdueTasks = summary.overdue_tasks;
    
    if (overdueTasks.length === 0) {
        container.innerHTML = '<p>No alerts at this time.</p>';
        return;
    }
    
    let html = '';
    
    for (const task of overdueTasks) {
        html += `
            <div class="alert overdue">
                <strong>Overdue Task:</strong> ${task.task_name} in project ${task.project_name}
                <div>Due: ${formatDate(task.due_date)}</div>
                <div>Owner: ${task.owner || 'Unassigned'}</div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Render projects
function renderProjects(projects) {
    const container = document.getElementById('projects-container');
    
    let html = '';
    
    for (const projectName in projects) {
        const project = projects[projectName];
        
        const completionPercentage = project.completion_percentage || 0;
        
        html += `
            <div class="project-card">
                <h3>${projectName}</h3>
                <div class="project-stats">
                    <div>Status: ${project.status}</div>
                    <div>Completion: ${completionPercentage.toFixed(1)}%</div>
                </div>
                <div class="project-progress">
                    <div class="progress-bar" style="width: ${completionPercentage}%"></div>
                </div>
                <div>Owner: ${project.owner || 'Unassigned'}</div>
                <div>Tasks: ${Object.keys(project.tasks).length}</div>
                
                <div class="task-list">
                    <h4>Recent Tasks</h4>
                    ${renderProjectTasks(project)}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Render project tasks
function renderProjectTasks(project) {
    const taskArray = Object.values(project.tasks);
    
    if (taskArray.length === 0) {
        return '<p>No tasks</p>';
    }
    
    // Sort tasks by due date (most urgent first)
    taskArray.sort((a, b) => {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date) - new Date(b.due_date);
    });
    
    let html = '';
    
    // Show up to 5 tasks
    const tasksToShow = taskArray.slice(0, 5);
    
    for (const task of tasksToShow) {
        html += `
            <div class="task-item">
                <div>${task.name}</div>
                <div>Status: ${task.status}</div>
                <div>Due: ${formatDate(task.due_date)}</div>
            </div>
        `;
    }
    
    return html;
}

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', renderDashboard);"""