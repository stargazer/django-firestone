"""
The ``serializers`` module exposes the classes responsible for
serializing the response bodies from python data structures to whatever output
format has been asked
"""

# Read the format given by Accept Header.
# IF supported, output to that format. If not supported, fallback to default
# serializer. Along with the serialized response, return the response's Content-type
