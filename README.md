# This is a toy project to practice the full tech stack:

1. Proper structure repo
   - Front and backend are separate folders, containers and packages
1. UI
   - Simple streamlit
1. Backend
   - Simple multiplication
   - Communication with other services:
     - frontend: queries user input from streamlit
     - SQL DB: random number from database
     - API: queries LLM
   - FastAPI wrapper
1. Docker
   - Basics
   - Volume Mounting
   - Multi-containers system and communication: docker-compose
   - Debugging with VS Code:
     - Remote debugging - connect the debugger from the local host to a running container
     - Internal debugging - start vscode debugger from within the computer -
     - Debug all containers simultaneously
   - Docker compose profiles
     - dev/prod
     - remote debugging
     - internal debugging
   - Best practices
     - Layering
     - Only expose the relevant environment variables to each container
     - Parametrization of docker variables
     - Mount containers' code locally
1. Pytest
   - Unit tests
   - Integration testing
   - Test coverage and report with Codecov
1. SWE hygiene
   - Packaging code as packaged that can be installed
   - .env file
   - Dependencies
     - Handled with Poetry
     - Pinned
   - Gitflow - branch protection
   - .sh scripts to keep logic clean
   - Make file
1. CICD
   - Pre-commits
   - GitHub actions
     - Linting
     - Tests coverage
     - Unit tests
     - Integration tests
     - Stack-up test
     - Deploy to Docker Hub
   - Environment variables
     - GitHub secrets
     - .env.ci file
