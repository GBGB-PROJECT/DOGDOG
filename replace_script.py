import os
import glob

files = glob.glob('backend/**/*.py', recursive=True)
for filepath in files:
    if 'test_' in filepath: continue
    if not os.path.isfile(filepath): continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'get_current_user_id' in content:
        new_content = content.replace('get_current_user_id', 'get_current_user')
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
