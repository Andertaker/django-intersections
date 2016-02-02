from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import ajax_request

from . forms import GroupsForm



class SubscribersIntersection(View, TemplateResponseMixin):

    template_name = 'intersections/subscribers_intersection.html'

    def get(self, request):
        return self.render_to_response({'form': GroupsForm})


@csrf_exempt
@ajax_request
def group_subscribers_update(request):
    link = request.POST['link']
    print link


    return {'succers': True}
