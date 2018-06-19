# -*- coding: utf-8 -*-
from ajax_select import register, LookupChannel
from cities.models import Country, Region

@register('countries')
class CountryLookup(LookupChannel):
	
	model = Country
	
	def get_query(self, q, request):
		return self.model.objects.filter(name__icontains=q)
	
	def format_item_display(self, item):
		return "<span class='tag'>{}</span>".format(item.name)

@register('regions')
class RegionLookup(LookupChannel):
	
	model = Region
	
	def get_query(self, q, request):
		return self.model.objects.filter(name__icontains=q)
	
	def format_item_display(self, item):
		return "<span class='tag'>{}, {}</span>".format(item.name, item.country.code)

