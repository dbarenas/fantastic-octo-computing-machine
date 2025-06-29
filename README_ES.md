# fantastic-octo-computing-machine

## 1. Descripción General del Proyecto

`fantastic-octo-computing-machine` es un sistema de procesamiento de documentos diseñado para extraer automáticamente información de diversos tipos de documentos, validar esta información y almacenarla para su uso posterior. Utiliza AWS Textract para el Reconocimiento Óptico de Caracteres (OCR) y una arquitectura modular para admitir diferentes formatos de documentos y lógica de procesamiento personalizada.

## 2. Componentes Principales

El sistema está organizado en varios módulos clave:

*   **`aws_lib/`**: Contiene funciones de utilidad para interactuar con los servicios de AWS.
    *   `s3.py`: Funciones para operaciones con buckets de S3 (aunque no son utilizadas directamente por `BaseExtractor` para cargar texto, que usa `boto3` a través de `aws_lib.textract`).
    *   `textract.py`: Maneja la extracción de texto de documentos almacenados en S3 utilizando AWS Textract.
*   **`document_processor/`**: La lógica principal de la aplicación reside aquí.
    *   **`base/`**:
        *   `base_extractor.py`: Define la clase abstracta `BaseExtractor`, de la cual deben heredar todos los extractores de documentos específicos.
        *   `base_validator.py`: Define la clase abstracta `BaseValidator`, de la cual deben heredar todos los validadores de documentos específicos.
    *   **`classifier.py`**: (Funcionalidad asumida) Responsable de determinar el tipo de un documento según su contenido.
    *   **`config.py`**: Almacena configuraciones generales del sistema, como configuraciones de logging, región de AWS y, potencialmente, rutas o parámetros para diferentes tipos de documentos.
    *   **`db/`**: Gestiona las interacciones con la base de datos.
        *   `database.py`: (Asumido) Contiene la configuración de la conexión a la base de datos.
        *   `insert.py`: (Asumido) Contiene funciones para insertar datos procesados en la base de datos.
        *   `models/`: Define el esquema de la base de datos utilizando SQLAlchemy o un ORM similar.
        *   `query.py`: (Asumido) Contiene funciones para consultar datos de la base de datos.
    *   **`extractors/`**: Contiene implementaciones específicas de extractores para diferentes tipos de documentos (p. ej., `certificado_final.py`, `facturas.py`).
    *   **`validators/`**: Contiene implementaciones específicas de validadores para diferentes tipos de documentos (p. ej., `certificado_final_validator.py`, `facturas_validator.py`).
    *   **`processor_factory.py`**: Un componente crucial que mapea los tipos de documentos a sus respectivas clases de extractor y validador. Proporciona una función `get_processor` para recuperar las herramientas de procesamiento correctas.
    *   **`pipeline.py`**: Orquesta todo el flujo de procesamiento de documentos, desde la extracción de texto hasta la validación y el almacenamiento.
    *   **`main.py`**: (Asumido) El punto de entrada principal para ejecutar el sistema de procesamiento de documentos.
    *   **`api.py`**: (Asumido) Si está presente, definiría una API para interactuar con el sistema de procesamiento de documentos (p. ej., cargar documentos, recuperar datos procesados).
    *   **`utils/`**: Contiene diversas funciones de utilidad para tareas como manipulación de fechas, operaciones de archivos, procesamiento de texto, etc.
*   **`tests/`**: Contiene pruebas de integración o a nivel de sistema.
*   **`document_processor/tests/`**: Contiene pruebas unitarias para los componentes dentro del módulo `document_processor`.

## 3. Flujo de Trabajo del Procesamiento de Documentos

El flujo de trabajo típico para procesar un documento es el siguiente:

1.  **Carga del Documento**: Se carga un documento (p. ej., a un bucket de S3).
2.  **Extracción de Texto (OCR)**: `DocumentProcessingPipeline` (a menudo a través de `aws_lib.textract`) extrae el texto sin formato del documento.
3.  **Clasificación**: El texto extraído es analizado por `DocumentClassifier` para determinar su tipo (p. ej., "factura", "certificado_final").
4.  **Selección del Procesador**: Se llama a la función `processor_factory.get_processor` con el tipo de documento y el texto extraído. Devuelve una instancia de `DocumentProcessor` que contiene el extractor y validador apropiados.
5.  **Extracción de Datos**: Se llama al método `extract()` del extractor seleccionado para obtener campos específicos del texto sin formato.
6.  **Validación de Datos**: Se llama al método `validate()` del validador seleccionado con los datos extraídos para verificar su corrección y coherencia con las reglas predefinidas.
7.  **Almacenamiento**: Los metadatos del documento original, el texto sin formato (o su ruta), los datos extraídos y los resultados de la validación se almacenan en una base de datos (p. ej., utilizando funciones de `db.insert`).
8.  **Salida**: El pipeline devuelve una representación estructurada del documento procesado.

## 4. Configuración

El archivo `document_processor/config.py` está destinado a contener parámetros generales del sistema. Esto podría incluir:

*   Configuraciones de AWS (p. ej., región, nombres de bucket de S3).
*   Cadenas de conexión a la base de datos.
*   Niveles y formatos de logging.
*   Constantes o umbrales utilizados en la lógica de extracción o validación.

Asegúrese de que este archivo esté configurado correctamente para su entorno.

## 5. Integración de un Nuevo Extractor

Para procesar un nuevo tipo de documento, deberá crear un extractor personalizado.

### 5.1. Crear la Clase del Extractor

Cree un nuevo archivo Python en el directorio `document_processor/extractors/` (p. ej., `mi_nuevo_extractor_documento.py`). En este archivo, defina una clase que herede de `BaseExtractor`:

```python
# document_processor/extractors/mi_nuevo_extractor_documento.py
from document_processor.base.base_extractor import BaseExtractor
# Importar cualquier otra utilidad necesaria (p. ej., regex, análisis de fechas)
import re

class MiNuevoExtractorDocumento(BaseExtractor):
    def __init__(self, bucket_name: str, document_key: str):
        super().__init__(bucket_name, document_key)
        # self.text ahora es cargado por el método _load_text_from_s3 de la clase padre

    def extract(self) -> dict:
        """
        Extrae información específica del texto del documento.
        """
        extracted_data = {
            "document_type": "MiNuevoTipoDocumento", # Importante para clasificación/enrutamiento
            "title": None,
            "date": None,
            "amount": None,
            # Agregue otros campos relevantes para su nuevo tipo de documento
        }

        # Ejemplo: Extraer un título usando una expresión regular simple
        title_match = re.search(r"Title:\s*(.*)", self.text, re.IGNORECASE)
        if title_match:
            extracted_data["title"] = title_match.group(1).strip()

        # Ejemplo: Extraer una fecha (podría usar un análisis de fechas más robusto)
        date_match = re.search(r"Date:\s*(\d{2}/\d{2}/\d{4})", self.text)
        if date_match:
            extracted_data["date"] = date_match.group(1).strip()

        # ... implementar más lógica de extracción para otros campos ...

        return extracted_data

```

**Puntos clave para el uso de `BaseExtractor`:**

*   El método `__init__` de su nuevo extractor debe llamar a `super().__init__(bucket_name, document_key)`.
*   El método `__init__` de `BaseExtractor` llama automáticamente a `_load_text_from_s3()`, que utiliza `aws_lib.textract.extract_text_from_document` para obtener y almacenar el contenido de texto del documento en `self.text`.
*   El método `extract()` debe ser implementado. Debe devolver un diccionario que contenga los pares clave-valor extraídos.

### 5.2. Implementar Lógica de Extracción

Dentro del método `extract()`, use manipulación de cadenas, expresiones regulares u otras técnicas de análisis para encontrar y recuperar la información requerida de `self.text`.

## 6. Integración de un Nuevo Validador

Después de extraer los datos, a menudo es necesario validarlos.

### 6.1. Crear la Clase del Validador

Cree un nuevo archivo Python en el directorio `document_processor/validators/` (p. ej., `mi_nuevo_validador_documento.py`). Defina una clase que herede de `BaseValidator`:

```python
# document_processor/validators/mi_nuevo_validador_documento.py
from document_processor.base.base_validator import BaseValidator
# Importar cualquier utilidad de validación necesaria (p. ej., comprobación de fechas)
from datetime import datetime

class MiNuevoValidadorDocumento(BaseValidator):
    def __init__(self, data: dict):
        super().__init__(data)
        # self.data ahora contiene el diccionario del extractor

    def validate(self) -> dict:
        """
        Valida los datos extraídos.
        Devuelve un diccionario con el estado de validación y detalles.
        """
        validation_results = {
            "is_valid": True, # Validez general
            "details": {},    # Mensajes de validación específicos del campo
            "errors": []      # Lista de mensajes de error
        }

        # Ejemplo: Validar el campo 'title'
        title = self.data.get("title")
        if not title or len(title) < 5:
            validation_results["is_valid"] = False
            validation_results["details"]["title"] = "El título falta o es demasiado corto."
            validation_results["errors"].append("Título inválido.")

        # Ejemplo: Validar el campo 'date'
        date_str = self.data.get("date")
        if date_str:
            try:
                datetime.strptime(date_str, "%d/%m/%Y")
                validation_results["details"]["date"] = "El formato de fecha es válido."
            except ValueError:
                validation_results["is_valid"] = False
                validation_results["details"]["date"] = "El formato de fecha es inválido. Se esperaba DD/MM/YYYY."
                validation_results["errors"].append("Formato de fecha inválido.")
        else:
            validation_results["is_valid"] = False
            validation_results["details"]["date"] = "Falta la fecha."
            validation_results["errors"].append("Falta la fecha.")

        # ... implementar más lógica de validación ...

        # Si ocurrió algún error, establecer la validez general en False
        if validation_results["errors"]:
            validation_results["is_valid"] = False

        return validation_results
```

**Puntos clave para el uso de `BaseValidator`:**

*   El método `__init__` de su nuevo validador debe llamar a `super().__init__(data)`, donde `data` es el diccionario devuelto por su extractor correspondiente.
*   El método `validate()` debe ser implementado. Debe devolver un diccionario que típicamente contenga:
    *   `is_valid` (bool): Estado de validez general.
    *   `details` (dict, opcional): Mensajes o estados de validación específicos del campo.
    *   `errors` (list, opcional): Una lista de mensajes de error específicos si la validación falla.

## 7. Registro de Nuevos Componentes

Después de crear su nuevo extractor y validador, debe registrarlos en el diccionario `PROCESSOR_MAPPING` dentro de `document_processor/processor_factory.py`.

1.  **Importe sus nuevas clases** en la parte superior de `document_processor/processor_factory.py`:

    ```python
    # ... otras importaciones ...
    from document_processor.extractors.mi_nuevo_extractor_documento import MiNuevoExtractorDocumento
    from document_processor.validators.mi_nuevo_validador_documento import MiNuevoValidadorDocumento
    # ...
    ```

2.  **Agregue una entrada a `PROCESSOR_MAPPING`**:
    Use una clave única para su nuevo tipo de documento (esta clave será utilizada por el clasificador u otras partes del sistema para identificar el tipo de documento).

    ```python
    PROCESSOR_MAPPING = {
        "certificado_final": {
            "extractor": CertificadoFinalExtractor,
            "validator": CertificadoFinalValidator,
        },
        "factura": {
            "extractor": FacturaExtractor,
            "validator": FacturaValidator,
        },
        # ... otros mapeos existentes ...
        "mi_nueva_clave_tipo_documento": { # Esta clave debe coincidir con lo que identifica su clasificador
            "extractor": MiNuevoExtractorDocumento,
            "validator": MiNuevoValidadorDocumento,
        },
        # ...
    }
    ```

## 8. Ejecución del Sistema

El sistema normalmente se inicia a través de `DocumentProcessingPipeline`. Esto podría ser activado por:

*   Un script principal (`document_processor/main.py`) que monitorea un bucket de S3 o una cola para nuevos documentos.
*   Un endpoint de API (definido en `document_processor/api.py`) que acepta cargas de documentos.

El pipeline luego usará el clasificador y `processor_factory` para procesar el documento con su extractor y validador recién integrados.

## 9. Pruebas (Testing)

Es crucial agregar pruebas para sus nuevos componentes:

*   **Pruebas del Extractor**: Cree pruebas en `document_processor/tests/` (p. ej., `test_mi_nuevo_extractor_documento.py`) para verificar que su extractor analiza correctamente los textos de documentos de muestra. Es posible que necesite simular (mock) la carga de texto de S3 si prueba localmente sin acceso directo a AWS, o proporcionar texto de muestra directamente.
*   **Pruebas del Validador**: Cree pruebas para asegurar que su validador identifica correctamente los datos válidos e inválidos según las reglas que ha implementado.

Consulte las pruebas existentes en `document_processor/tests/` para ver ejemplos sobre cómo estructurar sus pruebas (p. ej., `test_certificado_final.py`).

Siguiendo estos pasos, puede extender `fantastic-octo-computing-machine` para admitir nuevos tipos de documentos y lógica de procesamiento personalizada.
