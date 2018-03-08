import copy

class ShibIgnoredGroupsAdminMixin:
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_horizontal = list(self.filter_horizontal) if self.filter_horizontal else []
        self.filter_horizontal.append('shib_ignored_groups')

    def get_fieldsets(self, request, obj=None):
        fieldsets = copy.deepcopy(super().get_fieldsets(request, obj)) # Deep-copy to avoid multiple appends
        
        found = False
        for group_name, opts in fieldsets:
            fields = opts.get('fields', None)
            if not fields or 'groups' not in fields: continue

            fields = list(fields) # Convert to list so we can modify
            user_perms_pos = fields.index('groups') # Find position of existing permissions
            fields.insert(user_perms_pos + 1, 'shib_ignored_groups') # Add ours after this
            opts['fields'] = tuple(fields) # Update fieldset

            found = True

        if not found: raise TypeError("Couldn't find groups field. Maybe you need a custom admin?")

        return fieldsets
