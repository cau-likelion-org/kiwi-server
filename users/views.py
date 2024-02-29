from pathlib import Path
import os, json
from django.core.exceptions import ImproperlyConfigured
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from random import *
from .models import *


BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

adj = []
noun = []

def save_words():
    random_adj = os.path.join(BASE_DIR, 'random-adj.txt')
    random_noun = os.path.join(BASE_DIR, 'random-noun.txt')

    fa = open(random_adj, 'r', encoding='UTF8')
    while True:
        line = fa.readline().strip()
        if not line: 
            break
        adj.append(line)
    
    fn = open(random_noun, 'r', encoding='UTF8')
    while True:
        line = fn.readline().strip()
        if not line: 
            break
        noun.append(line)

        
REDIRECT_URL = get_secret("REDIRECT_URL")

def check_name(name):
    return User.objects.filter(name=name).exists()

# 구글 로그인 테스트용 코드
# GOOGLE_SCOPE_USERINFO = get_secret("GOOGLE_SCOPE_USERINFO");
# GOOGLE_REDIRECT = get_secret("GOOGLE_REDIRECT");
# from django.shortcuts import redirect

# def google_login(request):
#    scope = GOOGLE_SCOPE_USERINFO
#    client_id = get_secret("GOOGLE_CLIENT_ID")
#    return redirect(f"{GOOGLE_REDIRECT}?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    client_id = get_secret("GOOGLE_CLIENT_ID")
    client_secret = get_secret("GOOGLE_SECRET")
    body = json.loads(request.body.decode('utf-8'))
    code = body['code']
    # code = request.GET.get('code')
    
    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={REDIRECT_URL}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)

    google_access_token = token_req_json.get('access_token')

    email_response = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={google_access_token}")
    res_status = email_response.status_code

    if res_status != 200:
        return JsonResponse({'status': 400,'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
    
    email_res_json = email_response.json()
    email = email_res_json.get('email')

    email_arr = email.split('@')
    if email_arr[1].strip() != "gmail.com":
        return JsonResponse({
            "status" : "400",
            "message" : "Bad Request",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        token = RefreshToken.for_user(user)         # 자체 jwt 발급

        if user.is_active == True:
            return JsonResponse({
                "status" : "200",
                "message" : "Login Success",
                "data" : {
                    "email" : email,
                    "name" : user.name,
                    "joined_date" : user.joined_date,
                    "token" : {
                        "access_token" : str(token.access_token),
                        "refresh_token" : str(token),
                    }
                }
            }, status=status.HTTP_200_OK)
        else:
            raise Exception('Signup Required')
    except Exception:
        print(email)
        # 가입이 필요한 회원
        return JsonResponse({
            "status" : "202",
            "message" : "Signup Required",
            "data" : {
                "email" : email
            }
        }, status=status.HTTP_202_ACCEPTED)

class RegisterView(APIView):
    def post(self, request):
        body = json.loads(request.body.decode('utf-8'))
        email = body['email']
        name = body['name']
        if email == "" or name == "":
            return JsonResponse({
                "status" : "400",
                "message" : "Bad Request",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # user 생성
        user = User.objects.create_user(email, name)
        if user is None or user.is_active == False:
            return JsonResponse({
                "status" : "400",
                "message" : "Bad Request",
            }, status=status.HTTP_400_BAD_REQUEST)

        # 회원가입 완료
        token = RefreshToken.for_user(user)         # 자체 jwt 발급
        return JsonResponse({
            "status" : "201",
            "message" : "Register Success",
            "data" : {
                "email" : user.email,
                "name" : user.name,
                "joined_date" : user.joined_date,
                "token" : {
                    "access_token" : str(token.access_token),
                    "refresh_token" : str(token),
                }
            }
        }, status=status.HTTP_201_CREATED)
    
class CheckNameView(APIView):
    def get(self, request):
        name = request.GET['name']

        # name 중복 확인
        is_duplicated = check_name(name)

        if is_duplicated:
            return JsonResponse({
                "status" : "400",
                "message" : "Duplicated Nickname",
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({
                "status" : "200",
                "message" : "Nickname Available",
                "data" : {
                    "name" : name
                }
            }, status=status.HTTP_200_OK)

class RandomNameView(APIView):
    def get(self, request):
        if len(adj) == 0 or len(noun) == 0:
            save_words()

        rand_adj = adj[randrange(200)]
        rand_noun = noun[randrange(200)]
        name = rand_adj + " " + rand_noun

        while check_name(name):         # 랜덤 닉네임 중복 없을 때까지 반복
            rand_adj = adj[randrange(200)]
            rand_noun = noun[randrange(200)]
            name = rand_adj + " " + rand_noun

        return JsonResponse({
                "status" : "200",
                "message" : "Random Nickname",
                "data" : {
                    "name" : name
                }
            }, status=status.HTTP_200_OK)
