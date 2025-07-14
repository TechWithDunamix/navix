"""
CLI tool for Nexios App Router.

Provides commands for:
- Creating new projects
- Generating components and pages
- Managing the development environment
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .utils import (
    setup_development_environment,
    create_component_file,
    create_page,
    create_error_page,
    create_loading_page
)


def create_project(name: str, directory: Optional[str] = None):
    """Create a new App Router project."""
    if directory is None:
        directory = name
    
    project_dir = Path(directory)
    project_dir.mkdir(exist_ok=True)
    
    print(f"Creating Nexios App Router project: {name}")
    print(f"Directory: {project_dir.absolute()}")
    
    # Create project structure
    (project_dir / "app").mkdir(exist_ok=True)
    (project_dir / "components").mkdir(exist_ok=True)
    (project_dir / "static").mkdir(exist_ok=True)
    
    # Create main.py
    main_content = f'''"""
{name} - Nexios App Router Application
"""

from nexios.app_router.utils import create_app, setup_development_environment

# Set up development environment
setup_development_environment()

# Create the application with App Router
app = create_app(
    app_dir="app",
    components_dir="components", 
    static_dir="static"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
    
    (project_dir / "main.py").write_text(main_content)
    
    # Create requirements.txt
    requirements_content = """nexios>=0.1.0
jinja2>=3.0.0
uvicorn>=0.20.0
"""
    (project_dir / "requirements.txt").write_text(requirements_content)
    
    # Create README.md
    readme_content = f"""# {name}

A Nexios App Router application.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Open your browser to http://localhost:8000

## Project Structure

- `app/` - Application routes and pages
- `components/` - Reusable components
- `static/` - Static files (CSS, JS, images)
- `main.py` - Application entry point

## Development

- Add pages by creating files in the `app/` directory
- Create components in the `components/` directory
- Use `nexios-router generate` to create new files
"""
    (project_dir / "README.md").write_text(readme_content)
    
    # Set up development environment
    setup_development_environment(
        app_dir=str(project_dir / "app"),
        components_dir=str(project_dir / "components"),
        static_dir=str(project_dir / "static")
    )
    
    print("✅ Project created successfully!")
    print(f"📁 Navigate to: {project_dir.absolute()}")
    print("🚀 Run: python main.py")


def generate_component(name: str, components_dir: str = "components"):
    """Generate a new component."""
    print(f"Creating component: {name}")
    
    component_file = create_component_file(name, components_dir)
    
    print(f"✅ Component created: {component_file}")
    print(f"📝 Edit: {component_file}")


def generate_page(route: str, app_dir: str = "app", template: str = "page", props: bool = True):
    """Generate a new page."""
    print(f"Creating page: {route}")
    
    created_files = create_page(route, app_dir, template, props)
    
    print(f"✅ Page created with {len(created_files)} files:")
    for file_type, file_path in created_files.items():
        print(f"   📄 {file_type}: {file_path}")


def generate_error_pages(app_dir: str = "app"):
    """Generate error and loading pages."""
    print("Creating error and loading pages...")
    
    error_file = create_error_page(app_dir)
    loading_file = create_loading_page(app_dir)
    
    print(f"✅ Error page created: {error_file}")
    print(f"✅ Loading page created: {loading_file}")


def setup_dev_environment(app_dir: str = "app", components_dir: str = "components", static_dir: str = "static"):
    """Set up development environment."""
    print("Setting up development environment...")
    
    setup_development_environment(app_dir, components_dir, static_dir)
    
    print("✅ Development environment setup complete!")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Nexios App Router CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nexios-router create my-app
  nexios-router generate component Button
  nexios-router generate page /about
  nexios-router generate page /blog/[slug] --template api
  nexios-router setup
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create project command
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--directory", help="Project directory (defaults to project name)")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate files")
    generate_parser.add_argument("type", choices=["component", "page"], help="Type of file to generate")
    generate_parser.add_argument("name", help="Name or route path")
    generate_parser.add_argument("--template", choices=["page", "api", "layout"], default="page", help="Template type")
    generate_parser.add_argument("--no-props", action="store_true", help="Don't create props file")
    
    # Generate error pages command
    error_parser = subparsers.add_parser("generate-error", help="Generate error and loading pages")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up development environment")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "create":
            create_project(args.name, args.directory)
        
        elif args.command == "generate":
            if args.type == "component":
                generate_component(args.name)
            elif args.type == "page":
                generate_page(args.name, template=args.template, props=not args.no_props)
        
        elif args.command == "generate-error":
            generate_error_pages()
        
        elif args.command == "setup":
            setup_dev_environment()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 