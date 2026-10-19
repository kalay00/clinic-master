import os, re, subprocess

root = os.path.join(os.path.dirname(__file__), 'src')
views = os.path.join(root, 'views')

# collect all .vue files under views
vue_files = []
for dp, _, fns in os.walk(views):
    for fn in fns:
        if fn.endswith('.vue'):
            vue_files.append(os.path.relpath(os.path.join(dp, fn), views))

# For each vue file, check if referenced by ANY import in src (js or vue).
# Reference forms:
#   @/views/<relpath>
#   relative: ./<x>.vue or ../<x>.vue from some other file. We'll detect by basename+ext uniqueness:
#   if a file imports a path ending with the same basename AND the resolved path equals this file.
# Simplest robust: for each candidate, search whole src for a string that resolves to it.

def is_referenced(vf):
    vf_norm = vf.replace(os.sep, '/')
    # 1) absolute @/views/ reference
    pat = re.escape('@/views/' + vf_norm)
    r = subprocess.run(['grep','-rqE',pat], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode == 0:
        return True
    # 2) relative reference: scan all vue/js files, parse import/require paths, resolve, compare
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if not (fn.endswith('.vue') or fn.endswith('.js')):
                continue
            src_file = os.path.join(dp, fn)
            try:
                with open(src_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue
            for m in re.finditer(r"""from\s+['"]([^'"]+)['"]|import\(['"]([^'"]+)['"]\)|require\(['"]([^'"]+)['"]\)""", content):
                spec = m.group(1) or m.group(2) or m.group(3)
                if not spec:
                    continue
                if spec.startswith('@/views/'):
                    continue  # handled above
                if spec.startswith('.') and spec.endswith('.vue'):
                    base_dir = os.path.dirname(src_file)
                    resolved = os.path.normpath(os.path.join(base_dir, spec))
                    rel = os.path.relpath(resolved, views).replace(os.sep, '/')
                    if rel == vf_norm:
                        return True
    return False

unused = [v for v in vue_files if not is_referenced(v)]
print("TOTAL vue:", len(vue_files))
print("UNUSED count:", len(unused))
for u in sorted(unused):
    print(u)
