# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
"Attachment"
import os
<<<<<<< HEAD
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import sys
=======
from urllib.request import urlopen
from urllib.parse import urlparse, unquote
>>>>>>> origin/5.0
import gettext
import webbrowser
from functools import partial

from tryton.common import RPCExecute, RPCException, file_write, file_open
from tryton.gui.window.view_form.screen import Screen
from tryton.gui.window.win_form import WinForm

_ = gettext.gettext


class Attachment(WinForm):
    "Attachment window"

    def __init__(self, record, callback=None):
        self.resource = '%s,%s' % (record.model_name, record.id)
        self.attachment_callback = callback
        title = _('Attachments (%s)') % (record.rec_name())
        screen = Screen('ir.attachment', domain=[
            ('resource', '=', self.resource),
            ], mode=['tree', 'form'])
        super(Attachment, self).__init__(screen, self.callback,
            view_type='tree', title=title)
        screen.search_filter()

    def destroy(self):
        self.prev_view.save_width_height()
        super(Attachment, self).destroy()

    def callback(self, result):
        if result:
            self.screen.save_current()
        if self.attachment_callback:
            self.attachment_callback()

    def add_uri(self, uri):
        data_field = self.screen.group.fields['data']
        name_field = self.screen.group.fields[data_field.attrs['filename']]
        new_record = self.screen.new()
<<<<<<< HEAD
        file_name = os.path.basename(urllib.parse.urlparse(uri).path)
        name_field.set_client(new_record, file_name)
        uri = urllib.parse.unquote(uri)
        uri = uri.decode('utf-8').encode(sys.getfilesystemencoding())
        data_field.set_client(new_record, urllib.request.urlopen(uri).read())
=======
        uri = unquote(uri)
        file_name = os.path.basename(urlparse(uri).path)
        name_field.set_client(new_record, file_name)
        data_field.set_client(new_record, urlopen(uri).read())
>>>>>>> origin/5.0
        self.screen.display()

    def add_file(self, filename):
        self.add_uri('file:///' + filename)

    @staticmethod
    def get_attachments(record):
        attachments = []
        context = {}
        if record and record.id >= 0:
            context = record.get_context()
            try:
                attachments = RPCExecute('model', 'ir.attachment',
                    'search_read', [
                        ('resource', '=', '%s,%s' % (
                                record.model_name, record.id)),
                        ], 0, 20, None, ['rec_name', 'name', 'type', 'link'],
                    context=context)
            except RPCException:
                pass
        for attachment in attachments:
            name = attachment['rec_name']
            callback = getattr(
                Attachment, 'open_' + attachment['type'], Attachment.open_data)
            yield name, partial(
                callback, attachment=attachment, context=context)

    @staticmethod
    def open_link(attachment, context):
        if attachment['link']:
            webbrowser.open(attachment['link'], new=2)

    @staticmethod
    def open_data(attachment, context):
        try:
            value, = RPCExecute('model', 'ir.attachment', 'read',
                [attachment['id']], ['data'], context=context)
        except RPCException:
            return
        filepath = file_write(attachment['name'], value['data'])
        file_open(filepath)
