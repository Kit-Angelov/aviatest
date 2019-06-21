from .models import Itinerary, Flight


# получение всех вариантов перелета по source и dest
def get_flights_info(source, dest):
    relevance_dates = Itinerary.objects.filter(source=source, destination=dest).order_by('-relevance_date').values_list('relevance_date', flat=True)
    try:
        relevance_date = relevance_dates[0]
        itineraries = Itinerary.objects.filter(source=source, destination=dest, relevance_date=relevance_date)
        return itineraries
    except:
        return


# получение наиболее дорогого варианта перелета по source и dest
def get_most_expensive(source, dest):
    itineraries = get_flights_info(source, dest)
    if itineraries:
        most_expensive_qs = itineraries.order_by('-price_adult').exclude(price_adult=None)
        most_expensive = most_expensive_qs[0]
        return most_expensive
    else:
        return


# получение наиболее дешевого варианта перелета по source и dest
def get_cheapest(source, dest):
    itineraries = get_flights_info(source, dest)
    if itineraries:
        most_cheapest_qs = itineraries.order_by('price_adult').exclude(price_adult=None)
        most_cheapest = most_cheapest_qs[0]
        return most_cheapest
    else:
        return


# получение наиболее быстрого варианта перелета по source и dest
def get_fastest(source, dest):
    itineraries = get_flights_info(source, dest)
    if itineraries:
        fastest_itinerary_qs = itineraries.order_by('duration').exclude(duration=None).exclude(duration=0)
        fastest_itinerary = fastest_itinerary_qs[0]
        return fastest_itinerary
    return


# получение наиболее долгого варианта перелета по source и dest
def get_longest(source, dest):
    itineraries = get_flights_info(source, dest)
    if itineraries:
        longest_itinerary_qs = itineraries.order_by('-duration').exclude(duration=None)
        longest_itinerary = longest_itinerary_qs[0]
        return longest_itinerary
    return


# получение наиболее оптимального варианта перелета по source и dest
# оптимальный вариант - самый быстрый, а потом из самых быстрых самый дешевый
def get_most_optimal(source, dest):
    itineraries = get_flights_info(source, dest)
    if itineraries:
        optimal_itinerary_qs = itineraries.order_by('duration').exclude(duration=None).exclude(duration=0).order_by('price_adult').exclude(price_adult=None)
        optimal_itinerary = optimal_itinerary_qs[0]
        return optimal_itinerary
    return


# получение разницы между двумя последними запросами перелета по source и dest
# получилось громоздко и не очень информативно
def get_diff(source, dest):
    relevance_dates = Itinerary.objects.filter(source=source, destination=dest).order_by('-relevance_date').values_list('relevance_date', flat=True).distinct()
    diff = {}
    try:
        relevance_date = relevance_dates[0]
        prev_relevance_date = relevance_dates[1]
        actual_itineraries = Itinerary.objects.filter(source=source, destination=dest, relevance_date=relevance_date)
        prev_itineraries = Itinerary.objects.filter(source=source, destination=dest, relevance_date=prev_relevance_date)
    except:
        return diff

    zipped_itineraties = zip(actual_itineraries, prev_itineraries)
    for item in zipped_itineraties:
        actual_itinerary = item[0]
        prev_itinerary = item[1]
        # проверяем разницу по основным полям перелета
        departure_time_diff = actual_itinerary.departure_time == prev_itinerary.departure_time
        arrival_time_diff = actual_itinerary.arrival_time == prev_itinerary.arrival_time
        duration_diff = actual_itinerary.duration == prev_itinerary.duration
        price_adult_diff = actual_itinerary.price_adult == prev_itinerary.price_adult
        price_child_diff = actual_itinerary.price_child == prev_itinerary.price_child
        price_infant_diff = actual_itinerary.price_infant == prev_itinerary.price_infant

        actual_flights = actual_itinerary.flights.all()
        prev_flights = prev_itinerary.flights.all()

        # проверяем разницу по маршрутам onward. Отличие ищем в номере рейса
        actual_flights_onward = actual_flights.filter(onward=True)
        prev_flights_onward = prev_flights.filter(onward=True)
        actual_fligts_onward_route = list(actual_flights_onward.values_list('flight_number', flat=True))
        prev_fligts_onward_route = list(prev_flights_onward.values_list('flight_number', flat=True))
        if actual_fligts_onward_route != prev_fligts_onward_route:
            onward_diff = False
        else:
            onward_diff = True

        # проверяем разницу по маршрутам return. Отличие ищем в номере рейса
        actual_flights_return = actual_flights.filter(onward=False)
        prev_flights_return = prev_flights.filter(onward=False)
        actual_flights_return_route = list(actual_flights_return.values_list('flight_number', flat=True))
        prev_flights_return_route = list(prev_flights_return.values_list('flight_number', flat=True))
        if actual_flights_return_route != prev_flights_return_route:
            return_diff = False
        else:
            return_diff = True
        # собираем все данные в словаь и отдаем. Костыльно конечно же.
        diff[actual_itinerary.id] = {}
        if departure_time_diff: diff[actual_itinerary.id]['departure_time'] = departure_time_diff
        if arrival_time_diff: diff[actual_itinerary.id]['arrival_time'] = departure_time_diff
        if duration_diff: diff[actual_itinerary.id]['duration'] = departure_time_diff
        if price_adult_diff: diff[actual_itinerary.id]['price_adult'] = departure_time_diff
        if price_child_diff: diff[actual_itinerary.id]['price_child'] = departure_time_diff
        if price_infant_diff: diff[actual_itinerary.id]['price_infant'] = departure_time_diff
        if onward_diff: diff[actual_itinerary.id]['onward'] = departure_time_diff
        if return_diff: diff[actual_itinerary.id]['return'] = departure_time_diff

    return diff

