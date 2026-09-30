from django import template

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
