from django.shortcuts import redirect 

def AuthMiddleware(get_response):
     # one time initialization
     
     def middleware(request):
          return_url = request.META['PATH_INFO']
          
          if not request.session.get('customer'):
               return redirect(f'login?return_url={return_url}')               
          
          response = get_response(request)
          return response 
     
     return middleware