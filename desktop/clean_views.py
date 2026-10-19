import os, shutil, subprocess

root = os.path.join(os.path.dirname(__file__), 'src')
views = os.path.join(root, 'views')
unused_dir = os.path.join(views, '_unused')

# 重新计算未使用列表（与 scan 一致）
vue_files = []
for dp, _, fns in os.walk(views):
    for fn in fns:
        if fn.endswith('.vue'):
            vue_files.append(os.path.relpath(os.path.join(dp, fn), views))

import re
def is_referenced(vf):
    vf_norm = vf.replace(os.sep, '/')
    pat = re.escape('@/views/' + vf_norm)
    r = subprocess.run(['grep','-rqE',pat], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode == 0:
        return True
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
                if not spec or spec.startswith('@/views/'):
                    continue
                if spec.startswith('.') and spec.endswith('.vue'):
                    resolved = os.path.normpath(os.path.join(os.path.dirname(src_file), spec))
                    rel = os.path.relpath(resolved, views).replace(os.sep, '/')
                    if rel == vf_norm:
                        return True
    return False

moved = 0
for vf in vue_files:
    if vf.startswith('_unused' + os.sep):
        continue
    if is_referenced(vf):
        continue
    src = os.path.join(views, vf)
    dst = os.path.join(unused_dir, vf)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    moved += 1

# 清理空目录
for dp, dirs, fns in os.walk(views, topdown=False):
    for d in dirs:
        full = os.path.join(dp, d)
        if d == '_unused':
            continue
        try:
            if not os.listdir(full):
                os.rmdir(full)
        except OSError:
            pass

print(f"Moved {moved} unused vue files into views/_unused/")
