"""
Navix - A Next.js App Router inspired file-based routing system for Python.

This module provides a fullstack Python web framework with:
- File-based routing using `app/` folder structure
- Server-side rendering with Jinja2 templates
- Component system with pure Python functions
- Layout system for nested routes
- API routes support
- Error and loading handlers
"""

from .app_router import NavixRouter
from .component_system import Component, component
from .page_builder import PageBuilder
from .route_handler import RouteHandler
from .utils import create_app

__all__ = [
    "NavixRouter",
    "Component", 
    "component",
    "PageBuilder",
    "RouteHandler",
    "create_app"
] 