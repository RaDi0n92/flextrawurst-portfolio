from __future__ import annotations


class SecurityPolicyMiddleware:
    """Adds a strict policy to the public app without breaking Django's own admin UI."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        is_admin = path.startswith("/admin/")
        is_planner = "/Mein-Gesamtkonstrukt-planer/" in path
        is_replica_redteam = path.endswith("/replica-redteam-22/")
        is_replica_mobile_app = path.endswith("/replica-redteam-22-mobile-app/")
        is_replica_mobile_test = path.endswith("/replica-redteam-22-mobile-test/")

        if is_planner:
            response["Content-Security-Policy"] = (
                "default-src 'none'; img-src data: blob:; style-src 'unsafe-inline'; "
                "script-src 'unsafe-inline' blob:; connect-src 'self'; font-src data:; "
                "object-src 'none'; media-src data: blob:; worker-src blob:; "
                "frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
            )
        elif is_replica_redteam or is_replica_mobile_app:
            frame_ancestors = "'self'" if is_replica_mobile_app else "'none'"
            response["Content-Security-Policy"] = (
                "default-src 'none'; img-src data: blob:; style-src 'unsafe-inline'; "
                "script-src 'unsafe-inline'; connect-src 'none'; font-src data:; "
                "object-src 'none'; media-src data: blob:; frame-ancestors " + frame_ancestors + "; "
                "base-uri 'none'; form-action 'none'"
            )
        elif is_replica_mobile_test:
            response["Content-Security-Policy"] = (
                "default-src 'none'; style-src 'unsafe-inline'; frame-src 'self'; "
                "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
            )
        elif is_admin:
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "img-src 'self' data:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline'; "
                "font-src 'self'; connect-src 'self'; "
                "frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
            )
        else:
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "img-src 'self' data:; "
                "style-src 'self'; "
                "script-src 'self'; "
                "font-src 'self'; connect-src 'self'; "
                "object-src 'none'; media-src 'self'; "
                "frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
            )

        response["Permissions-Policy"] = (
            "accelerometer=(), autoplay=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Resource-Policy"] = "same-origin"
        response["X-Permitted-Cross-Domain-Policies"] = "none"

        private_prefixes = ("/admin/", "/de/inbox/", "/en/inbox/", "/es/inbox/", "/de/me/", "/en/me/", "/es/me/")
        if path.startswith(private_prefixes):
            response["Cache-Control"] = "no-store, private"

        return response
