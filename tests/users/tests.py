from handlers import UserHandler, DataHandler
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.admin.models import ContentType
from model_mommy import mommy
from random import randrange


def setup_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view

class SerializeToPython(TestCase):
    def test_model_handler_queryset_only_valid_fields(self):
        """
        Testing a model handler, when sending a queryset to the serializer.
        The handler's template defines only valid keys (keys that actually
        exist in the data that we sent it)
        """
        view = setup_view(
            UserHandler(), 
            RequestFactory().get('whateverpath/'),
        )
    
        # Create some ContentType records
        contenttypes = mommy.make(ContentType, 10)
        # Create some LogEntry records and assign them one ContentType each
        logentries = mommy.make(LogEntry, 10)
        for logentry in logentries:
            logentry.content_type = ContentType.objects.get(id=randrange(1, 11))
            logentry.save()
        # Along with the Logentry records, User records were also created.            
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
        self.assertEquals(
            len(ser[0].keys()), 
            len(view.template['fields']))
        # Does every ``logentry_set`` key in each dict in ``ser``, contain all
        # the fields that the ``logentry_template`` requires?
        for user in ser:
            for logentry in user['logentry_set']:
                self.assertItemsEqual(
                    logentry.keys(), 
                    view.logentry_template['fields']
                )
    
    def test_model_handler_queryset_also_invalid_fields(self):
        """
        Testing a model handler, when sending a queryset to the serializer.
        We modify the handler's template so that it defines some invalid keys.
        """
        view = setup_view(
            UserHandler(), 
            RequestFactory().get('whateverpath/'),
        )
        view.template['fields'].append('invalid_field1')
        view.template['fields'].append('invalid_field12')
        view.template['related']['invalid_field3'] = {'key':'value'}

        # Create some ContentType records
        contenttypes = mommy.make(ContentType, 10)
        # Create some LogEntry records and assign them one ContentType each
        logentries = mommy.make(LogEntry, 10)
        for logentry in logentries:
            logentry.content_type = ContentType.objects.get(id=randrange(1, 11))
            logentry.save()
        # Along with the Logentry records, User records were also created.            
        users = User.objects.all()

        # Serialize the queryset 
        ser = view.serialize_to_python(users)
        for user in ser:
            print ser
