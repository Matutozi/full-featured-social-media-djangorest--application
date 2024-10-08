from rest_framework.response import Response

class BaseResponseView:
    def generate_response(self, status_code, message, data=None, errors=None):
        """Generate a standardized response format."""
        response_data = {
            "status_code": status_code,
            "message": message,
        }
        if data:
            response_data["data"] = data
        if errors:
            response_data["errors"] = errors

        return Response(response_data, status=status_code)
