# Dudoxx Boiler Utilities

## Migration Script

### migrate_xml_to_odoo19.py

Automated migration tool for upgrading Odoo 16 XML files to Odoo 19 syntax.

**Features:**
- Convert `<tree>` to `<list>` tags
- Convert `attrs` to Python expressions
- Rename kanban templates (`kanban-box` → `card`)
- Fix action `view_mode` (`tree` → `list`)
- Fix search view groups (remove `expand`, change `string` to `name`)
- Validate and fix malformed invisible attributes

**Usage:**
```bash
# From module root
python utils/migrate_xml_to_odoo19.py --dry-run views/
python utils/migrate_xml_to_odoo19.py views/

# See help
python utils/migrate_xml_to_odoo19.py --help
```

**See Also:**
- [Migration Script Documentation](../../../odoo-19-how-to/08-migration-script.md)
- [Migration Guides](../../../odoo-19-how-to/)
