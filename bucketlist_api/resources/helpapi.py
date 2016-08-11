"""Script defined to handle Help API calls."""

from flask_restful import Resource, marshal_with
from bucketlist_api.serializers import help_message_serializer


class HelpAPI(Resource):
    """Provides a help platform for the user. """

    @marshal_with(help_message_serializer)
    def get(self):
        """Handles the get call to the HelpAPI."""
        help_message = {
            "message": "Access the app with url provided",
            "register": {
                "methods": "POST",
                "url": "auth/register",
                "PublicAccess": True,
             },
            "login": {
                "methods": "POST",
                "url": "/auth/login",
                "PublicAccess": True,
              },
            "bucketlists": {
                "methods": "GET, POST, PUT, DELETE",
                "url": ["/bucketlists", "/bucketlists/<int:id>"],
                "PublicAccess": False,
             },
            "items": {
                "methods": "POST, PUT, DELETE",
                "url": ["/bucketlists/<int:id>/items",
                        "/bucketlists/<int:id>/items/<int:item_id>"],
                "PublicAccess": False,
             },
        }
        return help_message
