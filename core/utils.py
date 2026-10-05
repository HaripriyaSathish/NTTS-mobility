from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import FooterSettings, SiteSettings, SMTPSettings


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


def send_html_email(subject, template, context, to_list, reply_to=None, text_template=None):
    smtp, connection = get_smtp()
    html = render_to_string(template, context)
    text = render_to_string(text_template, context) if text_template else strip_tags(html)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
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

def digits_only(phone):
    return "".join(ch for ch in phone or "" if ch.isdigit())


def send_booking_emails(booking):
    smtp, _ = get_smtp()
    site = SiteSettings.load()
    footer = FooterSettings.load()
    phone_digits = digits_only(booking.phone)
    context = {
        "booking": booking,
        "site_name": site.site_name if site else "New Track",
        "footer": footer,
        "call_link": f"tel:+{phone_digits}" if phone_digits else "",
        "whatsapp_link": f"https://wa.me/{phone_digits}" if phone_digits else "",
    }
    # notify the team
    send_html_email(
        subject=f"New {booking.trip_label} booking {booking.reference} – {booking.name} ({booking.vehicle_name})",
        template="emails/booking_admin.html",
        text_template="emails/booking_admin.txt",
        context=context,
        to_list=[smtp.receiver_email],
        reply_to=[booking.email] if booking.email else None,
    )
    # confirmation to the customer
    if booking.email:
        send_html_email(
            subject=f"Booking received {booking.reference} – {context['site_name']}",
            template="emails/booking_customer.html",
            text_template="emails/booking_customer.txt",
            context=context,
            to_list=[booking.email],
        )
