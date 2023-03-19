import ast
import os

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tree = ast.parse(content)
    classes = []
    functions = []
    imports = []
    globals = []
    docstrings = {}

    for node in tree.body:
        if isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef):
            docstring_node = ast.get_docstring(node)
            if docstring_node:
                docstrings[node.name] = docstring_node.strip()

            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            imports.extend(f"{module}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    globals.append(target.id)

    return {
        'classes': classes,
        'functions': functions,
        'imports': imports,
        'globals': globals,
        'docstrings': docstrings  # Add this line to include docstrings in the result
    }

def process_directory(root_dir):
    project_summary = {
        'files': {},
        'imports': set(),
        'classes': set(),
        'functions': set(),
        'globals': set(),
        'docstrings': {}
    }

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                file_summary = process_file(file_path)
                project_summary['files'][file_path] = file_summary

                project_summary['imports'].update(file_summary['imports'])
                project_summary['classes'].update(file_summary['classes'])
                project_summary['functions'].update(file_summary['functions'])
                project_summary['globals'].update(file_summary['globals'])
                project_summary['docstrings'].update(file_summary['docstrings'])

    return project_summary

def main():
    root_dir = '.'  # Set the root directory of your project
    project_summary = process_directory(root_dir)

    print('Project Summary:')
    print('Files:')
    for file_path, file_summary in project_summary['files'].items():
        print(f'  {file_path}:')
        print(f"    Classes: {', '.join(file_summary['classes'])}")
        print(f"    Functions: {', '.join(file_summary['functions'])}")
        print(f"    Imports: {', '.join(file_summary['imports'])}")
        print(f"    Globals: {', '.join(file_summary['globals'])}")
        print(f"    Docstrings:")  # Add this line to print the docstrings
        for name, docstring in file_summary['docstrings'].items():
            print(f"      {name}: {docstring}")

    print('\nOverall Summary:')
    print(f"Classes: {', '.join(sorted(project_summary['classes']))}")
    print(f"Functions: {', '.join(sorted(project_summary['functions']))}")
    print(f"Imports: {', '.join(sorted(project_summary['imports']))}")
    print(f"Globals: {', '.join(sorted(project_summary['globals']))}")


if __name__ == '__main__':
    main()
