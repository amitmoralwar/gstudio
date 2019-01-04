from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class user_json(object):
    def index(self,request):

        if request.method == 'POST':

            Username = request.POST.get('username')
            Password = request.POST.get('password')

        
            user = authenticate(username=Username, password=Password)

            username = request.user.username
            #Email ='admin@gmail.com'
            

            if user:
                user_email = user.email
                user_id = User.objects.get(username=Username).pk

                response_data = {}
                response_data['id'] = user_id
                response_data['name'] = Username
                response_data['email'] = user_email
                
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponse('Invalid Credentials')

        else:
            return HttpResponse('Connection failed!!!')

        return HttpResponse("test")