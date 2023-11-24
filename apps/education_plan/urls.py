from django.urls import path, include
from rest_framework import routers
from apps.education_plan.views import AddStudentToEducationPlan, EducationPlanViewSet, ModuleViewSet, CardViewSet, \
    LabelViewSet

router = routers.DefaultRouter()
router.register('', EducationPlanViewSet, basename='education_plan')
router.register('module', ModuleViewSet, basename='module')
router.register('card', CardViewSet, basename='card')
router.register('label', LabelViewSet, basename='label')

urlpatterns = [
    path('', include(router.urls)),
    path('invite/<str:invite_code>/', AddStudentToEducationPlan.as_view()),
]
