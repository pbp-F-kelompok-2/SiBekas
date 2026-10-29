"""Small project-level views that are shared by all modules."""

from django.db import DatabaseError, connection
from django.http import JsonResponse


def health_check(request):
    """Report application and database readiness for local or hosted checks."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})
