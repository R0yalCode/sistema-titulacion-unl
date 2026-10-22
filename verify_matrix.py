import re

with open('sgt-siaaf/specs/001-tramite-titulacion/tasks.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Count requirements in traceability matrix
req_rows = re.findall(r'\|\s*\*\*(RF|RNF)-\d+\*\*', content)
print('Requirements in traceability matrix:', len(req_rows))
print('Unique requirements:', len(set(req_rows)))

# Count tasks in traceability matrix
task_refs = re.findall(r'\`T(\d{3})\`', content)
task_refs_in_matrix = [t for t in task_refs if t in [f'{i:03d}' for i in range(1,47)]]
print('Task references in matrix:', len(task_refs_in_matrix))
print('Unique tasks referenced in matrix:', len(set(task_refs_in_matrix)))

# Check checklist items
checklist_items = re.findall(r'- \[x\] (.+)', content)
print('Checklist items checked:', len(checklist_items))
for item in checklist_items:
    print('  -', item[:80])