from django.contrib.auth.models import Group
from django.db import models

class ShibIgnoredGroupsMixin(models.Model):
	shib_ignored_groups = models.ManyToManyField(
		Group,
		verbose_name='Shibboleth ignored groups',
		blank = True,
		help_text='Groups that Shibboleth will ignore when adjusting this user\'s groups based on Affiliations. Add a group to prevent Shib from changing this user\'s membership in that group.',
		related_name='shib_ignored_groups_set',
		related_query_name='shib_ignored_groups'
	)

	class Meta:
		abstract = True
