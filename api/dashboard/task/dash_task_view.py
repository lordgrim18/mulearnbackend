import uuid
from rest_framework.views import APIView
from db.task import TaskList
from utils.permission import CustomizePermission, JWTUtils, RoleRequired
from utils.response import CustomResponse
from utils.types import RoleType
from utils.utils import CommonUtils, DateTimeUtils
from .dash_task_serializer import TaskListSerializer


class TaskApi(APIView):
    # authentication_classes = [CustomizePermission]
    def get(self, request):
        task_serializer = TaskList.objects.all()
        paginated_queryset = CommonUtils.get_paginated_queryset(task_serializer, request, ["id",
                                                                                           "hashtag",
                                                                                           "title",
                                                                                           "karma",
                                                                                           "channel",
                                                                                           "type",
                                                                                           "active",
                                                                                           "variable_karma",
                                                                                           "usage_count",
                                                                                           "created_by",
                                                                                           "created_at"])
        task_serializer_data = TaskListSerializer(paginated_queryset.get('queryset'), many=True).data

        return CustomResponse(response={
            "taskLists": task_serializer_data,
            'pagination': paginated_queryset.get('pagination')
        }).get_success_response()

    @RoleRequired(roles=[RoleType.ADMIN, ])
    def post(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        task_data = TaskList.objects.create(
            id=uuid.uuid4(),
            hashtag=request.data.get('hashtag'),
            title=request.data.get('title'),
            description=request.data.get('description'),
            karma=request.data.get('karma'),
            channel=request.data.get('channel'),
            active=request.data.get('active'),
            variable_karma=request.data.get('variable_karma'),
            usage_count=request.data.get('usage_count'),
            updated_by_id=user_id,
            updated_at=DateTimeUtils.get_current_utc_time(),
            created_by_id=user_id,
            created_at=DateTimeUtils.get_current_utc_time())
        serializer = TaskListSerializer(task_data)
        return CustomResponse(response={"taskList": serializer.data}).get_success_response()

    @RoleRequired(roles=[RoleType.ADMIN, ])
    def put(self, request, pk):
        user_id = JWTUtils.fetch_user_id(request)
        taskData = TaskList.objects.get(id=pk)
        fields_to_update = ["hashtag",
                            "title",
                            "karma",
                            "channel",
                            "type",
                            "active",
                            "variable_karma",
                            "usage_count"]
        for field in fields_to_update:
            if field in request.data:
                setattr(taskData, field, request.data[field])
        taskData.updated_by = user_id
        taskData.updated_at = DateTimeUtils.get_current_utc_time()
        taskData.save()
        serializer = TaskListSerializer(taskData)
        print(serializer.data)
        return CustomResponse(
            response={"taskList": serializer.data}
        ).get_success_response()

    @RoleRequired(roles=[RoleType.ADMIN, ])
    def patch(self, request, pk):
        user_id = JWTUtils.fetch_user_id(request)
        taskData = TaskList.objects.filter(id=pk).first()
        taskData.active = False
        taskData.updated_by = user_id
        taskData.updated_at = DateTimeUtils.get_current_utc_time()
        taskData.save()
        serializer = TaskListSerializer(taskData)
        return CustomResponse(
            response={"taskList": serializer.data}
        ).get_success_response()