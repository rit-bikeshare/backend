from rest_framework.permissions import *

class CanRentBike(BasePermission):
	message = 'You cannot rent bikes'

	def has_permission(self, request, view):
		return request.user.has_perm('bikeshare.rent_bike')

class CanReportDamage(BasePermission):
	message = 'You cannot report damage'

	def has_permission(self, request, view):
		return request.user.has_perm('bikeshare.report_damage')