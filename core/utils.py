from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import SMTPSettings


def get_smtp():
    smtp = SMTPSettings.get_solo()
    if not smtp:
        raise ValueError("SMTP settings are not configured in admin.")
    connection = get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=smtp.host,
        port=smtp.port,
        username=smtp.username,
        password=smtp.password,
        use_tls=smtp.use_tls,
        use_ssl=smtp.use_ssl,
        timeout=20,
    )
    return smtp, connection


def send_html_email(subject, template, context, to_list, reply_to=None):
    smtp, connection = get_smtp()
    html = render_to_string(template, context)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html),
        from_email=smtp.from_email,
        to=to_list,
        reply_to=reply_to,
        connection=connection,
    )
    msg.attach_alternative(html, "text/html")
    msg.send()


def send_enquiry_emails(enquiry):
    smtp, _ = get_smtp()
    # notify the NTTS team
    send_html_email(
        subject=f"New enquiry from {enquiry.name}",
        template="emails/admin_notification.html",
        context={"enquiry": enquiry},
        to_list=[smtp.receiver_email],
        reply_to=[enquiry.email],
    )
    # auto-reply to the customer
    send_html_email(
        subject="We received your enquiry - NTTS Mobility",
        template="emails/customer_reply.html",
        context={"enquiry": enquiry},
        to_list=[enquiry.email],
    )

def send_booking_emails(booking):
    smtp, _ = get_smtp()
    # notify the NTTS team
    send_html_email(
        subject=f"New ride booking: {booking.name} ({booking.vehicle_name})",
        template="emails/booking_admin.html",
        context={"booking": booking},
        to_list=[smtp.receiver_email],
        reply_to=[booking.email] if booking.email else None,
    )
    # confirmation to the customer (email is optional in the form)
    if booking.email:
        send_html_email(
            subject="We received your ride request - NTTS Mobility",
            template="emails/booking_customer.html",
            context={"booking": booking},
            to_list=[booking.email],
        )
