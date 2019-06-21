from lxml.etree import iterparse, _Element
from lxml import etree


# класс парсера, который умеет итеративно парсить xml и отдавать данные в словаре
class GetterInfo:

    def __init__(self, source_xml):
        self.source = source_xml
        self._context = None
        self._current = None
        self._event = None
        self.data = {}

    # Обработчик для корневого элемента. Из него мы берем дату актуальности запроса
    def handleRoot(self, handle_elem):
        context = etree.iterwalk(handle_elem, events=("end",))
        for event, elem in context:
            if elem == handle_elem:

                self.data['response_time'] = elem.get('ResponseTime')

    # обработчик для тега Flights
    def handleFlights(self, handle_elem):
        if self.data.get('flights_list') is None:
            self.data['flights_list'] = []

        flights = {'flight_list': {}}

        # теги в значениях которых содержаться нужные нам данные
        tags_dict = {
            'Carrier': 'carrier',
            'FlightNumber': 'flight_number',
            'Source': 'source',
            'Destination': 'destination',
            'DepartureTimeStamp': 'departure_timestamp',
            'ArrivalTimeStamp': 'arrival_timestamp',
            'Class': 'class',
            'NumberOfStops': 'number_of_stops',
            'TicketType': 'ticket_type',
        }

        flights['flight_list']['onward'] = []
        flights['flight_list']['return'] = []
        flights['pricing'] = []
        flight = {}

        # идем по закрывающим тегам, и отлавливаем инфу соответсвенно тоже (это позволяет не забирать из вложенных тегов ненужные данные)
        context = etree.iterwalk(handle_elem, events=("end",))

        onward = True
        for event, elem in context:
            if elem.tag in tags_dict.keys():
                flight[tags_dict[elem.tag]] = elem.text

            if elem.tag == 'Flight':
                if onward:
                    flights['flight_list']['onward'].append(flight)
                else:
                    flights['flight_list']['return'].append(flight)
                flight = {}
            if elem.tag == 'OnwardPricedItinerary':
                onward = False

            if elem.tag == 'ServiceCharges':
                price_type = elem.attrib['type']
                price_charge_type = elem.attrib['ChargeType']
                price_value = elem.text
                flights['pricing'].append({
                    'price_type': price_type,
                    'price_charge_type': price_charge_type,
                    'price_value': price_value
                })
            if elem.tag == 'Pricing':
                flights['pricing_currency'] = elem.attrib['currency']

        self.data['flights_list'].append(flights)

    # метод парсера, создает итеративный контекст, и после обработки нужного элемента удаляет его экономя нам память
    def parse(self):
        self._context = etree.iterparse(self.source, events=("start", "end"))
        on_handle = None
        for event, elem in self._context:
            if event == 'start' and on_handle is None:
                handle_method = getattr(self, '{}{}'.format('handle', elem.tag), None)
                if handle_method:
                    on_handle = elem
                    handle_method(elem)
            # очищаем только нужные элементы, чтобы не стереть рутовый элемент.
            elif event == 'end' and on_handle == elem:
                on_handle = None
                elem.clear()
            elif on_handle:
                elem.clear()

        # в конце обрабатываем рутовый элемент
        self.handleRoot(self._context.root)

    def get_data(self):
        return self.data
