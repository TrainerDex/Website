from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Gym
from .serializers import ElasticGymSerializer
from config.es_client import es_client
"""
@receiver(pre_save, sender=Gym, dispatch_uid="update_record")
def update_es_record(sender, instance, **kwargs):
    obj = ElasticGymSerializer(instance)
    obj.save(using=es_client)

@receiver(post_delete, sender=Gym, dispatch_uid="delete_record")
def delete_es_record(sender, instance, *args, **kwargs):
    obj = ElasticGymSerializer(instance)
    obj.delete(using=es_client, ignore=404)

"""
