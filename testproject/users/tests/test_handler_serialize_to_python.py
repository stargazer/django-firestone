"""
This module tests the ``BaseHandler.serialize_to_python`` method
"""
from firestone.handlers import ModelHandler
from firestone.handlers import BaseHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.admin.models import ContentType
from django.http import QueryDict
from model_mommy import mommy
from random import randrange

def setup_handler(handler, request, *args, **kwargs):
    """
    Mimics the behavior of ``firestone.views.View.__call__``, without of course
    invoking the handler.
    """
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestModelHandlerSerializeToPython(TestCase):
    def setUp(self):
        # Create some persistent records
        # ``ContentType``
        contenttypes = mommy.make(ContentType, 10)
        # ``LogEntry``, and assign one ContentType to each (along with the LogEntry
        # records, User records were created)
        logentries = mommy.make(LogEntry, 10)
        for logentry in logentries:
            logentry.content_type = ContentType.objects.get(id=randrange(1, 11))
            logentry.save()

        # Initialize a Model Handler
        modelhandler = ModelHandler()
        modelhandler.model = User

        modelhandler.content_type_template = {
            'fields': ['id', ],
            'flat': False,
        }            
        modelhandler.logentry_template = {
            'fields': ['action_flag', 'content_type'],     
            'related': {
                'content_type': modelhandler.content_type_template,
            }
        }
        modelhandler.template = {
            'fields': ['id', 'username', 'first_name', 'last_name',
                       'logentry_set', 'email', 'last_login'], 
            'related': {
                'logentry_set': modelhandler.logentry_template,
            }, 
            'exclude': ['password', 'date_joined',],
            'allow_missing': True,
        }            

        self.modelhandler = modelhandler

    def test_modelhandler_queryset(self):
        """
        Testing a model handler's ``serialize_to_python`` method, when
        sending a queryset to the serializer.
        """
        request = RequestFactory()
        request = request.get('whateverpath/')
        handler = setup_handler(
            self.modelhandler, 
            request,
        )

        # Queryset
        users = User.objects.all()
        # Serialize the queryset 
        ser = handler.serialize_to_python(request, users)
        
        # ** Assertions **
        # Is ``ser`` a list?
        self.assertEquals(type(ser), list)
        
        # Is every item in ``ser``, a dict?
        for user in ser:
            self.assertEqual(type(user), dict)
        
        # Have all the models in the queryset been serialized?     
        self.assertEquals(len(ser), users.count())
        
        # Does every dict in ``ser`` have all the fields that the template
        # requires?
        for item in ser:
            self.assertItemsEqual(item.keys(), handler.template['fields'])
        
        # Does every ``logentry_set`` key in each dict in ``ser``, contain all
        # the fields that the ``logentry_template`` requires?
        for user in ser:
            for logentry in user['logentry_set']:
                self.assertItemsEqual(
                    logentry.keys(), 
                    handler.logentry_template['fields']
                )

    def test_modelhandler_queryset_field_selection(self):                
        """
        Testing a model handler's ``serialize_to_python`` method, when
        sending a queryset to the serializer, and request level field selection
        is used.
        """
        request = RequestFactory()
        request = request.get('whateverpath/?field=id&field=username&field=logentry_set')
        # Initialize the class handler
        handler = setup_handler(
            self.modelhandler,
            request
        )

        # Queryset
        users = User.objects.all()
        # Serialize to python
        ser = handler.serialize_to_python(request, users)

        # ** Assertions **
        # Is ``ser`` a list?
        self.assertEquals(type(ser), list)
        
        # Is every item in ``ser``, a dict?
        for user in ser:
            self.assertEqual(type(user), dict)
        
        # Have all the models in the queryset been serialized?     
        self.assertEquals(len(ser), users.count())
        
        # Does every dict in ``ser`` have all the fields that the field
        # selection defined?
        for item in ser:
            self.assertItemsEqual(item.keys(), ('id', 'username', 'logentry_set'))
        
        # Does every ``logentry_set`` key in each dict in ``ser``, contain all
        # the fields that the ``logentry_template`` requires?
        for user in ser:
            for logentry in user['logentry_set']:
                self.assertItemsEqual(
                    logentry.keys(), 
                    handler.logentry_template['fields']
                )

    def test_modelhandler_model(self):
        """
        Testing a model handler's ``serialize_to_python`` method, when
        sending a model to the serializer.
        """
        request = RequestFactory()
        request = request.get('whateverpath/')
        # Initialize the handler
        handler = setup_handler(
            self.modelhandler,
            request
        )
        # Retrieve the model
        user = User.objects.get(id=1)
        # Serialize the model
        ser = handler.serialize_to_python(request, user)
        
        # ** Assertions **
        # Is ``ser`` a dict?
        self.assertEquals(type(ser), dict)
        
        # Does the dict have all the fields that the template
        # requires?
        self.assertItemsEqual(ser.keys(), handler.template['fields'])
        
        # Does every ``logentry_set`` key in the dict in ``ser``, contain all
        # the fields that the ``logentry_template`` requires?
        for logentry in ser['logentry_set']:
            self.assertItemsEqual(
                logentry.keys(), 
                handler.logentry_template['fields']
            ) 

    def test_modelhandler_model_field_selection(self):                
        """
        Testing a model handler's ``serialize_to_python`` method, when
        sending a queryset to the serializer, and request level field selection
        is used.
        """
        request = RequestFactory()
        request = request.get('whateverpath/?field=id&field=username&field=logentry_set')
        # Initialize the handler
        handler = setup_handler(
            self.modelhandler,
            request
        )

        # Queryset
        users = User.objects.get(id=1)
        # Serialize to python
        ser = handler.serialize_to_python(request, users)
        # ** Assertions **
        # Is ``ser`` a dict?
        self.assertEquals(type(ser), dict)
        
        # Does the dict in ``ser`` have all the fields that the field
        # selection defined?
        self.assertItemsEqual(ser.keys(), ('id', 'username', 'logentry_set'))
        
        # Does every ``logentry_set`` key in the dict in ``ser``, contain all
        # the fields that the ``logentry_template`` requires?
        for logentry in ser['logentry_set']:
            self.assertItemsEqual(
                logentry.keys(), 
                handler.logentry_template['fields']
            ) 

class TestBaseHandlerSerializeToPython(TestCase): 
    def setUp(self):
        # Create some User instances
        mommy.make(User, 10)

        # Initialize a basehandler
        basehandler = BaseHandler()

        basehandler.user_template = {
            'fields': ['id', 'username', 'email']
        }        
        basehandler.template = {
            'fields': ['dic', 'list', 'user'],
            'related': {
                'user': basehandler.user_template    
            }
        }

        self.basehandler = basehandler
                                
    def test_basehandler_dict(self):
        """
        Testing a base handler's ``serialize_to_python`` method, when
        giving it a dictionary (it will follow the ``template``s directions.
        """
        request = RequestFactory()
        request = request.get('whateverpath/')
        # Initialize the handler
        handler = setup_handler(
            self.basehandler, 
            request,
        )
        
        data = {
            'dic': {'a': 1, 'b': 2, 'c': 3},
            'list': [1, 2, 3],
            'user': User.objects.get(id=1)
        }
        ser = handler.serialize_to_python(request, data)
        
        # ** Assertions **
        # Is ``ser`` a dict?
        self.assertEquals(type(ser), dict)
        
        # Does the dict have all the fields that the template
        # requires?
        self.assertEquals(len(ser.keys()), len(handler.template['fields']))
        
        # Does the ``user`` key in the dict in ``ser``, contain all
        # the fields that the ``user_template`` requires?
        self.assertItemsEqual(
            ser['user'].keys(),
            handler.user_template['fields']
        )
                    
    def test_basehandler_dict_field_selection(self):
        """
        Testing a base handler's ``serialize_to_python`` method, when
        giving it a dictionary, and request level field selection is used
        """
        request = RequestFactory()
        request = request.get('whateverpath/?field=dic&field=list')
        # Initialize the handler
        handler = setup_handler(
            self.basehandler, 
            request,
        )
        
        data = {
            'dic': {'a': 1, 'b': 2, 'c': 3},
            'list': [1, 2, 3],
            'user': User.objects.get(id=1)
        }
        ser = handler.serialize_to_python(request, data)
        
        # ** Assertions **
        # Is ``ser`` a dict?
        self.assertEquals(type(ser), dict)
        
        # Does the dict have all the fields that the field selectiond defines?
        self.assertItemsEqual(ser.keys(), ('dic', 'list'))
        
    def test_basehandler_other(self):
        """
        Testing a base handler's ``serialize_to_python`` method, when
        giving it some other data structure. For dicts within the data
        structure, it will follow the template's rules. For other data types,
        it will jusat output them as they are.
        """
        request = RequestFactory()
        request = request.get('whateverpath/')
        # Initialize the handler
        handler = setup_handler(
            self.basehandler, 
            request
        )
        
        data = [
            {
                'dic': {'a': 1, 'b': 2, 'c': 3},
                'list': [1, 2, 3],
                'user': User.objects.get(id=1),
                'random_key': 'value',
            },
            {
                'dic': {'a': 1, 'b': 2, 'c': 3},
                'list': [1, 2, 3],
                'user': User.objects.get(id=2),
                'other_random_key': 'value',
            },
            'string',
            1,
            2,
            3
        ]

        ser = handler.serialize_to_python(request, data)
        
        # ** Assertions **
        # Is ``ser`` a list?
        self.assertEqual(type(ser), list)

        # Are all the items in ``data`` in the serialized data structure?
        self.assertEqual(len(ser), len(data)) 
        
        # Do the dicts in ``ser`` have only the fields that the template
        # requires?
        for item in ser:
            if isinstance(item, dict):
                self.assertItemsEqual(item.keys(), handler.template['fields'])

        # Do the ``user`` items in the dicts only have the fields that the
        # template requires?
        for item in ser:
            if isinstance(item, dict):
                if 'user' in item:
                    self.assertItemsEqual(
                        item['user'].keys(),
                        handler.user_template['fields']
                    )

        
            


