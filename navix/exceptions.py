class NavixException(Exception):
    """Base exception for all Navix errors."""
    pass

class NavixPagePropException(NavixException):
    """Raised when a page prop function fails or is not handled."""
    def __init__(self, message=None, route_path=None, original_exception=None):
        self.route_path = route_path
        self.original_exception = original_exception
        msg = message or "Unhandled exception in page prop."
        if route_path:
            msg += f" (Route: {route_path})"
        if original_exception:
            msg += f"\nOriginal exception: {original_exception}"
        super().__init__(msg)

class NavixRouteException(NavixException):
    """Raised for errors in route handling."""
    pass

class NavixTemplateException(NavixException):
    """Raised for errors in template rendering."""
    pass

class NavixComponentException(NavixException):
    """Raised for errors in component rendering or logic."""
    pass

# Add more as needed for Navix-specific error types 