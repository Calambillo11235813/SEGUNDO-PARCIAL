from django.apps import AppConfig

class MachineLearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'machine_learning'
    verbose_name = 'Machine Learning'
    
    def ready(self):
        """Configuración inicial cuando la app está lista"""
        import logging
        
        # Configurar logging para ML
        logger = logging.getLogger('machine_learning')
        logger.info("Aplicación Machine Learning iniciada correctamente")