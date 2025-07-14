"""
Component system for Nexios App Router.

Components are pure Python functions that return HTML strings.
They can accept props and be composed together.
"""

from typing import Any, Callable, Dict, Optional, Union
from functools import wraps


class Component:
    """Base class for components."""
    
    def __init__(self, func: Callable[..., str]):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
    
    def __call__(self, *args, **kwargs) -> str:
        return self.func(*args, **kwargs)
    
    def render(self, *args, **kwargs) -> str:
        """Render the component with given props."""
        return self.func(*args, **kwargs)


def component(func: Callable[..., str]) -> Component:
    """
    Decorator to create a component from a function.
    
    Example:
        @component
        def Button(text="Click me", variant="default"):
            return f"<button class='btn {variant}'>{text}</button>"
    """
    return Component(func)


def create_component(
    name: str,
    template: str,
    default_props: Optional[Dict[str, Any]] = None
) -> Component:
    """
    Create a component from a template string.
    
    Args:
        name: Component name
        template: HTML template string with {prop_name} placeholders
        default_props: Default props for the component
    
    Example:
        Button = create_component(
            "Button",
            "<button class='btn {variant}'>{text}</button>",
            {"variant": "default", "text": "Click me"}
        )
    """
    default_props = default_props or {}
    
    def component_func(**props):
        # Merge default props with provided props
        merged_props = {**default_props, **props}
        return template.format(**merged_props)
    
    component_func.__name__ = name
    return Component(component_func)


# Built-in components
@component
def Layout(title: str = "Nexios App", children: str = "") -> str:
    """Default layout component."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            {children}
        </div>
    </body>
    </html>
    """


@component
def Button(text: str = "Click me", variant: str = "default", **attrs) -> str:
    """Button component with variants."""
    variant_classes = {
        "default": "bg-blue-500 hover:bg-blue-700 text-white",
        "secondary": "bg-gray-500 hover:bg-gray-700 text-white",
        "danger": "bg-red-500 hover:bg-red-700 text-white",
        "success": "bg-green-500 hover:bg-green-700 text-white"
    }
    
    classes = f"px-4 py-2 rounded font-medium transition-colors {variant_classes.get(variant, variant_classes['default'])}"
    
    # Build additional attributes
    attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return f'<button class="{classes}" {attrs_str}>{text}</button>'


@component
def Card(title: str = "", children: str = "", **attrs) -> str:
    """Card component."""
    attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return f"""
    <div class="bg-white rounded-lg shadow-md p-6 {attrs.get('class', '')}" {attrs_str}>
        {f'<h3 class="text-xl font-semibold mb-4">{title}</h3>' if title else ''}
        {children}
    </div>
    """


@component
def Link(href: str, children: str, **attrs) -> str:
    """Link component."""
    attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return f'<a href="{href}" class="text-blue-600 hover:text-blue-800 underline {attrs.get('class', '')}" {attrs_str}>{children}</a>'


@component
def Input(
    name: str,
    type: str = "text",
    placeholder: str = "",
    value: str = "",
    **attrs
) -> str:
    """Input component."""
    attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return f'<input type="{type}" name="{name}" placeholder="{placeholder}" value="{value}" class="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 {attrs.get('class', '')}" {attrs_str}>'


@component
def Form(action: str = "", method: str = "POST", children: str = "", **attrs) -> str:
    """Form component."""
    attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return f'<form action="{action}" method="{method}" class="space-y-4 {attrs.get('class', '')}" {attrs_str}>{children}</form>'


# Export built-in components
__all__ = [
    "Component",
    "component", 
    "create_component",
    "Layout",
    "Button",
    "Card", 
    "Link",
    "Input",
    "Form"
] 