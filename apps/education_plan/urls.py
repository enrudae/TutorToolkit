from django.urls import path, include
from rest_framework import routers
from apps.education_plan.views import EducationPlanViewSet, AddStudentToInvitations, InvitationsViewSet

router = routers.DefaultRouter()
router.register('', EducationPlanViewSet, basename='education_plan')
router.register('invitation', InvitationsViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
    path('invite/<str:invite_code>/', AddStudentToInvitations.as_view()),
]
