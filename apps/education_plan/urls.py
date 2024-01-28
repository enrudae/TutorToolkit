from django.urls import path, include
from rest_framework import routers
from apps.education_plan.views import CheckPossibilityOfAddingByInviteCode, EducationPlanViewSet, ModuleViewSet, \
    CardViewSet, LabelViewSet, GetUsersData, AddStudentToTeacherByInviteCode

router = routers.DefaultRouter()
router.register('module', ModuleViewSet, basename='module')
router.register('card', CardViewSet, basename='card')
router.register('label', LabelViewSet, basename='label')
router.register('', EducationPlanViewSet, basename='education_plan')

urlpatterns = [
    path('', include(router.urls)),
    path('invite/<str:invite_code>/', CheckPossibilityOfAddingByInviteCode.as_view()),
    path('get_users_data', GetUsersData.as_view(), name='get_users_data'),
    path('invite_authorized_student', AddStudentToTeacherByInviteCode.as_view(), name='invite_authorized_student'),

]
