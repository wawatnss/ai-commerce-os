"""
AI Commerce OS - Agents

Standalone, framework-agnostic automation modules. Unlike `apps/api/app/*`
(which are FastAPI services with their own database models), packages under
`agents/` are meant to be pure business logic: given plain data in, they
return plain data out, with no database or web framework dependency. This
makes them trivially unit-testable and reusable from any context (the API,
a CLI script, a background job, ...).
"""
