import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assisted_test.settings')

application = get_wsgi_application()


# запускам воркер в потоке, который анализирует новые документы из папки new и кладет их в processed
from flight import worker
import threading

threading.Thread(target=worker.run, args=['new', 'processed']).start()