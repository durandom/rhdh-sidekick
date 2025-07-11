# Generic Planning Command for B4RT

This command handles creating comprehensive plans for any development task in the B4RT telemetry analysis system.

## Usage

When this command is invoked, it will guide you through a structured 5-step planning process for any development task.

## The 5-Step Planning Process

### Step 1: Requirements Gathering
- **Understand the task:** What exactly needs to be accomplished?
- **Gather context:** What existing systems/files are involved?
- **Identify constraints:** What limitations or requirements exist?
- **Define success criteria:** How will we know the task is complete?
- **Clarify scope:** What is in-scope vs out-of-scope?

### Step 2: Create Planning Document
- **Create plan document** in `docs/plans/<task_name>.md`
- **Document requirements** gathered in Step 1
- **Analyze current state** of relevant systems
- **Identify dependencies** and prerequisites
- **Draft initial approach** and architecture decisions

### Step 3: Refine Planning Document
- **Present the plan** to the user for review
- **Gather feedback** and make adjustments
- **Ensure all requirements** are captured accurately
- **Validate approach** with user's expectations
- **Get explicit approval** before proceeding to implementation

### Step 4: Execute Implementation
- **Follow the planned approach** step by step
- **Track progress** using TodoWrite tool for complex tasks
- **Document decisions** made during implementation
- **Handle unexpected issues** by updating the plan
- **Maintain communication** with user throughout

### Step 5: Implementation Report
- **Update the planning document** with implementation details
- **Document what was actually built** vs what was planned
- **Record key decisions** and rationale
- **Note any deviations** from the original plan
- **Include testing results** and validation
- **Provide next steps** or recommendations

## Workflow

When this command is invoked:

1. **Ask the user to describe their task:**
   ```
   What would you like to plan and implement?

   Please describe:
   - The goal or objective
   - Any specific requirements or constraints
   - Expected deliverables
   - Timeline or priority level
   ```

2. **Execute Step 1: Requirements Gathering**
   - Ask clarifying questions based on the task type
   - Explore existing codebase for relevant context
   - Identify potential challenges or blockers
   - Confirm understanding with the user

3. **Execute Step 2: Create Planning Document**
   - Generate comprehensive plan in `docs/plans/`
   - Include all sections: requirements, approach, files, testing
   - Use structured format for easy review and tracking

4. **Execute Step 3: Refine Planning Document**
   - Present plan to user for review
   - Incorporate feedback and make revisions
   - Ensure user approval before implementation

5. **Execute Step 4: Implementation**
   - Follow planned approach systematically
   - Use TodoWrite for task tracking if complex
   - Communicate progress and any issues

6. **Execute Step 5: Implementation Report**
   - Update planning document with final results
   - Document lessons learned and decisions made
   - Provide summary of deliverables and next steps

## Best Practices

### For Requirements Gathering
- Ask open-ended questions to understand the "why" behind requests
- Explore edge cases and error conditions
- Consider integration with existing systems
- Validate assumptions with the user

### For Planning Documents
- Be specific and actionable in plans
- Include concrete examples where helpful
- Consider both happy path and error scenarios
- Make plans reviewable and updateable

### For Implementation
- Follow the plan but be flexible when needed
- Document deviations and reasons
- Communicate regularly with the user
- Test incrementally as you build

### For Documentation
- Keep the planning document updated throughout
- Include both successes and failures
- Make it useful for future similar tasks
- Consider what future developers will need to know

## Example Usage Scenarios

### New Feature Development
- Planning new detectors or event types
- Adding new visualization capabilities
- Implementing new CLI commands
- Extending the streaming architecture

### Bug Fixes and Improvements
- Addressing performance issues
- Fixing data processing problems
- Improving error handling
- Enhancing user experience

### Refactoring Tasks
- Restructuring code organization
- Updating dependencies
- Improving test coverage
- Enhancing documentation

### Architecture Changes
- Modifying core data structures
- Changing processing pipelines
- Updating configuration systems
- Scaling system components
