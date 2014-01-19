"""
The ``serializers`` module exposes the classes responsible for
serializing the response bodies from python data structures to whatever output
format has been asked
"""
# Read the format given by Accept Header.
# IF supported, output to that format. If not supported, fallback to default
# serializer. Along with the serialized response, return the response's Content-type

def serialize_to_python(data):
    """
    returns the given data (which could include among others, models,
    querysets, etc) to pure python data structures.
    
    This means that the field selection is done here. Only fields that the
    handler specifies should be returned.

    The data structure returned, can be manipulated at will, before being
    passed on to the JSON serializer
    """
    if isinstance(data, list):
        return map(serialize_to_python, data)

    elif isinstance(data, dict):
        # return only the dictionary fields that the handler specifies
        for key, value in data.iteritems():
            return {key, serialize_to_python[value]}

    elif isinstance(data, model):
        # rerialize using django-preserialize 
        pass

    elif isinstance(data, queryset):
        # rerialize using django-preserialize 
        pass    

    else:
        return data

def serialize_to_json():
    """
    Takes a python data structure, and outputs its json representation
    """
    pass
