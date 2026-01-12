#!/usr/bin/env python3
"""
SQLModel Model Generator

Generates SQLModel classes with proper typing, relationships, and validation.

Usage:
    python generate_model.py <model_name> [options]

Examples:
    python generate_model.py User --fields "name:str email:str age:int=None"
    python generate_model.py Post --fields "title:str content:str user_id:int" --relationship "user:User"
"""

import sys
import argparse
from typing import List, Tuple


def parse_field(field_spec: str) -> Tuple[str, str, str]:
    """
    Parse field specification into name, type, and default.

    Format: name:type[=default]
    Examples:
        - name:str
        - age:int=None
        - is_active:bool=True
    """
    if '=' in field_spec:
        field_part, default = field_spec.split('=', 1)
        name, field_type = field_part.split(':', 1)
        return name.strip(), field_type.strip(), default.strip()
    else:
        name, field_type = field_spec.split(':', 1)
        return name.strip(), field_type.strip(), None


def parse_relationship(rel_spec: str) -> Tuple[str, str]:
    """
    Parse relationship specification.

    Format: field_name:RelatedModel
    Example: user:User
    """
    field_name, related_model = rel_spec.split(':', 1)
    return field_name.strip(), related_model.strip()


def generate_model_code(
    model_name: str,
    fields: List[str],
    relationships: List[str] = None,
    table: bool = True
) -> str:
    """Generate SQLModel class code."""

    # Parse fields
    parsed_fields = [parse_field(f) for f in fields]

    # Parse relationships
    parsed_relationships = []
    if relationships:
        parsed_relationships = [parse_relationship(r) for r in relationships]

    # Start building the code
    lines = []
    lines.append("from typing import Optional")
    lines.append("from sqlmodel import SQLModel, Field, Relationship")
    lines.append("")
    lines.append("")

    # Generate the model class
    if table:
        lines.append(f"class {model_name}(SQLModel, table=True):")
    else:
        lines.append(f"class {model_name}(SQLModel):")

    # Add ID field
    lines.append("    id: Optional[int] = Field(default=None, primary_key=True)")

    # Add regular fields
    for field_name, field_type, default in parsed_fields:
        if default is not None:
            lines.append(f"    {field_name}: {field_type} = {default}")
        else:
            lines.append(f"    {field_name}: {field_type}")

    # Add relationships
    for rel_field, rel_model in parsed_relationships:
        lines.append(f'    {rel_field}: Optional["{rel_model}"] = Relationship(back_populates="{model_name.lower()}s")')

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate SQLModel classes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s User --fields "name:str" "email:str" "age:Optional[int]=None"
  %(prog)s Post --fields "title:str" "content:str" "user_id:int" --relationship "user:User"
        """
    )

    parser.add_argument("model_name", help="Name of the model class")
    parser.add_argument(
        "--fields",
        nargs="+",
        required=True,
        help="Field specifications in format name:type or name:type=default"
    )
    parser.add_argument(
        "--relationship",
        "--relationships",
        dest="relationships",
        nargs="+",
        help="Relationship specifications in format field_name:RelatedModel"
    )
    parser.add_argument(
        "--no-table",
        action="store_true",
        help="Generate a model without table=True (for schemas/responses)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    # Generate the code
    code = generate_model_code(
        model_name=args.model_name,
        fields=args.fields,
        relationships=args.relationships,
        table=not args.no_table
    )

    # Output the code
    if args.output:
        with open(args.output, 'w') as f:
            f.write(code)
        print(f"Model generated successfully: {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()
