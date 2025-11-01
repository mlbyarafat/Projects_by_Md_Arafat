
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
import logging
import csv
import io

logger = logging.getLogger(__name__)

def make_csv_bytes(rows, headers):
    """Create CSV bytes from list of dicts and headers."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for r in rows:
        row = [r.get(h, '') for h in headers]
        writer.writerow(row)
    return buf.getvalue().encode('utf-8')

def send_email(smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str,
               subject: str, body: str, from_email: str, to_email: str,
               attachment_path: Optional[str] = None, use_tls: bool = True,
               html_body: Optional[str] = None, attach_csv_rows: Optional[dict] = None) -> None:
    """Send an email. If html_body provided, it will be included as an alternative part.
       attach_csv_rows: dict with keys {'rows': list_of_dicts, 'headers': list_of_headers, 'filename': 'report.csv'}
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(body or " ")

    if html_body:
        # add HTML alternative
        msg.add_alternative(html_body, subtype='html')

    if attachment_path:
        p = Path(attachment_path)
        with open(p, 'rb') as f:
            data = f.read()
        maintype = 'application'
        subtype = 'octet-stream'
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=p.name)

    if attach_csv_rows:
        try:
            csv_bytes = make_csv_bytes(attach_csv_rows['rows'], attach_csv_rows['headers'])
            fname = attach_csv_rows.get('filename', 'export.csv')
            msg.add_attachment(csv_bytes, maintype='text', subtype='csv', filename=fname)
        except Exception as e:
            logger.exception('Failed to attach CSV rows: %s', e)

    logger.info('Connecting to SMTP %s:%s', smtp_host, smtp_port)
    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        if use_tls:
            server.starttls()
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        server.send_message(msg)
    logger.info('Email sent to %s', to_email)
