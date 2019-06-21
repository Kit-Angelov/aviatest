from django.http import JsonResponse
from flight import core
from .serializers import ItinerarySerializer


# обработчик запроса всех перелетов по source и dest
def Flights(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'not allowed'}, status=405)
    source = request.GET.get('source')
    dest = request.GET.get('dest')
    if source and dest:
        flights = core.get_flights_info(source, dest)
        serializer = ItinerarySerializer(flights, many=True)
        return JsonResponse({'result': list(serializer.data)})
    else:
        return JsonResponse({'invalid params'}, 400)


# обработчик запроса САМЫХ-САМЫХ перелетов по source и dest
def Most(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'not allowed'}, status=405)
    source = request.GET.get('source')
    dest = request.GET.get('dest')
    if source and dest:
        flights_data = {}
        cheapest = core.get_cheapest(source, dest)
        expensive = core.get_most_expensive(source, dest)
        longest = core.get_longest(source, dest)
        fastest = core.get_fastest(source, dest)
        flights_data['cheapest'] = ItinerarySerializer(cheapest, many=False).data
        flights_data['expensive'] = ItinerarySerializer(expensive, many=False).data
        flights_data['longest'] = ItinerarySerializer(longest, many=False).data
        flights_data['fastest'] = ItinerarySerializer(fastest, many=False).data

        return JsonResponse({'result': flights_data})
    else:
        return JsonResponse({'invalid params'}, 400)


# обработчик запроса на разницу между последними запросами по source и dest
def Diff(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'not allowed'}, status=405)
    source = request.GET.get('source')
    dest = request.GET.get('dest')
    if source and dest:
        diff = core.get_diff(source, dest)
        return JsonResponse(diff)
    else:
        return JsonResponse({'invalid params'}, 400)
