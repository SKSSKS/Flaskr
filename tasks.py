from __future__ import absolute_import, unicode_literals
from celery import Celery
import pdfkit

app = Celery('tasks', broker='amqp://', backend='amqp://', include=['tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

@app.task
def html_to_pdf():
    return pdfkit.from_url('http://127.0.0.1:5000/', 'blogpost.pdf')
    