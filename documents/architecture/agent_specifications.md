# Antigine Agent Specifications

This document provides detailed specifications for all agents and orchestration components in the Antigine system.

## Overview

Antigine employs a **nine-agent architecture** organized into two main phases, coordinated by specialized orchestrators that manage workflow, state, and human interaction points.

## Phase Orchestrators

### Planning Phase Orchestrator
**Purpose:** Manages the workflow from GDD creation through feature request generation.

**Responsibilities:**
- Coordinates sequential execution of GDD Creator → Module Planner → Feature Request Writer
- Manages state transitions between planning agents
- Triggers mandatory human review checkpoints after each agent output
- Handles human feedback integration and agent re-execution when revisions are requested
- Registers approved documents (GDD, modules.md) to the file system
- Stores approved feature requests in `ledger.db` with metadata and relationships
- Manages cancellation and rollback scenarios
- Tracks planning session history and progress

**Technical Implementation:**
- Built using LangGraph for stateful workflow management
- Maintains planning session state including current stage, approval status, and revision history
- Integrates with database layer for feature request persistence
- Provides CLI interface for human operator interaction

### Implementation Phase Orchestrator
**Purpose:** Manages the 5-stage implementation pipeline from feature selection through code review.

**Responsibilities:**
- Coordinates feature selection from `ledger.db`
- Manages sequential execution through Technical Architecture → Implementation Planning → Coding → Code Review
- Handles review loops with automatic re-execution when agents require revisions
- Enforces review limits to prevent infinite revision cycles
- Triggers mandatory human approval at each stage boundary
- Stores approved documents (technical architecture, implementation plans) in `ledger.db`
- Links all documents to the parent feature request
- Manages code compilation and build error resolution workflows
- Handles version control integration and pull request creation
- Tracks implementation session progress and metrics

**Technical Implementation:**
- Built using LangGraph with complex conditional flows and review loops
- Maintains implementation session state including current stage, approval status, revision counts
- Integrates with build tools and version control systems
- Provides detailed progress tracking and error handling
- Manages background compilation processes and build feedback loops

## Planning Phase Agents

### 1. GDD Creator Agent
**Role:** Interactive chat agent for Game Design Document creation
**Input:** User responses to probing questions, existing GDD (if any)
**Output:** Minimalist Game Design Document

**Capabilities:**
- References GDD best practices and templates
- Asks targeted, probing questions to extract game vision and core mechanics
- Iteratively builds comprehensive but minimal GDD
- Validates completeness against industry-standard GDD requirements
- Adapts questioning based on game genre and complexity

**Prompt Engineering Focus:**
- Expert knowledge of game design principles
- Structured questioning methodology
- Validation of design coherence and feasibility
- Emphasis on minimalism while ensuring completeness

### 2. Module Planner Agent
**Role:** Breaks down GDD into architectural modules
**Input:** Approved Game Design Document, user clarifications
**Output:** `modules.md` with high-level architectural modules and feature lists

**Capabilities:**
- Analyzes GDD to identify major game systems and dependencies
- Creates logical module boundaries with clear responsibilities
- Generates feature lists for each module without detailed specifications
- Ensures all GDD requirements are captured across modules
- Identifies integration points and module dependencies

**Prompt Engineering Focus:**
- Systems thinking and architectural decomposition
- Clear module boundary definition
- Comprehensive coverage without feature overlap
- Logical dependency identification

### 3. Feature Request Writer Agent
**Role:** Creates detailed, implementable feature requests
**Input:** `modules.md`, GDD context, existing codebase analysis, user guidance
**Output:** Detailed feature requests with acceptance criteria

**Capabilities:**
- Converts module feature lists into specific, actionable feature requests
- Analyzes existing codebase to avoid duplication and ensure integration
- Creates small, incremental features that maintain playable game state
- Defines clear acceptance criteria and success metrics
- Establishes feature dependencies and prerequisites
- Adapts feature scope based on existing functionality

**Prompt Engineering Focus:**
- Feature decomposition and scope definition
- Integration awareness and dependency management
- Clear acceptance criteria definition
- Incremental development principles

## Implementation Phase Agents

### 4. Technical Architecture Writer Agent
**Role:** Designs comprehensive technical specifications
**Input:** Feature request, existing codebase context, framework documentation
**Output:** Technical architecture document

**Capabilities:**
- Creates detailed system design for requested features
- Specifies components, interfaces, and data structures
- Defines integration points with existing systems
- Ensures Love2D/Lua best practices and patterns
- Documents component interactions and data flow
- Maintains framework-agnostic design principles for future expansion

**Prompt Engineering Focus:**
- Technical system design expertise
- Framework-specific knowledge (Love2D/Lua initially)
- Component responsibility and interface design
- Integration pattern definition

### 5. Technical Architecture Reviewer Agent
**Role:** Validates architectural feasibility and scope
**Input:** Feature request, technical architecture document
**Output:** Structured review with approval/revision status and feedback

**Capabilities:**
- Validates completeness against feature requirements
- Assesses feasibility within Love2D/Lua constraints
- Reviews architectural simplicity and modularity
- Checks for proper separation of concerns
- Identifies potential integration issues
- Scores architecture across multiple dimensions (1-5 scale)

**Scoring Criteria:**
- **Completeness Score:** All features addressed, components defined, interactions documented
- **Feasibility Score:** Appropriate for Love2D/Lua, realistic data structures, efficient interactions
- **Simplicity Score:** Single responsibility components, loose coupling, minimal complexity

**Approval Requirements:** All scores ≥4 for approval

### 6. Implementation Plan Writer Agent
**Role:** Creates detailed implementation plans
**Input:** Approved technical architecture, existing codebase, framework documentation
**Output:** Feature Implementation Plan (FIP) with concrete development steps

**Capabilities:**
- Translates architecture into specific implementation phases
- Defines exact files to create/modify with function specifications
- Creates integration instructions with specific code locations
- Develops comprehensive testing requirements
- Establishes realistic timeline estimates (1-3 days per phase)
- Orders implementation by dependencies
- References actual codebase structure and existing patterns

**Prompt Engineering Focus:**
- Implementation planning and phase organization
- Concrete specification of development tasks
- Integration instruction clarity
- Testing requirement definition

### 7. Implementation Plan Reviewer Agent
**Role:** Validates implementation plan quality and architecture alignment
**Input:** Technical architecture, implementation plan
**Output:** Structured review with approval/revision status and feedback

**Capabilities:**
- Validates completeness against architectural components
- Reviews implementation phase organization and dependencies
- Assesses integration instruction specificity
- Evaluates testing requirement adequacy
- Checks alignment with architectural design
- Scores implementation plan across multiple dimensions

**Scoring Criteria:**
- **Completeness Score:** All architecture components covered, files specified, functions defined
- **Implementation Score:** Clear actionable instructions, realistic phases, specific integration points
- **Alignment Score:** Matches architecture, preserves design decisions, proper framework usage

**Approval Requirements:** All scores ≥4 for approval

### 8. Coder Agent
**Role:** Implements features and resolves build issues
**Input:** Approved implementation plan, existing codebase, framework documentation
**Output:** Code changes (new files, modifications), compilation verification

**Capabilities:**
- Writes Love2D/Lua code following implementation plan
- Integrates new code with existing codebase
- Compiles and tests code functionality
- Resolves build errors and compilation issues
- Accesses internet search for framework documentation and issue resolution
- Maintains code style consistency with existing codebase
- Creates unit tests as specified in implementation plan
- Provides detailed change descriptions for human review

**Prompt Engineering Focus:**
- Love2D/Lua coding expertise
- Integration and compatibility focus
- Build process management
- Error resolution and debugging

### 9. Code Reviewer Agent
**Role:** Final code quality and standards review
**Input:** Implementation plan, code changes, compilation results
**Output:** Code review with approval/revision status and feedback

**Capabilities:**
- Reviews syntax and code quality
- Validates adherence to Love2D/Lua best practices
- Checks consistency with existing code conventions
- Identifies duplicate, unnecessary, or deprecated code
- Verifies implementation matches approved plan
- Assesses integration quality and potential issues
- Reviews test coverage and quality

**Review Focus:**
- Code syntax and structure
- Best practice adherence
- Convention consistency
- Integration quality
- Test adequacy

## Agent Communication Patterns

### Inter-Agent Data Flow
1. **Planning Phase:** GDD → Modules → Feature Requests → Ledger Storage
2. **Implementation Phase:** Feature Selection → Architecture → Implementation Plan → Code → Review
3. **Review Loops:** Writer Agent ↔ Reviewer Agent (with revision limits)
4. **Human Interaction:** Mandatory review checkpoints between all major stages

### State Management
- **Session State:** Current phase, active agent, approval status, revision history
- **Document State:** Draft versions, approval status, review feedback, revision counts
- **Database State:** Feature metadata, document storage, relationship mappings
- **Build State:** Compilation status, error logs, test results

### Error Handling
- **Review Limit Enforcement:** Maximum 3 revisions per agent pair before escalation
- **Build Error Recovery:** Automatic retry with error feedback integration
- **Human Escalation:** Complex issues requiring human intervention
- **Rollback Capability:** Revert to previous stable state on critical failures

## Technical Implementation Notes

### LangGraph Integration
- **Planning Orchestrator:** Sequential flow with human checkpoints
- **Implementation Orchestrator:** Complex conditional flows with review loops
- **State Persistence:** Checkpoint system for session recovery
- **Parallel Processing:** Where applicable for efficiency

### Database Integration
- **Feature Storage:** Metadata, status tracking, relationship management
- **Document Versioning:** Draft and approved document storage
- **Audit Trail:** Complete history of all agent interactions and decisions
- **Search and Query:** Feature discovery and dependency analysis

### Framework Abstraction
- **Current Implementation:** Love2D/Lua specific prompts and validation
- **Future Expansion:** Plugin architecture for additional frameworks
- **Configuration Management:** Framework-specific settings and constraints
- **Validation Adaptation:** Framework-appropriate review criteria

This agent architecture ensures comprehensive coverage of the game development lifecycle while maintaining quality gates, human oversight, and systematic progress tracking throughout the entire process.
