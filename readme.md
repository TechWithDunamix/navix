# Navix

Navix is a static site generator for Python, designed to make building simple, content-driven websites effortless and SEO-optimized by default. It is ideal for blogs, documentation, portfolios, and landing pages—sites that don’t need dynamic forms or client-side loading.

---

## Key Features

- **Static HTML Output:**
  - All pages are generated as static HTML for maximum speed and SEO.
- **Automatic SEO:**
  - Title, description, canonical tags
  - Open Graph and Twitter Card meta
  - Sitemap.xml and robots.txt
  - Schema.org structured data
- **Layouts:**
  - Define reusable layouts (e.g., `layout.html`) for consistent site structure.
- **Markdown & HTML Content:**
  - Write content in Markdown or HTML. Navix handles conversion, linking, and SEO enhancements.
- **Component System:**
  - Build reusable static components with Python functions for use in templates.
- **Asset Handling:**
  - Simple static asset pipeline for CSS, JS, and images.
- **No Dynamic Features:**
  - No forms, loaders, or client-side routing. All navigation is standard HTML links.

---

## What Navix Is Not

- Not a React/SPA framework
- Not for building dashboards or apps
- Not for dynamic, user-interactive sites
- No server-side runtime or API endpoints

---

## Installation

```bash
pip install navix
```

---

## Quick Start

1. **Create your project structure:**

```
myproject/
├── app/                # Your pages (Markdown or HTML)
│   ├── layout.html     # Root layout
│   ├── index.md        # Home page (Markdown)
│   ├── about.md        # About page
│   └── blog/
│       ├── index.md    # Blog listing
│       └── hello.md    # Blog post
├── components/         # Reusable static components (Python)
│   └── Button.py
├── static/             # Static files (CSS, JS, images)
└── main.py             # (Optional) For local preview
```

2. **Write content in Markdown or HTML:**

```markdown
# Welcome to My Site
This is my homepage, built with Navix!
```

3. **Define a layout:**

```html
<!-- app/layout.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <meta name="description" content="{{ description }}">
    <!-- SEO meta tags auto-generated -->
</head>
<body>
    <header><h1>{{ site_name }}</h1></header>
    <main>{{ children }}</main>
    <footer>&copy; 2024 My Site</footer>
</body>
</html>
```

4. **Build your static site:**

```bash
navix build
```

All your pages will be generated as static HTML in the `output/` directory, complete with SEO enhancements.

---

## Usage

- Place Markdown (`.md`) or HTML (`.html`) files in the `app/` directory.
- Use layouts for consistent structure.
- Use Python components for static HTML snippets.
- Run `navix build` to generate your site.

---

## SEO by Default

Navix automatically generates:
- Meta tags (title, description, canonical)
- Open Graph and Twitter Card tags
- Sitemap.xml and robots.txt
- Structured data (Schema.org)

---

## Example Use Cases

- Personal blogs
- Documentation sites
- Marketing/landing pages
- Portfolio sites

---

## License

BSD-3-Clause 