"""
Workflow template data model.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WorkflowStep:
    """Workflow step data model."""
    agent: str
    task: str
    description: str
    estimated_duration: Optional[str] = None
    deliverables: Optional[List[str]] = None
    priority: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> 'WorkflowStep':
        """Create WorkflowStep from dictionary."""
        return WorkflowStep(
            agent=data.get('agent', ''),
            task=data.get('task', ''),
            description=data.get('description', ''),
            estimated_duration=data.get('estimated_duration'),
            deliverables=data.get('deliverables'),
            priority=data.get('priority')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            'agent': self.agent,
            'task': self.task,
            'description': self.description
        }
        if self.estimated_duration:
            result['estimated_duration'] = self.estimated_duration
        if self.deliverables:
            result['deliverables'] = self.deliverables
        if self.priority:
            result['priority'] = self.priority
        return result


@dataclass
class WorkflowTemplate:
    """Workflow template data model."""
    slug: str  # JSON object key
    name: str  # User-friendly display name
    description: str
    steps: List[WorkflowStep]
    created: Optional[str] = None

    @staticmethod
    def from_dict(slug: str, data: dict) -> 'WorkflowTemplate':
        """Create WorkflowTemplate from dictionary."""
        steps_data = data.get('steps', [])
        steps = [WorkflowStep.from_dict(s) for s in steps_data]

        return WorkflowTemplate(
            slug=slug,
            name=data.get('name', slug),
            description=data.get('description', ''),
            steps=steps,
            created=data.get('created')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            'name': self.name,
            'description': self.description,
            'steps': [s.to_dict() for s in self.steps]
        }
        if self.created:
            result['created'] = self.created
        return result