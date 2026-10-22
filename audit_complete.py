import re

with open('sgt-siaaf/specs/001-tramite-titulacion/tasks.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Verificar todas las tareas T001-T046
task_ids = re.findall(r'\*\*ID:\*\* `T(\d{3})`', content)
task_nums = sorted([int(t) for t in task_ids])
print(f'Tareas encontradas: {len(task_ids)} (T{task_nums[0]:03d} a T{task_nums[-1]:03d})')
print(f'Secuencia completa: {task_nums == list(range(1, 47))}')

# 2. Verificar secciones de paquetes
packages = re.findall(r'### PAQUETE (\d+): (.+)', content)
print(f'\nPaquetes encontrados: {len(packages)}')
for num, name in packages:
    print(f'  Paquete {num}: {name}')

# 3. Verificar requisitos en matriz de trazabilidad
req_rows = re.findall(r'\|\s*\*\*(RF|RNF)-\d+\*\*', content)
unique_reqs = set(re.findall(r'\*\*(RF|RNF)-\d+\*\*', content))
print(f'\nRequisitos en matriz: {len(req_rows)} filas, {len(unique_reqs)} únicos')
print(f'Requisitos únicos: {sorted(unique_reqs)}')

# 4. Verificar decisiones (DEC)
decisions = re.findall(r'DEC-\d+', content)
print(f'\nDecisiones referenciadas: {len(set(decisions))} únicas: {sorted(set(decisions))}')

# 5. Verificar artículos RRA-UNL
articles = re.findall(r'Art\.\s*\d+', content)
print(f'Artículos RRA-UNL referenciados: {len(set(articles))} únicos: {sorted(set(articles))}')

# 6. Verificar principios constitucionales
principles = re.findall(r'Principio C-\d+', content)
print(f'Principios constitucionales: {len(set(principles))} únicos: {sorted(set(principles))}')

# 6. Verificar checklist final
checklist = re.findall(r'- \[x\] (.+)', content)
print(f'\nChecklist items: {len(checklist)}')
for i, item in enumerate(checklist, 1):
    print(f'  {i}. {item[:100]}...')

# 7. Verificar historias de usuario
husers = re.findall(r'HU-\d+', content)
print(f'\nHistorias de usuario: {len(set(husers))} únicas: {sorted(set(husers))}')

# 8. Verificar casos de uso / AC
cacasos = re.findall(r'CA-\d+', content)
print(f'Casos de uso/AC: {len(set(cacasos))} únicos: {sorted(set(cacasos))}')

# 9. Verificar ambigüedades resueltas
aps = re.findall(r'AP-\d+', content)
print(f'Ambiguedades resueltas: {len(set(aps))} únicas: {sorted(set(aps))}')

# 10. Verificar evidencias de archivos
evidence_files = re.findall(r'Evidencia:.*?([\w./_-]+\.(?:py|md|yaml|yml|txt))', content)
print(f'\nArchivos de evidencia referenciados: {len(evidence_files)}')
for f in evidence_files[:10]:
    print(f'  {f}')

# 11. Verificar componentes afectados
components = re.findall(r'\*\*Componente Afectado:\*\* `([^`]+)`', content)
print(f'\nComponentes afectados únicos: {len(set(components))}')

# 12. Verificar dependencias circulares (ya verificado antes)
print('\n✅ Verificación completa')