import json
import logging

from django.utils import timezone
from rest_framework.views import APIView
from twilio.base.exceptions import TwilioRestException

from twiltwil.api.models import Contact, Message
from twiltwil.api.services import twilioservice
from twiltwil.api.utils import messageutils
from twiltwil.common import enums
from twiltwil.common.utils import viewutils

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "0.1.0"

logger = logging.getLogger(__name__)


class WebhookSmsView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info('SMS POST received: {}'.format(json.dumps(request.data)))

        # Store (or update, if this redundant) the contact and message in the database
        contact, created = Contact.objects.get_or_create(phone_number=request.data['From'], defaults={
            "sid": request.data['MessageSid'],
            "phone_number": request.data['From'],
        })

        message, created = Message.objects.update_or_create(sid=request.data['MessageSid'], defaults={
            "timestamp": timezone.now(),
            "channel": enums.CHANNEL_SMS,
            "sender": contact.sid,
            "recipient": request.data['To'],
            "direction": enums.MESSAGE_INBOUND,
            "status": request.data['SmsStatus'],
            "text": request.data['Body'],
            "addons": messageutils.cleanup_json(request.data['AddOns']) if 'AddOns' in request.data else None,
            "raw": json.dumps(request.data),
        })

        channel = twilioservice.get_or_create_channel(contact.phone_number, contact.sid)

        # Check if the other messages exist from this sender that are associated with an open Task
        sender_messages_with_tasks = Message.objects.not_resolved().inbound().for_contact(contact.sid).has_task()
        task = None
        if sender_messages_with_tasks.exists():
            db_task = sender_messages_with_tasks[0]

            try:
                task = twilioservice.get_task(db_task.task_sid)

                if task.assignment_status not in ['pending', 'reserved', 'assigned']:
                    task = None
                else:
                    logger.info('Found an open Task: {}'.format(task.sid))

                    message.task_sid = db_task.task_sid
                    message.worker_sid = db_task.worker_sid

                    message.save()
            except TwilioRestException as e:
                if e.status != 404:
                    raise e

                for message in sender_messages_with_tasks.iterator():
                    message.resolve = True
                    message.save()

        # If no open Task was found, create a new one
        if not task:
            attributes = {
                "from": message.sender
            }

            message_addons = json.loads(message.addons)
            if message_addons and \
                            "results" in message_addons and \
                            "ibm_watson_insights" in message_addons["results"] and \
                            "result" in message_addons["results"]["ibm_watson_insights"] and \
                            "language" in message_addons["results"]["ibm_watson_insights"]["result"]:
                attributes["language"] = message_addons["results"]["ibm_watson_insights"]["result"]["language"]

            attributes["channel"] = channel.unique_name

            twilioservice.create_task(attributes)

            twilioservice.send_sms(contact.phone_number,
                                   "Hey, your question has been received. Sit tight and we'll get you an answer ASAP!")

        twilioservice.send_chat_message(channel, message)

        return viewutils.get_empty_webhook_response()
