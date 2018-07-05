from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseBadRequest, Http404, HttpResponse

def Raise404UpdateURL(self, request):
	raise Http404("Update pages are under reconstruction")
