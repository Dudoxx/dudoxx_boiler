#!/usr/bin/env python3
"""
Odoo 16 to Odoo 19 XML Migration Script

This script automates common XML transformations needed when migrating
Odoo 16 modules to Odoo 19:

1. Convert <tree> tags to <list> tags
2. Convert attrs syntax to Python expressions
3. Convert kanban-box templates to card
4. Convert view_mode="tree" to view_mode="list"

Usage:
    python migrate_xml_to_odoo19.py <xml_file>
    python migrate_xml_to_odoo19.py views/  # Process directory
    python migrate_xml_to_odoo19.py --dry-run views/  # Preview changes
"""

import re
import sys
import os
import ast
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import argparse
import xml.etree.ElementTree as ET


class AttrsConverter:
    """Convert Odoo 16 attrs syntax to Odoo 19 Python expressions"""

    @staticmethod
    def parse_domain_condition(condition: tuple) -> str:
        """
        Parse a domain condition tuple like ('field', '=', 'value')
        and convert to Python expression like "field == 'value'"
        """
        if not isinstance(condition, tuple) or len(condition) != 3:
            return str(condition)

        field, operator, value = condition

        # Convert operators
        operator_map = {
            '=': '==',
            '!=': '!=',
            '>': '>',
            '<': '<',
            '>=': '>=',
            '<=': '<=',
            'in': 'in',
            'not in': 'not in',
        }

        python_op = operator_map.get(operator, operator)

        # Handle value formatting
        if isinstance(value, bool):
            value_str = str(value)
        elif isinstance(value, (int, float)):
            value_str = str(value)
        elif isinstance(value, str):
            value_str = f"'{value}'"
        elif isinstance(value, list):
            # Convert list to tuple for 'in' operators
            formatted_items = []
            for item in value:
                if isinstance(item, str):
                    formatted_items.append(f"'{item}'")
                else:
                    formatted_items.append(str(item))
            value_str = '(' + ', '.join(formatted_items) + ')'
        else:
            value_str = str(value)

        return f"{field} {python_op} {value_str}"

    @staticmethod
    def parse_domain(domain: list) -> str:
        """
        Parse a complete domain list and convert to Python expression

        Examples:
            [('state', '=', 'draft')] -> "state == 'draft'"
            ['|', ('a', '=', True), ('b', '=', False)] -> "a == True or b == False"
            [('state', 'in', ['a', 'b'])] -> "state in ('a', 'b')"
        """
        if not domain:
            return ""

        # Check for logical operators
        if domain[0] in ['|', '&', '!']:
            operator = domain[0]
            operator_map = {'|': ' or ', '&': ' and ', '!': 'not '}

            if operator == '!':
                # Unary operator
                rest = AttrsConverter.parse_domain(domain[1:])
                return f"not {rest}"
            else:
                # Binary operator - expecting 2 conditions after it
                python_op = operator_map[operator]
                conditions = []

                i = 1
                while i < len(domain):
                    if isinstance(domain[i], tuple):
                        conditions.append(AttrsConverter.parse_domain_condition(domain[i]))
                        i += 1
                    elif domain[i] in ['|', '&', '!']:
                        # Nested operator - this is complex, handle recursively
                        # For simplicity, we'll handle the most common case: 2 conditions
                        break
                    else:
                        i += 1

                if len(conditions) >= 2:
                    return python_op.join(conditions)
                elif len(conditions) == 1:
                    return conditions[0]
                else:
                    return ""
        else:
            # Simple domain with single condition
            if len(domain) == 1 and isinstance(domain[0], tuple):
                return AttrsConverter.parse_domain_condition(domain[0])
            else:
                # Multiple conditions without logical operator (implicitly AND)
                conditions = [AttrsConverter.parse_domain_condition(cond) for cond in domain if isinstance(cond, tuple)]
                return ' and '.join(conditions)

    @staticmethod
    def convert_attrs_value(attrs_str: str) -> Dict[str, str]:
        """
        Parse attrs string and convert to dict of attribute -> python expression

        Input: "{'invisible': [('state', '=', 'draft')]}"
        Output: {'invisible': "state == 'draft'"}
        """
        try:
            # Parse the Python dict literal
            attrs_dict = ast.literal_eval(attrs_str)

            result = {}
            for attr_name, domain in attrs_dict.items():
                if isinstance(domain, list):
                    python_expr = AttrsConverter.parse_domain(domain)
                    if python_expr:
                        result[attr_name] = python_expr

            return result
        except (ValueError, SyntaxError) as e:
            print(f"Warning: Could not parse attrs: {attrs_str[:100]}... Error: {e}")
            return {}


class XMLMigrator:
    """Main XML migration class using proper XML parsing"""

    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {
            'files_processed': 0,
            'tree_to_list': 0,
            'attrs_converted': 0,
            'kanban_templates': 0,
            'view_modes': 0,
            'invisible_validated': 0,
            'search_groups_fixed': 0,
        }

    def migrate_file(self, file_path: Path) -> bool:
        """Migrate a single XML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 1. Convert <tree> to <list>
            content, tree_count = self.convert_tree_to_list(content)
            self.stats['tree_to_list'] += tree_count

            # 2. Convert attrs to Python expressions (using XML parser)
            content, attrs_count = self.convert_attrs_with_parser(content)
            self.stats['attrs_converted'] += attrs_count

            # 3. Convert kanban templates
            content, kanban_count = self.convert_kanban_templates(content)
            self.stats['kanban_templates'] += kanban_count

            # 4. Convert view_mode tree to list
            content, viewmode_count = self.convert_view_modes(content)
            self.stats['view_modes'] += viewmode_count

            # 5. Validate and fix invisible/readonly/required attributes
            content, invisible_count = self.validate_invisible_attributes(content)
            self.stats['invisible_validated'] += invisible_count

            # 6. Fix search view group elements
            content, search_group_count = self.fix_search_view_groups(content)
            self.stats['search_groups_fixed'] = self.stats.get('search_groups_fixed', 0) + search_group_count

            # Only write if changes were made
            if content != original_content:
                self.stats['files_processed'] += 1

                if self.dry_run:
                    print(f"Would update: {file_path}")
                    if self.verbose:
                        print(f"  - Tree→List: {tree_count}")
                        print(f"  - Attrs: {attrs_count}")
                        print(f"  - Kanban: {kanban_count}")
                        print(f"  - ViewMode: {viewmode_count}")
                        print(f"  - Invisible Fixed: {invisible_count}")
                        print(f"  - Search Groups: {search_group_count}")
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Updated: {file_path}")
                    if self.verbose:
                        print(f"  - Tree→List: {tree_count}")
                        print(f"  - Attrs: {attrs_count}")
                        print(f"  - Kanban: {kanban_count}")
                        print(f"  - ViewMode: {viewmode_count}")
                        print(f"  - Invisible Fixed: {invisible_count}")
                        print(f"  - Search Groups: {search_group_count}")

                return True
            else:
                if self.verbose:
                    print(f"⏭️  Skipped (no changes): {file_path}")
                return False

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    def convert_tree_to_list(self, content: str) -> Tuple[str, int]:
        """Convert <tree> tags to <list> tags"""
        count = 0

        # Count tree tags
        count += len(re.findall(r'<tree[\s>]', content))

        # Replace opening tags
        new_content = re.sub(r'<tree(\s)', r'<list\1', content)
        new_content = re.sub(r'<tree>', r'<list>', new_content)

        # Replace closing tags
        new_content = re.sub(r'</tree>', r'</list>', new_content)

        return new_content, count

    def convert_attrs_with_parser(self, content: str) -> Tuple[str, int]:
        """
        Convert attrs attributes using regex to find and Python ast to parse

        This approach:
        1. Uses regex to find attrs attributes in the XML text
        2. Uses ast.literal_eval to parse the Python dict
        3. Converts domain to Python expression
        4. Replaces in original text
        """
        count = 0
        new_content = content

        # Find all attrs attributes with regex
        # Pattern: attrs="..." or attrs='...'
        pattern = r'attrs=["\'](\{[^"\']+\})["\']'

        def replace_attrs(match):
            nonlocal count
            attrs_value = match.group(1)

            # Convert attrs to new syntax
            converted = AttrsConverter.convert_attrs_value(attrs_value)

            if not converted:
                # Could not convert, return original
                return match.group(0)

            # Build new attributes string
            # We'll return just the converted attributes (invisible, readonly, etc.)
            # The actual replacement will remove the attrs and add new attributes
            new_attrs = []
            for attr_name, python_expr in converted.items():
                new_attrs.append(f'{attr_name}="{python_expr}"')

            count += 1
            # Return a marker that we'll replace later
            return f'__ATTRS_CONVERTED_{count}__::{"|".join(new_attrs)}'

        # Replace all attrs
        new_content = re.sub(pattern, replace_attrs, new_content)

        # Now replace the markers with actual attributes
        for i in range(1, count + 1):
            marker_pattern = f'__ATTRS_CONVERTED_{i}__::([^\\s]+)'
            match = re.search(marker_pattern, new_content)
            if match:
                attrs_str = match.group(1).replace('|', ' ')
                new_content = re.sub(marker_pattern, attrs_str, new_content)

        return new_content, count

    def convert_kanban_templates(self, content: str) -> Tuple[str, int]:
        """Convert kanban-box templates to card"""
        count = len(re.findall(r't-name="kanban-box"', content))
        new_content = content.replace('t-name="kanban-box"', 't-name="card"')
        return new_content, count

    def convert_view_modes(self, content: str) -> Tuple[str, int]:
        """Convert view_mode with tree to list"""
        count = 0
        new_content = content

        # Find all view_mode fields and replace tree with list
        # Pattern: <field name="view_mode">...tree...</field>
        def replace_view_mode(match):
            nonlocal count
            full_match = match.group(0)
            if 'tree' in full_match:
                count += full_match.count('tree')
                return full_match.replace('tree', 'list')
            return full_match

        new_content = re.sub(
            r'<field name="view_mode">[^<]+</field>',
            replace_view_mode,
            new_content
        )

        return new_content, count

    def validate_invisible_attributes(self, content: str) -> Tuple[str, int]:
        """
        Validate and fix invisible/readonly/required attributes that may have
        malformed syntax from failed attrs conversion
        """
        count = 0
        new_content = content

        # Find malformed invisible attributes like: invisible="('field'..."
        # These are failed attrs conversions that left tuple syntax
        pattern = r'(invisible|readonly|required)=(["\'])(\([^\)]*\)|\[[^\]]*\])["\']'

        def fix_malformed(match):
            nonlocal count
            attr_name = match.group(1)
            value = match.group(3)

            # This looks like a malformed conversion
            # Try to extract the actual condition
            if value.startswith('(') and ',' in value:
                # Looks like: ('field', 'operator', value)
                # Extract and convert
                try:
                    # Try to parse as Python tuple
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, tuple) and len(parsed) == 3:
                        python_expr = AttrsConverter.parse_domain_condition(parsed)
                        count += 1
                        return f'{attr_name}="{python_expr}"'
                except:
                    pass

            # Return original if can't fix
            print(f"Warning: Could not fix malformed {attr_name}: {value}")
            return match.group(0)

        new_content = re.sub(pattern, fix_malformed, new_content)

        return new_content, count

    def fix_search_view_groups(self, content: str) -> Tuple[str, int]:
        """
        Fix search view group elements for Odoo 19
        - Remove expand="0" or expand="1" attributes
        - Change string="Group By" to name="group_by"
        """
        count = 0
        new_content = content

        # Pattern to match group elements in search views with expand and/or string attributes
        # Look for: <group ...expand=...> or <group ...string="Group By"...>

        # First, remove expand attribute
        pattern_expand = r'<group([^>]*)\s+expand=["\'][^"\']*["\']'
        matches = re.findall(pattern_expand, new_content)
        count += len(matches)
        new_content = re.sub(pattern_expand, r'<group\1', new_content)

        # Second, replace string="Group By" with name="group_by"
        # This is typically in search views
        pattern_string_groupby = r'<group([^>]*)\s+string=["\']Group By["\']'
        matches = re.findall(pattern_string_groupby, new_content)
        if matches:
            count += len(matches)
            # Replace with name="group_by"
            new_content = re.sub(
                r'<group([^>]*)\s+string=["\']Group By["\']',
                r'<group\1 name="group_by"',
                new_content
            )

        # Also handle cases where string comes before other attributes
        pattern_string_first = r'<group\s+string=["\']Group By["\']\s+([^>]*)'
        matches = re.findall(pattern_string_first, new_content)
        if matches:
            count += len(matches)
            new_content = re.sub(
                r'<group\s+string=["\']Group By["\']\s+',
                r'<group name="group_by" ',
                new_content
            )

        return new_content, count

    def migrate_directory(self, dir_path: Path, pattern: str = "*.xml") -> None:
        """Migrate all XML files in a directory"""
        xml_files = list(dir_path.rglob(pattern))

        print(f"\n🔍 Found {len(xml_files)} XML files to process\n")

        for xml_file in xml_files:
            self.migrate_file(xml_file)

        self.print_stats()

    def print_stats(self):
        """Print migration statistics"""
        print("\n" + "="*60)
        print("📊 Migration Statistics")
        print("="*60)
        print(f"Files processed:      {self.stats['files_processed']}")
        print(f"Tree → List:          {self.stats['tree_to_list']}")
        print(f"Attrs converted:      {self.stats['attrs_converted']}")
        print(f"Kanban templates:     {self.stats['kanban_templates']}")
        print(f"View modes:           {self.stats['view_modes']}")
        print(f"Invisible fixed:      {self.stats['invisible_validated']}")
        print(f"Search groups fixed:  {self.stats['search_groups_fixed']}")
        print("="*60)

        total_changes = (
            self.stats['tree_to_list'] +
            self.stats['attrs_converted'] +
            self.stats['kanban_templates'] +
            self.stats['view_modes'] +
            self.stats['invisible_validated'] +
            self.stats['search_groups_fixed']
        )
        print(f"✅ Total changes:     {total_changes}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Odoo 16 XML files to Odoo 19 syntax',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate single file
  python migrate_xml_to_odoo19.py views/client_form_view.xml

  # Migrate entire directory
  python migrate_xml_to_odoo19.py views/

  # Dry run (preview changes)
  python migrate_xml_to_odoo19.py --dry-run views/

  # Verbose output
  python migrate_xml_to_odoo19.py -v views/
        """
    )

    parser.add_argument('path', help='XML file or directory to migrate')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Preview changes without modifying files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')
    parser.add_argument('--backup', '-b', action='store_true',
                        help='Create .bak backup files before modifying')

    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"❌ Error: Path does not exist: {path}")
        sys.exit(1)

    migrator = XMLMigrator(dry_run=args.dry_run, verbose=args.verbose)

    print("🚀 Odoo 16 → 19 XML Migration Tool")
    print("="*60)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")

    if path.is_file():
        if path.suffix == '.xml':
            if args.backup and not args.dry_run:
                backup_path = path.with_suffix('.xml.bak')
                import shutil
                shutil.copy2(path, backup_path)
                print(f"💾 Backup created: {backup_path}")

            migrator.migrate_file(path)
            migrator.print_stats()
        else:
            print(f"❌ Error: File is not an XML file: {path}")
            sys.exit(1)

    elif path.is_dir():
        if args.backup and not args.dry_run:
            print("⚠️  Warning: --backup not supported for directories")
            print("    Use git for version control instead\n")

        migrator.migrate_directory(path)

    else:
        print(f"❌ Error: Invalid path: {path}")
        sys.exit(1)

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")
    else:
        print("\n✅ Migration complete! Review changes and test installation.")
        print("💡 Tip: Use 'git diff' to review all changes")


if __name__ == '__main__':
    main()
