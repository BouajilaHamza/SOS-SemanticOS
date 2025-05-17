"""
Workflow Engine component for Modular Command Processing.

This component orchestrates multi-step workflows involving multiple agents.
It manages workflow state and transitions between steps.
"""

from typing import Dict, List, Any, Optional, Callable, Union
import threading
import uuid
import time
import json
from enum import Enum
from pathlib import Path

from .message_bus import Message, MessageBus


class WorkflowStatus(Enum):
    """Enum for workflow status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Enum for workflow step status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep:
    """Represents a single step in a workflow."""
    
    def __init__(self, 
                step_id: str,
                agent_id: str,
                action: str,
                parameters: Dict[str, Any] = None,
                dependencies: List[str] = None):
        """
        Initialize a workflow step.
        
        Args:
            step_id: Unique identifier for the step
            agent_id: ID of the agent responsible for this step
            action: Action to perform
            parameters: Parameters for the action
            dependencies: IDs of steps that must complete before this one
        """
        self.step_id = step_id
        self.agent_id = agent_id
        self.action = action
        self.parameters = parameters or {}
        self.dependencies = dependencies or []
        self.status = StepStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return {
            'step_id': self.step_id,
            'agent_id': self.agent_id,
            'action': self.action,
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        """Create step from dictionary."""
        step = cls(
            step_id=data['step_id'],
            agent_id=data['agent_id'],
            action=data['action'],
            parameters=data['parameters'],
            dependencies=data['dependencies']
        )
        step.status = StepStatus(data['status'])
        step.result = data['result']
        step.error = data['error']
        step.start_time = data['start_time']
        step.end_time = data['end_time']
        return step


class Workflow:
    """Represents a complete workflow with multiple steps."""
    
    def __init__(self, workflow_id: str, name: str, description: str = ""):
        """
        Initialize a workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Name of the workflow
            description: Description of the workflow
        """
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps = {}
        self.status = WorkflowStatus.PENDING
        self.create_time = time.time()
        self.start_time = None
        self.end_time = None
        self.context = {}
    
    def add_step(self, step: WorkflowStep) -> None:
        """
        Add a step to the workflow.
        
        Args:
            step: Step to add
        """
        self.steps[step.step_id] = step
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """
        Get a step by ID.
        
        Args:
            step_id: ID of the step to get
            
        Returns:
            Step or None if not found
        """
        return self.steps.get(step_id)
    
    def get_next_steps(self) -> List[WorkflowStep]:
        """
        Get steps that are ready to run.
        
        Returns:
            List of steps ready to run
        """
        ready_steps = []
        
        for step in self.steps.values():
            if step.status != StepStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in step.dependencies:
                dep_step = self.steps.get(dep_id)
                if not dep_step or dep_step.status != StepStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready_steps.append(step)
        
        return ready_steps
    
    def update_step_status(self, step_id: str, status: StepStatus, 
                          result: Any = None, error: str = None) -> bool:
        """
        Update the status of a step.
        
        Args:
            step_id: ID of the step to update
            status: New status
            result: Step result (for completed steps)
            error: Error message (for failed steps)
            
        Returns:
            True if successful, False otherwise
        """
        step = self.steps.get(step_id)
        if not step:
            return False
        
        step.status = status
        
        if status == StepStatus.RUNNING:
            step.start_time = time.time()
        elif status in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED):
            step.end_time = time.time()
            
            if status == StepStatus.COMPLETED:
                step.result = result
            elif status == StepStatus.FAILED:
                step.error = error
        
        return True
    
    def update_workflow_status(self) -> None:
        """Update the workflow status based on step statuses."""
        # If workflow is already completed or cancelled, don't change status
        if self.status in (WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED):
            return
        
        # Check if any steps are running
        has_running = False
        has_pending = False
        has_failed = False
        
        for step in self.steps.values():
            if step.status == StepStatus.RUNNING:
                has_running = True
            elif step.status == StepStatus.PENDING:
                has_pending = True
            elif step.status == StepStatus.FAILED:
                has_failed = True
        
        # Update workflow status
        if has_running:
            self.status = WorkflowStatus.RUNNING
            if self.start_time is None:
                self.start_time = time.time()
        elif has_failed:
            self.status = WorkflowStatus.FAILED
            self.end_time = time.time()
        elif not has_pending:
            self.status = WorkflowStatus.COMPLETED
            self.end_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'steps': {step_id: step.to_dict() for step_id, step in self.steps.items()},
            'status': self.status.value,
            'create_time': self.create_time,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create workflow from dictionary."""
        workflow = cls(
            workflow_id=data['workflow_id'],
            name=data['name'],
            description=data['description']
        )
        workflow.status = WorkflowStatus(data['status'])
        workflow.create_time = data['create_time']
        workflow.start_time = data['start_time']
        workflow.end_time = data['end_time']
        workflow.context = data['context']
        
        # Add steps
        for step_data in data['steps'].values():
            workflow.add_step(WorkflowStep.from_dict(step_data))
        
        return workflow


class WorkflowEngine:
    """
    Orchestrates multi-step workflows involving multiple agents.
    
    This class is responsible for:
    1. Managing workflow state and transitions between steps
    2. Coordinating agent interactions for workflow execution
    3. Providing monitoring and control of workflow execution
    """
    
    def __init__(self, message_bus: MessageBus, storage_dir: str = None):
        """
        Initialize the WorkflowEngine.
        
        Args:
            message_bus: Message bus for agent communication
            storage_dir: Directory to store workflow data
        """
        self.message_bus = message_bus
        self.workflows = {}
        self.active_workflows = set()
        self.lock = threading.RLock()
        self.storage_dir = None
        
        if storage_dir:
            self.storage_dir = Path(storage_dir).expanduser().absolute()
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Subscribe to workflow messages
        self.message_bus.subscribe_to_topic('workflow', self._handle_workflow_message)
    
    def create_workflow(self, name: str, description: str = "") -> str:
        """
        Create a new workflow.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
            
        Returns:
            Workflow ID
        """
        with self.lock:
            workflow_id = f"workflow_{uuid.uuid4().hex}"
            workflow = Workflow(workflow_id, name, description)
            self.workflows[workflow_id] = workflow
            
            # Save workflow
            self._save_workflow(workflow)
            
            return workflow_id
    
    def add_step(self, workflow_id: str, agent_id: str, action: str,
                parameters: Dict[str, Any] = None, dependencies: List[str] = None) -> str:
        """
        Add a step to a workflow.
        
        Args:
            workflow_id: ID of the workflow
            agent_id: ID of the agent responsible for this step
            action: Action to perform
            parameters: Parameters for the action
            dependencies: IDs of steps that must complete before this one
            
        Returns:
            Step ID
        """
        with self.lock:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            step_id = f"step_{uuid.uuid4().hex}"
            step = WorkflowStep(step_id, agent_id, action, parameters, dependencies)
            workflow.add_step(step)
            
            # Save workflow
            self._save_workflow(workflow)
            
            return step_id
    
    def start_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> bool:
        """
        Start a workflow.
        
        Args:
            workflow_id: ID of the workflow to start
            context: Initial context for the workflow
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            # Set initial context
            if context:
                workflow.context = context
            
            # Add to active workflows
            self.active_workflows.add(workflow_id)
            
            # Update status
            workflow.status = WorkflowStatus.RUNNING
            workflow.start_time = time.time()
            
            # Save workflow
            self._save_workflow(workflow)
            
            # Start initial steps
            self._process_workflow(workflow)
            
            return True
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a workflow.
        
        Args:
            workflow_id: ID of the workflow to cancel
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            # Update status
            workflow.status = WorkflowStatus.CANCELLED
            workflow.end_time = time.time()
            
            # Remove from active workflows
            self.active_workflows.discard(workflow_id)
            
            # Save workflow
            self._save_workflow(workflow)
            
            return True
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow information or None if not found
        """
        with self.lock:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return None
            
            return workflow.to_dict()
    
    def list_workflows(self, status: Optional[WorkflowStatus] = None) -> List[Dict[str, Any]]:
        """
        List workflows.
        
        Args:
            status: Filter by status
            
        Returns:
            List of workflow information dictionaries
        """
        with self.lock:
            workflows = []
            
            for workflow in self.workflows.values():
                if status is None or workflow.status == status:
                    workflows.append({
                        'workflow_id': workflow.workflow_id,
                        'name': workflow.name,
                        'description': workflow.description,
                        'status': workflow.status.value,
                        'create_time': workflow.create_time,
                        'start_time': workflow.start_time,
                        'end_time': workflow.end_time,
                        'step_count': len(workflow.steps)
                    })
            
            return workflows
    
    def update_step(self, workflow_id: str, step_id: str, status: StepStatus,
                   result: Any = None, error: str = None) -> bool:
        """
        Update a workflow step.
        
        Args:
            workflow_id: ID of the workflow
            step_id: ID of the step to update
            status: New status
            result: Step result (for completed steps)
            error: Error message (for failed steps)
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            # Update step status
            success = workflow.update_step_status(step_id, status, result, error)
            if not success:
                return False
            
            # Update workflow status
            workflow.update_workflow_status()
            
            # Save workflow
            self._save_workflow(workflow)
            
            # Process next steps if needed
            if workflow.status == WorkflowStatus.RUNNING:
                self._process_workflow(workflow)
            elif workflow.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED):
                # Remove from active workflows
                self.active_workflows.discard(workflow_id)
            
            return True
    
    def _process_workflow(self, workflow: Workflow) -> None:
        """
        Process a workflow by starting ready steps.
        
        Args:
            workflow: Workflow to process
        """
        # Get steps that are ready to run
        ready_steps = workflow.get_next_steps()
        
        for step in ready_steps:
            # Update step status
            workflow.update_step_status(step.step_id, StepStatus.RUNNING)
            
            # Create message for agent
            message = Message(
                sender="workflow_engine",
                recipients=[step.agent_id],
                topic="workflow",
                content={
                    'action': 'execute_step',
                    'workflow_id': workflow.workflow_id,
                    'step_id': step.step_id,
                    'step_action': step.action,
                    'parameters': step.parameters,
                    'context': workflow.context
                }
            )
            
            # Send message
            self.message_bus.publish(message)
    
    def _handle_workflow_message(self, message: Message) -> None:
        """
        Handle a workflow message.
        
        Args:
            message: Message to handle
        """
        content = message.content
        if not isinstance(content, dict):
            return
        
        action = content.get('action')
        
        if action == 'step_completed':
            # Handle step completion
            workflow_id = content.get('workflow_id')
            step_id = content.get('step_id')
            result = content.get('result')
            
            if workflow_id and step_id:
                self.update_step(workflow_id, step_id, StepStatus.COMPLETED, result)
        
        elif action == 'step_failed':
            # Handle step failure
            workflow_id = content.get('workflow_id')
            step_id = content.get('step_id')
            error = content.get('error')
            
            if workflow_id and step_id:
                self.update_step(workflow_id, step_id, StepStatus.FAILED, None, error)
    
    def _save_workflow(self, workflow: Workflow) -> bool:
        """
        Save a workflow to disk.
        
        Args:
            workflow: Workflow to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.storage_dir:
            return False
        
        try:
            file_path = self.storage_dir / f"{workflow.workflow_id}.json"
            
            with open(file_path, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving workflow: {e}")
            return False
    
    def _load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Load a workflow from disk.
        
        Args:
            workflow_id: ID of the workflow to load
            
        Returns:
            Workflow or None if not found
        """
        if not self.storage_dir:
            return None
        
        try:
            file_path = self.storage_dir / f"{workflow_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return Workflow.from_dict(data)
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return None
    
    def load_workflows(self) -> int:
        """
        Load all workflows from disk.
        
        Returns:
            Number of workflows loaded
        """
        if not self.storage_dir:
            return 0
        
        count = 0
        
        for file_path in self.storage_dir.glob("workflow_*.json"):
            try:
                workflow_id = file_path.stem
                workflow = self._load_workflow(workflow_id)
                
                if workflow:
                    self.workflows[workflow_id] = workflow
                    
                    # Add to active workflows if running
                    if workflow.status == WorkflowStatus.RUNNING:
                        self.active_workflows.add(workflow_id)
                    
                    count += 1
            except Exception as e:
                print(f"Error loading workflow {file_path}: {e}")
        
        return count
