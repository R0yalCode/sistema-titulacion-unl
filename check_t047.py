import re

with open('sgt-siaaf/specs/001-tramite-titulacion/tasks.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all task IDs
task_ids = re.findall(r'\*\*ID:\*\* `T(\d{3})`', content)
print('Total task IDs found:', len(task_ids))
print('Task IDs:', sorted(set(task_ids)))

# Check if T047 exists
if '047' in task_ids:
    print('T047 EXISTS')
else:
    print('T047 DOES NOT EXIST in tasks.md')

# Also check the last few lines for any mention of T047
if 'T047' in content:
    print('T047 mentioned somewhere in content')
else:
    print('T047 NOT mentioned anywhere in content')