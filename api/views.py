from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils import get_location_and_temperature


class GreetingView(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get(self, request):
        visitor_name = request.query_params.get("visitor_name", "Visitor")
        client_ip = self.get_client_ip(request)
        location, temperature = get_location_and_temperature(client_ip)
        greeting = None
        if location and temperature:
            greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location}"
        # else:
        #     greeting = f"Hello, {visitor_name}!, we couldn't determine your location and temperature."

        data = {"client_ip": client_ip, "location": location, "greeting": greeting}
        return Response(data, status=status.HTTP_200_OK)
