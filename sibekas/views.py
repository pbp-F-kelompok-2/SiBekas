"""Small project-level views that are shared by all modules."""

from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Report application and database readiness for local or hosted checks."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return JsonResponse({"status": "ok", "database": "ok"})
