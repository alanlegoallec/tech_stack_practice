# This is a toy project to practice the full tech stack:

0. Proper structure repo

- Front and backend are separate folders, containers and packages

1. UI: simple streamlit
2. Backend: simple multiplication - queries user input from streamlit, random number from database, and queries LLM using API
3. FastAPI
4. Docker
   - Basics
   - Volume Mounting
   - Containers communication: docker-compose
   - Docker compose profiles
   - Debugging with VS Code:
     - Remote debugging - connect the debugger from the local host to a running container
     - Internal debugging - start vscode debugger from within the computer -
     - Debug all containers simultaneously
   - Only expose the relevant environment variables to each container
5. Pytest
   - Unit tests
   - Integration testing
   - Test coverage and report with Codecov
6. Packaging code as packaged that can be installed
7. Dependencies
   - Handled with Poetry
   - Pinned
8. Pre-commits
9. GitHub actions
10. Make file
11. Parametrization of docker variables
12. Using .env to pass variables
13. Using .env.ci + GitHub secrets for CICD pipeline
14. CICD:
    - Linting
    - Tests coverage
    - Unit tests
    - Integration tests
    - Stack-up test
    - Deploy to Docker Hub
15. Use .sh scripts to keep logic clean
16. Mount container's code locally
17. GitFlow branch protections on GitHub
