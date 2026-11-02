"""OpenAPI specification for the CloudOps AI REST API."""

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "CloudOps AI API",
        "version": "0.1.0",
        "description": (
            "REST API for AI-assisted cloud monitoring, "
            "incident troubleshooting, application registration, "
            "and administrative operations."
        ),
    },
    "tags": [
        {"name": "Monitoring", "description": "Monitoring and health endpoints."},
        {"name": "Applications", "description": "Application management."},
        {"name": "Authentication", "description": "Administrator browser sessions."},
        {"name": "Discovery", "description": "Prometheus target discovery."},
    ],
    "components": {
        "securitySchemes": {
            "ManagementToken": {
                "type": "apiKey",
                "in": "header",
                "name": "X-CloudOps-Token",
                "description": "Administrator management API token.",
            },
            "BrowserSession": {
                "type": "apiKey",
                "in": "cookie",
                "name": "session",
                "description": (
                    "Flask administrator session cookie. "
                    "State-changing browser requests also require "
                    "CSRF validation."
                ),
            },
            "CSRFToken": {
                "type": "apiKey",
                "in": "header",
                "name": "X-CSRF-Token",
                "description": (
                    "CSRF token returned by administrator login "
                    "or session status."
                ),
            },
        },
    },
    "paths": {
        "/api/discovery/preview": {
            "get": {
                "tags": ["Discovery"],
                "summary": "Preview Prometheus target discovery",
                "description": (
                    "Preview generated Prometheus target groups for "
                    "registered applications. Requires either a valid "
                    "management token or an authenticated browser session. "
                    "This operation does not modify monitoring configuration."
                ),
                "security": [
                    {"ManagementToken": []},
                    {"BrowserSession": []},
                ],
                "responses": {
                    "200": {
                        "description": "Prometheus target groups returned.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": [
                                        "status",
                                        "count",
                                        "target_groups",
                                    ],
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "success",
                                        },
                                        "count": {
                                            "type": "integer",
                                            "minimum": 0,
                                        },
                                        "target_groups": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "additionalProperties": True,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "401": {
                        "description": "Authentication required.",
                    },
                    "403": {
                        "description": "Invalid or unauthorized management token.",
                    },
                },
            },
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Log in as administrator",
                "description": (
                    "Authenticate using the administrator token and establish "
                    "a browser session. Limited to five requests per minute. "
                    "HTTPS is required when CLOUDOPS_HTTPS_ENABLED=true."
                ),
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["token"],
                                "properties": {
                                    "token": {
                                        "type": "string",
                                        "format": "password",
                                        "description": "Administrator credential.",
                                    },
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Administrator authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["status", "csrf_token"],
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "authenticated",
                                        },
                                        "csrf_token": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "400": {"description": "Invalid JSON request."},
                    "401": {"description": "Invalid credentials."},
                    "403": {"description": "HTTPS is required."},
                    "429": {"description": "Login rate limit exceeded."},
                    "503": {"description": "Browser login is not configured."},
                },
            },
        },
        "/api/auth/logout": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Log out administrator",
                "description": (
                    "End the current authenticated browser session. "
                    "Requires a valid CSRF token."
                ),
                "security": [
                    {"BrowserSession": [], "CSRFToken": []},
                ],
                "responses": {
                    "200": {
                        "description": "Administrator logged out.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "logged_out",
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "401": {"description": "Authentication required."},
                    "403": {"description": "CSRF validation failed."},
                },
            },
        },
        "/api/auth/session": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get administrator session status",
                "description": (
                    "Check the authenticated browser session and return "
                    "its CSRF token."
                ),
                "security": [
                    {"BrowserSession": []},
                ],
                "responses": {
                    "200": {
                        "description": "Authenticated session information.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["status", "csrf_token"],
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "authenticated",
                                        },
                                        "csrf_token": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "401": {
                        "description": "Authentication required or invalid session.",
                    },
                },
            },
        },
        "/api/applications/{application_id}/monitoring-approval": {
            "patch": {
                "tags": ["Applications"],
                "summary": "Approve or revoke application monitoring",
                "description": (
                    "Update monitoring approval without activating "
                    "Prometheus targets. Requires either a management "
                    "token or an authenticated browser session with "
                    "CSRF validation."
                ),
                "security": [
                    {"ManagementToken": []},
                    {"BrowserSession": [], "CSRFToken": []},
                ],
                "parameters": [
                    {
                        "name": "application_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Registered application identifier.",
                    },
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["approved"],
                                "properties": {
                                    "approved": {"type": "boolean"},
                                },
                            },
                            "example": {"approved": True},
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Monitoring approval updated.",
                    },
                    "400": {"description": "Invalid request body."},
                    "401": {"description": "Authentication required."},
                    "403": {"description": "Authorization or CSRF validation failed."},
                    "404": {"description": "Application not found."},
                },
            },
        },
        "/api/applications": {
            "post": {
                "tags": ["Applications"],
                "summary": "Register an application",
                "description": (
                    "Register an application for monitoring. "
                    "Requires a management token or an authenticated "
                    "browser session with CSRF validation."
                ),
                "security": [
                    {"ManagementToken": []},
                    {"BrowserSession": [], "CSRFToken": []},
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": [
                                    "name",
                                    "environment",
                                    "health_url",
                                ],
                                "properties": {
                                    "name": {"type": "string"},
                                    "environment": {"type": "string"},
                                    "health_url": {
                                        "type": "string",
                                        "format": "uri",
                                    },
                                    "metrics_url": {
                                        "type": "string",
                                        "format": "uri",
                                    },
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "201": {
                        "description": "Application registered successfully.",
                    },
                    "400": {"description": "Invalid application data."},
                    "401": {"description": "Authentication required."},
                    "403": {"description": "Authorization or CSRF validation failed."},
                },
            },
            "get": {
                "tags": ["Applications"],
                "summary": "List registered applications",
                "description": (
                    "Return registered applications without exposing "
                    "their health or metrics endpoint URLs."
                ),
                "responses": {
                    "200": {
                        "description": "Registered applications returned.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": [
                                        "status", "count", "applications"
                                    ],
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "success",
                                        },
                                        "count": {"type": "integer"},
                                        "applications": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "name": {"type": "string"},
                                                    "environment": {
                                                        "type": "string"
                                                    },
                                                    "enabled": {
                                                        "type": "boolean"
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "/api/incidents": {
            "get": {
                "tags": ["Monitoring"],
                "summary": "List monitoring incidents",
                "description": (
                    "Retrieve active and pending Prometheus alerts "
                    "with rule-based or AI-assisted troubleshooting."
                ),
                "responses": {
                    "200": {
                        "description": "Monitoring incidents returned.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": [
                                        "status", "count", "incidents"
                                    ],
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "success",
                                        },
                                        "count": {"type": "integer"},
                                        "incidents": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "additionalProperties": True,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "503": {
                        "description": (
                            "Prometheus alert data is unavailable."
                        ),
                    },
                },
            },
        },
        "/health": {
            "get": {
                "tags": ["Monitoring"],
                "summary": "Check application health",
                "description": (
                    "Return the health status of the CloudOps AI service."
                ),
                "responses": {
                    "200": {
                        "description": "Health information returned successfully.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "additionalProperties": True,
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}
