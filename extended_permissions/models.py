from django.contrib.auth.models import Permission
from django.db import models

class ExtendedPermissionsMixin(models.Model):
	user_denied_permissions = models.ManyToManyField(
		Permission,
		verbose_name='permissions to deny to user',
		blank = True,
		help_text='Specific permissions that this user should never have.',
		related_name='user_denied_set',
		related_query_name='user_denied'
	)

	class Meta:
		abstract = True
