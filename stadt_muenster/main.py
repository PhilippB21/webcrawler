import requests
from bs4 import BeautifulSoup
import smtplib, ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

search_date_start = "01.06.2021"
search_date_end = "16.06.2021"
appointment = True

smtp_server = "smtp.example.de"
smtp_server_port = 465  # For starttls
sender_email = "peter@example.de"
sender_email_password = "geh_heim"
receiver_email = ["peter@example.de"]

message = MIMEMultipart("alternative")
message["Subject"] = "Termin Kinderreisepass"

logging.basicConfig(level=logging.INFO)

# Start Session and crawl entry page to get cookie
s = requests.Session()
r = s.get('https://termine.stadt-muenster.de/select2?md=1')

# Search URL for "Bürgerbüro Mitte" and "Kinderreisepass"
url = 'https://termine.stadt-muenster.de/suggest?loc=120&mdt=0&cnc-1046=1&filter_date_from=%s&filter_date_to=%s&suggest_filter=Filtern' % (search_date_start,search_date_end)
r = s.get(url)

soup = BeautifulSoup(r.text, 'html.parser')

# Check Page Content if Header exists
for i in soup.find_all('h1'):
    if "Kein freier Termin" in i.get_text():
        appointment = False
        logging.debug(i)

# If Appointment found then send html site content via mail
if not appointment:
    text = "Leider kein Termin verfügbar bis %s" % (search_date_end)
    message.attach(MIMEText(text, "plain"))
    logging.info('No Appointment found')
else:
    message.attach(MIMEText(r.text, "html"))
    logging.info('Appointment found')

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, smtp_server_port, context=context) as server:
    server.login(sender_email, sender_email_password)
    server.sendmail(sender_email, receiver_email, message.as_string())

logging.info('Send Mail')
