from constance import config
from django import forms
from django.contrib.gis import admin
from django.contrib.gis.geos import Point

from django.utils.timezone import now

from . import models

class DynamicStartMixin(admin.OSMGeoAdmin):
	def get_map_widget(self, *args, **kwargs):
		map = super().get_map_widget(*args, **kwargs)
		# OSM uses 3857 encoding while most humans use lat/lng, so convert it automatically
		pnt = Point(config.ADMIN_DEFAULT_LON, config.ADMIN_DEFAULT_LAT, srid=4326)
		pnt.transform(3857)
		map.params['default_lon'] = pnt.x
		map.params['default_lat'] = pnt.y
		map.params['default_zoom'] = config.ADMIN_DEFAULT_ZOOM
		return map
#endclass

@admin.register(models.BikeRack)
class BikeRackAdmin(DynamicStartMixin, admin.OSMGeoAdmin):
	# Controls the summary view
	list_display = ('name', 'description', 'id')
	search_fields = ('name', 'id')
	ordering = ('name',)

	# Controls the add/change pages
	prepopulated_fields = {"id": ("name",)}
	fieldsets = (
		('General', {
			'fields': ('name', 'description') 
		}),
		('Location', {
			'fields': (('location', 'check_in_area'),)
		}),
		('Advanced', {
			'fields': ('id',)
		})
	)

@admin.register(models.BikeLock)
class BikeLockAdmin(admin.ModelAdmin):
	pass

@admin.register(models.Rental)
class RentalAdmin(admin.ModelAdmin):
	# Controls the summary view
	list_display = ('id', 'renter', 'bike', 'rented_at', 'returned_at', 'is_complete', 'is_late')
	search_fields = ('renter__username', 'bike__id')
	ordering = ('rented_at',)

	# Controls the add/change pages
	fieldsets = (
		('General', {
			'fields': ('renter', 'bike') 
		}),
		('Times', {
			'fields': ('rented_at', 'returned_at')
		})
	)

@admin.register(models.Bike)
class BikeAdmin(DynamicStartMixin, admin.OSMGeoAdmin):
	# Controls the summary view
	list_display = ('id', 'is_rented', 'visible')
	search_fields = ('id',)
	ordering = ('id',)

	# Controls the add/change pages
	fieldsets = (
		('General', {
			'fields': ('visible', 'location', 'lock') 
		}),
		('Advanced', {
			'fields': ('id', 'current_rental', 'previous_rental')
		})
	)

	def get_readonly_fields(self, request, obj=None):
		ro = super().get_readonly_fields(request, obj)
		if obj is not None: ro += ('id',)
		return ro


class MaintenanceReportForm(forms.ModelForm):
	class Meta:
		model = models.MaintenanceReport
		exclude = []

	# Create a field to allow selecting of damages
	# The actual query will be constructed dynamically
	damages = forms.ModelMultipleChoiceField(queryset=models.DamageReport.objects.none())

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance:
			self.fields['damages'].queryset = models.DamageReport.objects.filter(resolved_by=None)

	def save(self, *args, **kwargs):
		# FIXME: 'commit' argument is not handled
		# TODO: Wrap reassignments into transaction
		# NOTE: Previously assigned Foos are silently reset
		instance = super().save(commit=False)
		instance.save()
		self.cleaned_data['damages'].update(resolved_by=instance)
		return instance


@admin.register(models.MaintenanceReport)
class MaintenanceReportAdmin(admin.ModelAdmin):
	# Controls the summary view
	list_display = ('id', 'bike', 'created_at')
	search_fields = ('bike', 'comments')
	ordering = ('-id',)

	# Controls the add/change pages
	form = MaintenanceReportForm
	fieldsets = (
		('General', {
			'fields': ('bike',) 
		}),
		('Maintenance', {
			'fields': ('damages', 'comments',)
		})
	)

@admin.register(models.DamageType)
class DamageTypeAdmin(admin.ModelAdmin):
	# Controls the summary view
	list_display = ('id', 'name', 'description')
	search_fields = ('name', 'id')
	ordering = ('name',)

	# Controls the add/change pages
	prepopulated_fields = {"id": ("name",)}
	fieldsets = (
		('General', {
			'fields': ('name', 'description', 'force_critical', 'rider_selectable') 
		}),
		('Advanced', {
			'fields': ('id',)
		})
	)

@admin.register(models.DamageReport)
class DamageReportAdmin(admin.ModelAdmin):
	# Controls the summary view
	list_display = ('id', 'bike', 'damage_type', 'reporter')
	search_fields = ('bike', 'damage_type')
	ordering = ('-id',)

	# Controls the add/change pages
	fieldsets = (
		('General', {
			'fields': ('reporter', 'bike') 
		}),
		('Damage', {
			'fields': ('damage_type', 'critical', 'comments')
		}),
		('Resolution', {
			'fields': ('resolved_by',)
		})
	)
