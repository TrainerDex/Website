# -*- coding: utf-8 -*-
from ajax_select import register, LookupChannel
from cities.models import Country, Region, Subregion, City, District

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

@register('subregions')
class SubregionLookup(LookupChannel):
	
	model = Subregion
	
	def get_query(self, q, request):
		return self.model.objects.filter(name__icontains=q)
	
	def format_item_display(self, item):
		return "<span class='tag'>{}, {}</span>".format(item, item.region)

@register('cities')
class CityLookup(LookupChannel):
	
	model = City
	
	def get_query(self, q, request):
		return self.model.objects.filter(name__icontains=q)
	
	def format_item_display(self, item):
		try:
			return "<span class='tag'>{}, {}, {}</span>".format(item, item.subregion, item.region.code)
		except AttributeError:
			return "<span class='tag'>{}</span>".format(item.name)

@register('districts')
class DistrictLookup(LookupChannel):
	
	model = District
	
	def get_query(self, q, request):
		return self.model.objects.filter(name__icontains=q)
	
	def format_item_display(self, item):
		try:
			return "<span class='tag'>{}, {}, {}</span>".format(item, item.city, item.region.code)
		except AttributeError:
			return "<span class='tag'>{}</span>".format(item, item.city)
