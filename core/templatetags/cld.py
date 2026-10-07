from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def cld(image, width=None):
    """Cloudinary URL with auto format/quality: {{ obj.image|cld:800 }}"""
    if not image:
        return ""
    options = {"fetch_format": "auto", "quality": "auto", "secure": True}
    if width:
        options.update(width=int(width), crop="limit")
    return image.build_url(**options)


@register.filter
def cld_car(image, width=None):
    """Car photo on a plain white background, whatever background the uploaded photo has:
    Cloudinary's AI removes the original background, then it is filled with white.
    {{ ride.image|cld_car:600 }}"""
    if not image:
        return ""
    resize = {"background": "white", "fetch_format": "auto", "quality": "auto"}
    if width:
        resize.update(width=int(width), crop="limit")
    return image.build_url(transformation=[{"effect": "background_removal"}, resize], secure=True)


@register.filter
def bold(text):
    """Words wrapped in **double stars** in admin show in bold: {{ slide.description|bold }}"""
    parts = str(text or "").split("**")
    if len(parts) % 2 == 0:
        # An unclosed ** is kept as plain text
        parts[-2:] = [parts[-2] + "**" + parts[-1]]
    return mark_safe("".join(
        f"<strong>{escape(part)}</strong>" if i % 2 else escape(part)
        for i, part in enumerate(parts)
    ))
