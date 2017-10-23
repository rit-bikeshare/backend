from django import forms
from django.contrib import admin
from . import models

@admin.register(models.BikeRack)
class BikeRackAdmin(admin.ModelAdmin):
	# Controls the summary view
	list_display = ('name', 'description', 'lon', 'lat', 'id')
	search_fields = ('name', 'id')
	ordering = ('name',)

	# Controls the add/change pages
	prepopulated_fields = {"id": ("name",)}
	fieldsets = (
		('General', {
			'fields': ('name', 'description') 
		}),
		('Location', {
			'fields': (('lon', 'lat'),)
		}),
		('Advanced', {
			'fields': ('id',)
		})
	)

@admin.register(models.Rental)
class RentalAdmin(admin.ModelAdmin):
	# Controls the summary view
	list_display = ('id', 'renter', 'bike', 'rented_at', 'should_return_at', 'returned_at', 'is_complete', 'is_late')
	search_fields = ('renter__username', 'bike__id')
	ordering = ('rented_at',)

	# Controls the add/change pages
	fieldsets = (
		('General', {
			'fields': ('renter', 'bike') 
		}),
		('Times', {
			'fields': ('rented_at','should_return_at', 'returned_at')
		})
	)

	def get_changeform_initial_data(self, request):
		d = super().get_changeform_initial_data(request)
		start = models.Rental.get_rental_start()
		end = models.Rental.get_rental_end(start)
		d.update({
			'rented_at': start,
			'should_return_at': end
		})

		return d

@admin.register(models.Bike)
class BikeAdmin(admin.ModelAdmin):
	# Controls the summary view
	list_display = ('id', 'is_rented', 'visible')
	search_fields = ('id',)
	ordering = ('id',)

	# Controls the add/change pages
	fieldsets = (
		('General', {
			'fields': ('visible', 'lat', 'lon') 
		}),
		('Advanced', {
			'fields': ('id',)
		})
	)


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
			self.fields['damages'].queryset = models.DamageReport.objects.filter(resolved_by=None, bike=self.instance.bike)

	def save(self, *args, **kwargs):
		# FIXME: 'commit' argument is not handled
		# TODO: Wrap reassignments into transaction
		# NOTE: Previously assigned Foos are silently reset
		instance = super().save(commit=False)
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
			'fields': ('name', 'description') 
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
			'fields': ('damage_type', 'comments')
		}),
		('Resolution', {
			'fields': ('resolved_by',)
		})
	)
