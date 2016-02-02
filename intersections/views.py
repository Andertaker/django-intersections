from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin



class SubscribersIntersection(View, TemplateResponseMixin):

    template_name = 'intersections/subscribers_intersection.html'

    def get(self, request):
        return self.render_to_response({})
