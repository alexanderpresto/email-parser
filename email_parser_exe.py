"""
Entry point for the Windows executable.
Detects if running as an executable and handles accordingly.
"""
import sys
import os

# Check if we're running as a frozen executable
if getattr(sys, 'frozen', False):
    # Running as executable - check for arguments
    if len(sys.argv) == 1:
        # No arguments provided - run interactive mode
        from email_parser.cli.interactive import main
        sys.exit(main())
    else:
        # Arguments provided - run main CLI
        from email_parser.cli.main import main
        sys.exit(main())
else:
    # Running as normal Python script
    from email_parser.cli.main import main
    sys.exit(main())