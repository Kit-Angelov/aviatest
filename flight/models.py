from django.db import models


class Flight(models.Model):
    onward = models.BooleanField(default=True)
    carrier = models.CharField(max_length=255, null=True, blank=True)
    flight_number = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    destination = models.CharField(max_length=255, null=True, blank=True)
    departure_timestamp = models.CharField(max_length=255, null=True, blank=True)
    arrival_timestamp = models.CharField(max_length=255, null=True, blank=True)
    flight_class = models.CharField(max_length=10, null=True, blank=True)
    number_of_stops = models.IntegerField(null=True, blank=True)
    ticket_type = models.CharField(max_length=10, null=True, blank=True)
    warning_text = models.TextField(null=True, blank=True)
    itinerary = models.ForeignKey('Itinerary', on_delete=models.CASCADE, null=True, blank=True, related_name='flights')

    def __str__(self):
        return "from {} to ".format(self.source, self.destination)


class Itinerary(models.Model):
    relevance_date = models.DateTimeField()
    source = models.CharField(max_length=255, null=True, blank=True)
    destination = models.CharField(max_length=255, null=True, blank=True)
    departure_timestamp = models.CharField(max_length=255, null=True, blank=True)
    arrival_timestamp = models.CharField(max_length=255, null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    price_adult = models.FloatField(null=True, blank=True)
    price_child = models.FloatField(null=True, blank=True)
    price_infant = models.FloatField(null=True, blank=True)

    def _str__(self):
        return "rel_date {} from {} to {}".format(self.relevance_date.strftime("%Y-%m-%d %H:%M:%S"),
                                                  self.source,
                                                  self.destination)
