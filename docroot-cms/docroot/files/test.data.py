# from myapp.models import Web_Region

context = {'title': 'my static title',
               'description': 'my static description',
               'data': 'my static data',
               }

def get_context(request):
    # region_list = Web_Region.objects.values_list('region_name', flat=True)
    context.update({'data': 'my dynamic data'})
    return context