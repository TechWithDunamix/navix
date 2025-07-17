"""
Page builder for composing layouts, pages, and components.

Handles the hierarchical structure of:
- Root layout
- Nested layouts
- Page content
- Error boundaries
"""

from pathlib import Path
from typing import Any, Dict, Optional, List
from nexios.http import Request, Response
from nexios.logging import create_logger
import re
import inspect
from nexios.dependencies import inject_dependencies

logger = create_logger("nexios.page_builder")


class PageBuilder:
    """Builds pages by composing layouts and content."""
    
    def __init__(self, route_handler):
        self.route_handler = route_handler
        
    def find_layouts(self, route_path: str) -> List[Path]:
        """Find all layout files for a given route path."""
        layouts = []
        path_parts = route_path.strip("/").split("/")
        
        # Build up the path and check for layouts at each level
        current_path = Path(self.route_handler.app_dir)
        
        # Check root layout
        root_layout = current_path / "layout.html"
        if root_layout.exists():
            layouts.append(root_layout)
        
        # Check nested layouts
        for part in path_parts:
            if not part:  # skip empty parts (root)
                continue
            if part.startswith("{") and part.endswith("}"):
                # Skip dynamic segments for layout finding
                continue
                
            current_path = current_path / part
            layout_path = current_path / "layout.html"
            
            if layout_path.exists():
                layouts.append(layout_path)
                
        return layouts
    
    def find_error_handlers(self, route_path: str) -> List[Path]:
        """Find error handlers for a given route path."""
        error_handlers = []
        path_parts = route_path.strip("/").split("/")
        
        # Build up the path and check for error handlers at each level
        current_path = Path(self.route_handler.app_dir)
        
        # Check root error handler
        root_error = current_path / "error.html"
        if root_error.exists():
            error_handlers.append(root_error)
        
        # Check nested error handlers
        for part in path_parts:
            if part.startswith("{") and part.endswith("}"):
                # Skip dynamic segments for error handler finding
                continue
                
            current_path = current_path / part
            error_path = current_path / "error.html"
            
            if error_path.exists():
                error_handlers.append(error_path)
                
        return error_handlers
    
    def find_loading_handlers(self, route_path: str) -> List[Path]:
        """Find loading handlers for a given route path."""
        loading_handlers = []
        path_parts = route_path.strip("/").split("/")
        
        # Build up the path and check for loading handlers at each level
        current_path = Path(self.route_handler.app_dir)
        
        # Check root loading handler
        root_loading = current_path / "loading.html"
        if root_loading.exists():
            loading_handlers.append(root_loading)
        
        # Check nested loading handlers
        for part in path_parts:
            if part.startswith("{") and part.endswith("}"):
                # Skip dynamic segments for loading handler finding
                continue
                
            current_path = current_path / part
            loading_path = current_path / "loading.html"
            
            if loading_path.exists():
                loading_handlers.append(loading_path)
                
        return loading_handlers
    
    async def build_page(
        self,
        route_path: str,
        request: Request,
        props: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build a complete page with all layouts and content."""
            # Find the page template
        page_path = self._find_page_template(route_path)
        if not page_path:
            raise FileNotFoundError(f"No page template found for route: {route_path}")
        
        # Get page props (now async)
        page_props = await self._get_page_props(route_path, request)
        if page_props:
            props = {**(props or {}), **page_props}
        
        # Render the page content
        page_content = self.route_handler.render_page(page_path, request, props)
        
        # Apply layouts
        layouts = self.find_layouts(route_path)
        final_content = page_content
        
        # Apply layouts from innermost to outermost
        for layout_path in reversed(layouts):
            try:
                template_path = str(layout_path.relative_to(self.route_handler.app_dir)).replace("\\", "/")
                layout_template = self.route_handler.template_env.get_template(template_path)
                
                # Merge props with request context
                context = {
                    "request": request,
                    "params": getattr(request, "path_params", {}),
                    "query": getattr(request, "query_params", {}),
                    "children": final_content,
                    **(props or {})
                }
                
                final_content = layout_template.render(**context)
                
            except Exception as e:
                logger.error(f"Failed to apply layout {layout_path}: {e}")
                # Continue without this layout
                continue
        
        return final_content
            
        
    
    def _route_to_filesystem(self, route_path: str) -> str:
        """Convert route path with {slug} to filesystem path with [slug] and catch-all."""
        def replacer(match):
            param = match.group(1)
            if ':' in param:
                # catch-all
                return f"[[...{param.split(':')[0]}]]"
            return f"[{param}]"
        return re.sub(r"{([^}]+)}", replacer, route_path.strip("/"))
    
    def _find_page_template(self, route_path: str) -> Optional[Path]:
        """Find the page template for a given route."""
        if route_path == "/":
            page_path = self.route_handler.app_dir / "page.html"
        else:
            fs_path = self._route_to_filesystem(route_path)
            page_path = self.route_handler.app_dir / fs_path / "page.html"
        
        return page_path if page_path.exists() else None
    
    async def _get_page_props(self, route_path: str, request: Request) -> Optional[Dict[str, Any]]:
        """Get props for a page, using Nexios DI system."""
        from .exceptions import NavixPagePropException
        if route_path == "/":
            props_path = self.route_handler.app_dir / "page.py"
        else:
            fs_path = self._route_to_filesystem(route_path)
            props_path = self.route_handler.app_dir / fs_path / "page.py"
        
        if props_path.exists():
            props_func = self.route_handler.load_page_props(props_path)
            if props_func:
                try:
                    injected = inject_dependencies(props_func)
                    result = injected(request)
                    if inspect.isawaitable(result):
                        return await result
                    return result
                except Exception as e:
                    raise e from NavixPagePropException(
                        message="Exception in page prop function.",
                        route_path=route_path,
                        original_exception=e
                    ) 
        
        return None
    
    def _render_error_page(self, route_path: str, request: Request, error: Exception) -> str:
        """Render an error page."""
        error_handlers = self.find_error_handlers(route_path)
        
        for error_path in error_handlers:
            try:
                error_handler = self.route_handler.load_error_handler(error_path)
                if error_handler:
                    return error_handler(request, error)
            except Exception as e:
                logger.error(f"Failed to use error handler {error_path}: {e}")
                continue
        
        # Fallback error page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <h1>Something went wrong</h1>
            <p>An error occurred while processing your request.</p>
            <p>Error: {str(error)}</p>
        </body>
        </html>
        """
    
    def render_loading_page(self, route_path: str, request: Request) -> str:
        """Render a loading page."""
        loading_handlers = self.find_loading_handlers(route_path)
        
        for loading_path in loading_handlers:
            try:
                loading_handler = self.route_handler.load_loading_handler(loading_path)
                if loading_handler:
                    return loading_handler(request)
            except Exception as e:
                logger.error(f"Failed to use loading handler {loading_path}: {e}")
                continue
        
        # Fallback loading page
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Loading...</title>
        </head>
        <body>
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                <div>Loading...</div>
            </div>
        </body>
        </html>
        """ 