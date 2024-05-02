from django.urls import path, include
from rest_framework import routers
from apps.education_plan.views import GetInviteInfoByCode, EducationPlanViewSet, ModuleViewSet, \
    CardViewSet, LabelViewSet, GetUsersData, test_send, AddStudentToTeacherByInviteCode, ChangeOrderOfElements, \
    TutorFilesView

router = routers.DefaultRouter()
router.register('module', ModuleViewSet, basename='module')
router.register('card', CardViewSet, basename='card')
router.register('label', LabelViewSet, basename='label')
router.register('', EducationPlanViewSet, basename='education_plan')

urlpatterns = [
    path('', include(router.urls)),
    path('invite_info/<str:invite_code>/', GetInviteInfoByCode.as_view()),
    path('get_users_data', GetUsersData.as_view(), name='get_users_data'),
    path('invite_authorized_student', AddStudentToTeacherByInviteCode.as_view(), name='invite_authorized_student'),
    path('test_send', test_send.as_view()),
    path('move_element', ChangeOrderOfElements.as_view(), name='move_element'),
    path('files', TutorFilesView.as_view(), name='tutor-files'),
]
