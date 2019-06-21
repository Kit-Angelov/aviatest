from rest_framework import serializers
from flight import models


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Flight
        fields = '__all__'


# простая сериализация данных из DRF
class ItinerarySerializer(serializers.ModelSerializer):
    flights = FlightSerializer(many=True)

    class Meta:
        model = models.Itinerary
        fields = ('relevance_date', 'source', 'destination',
                  'departure_time', 'arrival_time', 'duration',
                  'price_adult', 'price_child', 'price_infant', 'flights')