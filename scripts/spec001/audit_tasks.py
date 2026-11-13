import re

with open('sgt-siaaf/specs/001-tramite-titulacion/tasks.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all task IDs: **ID:** `T001`
task_ids = re.findall(r'\*\*ID:\*\* `T(\d{3})`', content)
print('Total task IDs found:', len(task_ids))
print('Task IDs:', sorted(set(task_ids)))

from collections import Counter
duplicates = [k for k, v in Counter(task_ids).items() if v > 1]
if duplicates:
    print('DUPLICATE IDs:', duplicates)
else:
    print('No duplicate IDs found')

all_ids = set(f'{i:03d}' for i in range(1, 47))
found_ids = set(task_ids)
missing = all_ids - found_ids
extra = found_ids - all_ids
print('Missing IDs (T001-T046):', sorted(missing))
print('Extra IDs:', sorted(extra))

# Now extract all dependencies
# Pattern: **Dependencias:** `T001`, `T002`
dep_matches = re.findall(r'\*\*Dependencias:\*\* ([^\n]*)', content)
all_deps = []
for match in dep_matches:
    deps = re.findall(r'T(\d{3})', match)
    all_deps.extend(deps)

print('\nAll dependency references found:', len(all_deps))
print('Unique dependency references:', sorted(set(all_deps)))

# Check if all dependencies reference valid task IDs
found_ids_set = set(task_ids)
invalid_deps = set(all_deps) - found_ids_set
if invalid_deps:
    print('INVALID DEPENDENCY REFERENCES:', sorted(invalid_deps))
else:
    print('All dependencies reference valid task IDs')

# Check for circular dependencies (simplified - check if any task depends on itself indirectly)
# Build adjacency list
from collections import defaultdict
adj = defaultdict(list)
dep_section_pattern = r'(#### T\d{3}:.*?)(?=#### T|\n---|\Z)'
sections = re.findall(dep_section_pattern, content, re.DOTALL)

# Extract task ID and its dependencies
task_deps = {}
for section in sections:
    id_match = re.search(r'\*\*ID:\*\* `T(\d{3})`', section)
    dep_match = re.search(r'\*\*Dependencias:\*\* ([^\n]*)', section)
    if id_match:
        tid = id_match.group(1)
        deps = re.findall(r'T(\d{3})', dep_match.group(1)) if dep_match else []
        task_deps[tid] = deps

# Check for cycles using DFS
def has_cycle(node, visited, rec_stack):
    visited.add(node)
    rec_stack.add(node)
    for neighbor in task_deps.get(node, []):
        if neighbor not in visited:
            if has_cycle(neighbor, visited, rec_stack):
                return True
        elif neighbor in rec_stack:
            return True
    rec_stack.remove(node)
    return False

visited = set()
rec_stack = set()
has_cycle_flag = False
for node in task_deps:
    if node not in visited:
        if has_cycle(node, visited, rec_stack):
            print('CYCLE DETECTED involving:', node)
            has_cycle_flag = True

if not has_cycle_flag:
    print('No circular dependencies detected')

print('\nAll task IDs with their dependencies:')
for tid in sorted(task_deps.keys()):
    print(f'  T{tid} -> {task_deps[tid]}')