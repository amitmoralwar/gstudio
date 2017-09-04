''' -- imports from python libraries -- '''
import json
import bson
from bson.json_util import dumps

''' -- imports from installed packages -- '''
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.admin import User
# from django.shortcuts import render_to_response
# from django.template import RequestContext
# from django.contrib.auth.decorators import login_required
# from django.core.urlresolvers import reverse

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import GSystemType, GSystem #, Group, Node, GSystem  #, Triple
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.models import node_collection,triple_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id


def api_get_group_gst_nodes(request, group_name_or_id):
    # GET: api/v1/<group_id>/<files>/<nroer_team>/
    # import ipdb; ipdb.set_trace()
    exception_occured = ''
    oid_name_dict = {}
    try:
        group_id = ObjectId(group_name_or_id)
    except Exception as e:
        group_name, group_id = get_group_name_id(group_name_or_id)
        oid_name_dict[group_id] = group_name

    gsystem_structure_dict = GSystem.structure
    gsystem_keys = gsystem_structure_dict.keys()

    gst_all_fields_dict = {i: 1 for i in gsystem_keys}
    gst_api_fields_dict = { "_id": 1, "name": 1, "altnames": 1, "language": 1, "content": 1, "if_file": 1, "tags": 1, "location": 1, "created_by": 1, "modified_by": 1, "contributors": 1, "legal": 1, "rating": 1, "created_at": 1, "last_update": 1, "collection_set": 1, "post_node": 1, "prior_node": 1, "access_policy": 1, "status": 1, "group_set": 1, "member_of": 1, "type_of": 1,
    # "relation_set": 1, "attribute_set": 1, 
     }

    query_dict = {
                    '_type': 'GSystem',
                    'group_set': ObjectId(group_id),
                    'status': u'PUBLISHED',
                    'access_policy': 'PUBLIC',
                    # 'member_of': ObjectId(gst_id),
                    # 'created_by': user_id,
                }

    sample_gs = GSystem()
    attributes = {}

    # GET parameters:
    get_parameters_dict = request.GET.dict()
    
    get_created_by = request.GET.get('created_by', None)
    if get_created_by:
        username_or_id_int = 0
        try:
            username_or_id_int = int(get_created_by)
        except Exception as e:
            pass

        auth_obj = node_collection.one({'_type': u'Author', '$or': [{'name': unicode(get_created_by)}, {'created_by': username_or_id_int} ] })
        if auth_obj:
            oid_name_dict[auth_obj._id] = auth_obj.name
            # user_id = auth_obj.created_by
            get_parameters_dict['created_by'] = auth_obj.created_by
        else:
            return HttpResponse('Requested user does not exists.', content_type='text/plain')

    get_resource_type = request.GET.get('resource_type', None)
    if get_resource_type:
        try:
            gst_id = ObjectId(get_resource_type)
        except Exception as e:
            gst_name, gst_id = GSystemType.get_gst_name_id(get_resource_type)
            oid_name_dict[gst_id] = gst_name
            get_parameters_dict['member_of'] = gst_id
            attributes = sample_gs.get_possible_attributes([gst_id]) 

    for key, val in get_parameters_dict.iteritems():
        # if ('gs_' in key):
            # stripped_key = key.lstrip('gs_').split('.')[0]
        stripped_key = key.split('.')[0]
        if stripped_key in gsystem_keys:
            # query_dict.update({key: {'$regex': val, '$options': 'i'}})
            query_dict.update({key: ({'$regex': val, '$options': 'i'} if isinstance(val, basestring or unicode) else val) })

        elif stripped_key in gst_attributes(gst_id):
            query_dict.update({('attribute_set.' + stripped_key): {'$regex': val, '$options': 'i'}})

    print "query_dict: ", query_dict

    human = eval(request.GET.get('human', '1'))

    gst_fields = gst_api_fields_dict if human else gst_all_fields_dict

    all_resources = node_collection.find(query_dict, gst_fields)


    if human:
        gst_fields = gst_api_fields_dict

        # converting ids to human readable names:
        # Django User:
        user_fields = ['created_by', 'modified_by', 'contributors']
        all_users = []
        for each_field in user_fields:
            all_users += all_resources.distinct(each_field)
        all_users = list(set(all_users))

        userid_name_dict_cur = node_collection.find({'_type': u'Author', 'created_by': {'$in': all_users}}, {'name': 1, 'created_by': 1, '_id': 0})
        userid_name_dict = {i['created_by']: i['name'] for i in userid_name_dict_cur}


        # Mongo ids
        oid_fields = [ k for k, v in gsystem_structure_dict.iteritems() if v in [bson.objectid.ObjectId, [bson.objectid.ObjectId]] ]
        all_oid_list = []
        for each_field in oid_fields:
            all_oid_list += all_resources.distinct(each_field)
        all_oid_list = list(set(all_oid_list))

        oid_name_dict_cur = node_collection.find({'_id': {'$in': all_oid_list}}, {'name': 1})
        oid_name_dict = {i['_id']: i['name'] for i in oid_name_dict_cur}



        python_cur_list = []
        python_cur_list_append = python_cur_list.append
        for each_gst in all_resources:

            # attaching attributes:
            # NEEDS to optimize.
            for key, value in each_gst.get_possible_attributes(each_gst.member_of).iteritems():
                each_gst[key] = value['data_type']
                each_gst[key] = value['object_value']

            # mapping user id to username.
            for each_field in user_fields:
                each_gst[each_field] = [userid_name_dict[i] for i in each_gst[each_field]] if isinstance(each_gst[each_field], list) else userid_name_dict[each_gst[each_field]]


            # mapping mongo _id to name.
            for each_field in oid_fields:
                each_gst[each_field] = [oid_name_dict[i] for i in each_gst[each_field]] if isinstance(each_gst[each_field], list) else oid_name_dict[each_gst[each_field]]


            python_cur_list_append(each_gst)

        json_result = json.dumps(python_cur_list, cls=NodeJSONEncoder)

    else:
        json_result = dumps(all_resources)

    return HttpResponse(json_result, content_type='application/json')


# helper methods:
def gst_attributes(gst_name_or_id):

    try:
        gst_id = ObjectId(gst_name_or_id)
    except Exception as e:
        gst_name, gst_id = GSystemType.get_gst_name_id(gst_name_or_id)

    return [at.name for at in node_collection.find({'_type': 'AttributeType', 'subject_type': gst_id})]
