import ctypes
import pyswip

class PrologMT(pyswip.Prolog):
    """
    Implementación de Prolog con soporte para múltiples hilos (Multi-Thread).
    Extiende la funcionalidad básica de pyswip.Prolog para manejar ejecución segura en entornos multi-hilo.
    """
    
    # Acceso a la biblioteca nativa de SWI-Prolog
    _swipl = pyswip.core._lib

    # Configuración de la función PL_thread_self de SWI-Prolog:
    # Obtiene el ID del motor Prolog del hilo actual
    PL_thread_self = _swipl.PL_thread_self
    PL_thread_self.restype = ctypes.c_int  # Devuelve un entero

    # Configuración de la función PL_thread_attach_engine de SWI-Prolog:
    # Crea un nuevo motor Prolog para un hilo
    PL_thread_attach_engine = _swipl.PL_thread_attach_engine
    PL_thread_attach_engine.argtypes = [ctypes.c_void_p]  # Acepta un puntero void
    PL_thread_attach_engine.restype = ctypes.c_int  # Devuelve un código de estado

    @classmethod
    def _init_prolog_thread(cls):
        """
        Inicializa un motor Prolog para el hilo actual.
        Garantiza que cada hilo tenga su propia instancia de motor Prolog.
        
        Excepciones:
            PrologError: Si falla la creación del motor
        """
        # Paso 1: Verificar si el hilo ya tiene un motor
        pengine_id = cls.PL_thread_self()
        
        # Paso 2: Si no tiene motor, crear uno nuevo
        if pengine_id == -1:
            pengine_id = cls.PL_thread_attach_engine(None)
            
        # Paso 3: Verificar si la creación fue exitosa
        if pengine_id == -1:
            raise pyswip.prolog.PrologError("No se pudo crear un motor Prolog para este hilo")

    class _QueryWrapper(pyswip.Prolog._QueryWrapper):
        """
        Envoltura (wrapper) para consultas Prolog que garantiza seguridad en hilos.
        Se ejecuta automáticamente antes de cada consulta.
        """
        
        def __call__(self, *args, **kwargs):
            """
            Ejecuta una consulta Prolog con seguridad para hilos.
            
            Flujo:
            1. Inicializa motor Prolog para el hilo actual
            2. Ejecuta la consulta usando la lógica original
            """
            # Asegurar que el hilo tenga motor Prolog
            PrologMT._init_prolog_thread()
            
            # Ejecutar la consulta normalmente
            return super().__call__(*args, **kwargs)