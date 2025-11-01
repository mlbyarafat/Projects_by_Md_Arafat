
# Make running this file from inside the `src/` folder work:
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

"""Entry point for the Email & Excel Automation tool.

Example:
    python -m src.main --input sample_data/report.xlsx
    python -m src.main --input sample_data/report.xlsx --daily --hour 9 --minute 30
"""
import argparse
import os
from dotenv import load_dotenv
from pathlib import Path
from src.excel_utils import read_table, compute_summary, write_summary
from src.emailer import send_email
from src.scheduler import run_daily
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('email_excel_automation')

def render_html_template(template_path: str, summary: dict) -> str:
    # VERY simple templating: replace a loop placeholder with rows
    tpl = Path(template_path).read_text(encoding='utf-8')
    # build rows html
    rows_html = []
    for k, v in summary.items():
        rows_html.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
    body = tpl.replace('{% for k, v in summary.items() %}', '').replace('{% endfor %}', '')
    # replace the table body markers directly
    body = body.replace('<tbody>', '<tbody>\n' + "\n".join(rows_html))
    return body

def job(input_path: str, numeric_fields: list, attach: bool, html: bool, attach_csv: bool):
    logger.info('Job started for %s', input_path)
    rows = read_table(input_path)
    summary = compute_summary(rows, numeric_fields)
    # write summary back to same file (overwrites existing Summary sheet)
    out = write_summary(input_path, summary)
    # compose email body (plain text)
    body_lines = [f"{k}: {v}" for k, v in summary.items()]
    body = "\n".join(body_lines)
    html_body = None
    if html:
        tpl_path = Path(os.path.dirname(os.path.dirname(__file__))) / 'templates' / 'report_template.html'
        html_body = render_html_template(str(tpl_path), summary)

    # send email if configured
    smtp_host = os.getenv('SMTP_HOST')
    if smtp_host:
        try:
            send_email(
                smtp_host=smtp_host,
                smtp_port=int(os.getenv('SMTP_PORT', '587')),
                smtp_user=os.getenv('SMTP_USER'),
                smtp_password=os.getenv('SMTP_PASSWORD'),
                subject=os.getenv('SUBJECT', 'Excel Summary Report'),
                body=body,
                from_email=os.getenv('FROM_EMAIL'),
                to_email=os.getenv('TO_EMAIL'),
                attachment_path=input_path if attach else None,
                use_tls=os.getenv('USE_TLS', 'True').lower() in ('1','true','yes'),
                html_body=html_body,
                attach_csv_rows={'rows': rows, 'headers': list(rows[0].keys()) if rows else [], 'filename': 'report_export.csv'} if attach_csv else None
            )
            logger.info('Email sent successfully.')
        except Exception as e:
            logger.exception('Failed to send email: %s', e)
    else:
        logger.info('SMTP not configured. Skipping email send.')
    logger.info('Summary written to: %s', out)
    logger.info('Summary content:\n%s', body)

def main():
    parser = argparse.ArgumentParser(description='Email & Excel Automation Tool')
    parser.add_argument('--input', required=True, help='Path to Excel file')
    parser.add_argument('--fields', nargs='*', default=[], help='Numeric fields to summarize (column headers)')
    parser.add_argument('--attach', action='store_true', help='Attach the input file to email')
    parser.add_argument('--daily', action='store_true', help='Run daily using built-in scheduler')
    parser.add_argument('--hour', type=int, default=8, help='Hour for daily schedule (0-23)')
    parser.add_argument('--minute', type=int, default=0, help='Minute for daily schedule (0-59)')
    parser.add_argument('--html', action='store_true', help='Send HTML formatted email (uses templates/report_template.html)')
    parser.add_argument('--attach-csv', action='store_true', help='Attach CSV export of the sheet to the email')
    args = parser.parse_args()

    # load environment
    root_env = Path(__file__).resolve().parents[1] / ".env"
    if root_env.exists():
        load_dotenv(dotenv_path=root_env)   

    input_path = args.input
    if not Path(input_path).exists():
        logger.error('Input file not found: %s', input_path)
        return

    if args.daily:
        logger.info('Starting scheduler...')
        run_daily(lambda: job(input_path, args.fields, args.attach, args.html, args.attach_csv),
                  hour=args.hour, minute=args.minute)
    else:
        job(input_path, args.fields, args.attach, args.html, args.attach_csv)

if __name__ == '__main__':
    main()
