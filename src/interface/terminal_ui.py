"""
Terminal UI component for Natural Language Interface.

This component implements the visual interface using the Textual library.
It provides a chat-like interface with clear input/output distinction.
"""

from typing import Callable, Dict, List, Any, Optional
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, Static, Label
from textual.reactive import reactive
from textual.binding import Binding
from rich.markdown import Markdown
from rich.text import Text
from rich.console import Console
from rich.panel import Panel


class MessageDisplay(Static):
    """Widget to display a single message in the chat interface."""
    
    def __init__(self, content: str, sender: str = "system", **kwargs):
        """
        Initialize the message display.
        
        Args:
            content: Message content
            sender: Message sender (user, assistant, or system)
        """
        super().__init__(**kwargs)
        self.content = content
        self.sender = sender
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Static(self._format_message())
    
    def _format_message(self) -> Any:
        """Format the message based on sender."""
        if self.sender == "user":
            return Panel(
                Markdown(self.content) if "```" in self.content else Text(self.content),
                title="You",
                border_style="blue",
                padding=(1, 2)
            )
        elif self.sender == "assistant":
            return Panel(
                Markdown(self.content) if "```" in self.content else Text(self.content),
                title="Semantic OS",
                border_style="green",
                padding=(1, 2)
            )
        else:  # system
            return Panel(
                Text(self.content, style="italic"),
                title="System",
                border_style="yellow",
                padding=(1, 2)
            )


class ChatInterface(Container):
    """Container for the chat messages."""
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Static(id="messages_container")
    
    def add_message(self, content: str, sender: str = "system"):
        """
        Add a message to the chat interface.
        
        Args:
            content: Message content
            sender: Message sender (user, assistant, or system)
        """
        messages = self.query_one("#messages_container")
        message = MessageDisplay(content, sender)
        messages.mount(message)
        messages.scroll_end(animate=False)


class TerminalApp(App):
    """Main terminal application for the natural language interface."""
    
    CSS = """
    #messages_container {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    
    #input_container {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    #user_input {
        width: 1fr;
        height: 3;
        padding: 1;
    }
    
    #send_button {
        width: 10;
        height: 3;
    }
    
    #status_bar {
        width: 100%;
        height: 1;
        background: $surface;
        color: $text;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+k", "clear", "Clear"),
    ]
    
    def __init__(self, message_callback: Callable[[str], None] = None):
        """
        Initialize the terminal application.
        
        Args:
            message_callback: Callback function for processing user messages
        """
        super().__init__()
        self.message_callback = message_callback
    
    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)
        
        # Chat interface
        yield ChatInterface(id="chat_interface")
        
        # Input area
        with Horizontal(id="input_container"):
            yield Input(placeholder="Type your message here...", id="user_input")
            yield Button("Send", id="send_button")
        
        # Status bar
        yield Static("Ready", id="status_bar")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.add_system_message("Welcome to Semantic OS! How can I help you today?")
        self.query_one("#user_input").focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "send_button":
            self.send_message()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission events."""
        self.send_message()
    
    def send_message(self) -> None:
        """Send the user message."""
        input_widget = self.query_one("#user_input")
        message = input_widget.value.strip()
        
        if not message:
            return
        
        # Add user message to chat
        self.add_user_message(message)
        
        # Clear input
        input_widget.value = ""
        input_widget.focus()
        
        # Update status
        self.update_status("Processing...")
        
        # Process message using callback if provided
        if self.message_callback:
            # In a real application, this would be done asynchronously
            # For now, we'll use a simple approach
            try:
                self.message_callback(message)
            except Exception as e:
                self.add_system_message(f"Error processing message: {str(e)}")
                self.update_status("Error")
    
    def add_user_message(self, content: str) -> None:
        """
        Add a user message to the chat.
        
        Args:
            content: Message content
        """
        chat = self.query_one("#chat_interface")
        chat.add_message(content, sender="user")
    
    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message to the chat.
        
        Args:
            content: Message content
        """
        chat = self.query_one("#chat_interface")
        chat.add_message(content, sender="assistant")
        self.update_status("Ready")
    
    def add_system_message(self, content: str) -> None:
        """
        Add a system message to the chat.
        
        Args:
            content: Message content
        """
        chat = self.query_one("#chat_interface")
        chat.add_message(content, sender="system")
    
    def update_status(self, status: str) -> None:
        """
        Update the status bar.
        
        Args:
            status: Status text
        """
        status_bar = self.query_one("#status_bar")
        status_bar.update(status)
    
    def action_clear(self) -> None:
        """Clear the chat interface."""
        chat = self.query_one("#chat_interface")
        messages = chat.query_one("#messages_container")
        messages.remove_children()
        self.add_system_message("Chat cleared.")


class TerminalUI:
    """
    Terminal UI component for the Natural Language Interface.
    
    This class provides a high-level interface for the terminal UI,
    abstracting the details of the Textual implementation.
    """
    
    def __init__(self):
        """Initialize the Terminal UI."""
        self.app = None
        self.message_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
    
    def set_message_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set the callback function for processing user messages.
        
        Args:
            callback: Callback function that takes a message string
        """
        self._message_callback = callback
    
    def _handle_message(self, message: str) -> None:
        """
        Handle a user message.
        
        Args:
            message: User message
        """
        # Put the message in the queue for processing
        asyncio.create_task(self.message_queue.put(message))
        
        # Call the callback if set
        if hasattr(self, '_message_callback'):
            self._message_callback(message)
    
    async def get_next_message(self) -> str:
        """
        Get the next user message from the queue.
        
        Returns:
            User message
        """
        return await self.message_queue.get()
    
    def display_response(self, response: str) -> None:
        """
        Display an assistant response in the UI.
        
        Args:
            response: Assistant response
        """
        if self.app:
            self.app.add_assistant_message(response)
    
    def display_system_message(self, message: str) -> None:
        """
        Display a system message in the UI.
        
        Args:
            message: System message
        """
        if self.app:
            self.app.add_system_message(message)
    
    def update_status(self, status: str) -> None:
        """
        Update the status bar.
        
        Args:
            status: Status text
        """
        if self.app:
            self.app.update_status(status)
    
    def run(self) -> None:
        """Run the terminal UI."""
        print("Semantic OS CLI started. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() == 'exit':
                break
            response = self._handle_message(user_input)
            print("SemanticOS:", response)
    
    def stop(self) -> None:
        """Stop the terminal UI."""
        if self.app:
            self.app.exit()
