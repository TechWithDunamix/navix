"""
Main AppRouter class for handling file-based routing.

This is the core class that:
- Scans the app directory for routes
- Registers routes with the Nexios application
- Handles dynamic routing
- Manages layouts and error boundaries
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from urllib.parse import urlparse

from nexios.application import NexiosApp
from nexios.routing import Routes
from nexios.logging import create_logger
from .route_handler import RouteHandler
from .page_builder import PageBuilder

logger = create_logger("nexios.app_router")


class NavixRouter:
    """
    Next.js App Router inspired file-based routing for Nexios.
    
    Features:
    - File-based routing with app/ directory
    - Server-side rendering with Jinja2
    - Layout system
    - Error boundaries
    - Loading states
    - API routes
    """
    
    def __init__(
        self,
        app: NexiosApp,
        app_dir: str = "app",
        components_dir: str = "components",
        template_env: Optional[Any] = None,
        force_create_folder: bool = False
    ):
        self.app = app
        self.app_dir = Path(app_dir)
        self.components_dir = Path(components_dir)
        
        # Create directories if they don't exist
       
        if force_create_folder:
            self.app_dir.mkdir(parents=True, exist_ok=True)
            self.components_dir.mkdir(parents=True, exist_ok=True)
        # Initialize handlers
        self.route_handler = RouteHandler(str(self.app_dir), template_env)
        self.page_builder = PageBuilder(self.route_handler)
        
        # Route cache
        self._routes_cache: Dict[str, Any] = {}
        
        # Register routes
        self.config = self.app.config
        self._register_routes()
    
    def _register_routes(self):
        """Scan app directory and register all routes."""
        logger.info(f"Scanning app directory: {self.app_dir}")
        
        # Find all page.html files
        for page_file in self.app_dir.rglob("page.html"):
            route_path = self._get_route_path_from_file(page_file)
            if route_path:
                self._register_page_route(route_path, page_file)
        
        # Find all route.py files (API routes)
        for route_file in self.app_dir.rglob("route.py"):
            route_path = self._get_route_path_from_file(route_file)
            if route_path:
                self._register_api_route(route_path, route_file)
        
    
    def _get_route_path_from_file(self, file_path: Path) -> Optional[str]:
        """Convert file path to route path."""
        # Get relative path from app directory
        relative_path = file_path.relative_to(self.app_dir)
        
        # Convert to route path
        path_parts = []
        for part in relative_path.parts[:-1]:  # Exclude the filename
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
        
        # Build route path
        route_path = "/" + "/".join(path_parts) if path_parts else "/"
        
        # Handle root page
        if file_path.name == "page.html" and route_path == "/page":
            route_path = "/"
        
        return route_path
    
    def _register_page_route(self, route_path: str, page_file: Path):
        """Register a page route."""
        logger.debug(f"Registering page route: {route_path} -> {page_file}")
        
        async def page_handler(request, response):
           
            content = await self.page_builder.build_page(route_path, request)
            return response.html(content)
           
        # Register the rout
        self.app.add_route(
            Routes(
                path=route_path,
                handler=page_handler,
                methods=["GET"],
                name=f"page_{route_path.replace('/', '_').strip('_')}",
                summary=f"Page route for {route_path}",
                description=f"Renders the page at {route_path}",
                exclude_from_schema=self.config.exlude_page_from_schem or True

            )
        )
        
        self._routes_cache[route_path] = {
            "type": "page",
            "file": page_file,
            "handler": page_handler
        }
    
    def _register_api_route(self, route_path: str, route_file: Path):
        """Register an API route."""
        
        # Load API handlers
        handlers = self.route_handler.load_api_route(route_file)
        if not handlers:
            return
        
        # Register each HTTP method
        for method, handler in handlers.items():
            async def api_handler(request, response, method=method, handler=handler):
                
                result = await handler(request, response)
                return result
                
            
            # Register the route
            self.app.add_route(
                Routes(
                    path=route_path,
                    handler=api_handler,
                    methods=[method],
                    name=f"api_{method.lower()}_{route_path.replace('/', '_').strip('_')}",
                    summary=f"API route for {route_path} ({method})",
                    description=f"Handles {method} requests for {route_path}"
                )
            )
            
            cache_key = f"{route_path}:{method}"
            self._routes_cache[cache_key] = {
                "type": "api",
                "file": route_file,
                "method": method,
                "handler": api_handler
            }
    
    def get_route_info(self, route_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered route."""
        return self._routes_cache.get(route_path)
    
    def list_routes(self) -> List[Dict[str, Any]]:
        """List all registered routes."""
        return list(self._routes_cache.values())
    
    def reload_routes(self):
        """Reload all routes from the app directory."""
        logger.info("Reloading routes...")
        
        # Clear cache
        self._routes_cache.clear()
        
        # Re-register routes
        self._register_routes()
        
        logger.info("Routes reloaded successfully")
    
    def add_component(self, name: str, component_func: Callable):
        """Add a component to the global component registry."""
        # This would integrate with the component system
        # For now, we'll just log it
        logger.info(f"Added component: {name}")
    
    def get_component(self, name: str) -> Optional[Callable]:
        """Get a component from the registry."""
        # This would look up components
        # For now, return None
        return None
    
    def create_route_group(self, name: str, routes: List[Dict[str, Any]]):
        """Create a route group for organization."""
        logger.info(f"Creating route group: {name} with {len(routes)} routes")
        # Implementation for route groups
        pass
    
    def add_middleware(self, middleware_func: Callable):
        """Add middleware to all routes."""
        # This would add middleware to the Nexios app
        # For now, we'll just log it
        logger.info("Adding middleware to all routes")
    
    def set_error_handler(self, error_handler: Callable):
        """Set a global error handler."""
        # This would set up global error handling
        # For now, we'll just log it
        logger.info("Setting global error handler")
    
    def set_loading_handler(self, loading_handler: Callable):
        """Set a global loading handler."""
        # This would set up global loading handling
        # For now, we'll just log it
        logger.info("Setting global loading handler") 