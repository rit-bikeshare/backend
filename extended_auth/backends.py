from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

class ExtendedModelBackend(ModelBackend):
	def _get_user_permissions(self, user_obj):
		if user_obj.is_superuser:
			return Permission.objects.all() # Superuser gets everything
		else:
			return super()._get_user_permissions(user_obj)

	def _get_user_denied_permissions(self, user_obj):
		return user_obj.user_denied_permissions.all()

	def _get_permissions(self, user_obj, obj, from_name):
		"""
		Return the permissions of `user_obj` from `from_name`. `from_name` can
		be either "group" or "user" to return permissions from
		`_get_group_permissions` or `_get_user_permissions` respectively.
		"""
		if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
			return set()

		perm_cache_name = '_%s_perm_cache' % from_name
		if not hasattr(user_obj, perm_cache_name):
			perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
			perms = perms.values_list('content_type__app_label', 'codename').order_by()

			setattr(user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
		return getattr(user_obj, perm_cache_name)

	def get_user_permissions(self, user_obj, obj=None):
		"""
		In case some code wants to check only user level permissions.
		We need to override this because it's not safe to call due to
		extended permissions
		"""
		raise NotImplementedError()

	def get_user_granted_permissions(self, user_obj, obj=None):
		"""
		Return a set of permission strings the user `user_obj` has from their
		`user_denied_permissions`.
		"""
		return self._get_permissions(user_obj, obj, 'user')

	def get_user_denied_permissions(self, user_obj, obj=None):
		"""
		Return a set of permission strings the user `user_obj` has from their
		`user_denied_permissions`.
		"""
		return self._get_permissions(user_obj, obj, 'user_denied')

	def get_all_permissions(self, user_obj, obj=None):
		if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
			return set()
		if not hasattr(user_obj, '_perm_cache'):
			granted_perms = set() # user has no permissions by default
			
			user_granted, user_denied = self.get_user_granted_permissions(user_obj), self.get_user_denied_permissions(user_obj)
			group_granted, group_denied = self.get_group_permissions(user_obj), set()

			# Now we calculate our permissions.
			# Permissions default to "Not set" and can be either explicitly granted or denied.
			# Precedence goes Denied, Granted, Not Set
			# So a denied permission overrides a granted permission which overrides not set
			# Set user permissions override group permissions completely, so user.granted overrides group.denied

			granted_perms.update(group_granted)
			granted_perms.difference_update(group_denied)
			granted_perms.update(user_granted)
			granted_perms.difference_update(user_denied)

			user_obj._perm_cache = granted_perms
		return user_obj._perm_cache

