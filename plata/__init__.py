VERSION = (1, 2, 0, 'pre')
__version__ = '.'.join(map(str, VERSION))


import logging
logger = logging.getLogger('plata')


class LazySettings(object):
    def _load_settings(self):
        from plata import default_settings
        from django.conf import settings as django_settings

        for key in dir(default_settings):
            if not key.startswith(('PLATA', 'CURRENCIES')):
                continue

            setattr(self, key, getattr(django_settings, key,
                getattr(default_settings, key)))

    def __getattr__(self, attr):
        self._load_settings()
        del self.__class__.__getattr__
        return self.__dict__[attr]

settings = LazySettings()


shop_instance_cache = None
def register(instance):
    logger.debug('Registering shop instance: %s' % instance)

    global shop_instance_cache
    shop_instance_cache = instance

def shop_instance():
    """
    This method ensures that all views and URLs are properly loaded, and
    returns the centrally instantiated :class:`plata.shop.views.Shop` object.
    """

    if not shop_instance_cache:
        # Load default URL patterns to ensure that the shop
        # object has been created
        from django.core.urlresolvers import get_resolver
        get_resolver(None)._populate()

    return shop_instance_cache

def product_model():
    """
    Return the product model defined by the ``PLATA_SHOP_PRODUCT`` setting.
    """
    from django.db.models import loading
    return loading.get_model(*settings.PLATA_SHOP_PRODUCT.split('.'))

def tax_model():
    """
    Return the tax model defined by the ``PLATA_TAX_MODEL`` setting.
    """
    from django.db.models import loading
    return loading.get_model(*settings.PLATA_TAX_MODEL.split('.'))

def stock_model():
    """
    Return the stock transaction model definded by the ``PLATA_STOCK_TRACKING_MODEL``
    setting or None in case stock transactions are turned off.
    """
    if not settings.PLATA_STOCK_TRACKING:
        return None
    from django.db.models import loading
    return loading.get_model(*settings.PLATA_STOCK_TRACKING_MODEL.split('.'))
