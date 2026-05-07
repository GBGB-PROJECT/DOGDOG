import ast
import os
import sys

def check_await_outside_async(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        # If it's a SyntaxError, it might be the await issue itself
        # But ast.parse will throw it. Let's catch it.
        return [f"SyntaxError: {e}"]

    errors = []
    class AwaitVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_async = False
        
        def visit_AsyncFunctionDef(self, node):
            old_in_async = self.in_async
            self.in_async = True
            self.generic_visit(node)
            self.in_async = old_in_async
            
        def visit_Await(self, node):
            if not self.in_async:
                errors.append(f"Line {node.lineno}: await outside async function")
            self.generic_visit(node)

    visitor = AwaitVisitor()
    visitor.visit(tree)
    return errors

if __name__ == "__main__":
    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                errs = check_await_outside_async(path)
                if errs:
                    print(f"File: {path}")
                    for e in errs:
                        print(f"  {e}")
