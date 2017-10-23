from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

class BikeRack(models.Model):
	id = models.SlugField(primary_key=True, help_text='The ID for this bike rack. This should match the QR code on the rack')	
	name = models.CharField(max_length=50, blank=False, unique=True, help_text='Friendly name of the bike rack such as "Grace Watson Rack"')
	description = models.CharField(max_length=255, blank=False, help_text='Description of where the rack is located')
	lon = models.DecimalField(max_digits=9, decimal_places=6, help_text='Longitude of the bike rack\'s coordinates')
	lat = models.DecimalField(max_digits=9, decimal_places=6, help_text='Latitude of the bike rack\'s coordinates')

	def __str__(self):
		return self.name
	#enddef


class Bike(models.Model):
	id = models.SlugField(primary_key=True, help_text='ID for the bike. This should match the QR code on the bike')
	visible = models.BooleanField(default=True, help_text='Determines if this bike is rentable. Use this instead of deleting bikes')
	bikerack = models.ForeignKey(BikeRack, help_text='The most recent location of the bike.')

	def get_current_rental(self):
		# a bike is rented if the most recent rental started but hasn't completed
		try:
			r = Rental.objects.filter(bike=self).latest('rented_at').first()
			if not r or r.returned_at == None: return None
			return r
		except Exception as e:
			return None
	#enddef

	def is_rented(self):
		return self.get_current_rental() is not None
	#enddef
	is_rented.boolean = True

	def __str__(self):
		return self.id
	#enddef


class Rental(models.Model):
	renter = models.ForeignKey(settings.AUTH_USER_MODEL, help_text='User who rented the bike')
	bike = models.ForeignKey(Bike, help_text='The bike they rented')
	rented_at = models.DateTimeField(help_text='When the rental began')
	should_return_at = models.DateTimeField(help_text='When the renter was supposed to return the bike by')
	returned_at = models.DateTimeField(null=True, blank=True, help_text='When the bike was actually returned')

	@classmethod
	def get_rental_start(cls):
		return timezone.now()
	#enddef

	@classmethod
	def get_rental_end(cls, start, duration=timedelta(1)):
		return start + duration
	#enddef

	def is_complete(self):
		return self.returned_at is not None
	#enddef
	is_complete.boolean = True

	def is_late(self):
		r_date = self.returned_at if self.is_complete() else timezone.now()
		return r_date > self.should_return_at
	#enddef
	is_late.boolean = True

	def __str__(self):
		return str(self.id)

class MaintenanceReport(models.Model):
	bike = models.ForeignKey(Bike, help_text='Bike that is the subject of this report')
	created_at = models.DateTimeField(auto_now_add=True, help_text='When this report was entered')
	comments = models.TextField(help_text='Any additional comments about this bike')


class DamageType(models.Model):
	id = models.SlugField(primary_key=True, help_text='The ID for this damage type')
	name = models.CharField(max_length=50, help_text='Friendly name of this damage, such as "Flat tire"')
	description = models.CharField(max_length=255, help_text='Description of what this damage type means')


	def __str__(self):
		return self.name
	#enddef


class DamageReport(models.Model):
	reporter = models.ForeignKey(settings.AUTH_USER_MODEL, help_text='The user who reported the damage')
	bike = models.ForeignKey(Bike, help_text='The bike that was damaged')
	damage_type = models.ForeignKey(DamageType, help_text='The type of damage done')
	reported_at = models.DateTimeField(auto_now_add=True, help_text='When the damage was reported')
	comments = models.TextField(help_text='Additional comments about the damage')
	resolved_by = models.ForeignKey(MaintenanceReport, blank=True, null=True, help_text='The maintenance report that resolved this damage')

	def __str__(self):
		return '{} - {}'.format(self.bike.id, self.damage_type.name)
	#enddef
