# Gobernanza

## 1. Modelo central: colaboración abierta, admisión curada

WorldWORDS ANTIBIBEL está abierto a contribuciones, pero el registro oficial no es un canon mayoritario que crece automáticamente. Cualquiera puede presentar material. Daniel, como curador fundador, decide qué términos quiere admitir en el registro oficial.

Esta autoridad solo se aplica a la etiqueta **«admitido por Daniel en el registro oficial de WorldWORDS»**. No limita los forks ni el derecho de otras personas a mantener registros con decisiones distintas.

## 2. Contribuciones posibles

Las contribuciones pueden incluir:

- palabras brutas nuevas y variantes ortográficas,
- fuentes exactas y entradas originales,
- historias de origen,
- interpretaciones y contra-interpretaciones,
- límites y significados expresamente excluidos,
- traducciones de las explicaciones,
- encarnaciones reales en proyectos, archivos, funciones o sistemas,
- correcciones de procedencia,
- avisos sobre alucinaciones o atribuciones falsas.

## 3. Flujo de estados

`SUBMITTED → EVIDENCE_CHECK → DANIEL_REVIEW → ACCEPTED / DEFERRED / DECLINED / WITHDRAWN`

Estados posteriores:

`ACTIVE → SUPERSEDED / DEPRECATED / RETIRED`

Ningún cambio de estado borra la historia anterior. Los cambios se añaden como eventos nuevos.

## 4. Decisiones de Daniel

Daniel puede admitir una contribución:

- como término independiente,
- como variante ortográfica,
- como traducción o mutación lingüística,
- como interpretación de un término existente,
- aplazarla para buscar más fuentes,
- rechazarla,
- cerrarla porque no puede publicarse legalmente.

La admisión solo es oficial cuando existe un archivo en `data/approvals/` que registra como mínimo la ID del término, la decisión, la fecha, Daniel como responsable y una justificación.

## 5. Procedencia inmutable

En los términos admitidos se conservan como mínimo:

- la forma y capitalización originales,
- quien presentó o transmitió el término,
- el estado conocido de autoría, incluida la incertidumbre,
- la fecha o la incertidumbre de fecha explícita,
- la cita original o el cuerpo exacto de entrada,
- la referencia de fuente y su hash cuando exista,
- interpretaciones anteriores,
- responsables de traducción,
- la decisión de admisión de Daniel.

Las atribuciones erróneas se corrigen, pero no se sobrescriben en silencio. El evento antiguo permanece marcado como `corrected` o `retracted`.

## 6. Procedencia persona–IA

Las contribuciones de IA no se presentan en bloque como autoría humana. Cuando sea posible se separan:

- operador humano,
- sistema o modelo de IA,
- sesión o cuerpo de conversación,
- formulación exacta de la IA,
- selección, modificación o confirmación humana,
- incertidumbre sobre el nacimiento real de la palabra.

Un campo `role=user`, una atribución de base de datos o un resumen posterior no bastan para probar autoría.

## 7. Forma bruta y traducción

La forma bruta de la palabra permanece intacta. Las versiones lingüísticas traducen la **explicación**, no sustituyen la palabra a escondidas. Una forma traducida o mutada puede proponerse como contribución separada con su propia procedencia.

## 8. Seguridad y privacidad

Conservar la crudeza no exige publicar credenciales, direcciones privadas, datos personales inéditos ni textos completos protegidos de terceros. Las omisiones necesarias se registran de forma visible. La procedencia pública puede apuntar a un origen privado mediante hash cuando publicarlo no sea legal.

## 9. Forks y etiqueta oficial

Los forks pueden modificar todo el material licenciado y crear sus propios mecanismos de admisión. El campo `accepted_by_daniel: true` solo puede utilizarse con un registro de decisión de Daniel intacto o continuado de forma trazable.

## 10. Cambios de gobernanza

Los cambios de gobernanza se tratan como propuestas. La regla sobre quién decide la admisión en el registro principal oficial solo puede modificarse mediante una decisión explícita y documentada de Daniel.
