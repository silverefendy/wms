# Contributing to WMS

## Development Rules

1. **Do not modify Frappe core** - Use hooks, APIs, and extension mechanisms
2. **Do not modify ERPNext core** - Extend, do not replace
3. **Do not create duplicate ERPNext master data** without architectural justification
4. **Do not create a second stock ledger** - ERPNext Stock Ledger is authoritative
5. **Do not use direct SQL to manipulate stock balances** - Use Frappe APIs
6. **Document important architectural decisions** - Create ADRs for significant decisions
7. **Add tests for non-trivial business logic** - Maintain code quality
8. **Keep changes small and focused** - One logical change per commit
9. **Update relevant documentation** - When behavior changes
10. **Use meaningful commit messages** - Follow conventional commits format

## Commit Message Format

Use conventional commits:

```
feat: add receiving workflow UI
fix: resolve barcode scanning timeout
refactor: simplify stock adjustment logic
docs: update architecture diagram
test: add unit tests for putaway
chore: update dependencies
```

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Add/update tests
4. Update documentation
5. Submit a pull request
6. Ensure CI checks pass
7. Request code review
8. Address review feedback
9. Merge after approval

## Code Quality

- Follow PEP 8 for Python code
- Use type hints where practical
- Write clear, self-documenting code
- Add comments only when necessary
- Avoid premature abstractions
- Keep functions small and focused
- Handle errors explicitly

## Testing

- Write unit tests for business logic
- Write integration tests for workflows
- Test on Frappe v16 + ERPNext v16
- Ensure no regressions in existing functionality

## Questions?

Open an issue for questions or discussion before implementing significant changes.
