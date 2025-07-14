"""
Route handler for processing different file types in the app directory.

Handles:
- page.html -> Jinja2 templates
- page.py -> Python logic/props
- layout.html -> Layout templates
- error.html -> Error handlers
- loading.html -> Loading handlers
- route.py -> API routes
"""

import os
import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable
from functools import wraps

from jinja2 import Environment, FileSystemLoader, Template
from nexios.http import Request, Response
from nexios.logging import create_logger

logger = create_logger("nexios.app_router")


class RouteHandler:
    """Handles different route file types in the app directory."""
    
    def __init__(self, app_dir: str = "app", template_env: Optional[Environment] = None):
        self.app_dir = Path(app_dir)
        self.template_env = template_env or self._create_template_env()
        self.components_dir = Path("components")
        
    def _create_template_env(self) -> Environment:
        """Create Jinja2 environment with app directory and components support."""
        env = Environment(
            loader=FileSystemLoader([str(self.app_dir), str(self.components_dir)]),
            auto_reload=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters and globals for components
        env.globals.update({
            'component': self._render_component,
            'render': self._render_template
        })
        
        return env
    
    def _render_component(self, component_name: str, **props) -> str:
        """Render a component by name."""
        try:
            # Try to import component from components directory
            component_path = self.components_dir / f"{component_name}.py"
            if component_path.exists():
                spec = importlib.util.spec_from_file_location(component_name, component_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for a function with the same name as the component
                if hasattr(module, component_name):
                    component_func = getattr(module, component_name)
                    return component_func(**props)
                    
        except Exception as e:
            logger.warning(f"Failed to render component {component_name}: {e}")
            
        return f"<!-- Component {component_name} not found -->"
    
    def _render_template(self, template_name: str, **context) -> str:
        """Render a template with context."""
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            return f"<!-- Template {template_name} not found -->"
    
    def get_route_path(self, file_path: Path) -> str:
        """Convert file path to route path."""
        # Remove app_dir prefix and file extension
        relative_path = file_path.relative_to(self.app_dir)
        
        # Convert to route path
        path_parts = []
        for part in relative_path.parts:
            if part.startswith("(") and part.endswith(")"):
                # Route groups - ignore
                continue
            elif part.startswith("[") and part.endswith("]"):
                # Dynamic routes
                param_name = part[1:-1]
                path_parts.append(f"{{{param_name}}}")
            elif part.startswith("[[") and part.endswith("]]"):
                # Catch-all routes
                param_name = part[2:-2]
                path_parts.append(f"{{{param_name}:path}}")
            else:
                path_parts.append(part)
        
        # Remove file extensions
        route_path = "/".join(path_parts)
        route_path = route_path.replace(".html", "").replace(".py", "")
        
        # Handle special files
        if route_path.endswith("/page"):
            route_path = route_path[:-5]  # Remove /page
        elif route_path.endswith("/layout"):
            route_path = route_path[:-7]  # Remove /layout
        elif route_path.endswith("/error"):
            route_path = route_path[:-6]  # Remove /error
        elif route_path.endswith("/loading"):
            route_path = route_path[:-8]  # Remove /loading
        elif route_path.endswith("/route"):
            route_path = route_path[:-6]  # Remove /route
        
        # Ensure root path is "/"
        if route_path == "":
            route_path = "/"
        
        return route_path
    
    def load_page_props(self, page_path: Path) -> Optional[Callable]:
        """Load page.py file and return the props function."""
        if not page_path.exists():
            return None
            
        try:
            spec = importlib.util.spec_from_file_location("page", page_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for props function
            if hasattr(module, "props"):
                return getattr(module, "props")
            elif hasattr(module, "get_props"):
                return getattr(module, "get_props")
            elif hasattr(module, "page_props"):
                return getattr(module, "page_props")
                
        except Exception as e:
            logger.error(f"Failed to load page props from {page_path}: {e}")
            
        return None
    
    def load_layout(self, layout_path: Path) -> Optional[Template]:
        """Load layout.html file."""
        if not layout_path.exists():
            return None
            
        try:
            return self.template_env.get_template(str(layout_path.relative_to(self.app_dir)))
        except Exception as e:
            logger.error(f"Failed to load layout from {layout_path}: {e}")
            return None
    
    def load_error_handler(self, error_path: Path) -> Optional[Callable]:
        """Load error.html file and return error handler."""
        if not error_path.exists():
            return None
            
        try:
            spec = importlib.util.spec_from_file_location("error", error_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for error handler function
            if hasattr(module, "error_handler"):
                return getattr(module, "error_handler")
            elif hasattr(module, "handle_error"):
                return getattr(module, "handle_error")
                
        except Exception as e:
            logger.error(f"Failed to load error handler from {error_path}: {e}")
            
        return None
    
    def load_loading_handler(self, loading_path: Path) -> Optional[Callable]:
        """Load loading.html file and return loading handler."""
        if not loading_path.exists():
            return None
            
        try:
            spec = importlib.util.spec_from_file_location("loading", loading_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for loading handler function
            if hasattr(module, "loading_handler"):
                return getattr(module, "loading_handler")
            elif hasattr(module, "handle_loading"):
                return getattr(module, "handle_loading")
                
        except Exception as e:
            logger.error(f"Failed to load loading handler from {loading_path}: {e}")
            
        return None
    
    def load_api_route(self, route_path: Path) -> Optional[Callable]:
        """Load route.py file and return API handler."""
        if not route_path.exists():
            return None
            
        try:
            spec = importlib.util.spec_from_file_location("route", route_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for HTTP method handlers
            methods = ["get", "post", "put", "patch", "delete", "head", "options"]
            handlers = {}
            
            for method in methods:
                if hasattr(module, method):
                    handlers[method.upper()] = getattr(module, method)
                    
            return handlers if handlers else None
                
        except Exception as e:
            logger.error(f"Failed to load API route from {route_path}: {e}")
            
        return None
    
    def render_page(
        self,
        page_path: Path,
        request: Request,
        props: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render a page with its template and props."""
        if not page_path.exists():
            raise FileNotFoundError(f"Page template not found: {page_path}")
            
        try:
            template_path = str(page_path.relative_to(self.app_dir)).replace("\\", "/")
            template = self.template_env.get_template(template_path)
            
            # Merge props with request context
            context = {
                "request": request,
                "params": getattr(request, "path_params", {}),
                "query": getattr(request, "query_params", {}),
                **(props or {})
            }
            
            return template.render(**context)
            
        except Exception as e:
            logger.error(f"Failed to render page {page_path}: {e}")
            raise 