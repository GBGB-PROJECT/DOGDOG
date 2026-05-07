# Domain Routers
from .pets.api.pets_api import router as pets_router
from .users.users_api import router as users_router
from .auth.api.auth_api import router as auth_router
from .logs.api.numeric_api import router as numeric_router
from .home.api.dashboard_api import router as dashboard_router
from .logs.api.logs_api import router as logs_router
from .logs.api.feeding_api import router as feeding_router
from .calc_feeding.calc_feeding_api import router as calc_feeding_router
from .products.products_api import router as products_router
from .onboarding.api.onboarding_api import router as onboarding_router
from .notifications.api.notifications_api import router as notifications_router
from .subscriptions.api.subscriptions_api import router as subscriptions_router
from .images_api import router as images_router