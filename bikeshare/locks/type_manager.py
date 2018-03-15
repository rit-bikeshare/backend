class SubclassRepository:
	def __init__(self, base_model, meta_type):
		if not isinstance(base_model, type):
			raise TypeError("base_model must be a class")
		if not isinstance(meta_type, type):
			raise TypeError("meta_type must be a class")
		
		self.subclasses = {}
		self.base_model = base_model
		self.meta_type = meta_type
	
	@property
	def subclass_list(self):
		return list(self.subclasses.keys())

	def __getitem__(self, model):
		if not isinstance(model, type):
			model = type(model)
		return self._get_model_meta(model)

	def _get_model_meta(self, model):
		try:
			return self.subclasses.get(model)
		except KeyError:
			raise KeyError("Model '{}' not registered".format(model))

	def register(self, model, overwrite=False):
		if not isinstance(model, type):
			raise TypeError("model must be a class")

		if not issubclass(model, self.base_model):
			raise TypeError("{} must be a subclass of {}".format(model, self.base_model))

		meta = self.meta_type()

		if overwrite:
			self.subclasses[model] = meta
		else:
			if id(self.subclasses.setdefault(model, meta)) != id(meta):
				raise ValueError("Model '{}' already registered".format(model))
	#enddef

class SerializerMetaMixin:
	def __init__(self):
		super().__init__()
		self.serializer = None

from bikeshare.models import BikeLock
lock_manager = SubclassRepository(BikeLock, SerializerMetaMixin)

def register_serializer(model, repository=lock_manager):
	def decorator(serializer_cls):
		repository[model].serializer = serializer_cls
		return serializer_cls
	return decorator
