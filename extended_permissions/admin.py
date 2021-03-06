import copy

class ExtendedUserAdminMixin:
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_horizontal = list(self.filter_horizontal) if self.filter_horizontal else []
        self.filter_horizontal.append('user_denied_permissions')

    def get_fieldsets(self, request, obj=None):
        fieldsets = copy.deepcopy(super().get_fieldsets(request, obj)) # Deep-copy to avoid multiple appends
        
        found = False
        for group_name, opts in fieldsets:
            fields = opts.get('fields', None)
            if not fields or 'user_permissions' not in fields: continue

            fields = list(fields) # Convert to list so we can modify
            user_perms_pos = fields.index('user_permissions') # Find position of existing permissions
            fields.insert(user_perms_pos + 1, 'user_denied_permissions') # Add ours after this
            opts['fields'] = tuple(fields) # Update fieldset

            found = True

        if not found: raise TypeError("Couldn't find user_permissions field. Maybe you need a custom admin?")

        return fieldsets

