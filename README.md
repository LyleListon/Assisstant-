# Personal Assistant

A modular personal assistant system designed with independence and scalability in mind. Each module operates independently with minimal cross-module dependencies, making the system easy to maintain and extend.

## Architecture

The system follows a modular architecture with:

- **Core Dispatcher**: Routes requests between independent modules
- **Independent Modules**: Each handling specific functionality
- **Message-based Communication**: Clean, typed interfaces between components
- **State Management**: Each module manages its own state

### Current Modules

1. **Core Dispatcher**: Routes messages between modules
2. **File Operations**: Handles all file-related tasks
3. **Command Execution**: System command handling and process management
4. **Browser Control**: Web automation and interaction
5. **Search**: File and content search functionality
6. **Receipt Organizer**: Email receipt collection and organization

## Module Features

### Command Execution
- Execute system commands with output capture
- Run background processes
- Monitor running processes
- Process termination handling

### Browser Control
- Headless Chrome automation
- URL navigation
- Element interaction (click, type)
- Text extraction
- Screenshot capture

### Search
- File name pattern searching
- Content text searching
- Regex pattern matching
- File extension filtering
- Parallel search execution

### Receipt Organizer
- Email receipt collection
- Data extraction (vendor, amount, date)
- Organized storage structure
- Search capabilities
- Report generation

## Project Structure

```
personal_assistant/
├── modules/
│   ├── core/
│   │   └── dispatcher.py     # Message routing
│   ├── file_ops/
│   │   └── main.py          # File operations
│   ├── command_exec/
│   │   └── main.py          # Command execution
│   ├── browser_control/
│   │   └── main.py          # Web automation
│   ├── search/
│   │   └── main.py          # Search functionality
│   └── receipt_organizer/
│       └── main.py          # Receipt management
├── tests/                   # Test suites
├── data/                    # Data storage
└── docs/                    # Documentation
```

## Design Philosophy

- Small, independent programs
- Minimal communication between modules
- Single responsibility principle
- Loose coupling, high cohesion
- Easy testing and maintenance

## Development Status

The project is actively developed with all core modules implemented and tested:

- ✅ Modular architecture implemented
- ✅ Core dispatcher operational
- ✅ All main modules complete with tests
- ✅ Type hints verified (mypy)
- ✅ Comprehensive test coverage

Current focus:
- Receipt organizer enhancements
- Email collection implementation
- Report generation features
- Search optimization

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/LyleListon/Assisstant-.git
```

2. Install dependencies:
```bash
cd personal_assistant
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License (to be added)
