from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ecommerce.views import OrderDetailViewSet, OrderViewSet, ProductViewSet


router = routers.DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'order', OrderViewSet)
router.register(r'order_detail', OrderDetailViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # routers
    re_path(r'^api/(?P<version>v1)/', include(router.urls)),

    # rest_framework
    path('api-auth/', include('rest_framework.urls')),

    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # OpenAPI
    path('openapi-schema/', get_schema_view(
        title='E-commerce example',
        description='E-commerce endpoints',
        version='1.0.0'
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]
