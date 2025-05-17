"""
Message Bus component for Modular Command Processing.

This component facilitates communication between agents using a standardized message format.
It implements publish-subscribe patterns for message distribution.
"""

from typing import Dict, List, Any, Optional, Callable, Set
import threading
import uuid
import time
import json
from queue import Queue, Empty
from dataclasses import dataclass, asdict, field


@dataclass
class Message:
    """Message data structure for agent communication."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    topic: str = ""
    content: Any = None
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(**data)


class MessageBus:
    """
    Facilitates communication between agents using a standardized message format.
    
    This class is responsible for:
    1. Implementing publish-subscribe patterns for message distribution
    2. Supporting synchronous and asynchronous communication modes
    3. Providing message validation and routing
    """
    
    def __init__(self):
        """Initialize the MessageBus."""
        self.subscribers = {}
        self.topic_subscribers = {}
        self.message_history = {}
        self.lock = threading.RLock()
        self.max_history_per_topic = 100
    
    def publish(self, message: Message) -> str:
        """
        Publish a message to the bus.
        
        Args:
            message: Message to publish
            
        Returns:
            Message ID
        """
        with self.lock:
            # Store message in history
            topic = message.topic
            if topic not in self.message_history:
                self.message_history[topic] = []
            
            self.message_history[topic].append(message)
            
            # Trim history if needed
            if len(self.message_history[topic]) > self.max_history_per_topic:
                self.message_history[topic] = self.message_history[topic][-self.max_history_per_topic:]
            
            # Deliver to specific recipients
            for recipient in message.recipients:
                if recipient in self.subscribers:
                    for callback in self.subscribers[recipient]:
                        try:
                            callback(message)
                        except Exception as e:
                            print(f"Error delivering message to {recipient}: {e}")
            
            # Deliver to topic subscribers
            if topic in self.topic_subscribers:
                for callback in self.topic_subscribers[topic]:
                    try:
                        callback(message)
                    except Exception as e:
                        print(f"Error delivering message to topic {topic}: {e}")
            
            return message.id
    
    def subscribe(self, agent_id: str, callback: Callable[[Message], None]) -> None:
        """
        Subscribe an agent to receive messages addressed to it.
        
        Args:
            agent_id: ID of the subscribing agent
            callback: Function to call when a message is received
        """
        with self.lock:
            if agent_id not in self.subscribers:
                self.subscribers[agent_id] = set()
            
            self.subscribers[agent_id].add(callback)
    
    def unsubscribe(self, agent_id: str, callback: Optional[Callable[[Message], None]] = None) -> None:
        """
        Unsubscribe an agent from receiving messages.
        
        Args:
            agent_id: ID of the agent to unsubscribe
            callback: Specific callback to remove (None to remove all)
        """
        with self.lock:
            if agent_id in self.subscribers:
                if callback is None:
                    # Remove all callbacks
                    del self.subscribers[agent_id]
                else:
                    # Remove specific callback
                    self.subscribers[agent_id].discard(callback)
                    
                    # Clean up if no callbacks remain
                    if not self.subscribers[agent_id]:
                        del self.subscribers[agent_id]
    
    def subscribe_to_topic(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        Subscribe to a topic to receive all messages on that topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is received
        """
        with self.lock:
            if topic not in self.topic_subscribers:
                self.topic_subscribers[topic] = set()
            
            self.topic_subscribers[topic].add(callback)
    
    def unsubscribe_from_topic(self, topic: str, callback: Optional[Callable[[Message], None]] = None) -> None:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            callback: Specific callback to remove (None to remove all)
        """
        with self.lock:
            if topic in self.topic_subscribers:
                if callback is None:
                    # Remove all callbacks
                    del self.topic_subscribers[topic]
                else:
                    # Remove specific callback
                    self.topic_subscribers[topic].discard(callback)
                    
                    # Clean up if no callbacks remain
                    if not self.topic_subscribers[topic]:
                        del self.topic_subscribers[topic]
    
    def get_message_history(self, topic: Optional[str] = None, limit: int = 100) -> List[Message]:
        """
        Get message history for a topic.
        
        Args:
            topic: Topic to get history for (None for all topics)
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        with self.lock:
            if topic is not None:
                # Get history for specific topic
                return self.message_history.get(topic, [])[-limit:]
            else:
                # Get history for all topics
                all_messages = []
                for topic_messages in self.message_history.values():
                    all_messages.extend(topic_messages)
                
                # Sort by timestamp
                all_messages.sort(key=lambda m: m.timestamp)
                
                return all_messages[-limit:]
    
    def request_response(self, request: Message, timeout: float = 5.0) -> Optional[Message]:
        """
        Send a request and wait for a response.
        
        Args:
            request: Request message
            timeout: Maximum time to wait for response (seconds)
            
        Returns:
            Response message or None if timeout
        """
        response_queue = Queue()
        
        # Create a correlation ID if not present
        if not request.correlation_id:
            request.correlation_id = str(uuid.uuid4())
        
        # Define response handler
        def response_handler(message: Message):
            if message.correlation_id == request.correlation_id:
                response_queue.put(message)
        
        # Subscribe to responses
        for recipient in request.recipients:
            self.subscribe(recipient, response_handler)
        
        # Send request
        self.publish(request)
        
        try:
            # Wait for response
            return response_queue.get(timeout=timeout)
        except Empty:
            return None
        finally:
            # Unsubscribe from responses
            for recipient in request.recipients:
                self.unsubscribe(recipient, response_handler)
    
    def clear_history(self, topic: Optional[str] = None) -> None:
        """
        Clear message history.
        
        Args:
            topic: Topic to clear history for (None for all topics)
        """
        with self.lock:
            if topic is not None:
                # Clear history for specific topic
                if topic in self.message_history:
                    self.message_history[topic] = []
            else:
                # Clear all history
                self.message_history = {}
