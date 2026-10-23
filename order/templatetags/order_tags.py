from django import template

from cart.services import format_rupiah

register = template.Library()
register.filter("rupiah", format_rupiah)
