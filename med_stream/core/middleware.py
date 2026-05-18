import logging
import time

from django.db import connection
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger("hospital_media_system")


class RequestTimingMiddleware(MiddlewareMixin):
    """
    Measures request execution timing and template render timing.
    Logs:
    - request total time (ms)
    - db query count and cumulative db time (ms, when available)
    - template render time (ms) for TemplateResponse
    """

    def __call__(self, request):
        request_start = time.perf_counter()
        db_queries_before = len(connection.queries)

        response = self.get_response(request)

        request_elapsed_ms = (time.perf_counter() - request_start) * 1000
        db_queries_after = len(connection.queries)
        db_query_count = db_queries_after - db_queries_before

        db_time_ms = 0.0
        if db_query_count > 0:
            # Django stores query duration in seconds as string in "time".
            recent_queries = connection.queries[db_queries_before:db_queries_after]
            for query in recent_queries:
                try:
                    db_time_ms += float(query.get("time", 0)) * 1000
                except (TypeError, ValueError):
                    continue

        # Expose timing in response headers for quick browser inspection.
        response["X-Response-Time-ms"] = f"{request_elapsed_ms:.2f}"
        response["X-DB-Query-Count"] = str(db_query_count)
        response["X-DB-Time-ms"] = f"{db_time_ms:.2f}"
        response["Server-Timing"] = (
            f"app;dur={request_elapsed_ms:.2f},db;dur={db_time_ms:.2f}"
        )

        logger.info(
            "PERF path=%s method=%s status=%s total_ms=%.2f db_queries=%s db_ms=%.2f",
            request.path,
            request.method,
            getattr(response, "status_code", "NA"),
            request_elapsed_ms,
            db_query_count,
            db_time_ms,
        )

        # Capture template render timing for TemplateResponse-like objects.
        if hasattr(response, "add_post_render_callback"):
            render_start = time.perf_counter()

            def _log_template_render_time(rendered_response):
                render_elapsed_ms = (time.perf_counter() - render_start) * 1000
                rendered_response["X-Template-Render-ms"] = f"{render_elapsed_ms:.2f}"

                existing_server_timing = rendered_response.get("Server-Timing", "")
                if existing_server_timing:
                    rendered_response["Server-Timing"] = (
                        f"{existing_server_timing},tpl;dur={render_elapsed_ms:.2f}"
                    )
                else:
                    rendered_response["Server-Timing"] = f"tpl;dur={render_elapsed_ms:.2f}"

                logger.info(
                    "PERF_TEMPLATE path=%s render_ms=%.2f",
                    request.path,
                    render_elapsed_ms,
                )
                return rendered_response

            response.add_post_render_callback(_log_template_render_time)

        return response
