from django import template

register = template.Library()


@register.filter
def air_nanitozo_count(air):
    all_list = air_nanitozo_all_list(air)
    nanitozo_count = len(all_list['nanitozo_list'])
    good_count = len(all_list['good_list'])
    comment_count = len(all_list['comment_recommend_list']) + len(all_list['comment_list']) + len(all_list['comment_negative_list'])
    score = (nanitozo_count * 2) + (good_count * 5) + (comment_count * 1)
    return {
        'nanitozo_count': nanitozo_count,
        'good_count': good_count,
        'comment_count': comment_count,
        'score': score,
    }


@register.filter
def air_nanitozo_done(air, request_user):
    all_list = air_nanitozo_all_list(air)
    my_nanitozo_list = list(filter(lambda x: x.user == request_user, all_list['nanitozo_list']))
    my_good_list = list(filter(lambda x: x.user == request_user, all_list['good_list']))
    my_comment_recommend_list = list(filter(lambda x: x.user == request_user, all_list['comment_recommend_list']))
    my_comment_list = list(filter(lambda x: x.user == request_user, all_list['comment_list']))
    my_comment_negative_list = list(filter(lambda x: x.user == request_user, all_list['comment_negative_list']))
    comment_done = bool(my_comment_recommend_list) or bool(my_comment_list) or bool(my_comment_negative_list)
    return {
        'nanitozo_done': bool(my_nanitozo_list),
        'good_done': bool(my_good_list),
        'comment_done': comment_done,
    }


# - - - -
def air_nanitozo_list(air):
    return air.nanitozo_set.all()


def air_nanitozo_all_list(air):
    nanitozo_list = air_nanitozo_list(air)
    good_list = list(filter(lambda x: x.good == True, nanitozo_list))
    comment_recommend_list = list(filter(lambda x: x.comment_open == True and x.comment_recommend != None and len(x.comment_recommend) != 0, nanitozo_list))
    comment_list = list(filter(lambda x: x.comment_open == True and x.comment != None and len(x.comment) != 0, nanitozo_list))
    comment_negative_list = list(filter(lambda x: x.comment_open == True and x.comment_negative != None and len(x.comment_negative) != 0, nanitozo_list))
    return {
        'nanitozo_list': nanitozo_list,
        'good_list': good_list,
        'comment_recommend_list': comment_recommend_list,
        'comment_list': comment_list,
        'comment_negative_list': comment_negative_list,
    }
