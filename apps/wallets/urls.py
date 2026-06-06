from rest_framework.routers import DefaultRouter

from apps.wallets.views import WalletViewSet


router = DefaultRouter()
router.register("wallets", WalletViewSet, basename="wallet")

urlpatterns = router.urls
