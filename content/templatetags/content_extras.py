from django import template

register = template.Library()

@register.filter(name='makeminutes')
def makeminutes(value):
	seconds = value % 60
	minutes = value / 60
	return "%02d:%02d" %(minutes,seconds)