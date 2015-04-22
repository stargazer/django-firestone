import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

# Necessary for Django >= 1.7. See https://docs.djangoproject.com/en/dev/releases/1.7/#app-loading-changes
import django
from distutils.version import LooseVersion
if LooseVersion(django.get_version()) >= LooseVersion('1.7'):
    django.setup()

from django.test.utils import get_runner
from django.conf import settings

def run():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=True)
    try:
        # Django 1.5
        failures = test_runner.run_tests(['testapp',])
    except ImportError:
        # Django >= 1.6
        failures = test_runner.run_tests(['testproject.testapp',])

    sys.exit(failures)

