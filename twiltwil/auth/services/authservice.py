"""
Authentication service functions.
"""

import logging

from django.contrib.auth import logout, get_user_model, login
from django.core.urlresolvers import reverse

from twiltwil.auth.services import twilioauthservice

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Alex Laird'
__version__ = '0.1.0'

logger = logging.getLogger(__name__)


def process_register(request, user):
    """
    At this point the user will be created in the database and a worker created.

    :param request: the request
    :param user: the user that has been created
    :return: a redirect for the next page in the registration flow
    """
    logger.info('Registered new user with username: {}'.format(user.get_username()))

    # TODO: either get this from a .env or query for it on startup
    workspace_sid = 'WS86557ca494226e8435fe0c7aff420556'

    user = get_user_model().objects.get(username=user.username)

    attributes = {
        "time_zone": user.time_zone,
        "languages": list(user.languages.all().values_list('id', flat=True)),
        "skills": list(user.skills.all().values_list('id', flat=True))
    }

    worker = twilioauthservice.create_worker(workspace_sid, user.username, attributes)

    user.workspace_sid = workspace_sid
    user.worker_sid = worker.sid
    user.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    return reverse('portal')


def process_logout(request):
    """
    Log the authenticated user out, then delete them.

    :param request: the request
    :return:
    """
    username = request.user.username
    logout(request)

    user = get_user_model().objects.get(username=username)
    if not user.is_superuser:
        user.delete()

    logger.info('Logged out and deleted user {}'.format(username))
