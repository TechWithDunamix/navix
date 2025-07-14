# Navix

A Next.js App Router inspired file-based routing system for Python web applications built on nexios .

## Features

- **File-based Routing**: Organize routes using the familiar `app/` directory structure
- **Server-Side Rendering**: Render pages with Jinja2 templates
- **Component System**: Build reusable components with pure Python functions
- **Layout System**: Create nested layouts for consistent page structure
- **API Routes**: Create API endpoints alongside your pages
- **Dynamic Routing**: Support for dynamic segments and catch-all routes
- **Error Handling**: Built-in error boundaries and loading states

## Installation

```bash
pip install navix
```

## Quick Start

```python
from navix import create_app

app = create_app(
    app_dir="app",
    components_dir="components",
    static_dir="static"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## Project Structure

```
myproject/
├── app/                          # App directory (routes)
│   ├── layout.html              # Root layout
│   ├── page.html                # Home page
│   ├── page.py                  # Home page props
│   ├── about/
│   │   └── page.html            # About page
│   ├── blog/
│   │   ├── page.html            # Blog listing
│   │   ├── page.py              # Blog props
│   │   └── [slug]/              # Dynamic blog posts
│   │       ├── page.html
│   │       └── page.py
│   └── api/
│       └── status/
│           └── route.py         # API route
├── components/                   # Reusable components
│   ├── Button.py
│   └── Card.py
├── static/                       # Static files
└── main.py                       # Application entry point
```

## Usage Examples

### File-based Routing

Create routes by adding files to the `app/` directory:

- `app/page.html` → `/` (home page)
- `app/about/page.html` → `/about`
- `app/blog/page.html` → `/blog`
- `app/blog/[slug]/page.html` → `/blog/hello-world` (dynamic route)

### Page Templates

Create HTML templates with Jinja2 syntax:

```html
<!-- app/page.html -->
<div class="home-page">
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
    
    {% for feature in features %}
    <div class="feature">
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.description }}</p>
    </div>
    {% endfor %}
</div>
```

### Page Props

Provide data to your pages using Python functions:

```python
# app/page.py
from navix.http import Request
from typing import Dict, Any

def props(request: Request) -> Dict[str, Any]:
    return {
        "title": "Welcome",
        "description": "Hello from Navix",
        "features": [
            {"title": "Fast", "description": "Lightning fast performance"},
            {"title": "Simple", "description": "Easy to use and understand"}
        ]
    }
```

### Components

Create reusable components with pure Python functions:

```python
# components/Button.py
from navix import component

@component
def Button(text="Click me", variant="default", **attrs):
    variant_classes = {
        "default": "btn",
        "primary": "btn btn-primary",
        "secondary": "btn btn-secondary"
    }
    
    classes = variant_classes.get(variant, variant_classes["default"])
    attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return f'<button class="{classes}" {attrs_str}>{text}</button>'
```

Use components in your templates:

```html
{{ component('Button', text='Hello World', variant='primary') }}
```

### API Routes

Create API endpoints alongside your pages:

```python
# app/api/status/route.py
from navix.http import Request, Response

async def get(request: Request, response: Response) -> Response:
    return response.json({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })

async def post(request: Request, response: Response) -> Response:
    data = await request.json()
    return response.json({"received": data})
```

## License

BSD-3-Clause 