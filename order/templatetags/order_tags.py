from django import template

from sibekas.utils import format_rupiah

register = template.Library()
register.filter("rupiah", format_rupiah)
