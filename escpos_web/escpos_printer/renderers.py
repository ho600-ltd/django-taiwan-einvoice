import re, logging
import string

from datetime import datetime
from io import BytesIO

from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from rest_framework.renderers import BrowsableAPIRenderer, HTMLFormRenderer


from escpos_printer.models import TEAWeb


def _get_template_name(template_name, sub_dir='', show_template_filename=False, lang=''):
    """ finding order: (sub_dir, langs) > (sub_dir) > (langs) > ()
    """
    import os, itertools
    from django.conf import settings
    from django.utils.translation import get_language
    from django.template import TemplateDoesNotExist

    if not lang: lang = get_language()
    if not template_name.endswith('.html'): template_name += '.html'
    lg = logging.getLogger('info')

    _langs = [lang] + [l[0] for l in settings.LANGUAGES[:]]
    langs = []
    for _lang in _langs:
        if _lang and _lang not in langs: langs.append(_lang)
    lg.debug(langs)

    orders = [
        [[sub_dir], langs],
        [[sub_dir]],
        [langs],
        [],
    ]
    t = None
    for order in orders:
        lg.debug(order)
        _L = list(itertools.product(*order))
        for _l in _L:
            _l = list(_l) + [template_name]
            lg.debug("_l: {}".format(_l))
            _path = os.path.join(*_l)
            lg.debug("_path: {}".format(_path))
            try:
                temp_template = get_template(_path)
            except (TemplateDoesNotExist, TypeError):
                continue
            else:
                t = os.path.join(_path)
                break
        if t:
            break
    if show_template_filename:
        lg.info('Use template: "%s"' % t)

    return t



class EPWBrowsableAPIRenderer(BrowsableAPIRenderer):
    template = "escpos_printer/api.html"



class EPWOriginHTMLRenderer(EPWBrowsableAPIRenderer):
    template = _get_template_name('printer_list', sub_dir='escpos_printer', show_template_filename=True)
    content_template = _get_template_name('printer_list_content', sub_dir='escpos_printer', show_template_filename=True)
    format = 'html'


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['data'] = data
        return  res


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        if getattr(data.get('detail', ''), 'code', ''):
            return data['detail']
        request = renderer_context['request']
        t = get_template(self.content_template)
        html = t.render({"data": data}, request)
        return html



class PrinterHtmlRenderer(EPWOriginHTMLRenderer):
    pass



class TEAWebHtmlRenderer(EPWOriginHTMLRenderer):
    template = _get_template_name('teaweb_list', sub_dir='escpos_printer', show_template_filename=True)
    content_template = _get_template_name('teaweb_list_content', sub_dir='escpos_printer', show_template_filename=True)



class OutgoingIPHtmlRenderer(EPWOriginHTMLRenderer):
    template = _get_template_name('outgoingip_list', sub_dir='escpos_printer', show_template_filename=True)
    content_template = _get_template_name('outgoingip_list_content', sub_dir='escpos_printer', show_template_filename=True)


