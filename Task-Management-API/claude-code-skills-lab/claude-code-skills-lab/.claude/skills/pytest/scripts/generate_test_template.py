#!/usr/bin/env python3
"""
Generate a pytest test file template for a given module or class.

Usage:
    python generate_test_template.py module_name.py
    python generate_test_template.py module_name.py ClassName
"""

import sys
import ast
import os
from pathlib import Path
from typing import List, Tuple


def extract_functions_and_classes(file_path: str) -> Tuple[List[str], List[Tuple[str, List[str]]]]:
    """Extract function and class names from a Python file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Top-level functions only
            if not isinstance(getattr(node, 'parent', None), ast.ClassDef):
                if not node.name.startswith('_'):
                    functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if not item.name.startswith('_') or item.name == '__init__':
                        methods.append(item.name)
            classes.append((class_name, methods))

    return functions, classes


def generate_test_template(module_path: str, class_name: str = None) -> str:
    """Generate test template content."""
    module_name = Path(module_path).stem
    functions, classes = extract_functions_and_classes(module_path)

    # Build import statement
    import_line = f"from {module_name} import "
    if class_name:
        import_line += class_name
    else:
        imports = [f for f in functions]
        imports += [cls[0] for cls in classes]
        import_line += ", ".join(imports) if imports else "*"

    template = f'''"""
Tests for {module_name}.py
"""
import pytest
{import_line}


'''

    # Generate test stubs for functions
    if functions and not class_name:
        template += "# Function Tests\n\n"
        for func in functions:
            template += f'''def test_{func}():
    """Test {func} function."""
    # Arrange
    # TODO: Set up test data

    # Act
    # result = {func}()

    # Assert
    # TODO: Add assertions
    pass


'''

    # Generate test stubs for classes
    if classes:
        for cls_name, methods in classes:
            if class_name and cls_name != class_name:
                continue

            template += f'''
class Test{cls_name}:
    """Tests for {cls_name} class."""

    @pytest.fixture
    def {cls_name.lower()}(self):
        """Create a {cls_name} instance for testing."""
        # TODO: Initialize with appropriate parameters
        return {cls_name}()

'''
            for method in methods:
                if method == '__init__':
                    continue

                template += f'''    def test_{method}(self, {cls_name.lower()}):
        """Test {cls_name}.{method} method."""
        # Arrange
        # TODO: Set up test data

        # Act
        # result = {cls_name.lower()}.{method}()

        # Assert
        # TODO: Add assertions
        pass

'''

    return template


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_test_template.py <module_file> [ClassName]")
        print("\nExamples:")
        print("  python generate_test_template.py mymodule.py")
        print("  python generate_test_template.py mymodule.py User")
        sys.exit(1)

    module_path = sys.argv[1]
    class_name = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(module_path):
        print(f"Error: File '{module_path}' not found")
        sys.exit(1)

    # Generate test file name
    module_name = Path(module_path).stem
    test_file = f"test_{module_name}.py"

    # Generate template
    template = generate_test_template(module_path, class_name)

    # Write to file
    output_path = Path("tests") / test_file
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(template)

    print(f"Generated test template: {output_path}")
    print(f"\nNext steps:")
    print(f"1. Review and update the test stubs in {output_path}")
    print(f"2. Fill in the TODO sections with actual test logic")
    print(f"3. Run tests: pytest {output_path}")


if __name__ == "__main__":
    main()
