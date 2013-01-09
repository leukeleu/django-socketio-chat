from rest_framework.renderers import JSONRenderer

from django.utils import simplejson

def prepare_for_emit(obj):
    """
    Prepare the object for emit() by Tornadio2's (too simple) JSON renderer
    - render to JSON using Django REST Framework 2's JSON renderer
    - convert back to _simple_ Python object using Django's simplejson
    """

    json = JSONRenderer().render(obj)

    return simplejson.loads(json)
