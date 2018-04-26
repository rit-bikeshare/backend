from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point
import json
from asgiref.sync import async_to_sync
from bikeshare import models
from channels.generic.websocket import WebsocketConsumer

class LockConsumer(WebsocketConsumer):
	def connect(self):
		self.lock_id = self.scope["url_route"]["kwargs"]["id"]

		lock = get_object_or_404(models.BikeLock, id=self.lock_id)
		lock.channel_name = self.channel_name
		lock.save()

		self.accept()
	
	def receive(self, text_data=None, bytes_data=None):
		msg = json.loads(text_data)
		bike = models.BikeLock.objects.get(id=self.lock_id).bike
		rental_id = bike.current_rental_id

		print(msg)

		location = msg.get('location', None)
		if location:
			bike.location = Point(location['lon'], location['lat'], srid=4326)
			bike.save()

		state = msg.get('state', None)
		if state and rental_id:
			async_to_sync(self.channel_layer.group_send)('rental_' + str(rental_id), {
				'type': 'lock.state',
				'state': state
			})

	def lock_control(self, event):
		self.send('{{"command": "{}"}}'.format(event['command']))

class RentalLockState(WebsocketConsumer):
	def connect(self):
		self.rental_id = self.scope["url_route"]["kwargs"]["id"]
		self.accept()
		async_to_sync(self.channel_layer.group_add)("rental_" + str(self.rental_id), self.channel_name)

	def disconnect(self, close_code):
		async_to_sync(self.channel_layer.group_discard)("rental_" + str(self.rental_id), self.channel_name)
	
	def lock_state(self, event):
		self.send('{{"state": "{}"}}'.format(event['state']))
