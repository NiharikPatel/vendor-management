from django.apps import AppConfig

# from vendor_management import vendor_app


class VendorAppConfig(AppConfig):
    name = 'vendor_app'

    def ready(self):
       import vendor_app.signals




