"""
Utility functions for Navix.

Provides convenient functions for:
- Creating applications with App Router
- Configuring templates and components
- Setting up development environment
"""

from pathlib import Path
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader

from nexios import NexiosApp
from nexios.logging import create_logger
from nexios.static import StaticFiles
from .app_router import NavixRouter
from .route_handler import RouteHandler

logger = create_logger("navix.utils")


def create_app(
    app_dir: str = "app",
    components_dir: str = "components",
    template_dir: Optional[str] = None,
    static_dir: str = "static",
    **config
) -> Any:
    """
    Create a Nexios application with Navix Router.
    
    Args:
        app_dir: Directory containing the app routes
        components_dir: Directory containing components
        template_dir: Directory for additional templates
        static_dir: Directory for static files
        **config: Additional configuration options
    
    Returns:
        Configured Nexios application with App Router
    """
    # Create the base application
    app = NexiosApp()
    
    # Configure static files
    if static_dir and Path(static_dir).exists():
        app.register(StaticFiles(directory=static_dir), "/static")
    
    # Create template environment
    template_dirs = [app_dir, components_dir]
    if template_dir:
        template_dirs.append(template_dir)
    
    template_env = Environment(
        loader=FileSystemLoader(template_dirs),
        auto_reload=True,
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    # Create and configure App Router and RouteHandler
    route_handler = RouteHandler(app_dir, template_env)
    # Add custom filters and globals
    template_env.globals.update({
        'component': route_handler._render_component,
        'render': route_handler._render_template,
        'url_for': lambda name, **kwargs: f"/{name}",
        'static': lambda path: f"/static/{path}",
    })
    
    # Create and configure App Router
    app_router = NavixRouter(
        app=app,
        app_dir=app_dir,
        components_dir=components_dir,
        template_env=template_env
    )
    
    # Store app_router reference for later use
    if not hasattr(app, "state"):
        from types import SimpleNamespace
        app.state = SimpleNamespace()
    app.state.app_router = app_router
    
    logger.info(f"Created Navix application with app_dir: {app_dir}")
    
    return app


def create_component_file(name: str, components_dir: str = "components") -> Path:
    """
    Create a new component file.
    
    Args:
        name: Component name
        components_dir: Components directory
    
    Returns:
        Path to the created component file
    """
    components_path = Path(components_dir)
    components_path.mkdir(exist_ok=True)
    
    component_file = components_path / f"{name}.py"
    
    if component_file.exists():
        logger.warning(f"Component {name} already exists")
        return component_file
    
    # Create component template
    component_content = f'''"""
{name} component.
"""

from nexios.app_router import component


@component
def {name}(**props):
    """
    {name} component.
    
    Args:
        **props: Component props
    
    Returns:
        HTML string
    """
    return f"""
    <div class="{name.lower()}-component">
        <!-- {name} component content -->
        {{% for key, value in props.items() %}}
            <div>{{{{ key }}}}: {{{{ value }}}}</div>
        {{% endfor %}}
    </div>
    """
'''
    
    component_file.write_text(component_content)
    logger.info(f"Created component: {component_file}")
    
    return component_file


def create_page(
    route_path: str,
    app_dir: str = "app",
    template: str = "page",
    props: bool = True
) -> Dict[str, Path]:
    """
    Create a new page with template and optional props.
    
    Args:
        route_path: Route path (e.g., "/about", "/blog/[id]")
        app_dir: App directory
        template: Template type ("page", "api", "layout")
        props: Whether to create a props file
    
    Returns:
        Dictionary with created file paths
    """
    app_path = Path(app_dir)
    
    # Convert route path to file path
    if route_path == "/":
        page_dir = app_path
    else:
        # Remove leading slash and split
        parts = route_path.strip("/").split("/")
        page_dir = app_path
        
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                # Dynamic route
                page_dir = page_dir / part
            elif part.startswith("[[") and part.endswith("]]"):
                # Catch-all route
                page_dir = page_dir / part
            else:
                page_dir = page_dir / part
    
    # Create directory
    page_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = {}
    
    if template == "page":
        # Create page.html
        page_html = page_dir / "page.html"
        if not page_html.exists():
            page_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title or "Page" }}}}</title>
</head>
<body>
    <div class="page">
        <h1>{{{{ title or "Welcome" }}}}</h1>
        <div class="content">
            <!-- Page content here -->
            <p>This is the {route_path} page.</p>
        </div>
    </div>
</body>
</html>'''
            page_html.write_text(page_content)
            created_files["page_html"] = page_html
        
        # Create page.py if requested
        if props:
            page_py = page_dir / "page.py"
            if not page_py.exists():
                props_content = f'''"""
Props for {route_path} page.
"""

from nexios.http import Request
from typing import Dict, Any


def props(request: Request) -> Dict[str, Any]:
    """
    Get props for the {route_path} page.
    
    Args:
        request: HTTP request
    
    Returns:
        Props dictionary
    """
    return {{
        "title": "{route_path.title()}",
        "path": request.path,
        "method": request.method,
    }}
'''
                page_py.write_text(props_content)
                created_files["page_py"] = page_py
    
    elif template == "api":
        # Create route.py for API
        route_py = page_dir / "route.py"
        if not route_py.exists():
            api_content = f'''"""
API route for {route_path}.
"""

from nexios.http import Request, Response
from typing import Dict, Any


async def get(request: Request, response: Response) -> Response:
    """
    Handle GET requests for {route_path}.
    """
    return response.json({{
        "message": "Hello from {route_path}",
        "method": "GET"
    }})


async def post(request: Request, response: Response) -> Response:
    """
    Handle POST requests for {route_path}.
    """
    data = await request.json()
    return response.json({{
        "message": "Data received",
        "data": data,
        "method": "POST"
    }})
'''
            route_py.write_text(api_content)
            created_files["route_py"] = route_py
    
    elif template == "layout":
        # Create layout.html
        layout_html = page_dir / "layout.html"
        if not layout_html.exists():
            layout_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title or "Layout" }}}}</title>
</head>
<body>
    <div class="layout">
        <header>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
            </nav>
        </header>
        
        <main>
            {{{{ children }}}}
        </main>
        
        <footer>
            <p>&copy; 2024 Your App</p>
        </footer>
    </div>
</body>
</html>'''
            layout_html.write_text(layout_content)
            created_files["layout_html"] = layout_html
    
    logger.info(f"Created {template} for route: {route_path}")
    return created_files


def create_error_page(app_dir: str = "app") -> Path:
    """Create a global error page."""
    app_path = Path(app_dir)
    error_html = app_path / "error.html"
    
    if not error_html.exists():
        error_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
</head>
<body>
    <div class="error-page">
        <h1>Something went wrong</h1>
        <p>An error occurred while processing your request.</p>
        <a href="/">Go back home</a>
    </div>
</body>
</html>'''
        error_html.write_text(error_content)
        logger.info("Created global error page")
    
    return error_html


def create_loading_page(app_dir: str = "app") -> Path:
    """Create a global loading page."""
    app_path = Path(app_dir)
    loading_html = app_path / "loading.html"
    
    if not loading_html.exists():
        loading_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
</head>
<body>
    <div class="loading-page">
        <div class="spinner"></div>
        <p>Loading...</p>
    </div>
    <style>
        .loading-page {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</body>
</html>'''
        loading_html.write_text(loading_content)
        logger.info("Created global loading page")
    
    return loading_html


def setup_development_environment(
    app_dir: str = "app",
    components_dir: str = "components",
    static_dir: str = "static"
):
    """Set up a complete development environment."""
    logger.info("Setting up development environment...")
    
    # Create directories
    Path(app_dir).mkdir(exist_ok=True)
    Path(components_dir).mkdir(exist_ok=True)
    Path(static_dir).mkdir(exist_ok=True)
    
    # Create basic files
    create_error_page(app_dir)
    create_loading_page(app_dir)
    
    # Create root layout
    create_page("/", app_dir, "layout")
    
    # Create home page
    create_page("/", app_dir, "page", props=True)
    
    # Create a sample component
    create_component_file("Button", components_dir)
    
    logger.info("Development environment setup complete!")


def get_app_router(app) -> Optional[NavixRouter]:
    """Get the App Router instance from an application."""
    return getattr(app.state, "app_router", None) 