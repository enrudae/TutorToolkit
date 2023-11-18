from django.urls import path, include
from rest_framework import routers
from apps.education_plan.views import AddStudentToInvitations, InvitationsViewSet, GetEducationPlan

router = routers.DefaultRouter()
router.register('invitation', InvitationsViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
    path('invite/<str:invite_code>/', AddStudentToInvitations.as_view()),
    path('get_education_plan/<int:invitation_id>/', GetEducationPlan.as_view()),
]
