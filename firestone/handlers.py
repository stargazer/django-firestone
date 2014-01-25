from django.views.generic.base import View
from django.http import HttpResponse
from preserialize.serialize import serialize


class BaseHandler(View):
    # Override to define the handler's output representation. It should follow
    # the syntax of ``django-preserialize`` templates.
    # See <https://github.com/bruth/django-preserialize#conventions>
    template = {}           

    def dispatch(self, request, *args, **kwargs):
        """
        Entry point. Coordinates pre and post processing actions, as well as
        selects and calls the main action method.
        """
        self.preprocess(self, request, *args, **kwargs)

        data = super(BaseHandler, self).dispatch(request, *args, **kwargs)

        final_data = self.postprocess(request, data, *args, **kwargs)

        # create response and return it
        return HttpResponse(final_data)

    def preprocess(self, request, *args, **kwargs):
        """
        Preprocess the request.
        """
        pass

    def postprocess(self, request, data, *args, **kwargs):
        """
        Postprocess the data result
        """
        data = self.serialize_to_python(request, data)   
        return data

    def serialize_to_python(self, request, data):
        """
        @param request: Incoming HTTPRequest object
        @param data   : Result of the handler's action

        Serializes the output of a handler's action to python data structures, 
        according to the definition of the handler's ``template`` variable, or
        to reqeust level field selection, by querystring parameter ``field``.
        """
        # NOTE: The request level field selection doesn not work if the
        # handler's ``template`` attribute uses ``django-preserialize``'s
        # pseudo selectors
        # See <https://github.com/bruth/django-preserialize#my-model-has-a-ton-of-fields-and-i-dont-want-to-type-them-all-out-what-do-i-do>
        # It only works when the ``fields`` are defined one by one in a list.
        field_selection = set(request.GET.getlist('field'))
        if field_selection:
            intersection = field_selection.intersection(set(self.template['fields']))
            template = {key: value for key, value in self.template.items()}
            template['fields'] = intersection
            return serialize(data, **template)

        return serialize(data, **self.template)

class ModelHandler(BaseHandler):
    # Override to define the handler's model
    model = None





"""
Example of BaseHandler
class RandomHandler(BaseHandler):
    user_template = {
        'fields': ['id', 'domain', 'email'],
    }
    push_template = {
        'fields': ['id', 'creator'],
        'related': {
            'creator': user_template
        },
    }
    nouncy_template = {
        'fields': ['id', 'title', 'pushes', 'user'],
        'related': {
            'pushes': push_template,
            'user'  : user_template,
        },
    }
    # Say this handler outputs a dictionary like 
    # {'a': <value>, 'b': <value>, 'c': <Nouncy>}
    template = {
        'fields': ['a', 'b', 'nouncy'],
        'related': {
            'nouncy': nouncy_template,
        }
    }            
"""
"""
Example of ModelHandler
class ContactHandler(ModelHandler):
    model = Contact

    media_template = {
        'exclude': ['user',],
    }
    template = {
        'exclude': ['user',],
        'related': {
            'media': media_template,
        },
    }
"""
