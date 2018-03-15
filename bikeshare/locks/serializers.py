from rest_framework import serializers

from bikeshare.serializers import BikeLockSerializer
from bikeshare.locks import models
from bikeshare.locks.type_manager import register_serializer

class LockSerializerBase(serializers.ModelSerializer):
	type_id = serializers.SerializerMethodField()

	def get_type_id(self, obj): return obj.type_id

class LockSerializerMetaBase:
	exclude = ('polymorphic_ctype',)
	read_only_fields = ('id','type_id')

@register_serializer(models.KeyLock)
class KeyLockSerializer(LockSerializerBase):
	class Meta(LockSerializerMetaBase):
		model = models.KeyLock

@register_serializer(models.CombinationLock)
class CombinationLockSerializer(LockSerializerBase):
	class Meta(LockSerializerMetaBase):
		model = models.CombinationLock

@register_serializer(models.LinkaLock)
class LinkaLockSerializer(LockSerializerBase):
	class Meta(LockSerializerMetaBase):
		model = models.LinkaLock

