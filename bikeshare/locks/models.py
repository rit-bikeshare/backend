from django.db import models
from bikeshare.models import BikeLock
from bikeshare.locks.type_manager import lock_manager
from macaddress.fields import MACAddressField

class KeyLock(BikeLock):
	key_number = models.CharField(max_length=10, unique=True)

	def lock(self, request):
		pass
	
	def unlock(self, request):
		pass

class CombinationLock(BikeLock):
	combination = models.CharField(max_length=10)

	def unlock(self, request):
		return str(self.combination)

	def lock(self, request):
		pass

class LinkaLock(BikeLock):
	mac = MACAddressField(unique=True, help_text='MAC Address of the lock', verbose_name="MAC")

	class Meta:
		verbose_name = 'Linka lock'

	def unlock(self, request):
		pass

	def lock(self, request):
		pass

lock_manager.register(KeyLock)
lock_manager.register(CombinationLock)
lock_manager.register(LinkaLock)
