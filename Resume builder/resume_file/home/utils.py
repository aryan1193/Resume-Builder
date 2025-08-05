from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import io

def render_to_pdf(template_src, context_dict={}):
    html_string = render_to_string(template_src, context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_string.encode('UTF-8')), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
        return response
    return HttpResponse('We had some errors while generating the PDF')
