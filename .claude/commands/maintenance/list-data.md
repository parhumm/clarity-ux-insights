# List Available Data

List all dates with available data in the database.

## Usage

```bash
python clarity_cli.py list
```

## Options

```bash
# Basic list
python clarity_cli.py list

# Show all dates (verbose)
python clarity_cli.py list --verbose

# List page-specific data
python clarity_cli.py list --scope page
```

## Output

Shows:
- Total number of dates with data
- Latest data date
- Earliest data date
- All dates (if --verbose)

## Example Output

```
📋 Available data:
   Total dates: 30
   Latest: 2025-11-25
   Earliest: 2025-10-27
```

## Use Cases

**Check data availability:**
```bash
python clarity_cli.py list
```

**See all dates:**
```bash
python clarity_cli.py list --verbose
```

**Check page data:**
```bash
python clarity_cli.py list --scope page
```
