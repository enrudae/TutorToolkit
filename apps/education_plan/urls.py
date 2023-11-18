from django.urls import path, include
from rest_framework import routers
from apps.education_plan.views import AddStudentToEducationPlan, EducationPlanViewSet, GetEducationPlan

router = routers.DefaultRouter()
router.register('', EducationPlanViewSet, basename='education_plan')

urlpatterns = [
    path('', include(router.urls)),
    path('invite/<str:invite_code>/', AddStudentToEducationPlan.as_view()),
    path('get_education_plan/<int:plan_id>/', GetEducationPlan.as_view()),
]
