"""Inspect documentation and static Python call shapes without executing code."""
import ast
import os
import re
from pathlib import Path
from .phrases import UUIDVALIDATION, NOUUIDVALIDATION, GENERIC_NAMES



def normalize(text):
    return ' '.join(text.lower().replace("n't", ' not').replace('-', ' ').split())

def prose(text):
    output = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) and not marker.group(2).strip():
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            output.append('')
        else:
            output.append(line)
    return '\n'.join(output)

def matches(text):
    yes, no = [], []
    for paragraph in re.split(r'\n\s*\n', prose(text)):
        value = normalize(paragraph)
        for phrases, found in ((NOUUIDVALIDATION, no), (UUIDVALIDATION, yes)):
            for phrase in sorted(phrases, key=lambda s: (-len(s), s)):
                pattern = r'(?<!\w)' + re.escape(phrase) + r'(?!\w)'
                if re.search(pattern, value):
                    found.append(phrase)
                    value = re.sub(pattern, ' ', value)
    return yes, no

def evidence(source):
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return False
    imports, defined, assigned = {}, set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        if isinstance(node, ast.Import):
            for item in node.names:
                imports[item.asname or item.name.split('.')[0]] = item.name if item.asname else item.name.split('.')[0]
        if isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for item in node.names:
                imports[item.asname or item.name] = node.module + '.' + item.name
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            targets = [item.optional_vars for item in node.items if item.optional_vars]
        for target in targets:
            assigned.update(n.id for n in ast.walk(target) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store))
    shadowed = defined | (assigned & imports.keys())

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Name):
            origin = imports.get(fn.id, '')
            leaf = origin.rsplit('.', 1)[-1]
            if fn.id in shadowed or leaf in defined:
                continue
            if origin in {'uuid.UUID', 'validators.uuid'} or (origin and leaf in GENERIC_NAMES):
                return True
        elif isinstance(fn, ast.Attribute) and fn.attr not in defined:
            parts = []
            base = fn
            while isinstance(base, ast.Attribute):
                parts.append(base.attr)
                base = base.value
            if isinstance(base, ast.Name) and base.id in shadowed:
                continue
            origin = imports.get(base.id, '') if isinstance(base, ast.Name) else ''
            chain = list(reversed(parts))
            if (origin, chain) in [('uuid', ['UUID']), ('validators', ['uuid'])]:
                return True
            if fn.attr in GENERIC_NAMES:
                return True

    return False

def audit(root, ignores=()):
    root = Path(root)
    if root.is_file() and not root.is_symlink():
        yes, no = matches(root.read_text(encoding='utf-8'))
        claims = [{'path': root.name, 'phrase': x} for x in yes]
        denials = [{'path': root.name, 'phrase': x} for x in no]
        findings = ([{'id': 'documented-uuid-validation-claim-false', 'severity': 'HIGH', 'claims': claims}] if claims else [])
        return {'findings': findings, 'claims': claims, 'denials': denials, 'production_evidence': [], 'test_evidence': []}
    if root.is_symlink() or not root.is_dir() or not os.access(root, os.R_OK | os.X_OK):
        raise OSError('root is not a readable directory')
    prefixes = [s.replace('\\', '/').strip('/') for s in ignores]
    claims, denials, production, tests = [], [], [], []
    def ignored(path):
        rel = path.relative_to(root).as_posix()
        return any(rel == x or rel.startswith(x + '/') for x in prefixes if x)
    def onerror(error):
        raise error
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        parent = Path(directory)
        dirs[:] = sorted(d for d in dirs if not (parent / d).is_symlink() and not ignored(parent / d))
        for name in sorted(files):
            path = parent / name
            if path.is_symlink() or ignored(path):
                continue
            rel = path.relative_to(root)
            if rel == Path('README.md') or ('docs' in rel.parts and path.suffix == '.md'):
                yes, no = matches(path.read_text(encoding='utf-8'))
                claims.extend({'path': str(rel), 'phrase': x} for x in yes)
                denials.extend({'path': str(rel), 'phrase': x} for x in no)
            if path.suffix == '.py' and not set(rel.parts) & {'fixtures', 'docs', 'examples'}:
                if evidence(path.read_text(encoding='utf-8')):
                    is_test = 'tests' in rel.parts or name.startswith('test_') or name.endswith('_test.py')
                    (tests if is_test else production).append(str(rel))
    findings = []
    if claims and not production:
        findings.append({'id': 'documented-uuid-validation-claim-false', 'severity': 'MEDIUM' if tests else 'HIGH', 'claims': claims})
    if denials and production:
        findings.append({'id': 'documented-no-uuid-validation-claim-false', 'severity': 'HIGH', 'claims': denials})
    return {'findings': findings, 'claims': claims, 'denials': denials, 'production_evidence': production, 'test_evidence': tests}
