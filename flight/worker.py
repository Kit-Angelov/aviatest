import os
from shutil import move
from django.conf import settings
from .parser import GetterInfo
from .models import Itinerary, Flight
import time
import datetime


# функция записывающая в бд данные, приходящие из файла. Получилось громоздко и хардкодно, далее стоит ее отрефакторить
def write_data(data):
    response_time_str = data.get('response_time', None)
    if response_time_str:
        response_time = datetime.datetime.strptime(response_time_str, '%d-%m-%Y %H:%M:%S')
    flights_list = data.get('flights_list', [])
    for flight_info in flights_list:
        flights = flight_info.get('flight_list')

        source_dest = [None, None]
        departure_arrival = [None, None]
        flight_items = []

        # тут есть повторения извлечения данных, отличия лишь в флаге onward. Пока оставил для наглядности. В дальнейшем нужно вынести в отдельную функцию
        onward_flights = flights.get('onward', None)
        if onward_flights:
            for flight in onward_flights:
                carrier = flight.get('carrier', '')
                flight_number = flight.get('flight_number', 0)
                source = flight.get('source', '')
                destination = flight.get('destination', '')
                departure_timestamp = flight.get('departure_timestamp', '')
                arrival_timestamp = flight.get('arrival_timestamp', '')
                flight_class = flight.get('class', '')
                number_of_stops = flight.get('number_of_stops', 0)
                warning_text = flight.get('warning_text', '')
                ticket_type = flight.get('ticket_type', '')

                if not source_dest[0]:
                    source_dest[0] = source
                source_dest[1] = destination
                if not departure_arrival[0]:
                    departure_arrival[0] = departure_timestamp
                departure_arrival[1] = arrival_timestamp

                new_flight = Flight(
                    onward=True,
                    carrier=carrier,
                    flight_number=int(flight_number),
                    source=source,
                    destination=destination,
                    departure_timestamp=departure_timestamp,
                    arrival_timestamp=arrival_timestamp,
                    flight_class=flight_class,
                    number_of_stops=number_of_stops,
                    warning_text=warning_text,
                    ticket_type=ticket_type
                )
                flight_items.append(new_flight)

        return_flights = flights.get('return', None)
        if return_flights:
            for flight in return_flights:
                carrier = flight.get('carrier', '')
                flight_number = flight.get('flight_number', 0)
                source = flight.get('source', '')
                destination = flight.get('destination', '')
                departure_timestamp = flight.get('departure_timestamp', '')
                arrival_timestamp = flight.get('arrival_timestamp', '')
                flight_class = flight.get('class', '')
                number_of_stops = flight.get('number_of_stops', 0)
                warning_text = flight.get('warning_text', '')
                ticket_type = flight.get('ticket_type', '')

                new_flight = Flight(
                    onward=False,
                    carrier=carrier,
                    flight_number=int(flight_number),
                    source=source,
                    destination=destination,
                    departure_timestamp=departure_timestamp,
                    arrival_timestamp=arrival_timestamp,
                    flight_class=flight_class,
                    number_of_stops=number_of_stops,
                    warning_text=warning_text,
                    ticket_type=ticket_type
                )
                flight_items.append(new_flight)

        if departure_arrival[0]:
            departure_time = datetime.datetime.strptime(departure_arrival[0], '%Y-%m-%dT%H%M')
        if departure_arrival[1]:
            arrival_time = datetime.datetime.strptime(departure_arrival[1], '%Y-%m-%dT%H%M')
        if departure_arrival[0] and departure_arrival[1]:
            duration = (arrival_time - departure_time).seconds

        # создаем новый обьект перелета, которому потом приписываем маршруты onward и return
        new_itinerary = Itinerary(
            relevance_date=response_time,
            source=source_dest[0],
            destination=source_dest[1],
            departure_timestamp=departure_arrival[0],
            arrival_timestamp=departure_arrival[1],
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration=duration
        )

        # цены берем только TotalAmount и добавляем в обьект перелета
        pricing = flight_info.get('pricing', [])
        for price in pricing:
            price_type = price.get('price_type')
            price_charge_type = price.get('price_charge_type')
            price_value = price.get('price_value')
            if price_charge_type == 'TotalAmount':
                if price_type == 'SingleAdult' and price_value:
                    new_itinerary.price_adult = float(price_value)
                elif price_type == 'SingleChild' and price_value:
                    new_itinerary.price_child = float(price_value)
                elif price_type == 'SingleInfant' and price_value:
                    new_itinerary.price_infant = float(price_value)

        new_itinerary.save()
        for flight_item in flight_items:
            flight_item.itinerary = new_itinerary
            flight_item.save()


# функция проходит по директории, запускает аназатор и кладет файл в директорию обработанных файлов
def walk_a_dir(dir_to_new_files, dir_to_processed_files):
    path_to_new_files = os.path.join(settings.MEDIA_ROOT, dir_to_new_files)
    path_to_processed_files = os.path.join(settings.MEDIA_ROOT, dir_to_processed_files)
    if not os.path.exists(path_to_processed_files):
        os.mkdir(path_to_processed_files)

    if not os.path.exists(path_to_new_files):
        return

    for dirpath, _, filenames in os.walk(path_to_new_files):
        for filename in filenames:
            f_path = os.path.join(dirpath, filename)
            f_name, ext = os.path.splitext(f_path)
            if ext != '.xml':
                continue
            # инициализация анализатора и его запуск на файле
            getter_info = GetterInfo(f_path)
            getter_info.parse()
            parsed_data = getter_info.get_data()
            # после получеия данных из файла записываем их в бд
            write_data(parsed_data)

            processed_file_path = os.path.join(path_to_processed_files, filename)
            # переносим файл в директорию обработанных документов
            move(f_path, processed_file_path)


# точка входа в воркер анализа документа
def run(dir_to_new_files, dir_to_processed_files):
    while True:
        # проходим по директории и анализируем новые файлы
        walk_a_dir(dir_to_new_files, dir_to_processed_files)
        time.sleep(15)
