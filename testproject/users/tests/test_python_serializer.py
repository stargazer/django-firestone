from testproject.users.handlers import UserHandler, DataHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.admin.models import ContentType
from django.http import QueryDict
from model_mommy import mommy
from random import randrange

def setup_view(view, request, *args, **kwargs):
    request.GET = QueryDict('')
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class SerializeToPython(TestCase):
    def setUp(self):
        # Create some persistent records we need for the tests
        # ContentType
        contenttypes = mommy.make(ContentType, 10)
        # LogEntry, and assign one ContentType to each (along with the LogEntry
        # records, User records were created)
        logentries = mommy.make(LogEntry, 10)
        for logentry in logentries:
            logentry.content_type = ContentType.objects.get(id=randrange(1, 11))
            logentry.save()

    def test_modelhandler_queryset(self):
        """
        Testing a model handler's ``serialize_to_python`` method, when
        sending a queryset to the serializer.
        """
        request = RequestFactory()
        request.get('whateverpath/')
        view = setup_view(
            UserHandler(), 
            request,
        )

        # Queryset
        users = User.objects.all()
        # Serialize the queryset 
        ser = view.serialize_to_python(users)
        
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
        self.assertItemsEqual(ser[0].keys(), view.template['fields'])
        
        # Does every ``logentry_set`` key in each dict in ``ser``, contain all
        # the fields that the ``logentry_template`` requires?
        for user in ser:
            for logentry in user['logentry_set']:
                self.assertItemsEqual(
                    logentry.keys(), 
                    view.logentry_template['fields']
                )

    def test_modelhandler_model(self):
        """
        Testing a model handler's ``serialize_to_python`` method, when
        sending a model to the serializer.
        """
        request = RequestFactory()
        request.get('whateverpath/'),
        # Initialize the class based view instance
        view = setup_view(
            UserHandler(), 
            request
        )
        # Retrieve the model
        user = User.objects.get(id=1)
        # Serialize the model
        ser = view.serialize_to_python(user)
        
        # ** Assertions **
        # Is ``ser`` a dict?
        self.assertEquals(type(ser), dict)
        
        # Does the dict have all the fields that the template
        # requires?
        self.assertItemsEqual(ser.keys(), view.template['fields'])
        
        # Does every ``logentry_set`` key in the dict in ``ser``, contain all
        # the fields that the ``logentry_template`` requires?
        for logentry in ser['logentry_set']:
            self.assertItemsEqual(
                logentry.keys(), 
                view.logentry_template['fields']
            ) 

    def test_basehandler_dict(self):
        """
        Testing a base handler's ``serialize_to_python`` method, when
        giving it a dictionary (it will follow the ``template``s directions.
        """
        request = RequestFactory()
        request.get('whateverpath/'),
        # Initialize the class based view instance
        view = setup_view(
            DataHandler(), 
            request,
        )
        
        data = {
            'dic': {'a': 1, 'b': 2, 'c': 3},
            'list': [1, 2, 3],
            'user': User.objects.get(id=1)
        }
        ser = view.serialize_to_python(data)
        
        # ** Assertions **
        # Is ``ser`` a dict?
        self.assertEquals(type(ser), dict)
        
        # Does the dict have all the fields that the template
        # requires?
        self.assertEquals(len(ser.keys()), len(view.template['fields']))
        
        # Does the ``user`` key in the dict in ``ser``, contain all
        # the fields that the ``user_template`` requires?
        self.assertItemsEqual(
            ser['user'].keys(),
            view.user_template['fields']
        )

    def test_basehandler_other(self):
        """
        Testing a base handler's ``serialize_to_python`` method, when
        giving it some other data structure. For dicts within the data
        structure, it will follow the template's rules. For other data types,
        it will jusat output them as they are.
        """
        request = RequestFactory()
        request.get('whateverpath/')
        # Initialize the class based view instance
        view = setup_view(
            DataHandler(), 
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

        ser = view.serialize_to_python(data)
        
        # ** Assertions **
        # Is ``ser`` a list?
        self.assertEqual(type(ser), list)

        # Are all the items in ``data`` in the serialized data structure?
        self.assertEqual(len(ser), len(data)) 
        
        # Do the dicts in ``ser`` have only the fields that the template
        # requires?
        for item in ser:
            if isinstance(item, dict):
                self.assertItemsEqual(item.keys(), view.template['fields'])

        # Do the ``user`` items in the dicts only have the fields that the
        # template requires?
        for item in ser:
            if isinstance(item, dict):
                if 'user' in item:
                    self.assertItemsEqual(
                        item['user'].keys(),
                        view.user_template['fields']
                    )

        
            


