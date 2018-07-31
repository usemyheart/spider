# -*- coding=utf8 -*-
# author:jiyuan

from django.shortcuts import HttpResponse
import json
import get_car_config as gcc


# data={'car':'AB'}
def get_autohome_car_config(request):
    r=request.body
    data=json.loads(r)
    car_sort=data['car']
    count=gcc.get_car_config_info(car_sort)

    return HttpResponse('success get car info {}'.format(count))