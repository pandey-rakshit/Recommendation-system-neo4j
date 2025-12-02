import traceback
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed
from app.exceptions.api_error import APIError


def register_error_handlers(app):

    @app.errorhandler(Exception)
    def handle_exception(e):

        # ---------------------------
        # 1. APIError (custom errors)
        # ---------------------------
        if isinstance(e, APIError):
            return jsonify({
                "success": False,
                "error": str(e),
                "type": "APIError",
                "path": request.path
            }), e.status_code


        # ---------------------------
        # 2. Not Found (404)
        # Avoid huge stacktrace log spam
        # ---------------------------
        if isinstance(e, NotFound):
            return jsonify({
                "success": False,
                "error": "Route not found",
                "type": "NotFound",
                "path": request.path
            }), 404


        # ---------------------------
        # 3. Method Not Allowed (405)
        # ---------------------------
        if isinstance(e, MethodNotAllowed):
            return jsonify({
                "success": False,
                "error": "Method not allowed",
                "type": "MethodNotAllowed",
                "path": request.path
            }), 405


        # ---------------------------
        # 4. Common simple exceptions
        # ---------------------------
        if isinstance(e, (ValueError, KeyError, TypeError)):
            return jsonify({
                "success": False,
                "error": str(e),
                "type": e.__class__.__name__,
                "path": request.path
            }), 400


        # ---------------------------
        # 5. Werkzeug HTTP exceptions (has .code)
        # ---------------------------
        if hasattr(e, "code"):
            return jsonify({
                "success": False,
                "error": str(e),
                "type": e.__class__.__name__,
                "path": request.path
            }), e.code


        # ---------------------------
        # 6. UNKNOWN ERRORS → 500
        # Show traceback ONLY for real internal server errors
        # ---------------------------
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": "An internal server error occurred.",
            "type": e.__class__.__name__,
            "path": request.path
        }), 500

    return app
