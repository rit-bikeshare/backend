from django.conf import settings
from django.contrib.gis.db import models
from django.utils import timezone
from datetime import timedelta

from constance import config

class BikeRack(models.Model):
	id = models.SlugField(primary_key=True, help_text='The ID for this bike rack. This should match the QR code on the rack')	
	name = models.CharField(max_length=50, blank=False, unique=True, help_text='Friendly name of the bike rack such as "Grace Watson Rack"')
	description = models.CharField(max_length=255, blank=False, help_text='Description of where the rack is located')
	location = models.PointField(help_text='Location of the bike rack')
	check_in_area = models.PolygonField(help_text='Area where bikes can be "check in" to this bike rack')

	def __str__(self):
		return self.name
	#enddef

class BikeLock(models.Model):
	channel_name = models.SlugField(db_index=True, blank=True, editable=False)
	def __str__(self):
		return str(self.id)

class Bike(models.Model):
	def _get_next_id():
		prev = Bike.objects.aggregate(models.Max('id'))['id__max']
		return prev + 1 if prev is not None else 1

	id = models.IntegerField(primary_key=True, default=_get_next_id, help_text='ID for the bike. This should match the QR code on the bike')
	visible = models.BooleanField(default=True, help_text='Determines if this bike is rentable. Use this instead of deleting bikes')
	location = models.PointField(help_text='Location of the bike')
	current_rental = models.ForeignKey('Rental', on_delete=models.SET_NULL, blank=True, default=None, null=True, help_text='The current rental for this bike', related_name='current_rental')
	previous_rental = models.ForeignKey('Rental', on_delete=models.SET_NULL, blank=True, default=None, null=True, help_text='The previous rental for this bike', related_name='previous_rental')
	lock = models.OneToOneField(BikeLock, on_delete=models.PROTECT, blank=True, default=None, null=True, help_text='Lock for the bike', related_name='bike')

	class Meta:
		permissions = (
			('rent_bike', 'Can rent a bike'),
			('rent_hidden_bike', "Can rent a bike that's not visible"),
		)

	def is_rented(self):
		return self.current_rental is not None
	#enddef
	is_rented.boolean = True

	def __str__(self):
		return str(self.id)
	#enddef

	@classmethod
	def rentable_bikes(klass, user, query=None):
		if query is None:
			query = klass.objects.all()

		query = query.filter(current_rental=None)

		if not user.has_perm('bikeshare.rent_hidden_bike'):
			query = query.filter(visible=True)

		damaged_bikes = DamageReport.objects.filter(
			resolved_by=None,
		).filter(
			Q(critical=True) | Q(acknowledged=True)
		).values_list('bike', flat=True)

		query = query.exclude(id__in=damaged_bikes)

		return query


class Rental(models.Model):
	renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='User who rented the bike')
	bike = models.ForeignKey(Bike, on_delete=models.CASCADE, help_text='The bike that was rented rented')
	rented_at = models.DateTimeField(help_text='When the rental began', default=timezone.now, db_index=True)
	returned_at = models.DateTimeField(null=True, blank=True, help_text='When the bike was actually returned')

	def is_complete(self):
		return self.returned_at is not None
	#enddef
	is_complete.boolean = True

	def is_late(self):
		r_date = self.returned_at if self.is_complete() else timezone.now()
		return r_date > self.rented_at + config.RENTAL_LENGTH
	#enddef
	is_late.boolean = True

	def __str__(self):
		return 'To {} on {}'.format(self.renter, self.rented_at)

class MaintenanceReport(models.Model):
	bike = models.ForeignKey(Bike, on_delete=models.CASCADE, help_text='Bike that is the subject of this report')
	created_at = models.DateTimeField(auto_now_add=True, help_text='When this report was entered')
	comments = models.TextField(help_text='Any additional comments about this bike')


class DamageType(models.Model):
	id = models.SlugField(primary_key=True, help_text='The ID for this damage type')
	name = models.CharField(max_length=50, help_text='Friendly name of this damage, such as "Flat tire"')
	description = models.CharField(max_length=255, help_text='Description of what this damage type means')
	force_critical = models.BooleanField(help_text='Should this damage type always be critical?')
	rider_selectable = models.BooleanField(db_index=True, help_text='Should this damage type be selectable by normal users')

	def __str__(self):
		return self.name
	#enddef


class DamageReport(models.Model):
	reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='The user who reported the damage')
	bike = models.ForeignKey(Bike, on_delete=models.CASCADE, help_text='The bike that was damaged')
	damage_type = models.ForeignKey(DamageType, on_delete=models.PROTECT, help_text='The type of damage done')
	comments = models.TextField(help_text='Additional comments about the damage')
	critical = models.BooleanField(help_text='If this damage interferes with the operation of the bike. Selecting this makes the bike unavailable for rental.')
	reported_at = models.DateTimeField(auto_now_add=True, help_text='When the damage was reported')
	resolved_by = models.ForeignKey(MaintenanceReport, on_delete=models.CASCADE, blank=True, null=True, help_text='The maintenance report that resolved this damage')
	acknowledged = models.BooleanField(default=False, help_text='If this report has been acknowledged')

	class Meta:
		permissions = (
			('report_damage', 'Can report damage to a bike'),
		)

	def __str__(self):
		return '{} - {}'.format(self.bike.id, self.damage_type.name)
	#enddef
