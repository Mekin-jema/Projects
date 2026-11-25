# Proposal: Enterprise AI Assistant Pilot

**Platform:** AgenticOS  
**Prepared for:** Company Management  
**Prepared by:** AI Platform Development Team  
**Date:** 24 November 2026  
**Status:** For approval

## Decision requested

Approve a bounded AgenticOS pilot for selected, low-risk business workflows. The
pilot will configure and evaluate three assistants using approved company
information and representative tasks. It will measure answer quality, task time,
usability, access controls, and operating cost before any decision to expand.

Approval would also assign an executive sponsor, a business owner for each pilot
workflow, a security and data contact, and a small group of pilot users. The
pilot does not request unrestricted access to company systems or approval for
production-wide deployment.

## Executive summary

Employees often spend time locating internal guidance, reading documents,
checking spreadsheet results, and preparing recurring business outputs. These
tasks can be supported by AI, but a general-purpose chatbot alone does not
provide the company context, controlled access, repeatable behavior, or
oversight needed for business use.

AgenticOS provides a shared platform for building and operating specialized AI
assistants. Teams can configure an assistant's instructions, model, approved
knowledge sources, tools, and budget in a browser. Publishing creates a
versioned assistant that can be reviewed and used through supported interfaces.
The same platform provides organization-level access controls, run history,
spending limits, and approval gates for tools that can change external state.

The proposed pilot uses these existing platform capabilities to test a small
number of practical workflows. It is not a proposal to build a new AI platform
from scratch, nor a claim that AI output is ready to act on without review.
Company-specific knowledge, access rules, model and data-flow choices, and
evaluation criteria still need to be agreed and configured.

## Business opportunity

Company information is distributed across policies, procedures, reports,
spreadsheets, and other business documents. Employees may need to search several
sources, interpret the material, and then prepare an answer, analysis, or
first-draft document.

A controlled assistant pilot can test whether AI helps employees:

- Find relevant information in approved company documents more quickly.
- Get answers that identify their source and acknowledge missing information.
- Explore approved spreadsheet data and produce checkable calculations and
  charts.
- Turn business material into structured drafts, such as requirements and
  summaries.
- Reuse a governed platform instead of creating isolated AI tools for each
  department.

These are hypotheses for the pilot to measure, not guaranteed outcomes.

## Proposed pilot

Start with three assistants. Keep each one limited to an agreed task, approved
data, and a named user group.

### 1. Policy and knowledge assistant

**Purpose:** Answer employee questions from a selected collection of approved
company policies and procedures.

**Pilot tasks:**

- Find the relevant policy passages for common questions.
- Cite the documents used in an answer.
- Combine information from multiple documents when needed.
- Say when the approved source material does not answer a question.

**Example:** “What steps and approvals are required for this process?”

**Human responsibility:** The employee checks the cited source. The assistant
does not replace the policy owner or provide authoritative legal, employment,
or compliance determinations.

### 2. Data analysis assistant

**Purpose:** Help users inspect an approved, representative CSV or spreadsheet
and produce a transparent first-pass analysis.

**Pilot tasks:**

- Summarize the data fields and identify missing or unusual values.
- Calculate agreed totals or comparisons.
- Create a chart and save the calculation script and output for review.
- State the rows and assumptions used; do not fill gaps with invented data.

**Example:** “Compare monthly totals by region, show the calculation, and
prepare a chart.”

**Conditions:** Spreadsheet attachment and analysis are supported, but
reproducible calculations require the appropriate sandbox connection and
runtime to be configured. A person reviews the script, results, and source data
before using them for a decision.

### 3. Business analysis assistant

**Purpose:** Turn approved business documents and a user's stated objective
into a structured working draft.

**Pilot tasks:**

- Summarize a proposal or process description.
- Draft requirements, user stories, acceptance criteria, risks, and open
  questions.
- Separate source facts from assumptions and recommendations.
- Identify missing information for the business owner to resolve.

**Example:** “Review this proposal and produce a requirements draft with
stakeholders, dependencies, risks, and unanswered questions.”

**Human responsibility:** Business owners validate the draft and make all
decisions. The assistant is not an approval authority.

### Later candidates

If the pilot meets its acceptance criteria, the company can consider a solution
architecture assistant or a communications drafting assistant. External
communications would remain subject to human approval before publication.
Additional assistants should be prioritized using pilot evidence rather than
assumed demand.

## How AgenticOS supports the pilot

The pilot reuses the platform's existing operating model:

1. **Configure:** Define an assistant's instructions, model profile, approved
   capabilities, knowledge collections, and budget.
2. **Publish:** Freeze the configuration as a version so runs can be traced to
   the instructions and tools that were active.
3. **Run:** Let pilot users interact through the console. Other surfaces, such
   as an API or messaging channel, can be considered later if the use case
   justifies them.
4. **Review:** Inspect run history, retrieved passages, tool activity,
   approvals, and recorded usage.
5. **Improve:** Adjust the draft, test it against the same evaluation tasks,
   and publish a new version when it is ready.

Relevant platform capabilities include:

- **Knowledge retrieval:** Ingest approved documents into organization-scoped
  collections. An agent searches only the collections bound to its
  configuration and can cite retrieved sources.
- **File analysis:** Chat accepts supported document and spreadsheet formats.
  When configured with a sandbox, an agent can use files and shell tools for
  scripted analysis; the chart capability can visualize computed results.
- **Specialized configuration:** Build separate assistants for separate tasks
  without creating a separate application for each one. Capabilities are
  enabled deliberately for each agent.
- **Governance:** Organization roles and resource grants control access.
  Agent and organization budgets, run records, and audit facilities support
  oversight. Side-effecting tools can require human approval.
- **Deployment choices:** AgenticOS is self-hostable and can use configured
  model providers, including local model deployments where supported. Provider
  selection does not by itself determine where every data-processing step
  happens.

These capabilities provide a foundation, not a preconfigured company solution.
The pilot team must supply the approved documents, select models and providers,
configure access, establish any required sandbox runtime, and test the actual
workflows.

## Proposed architecture and data flow

The pilot uses the existing AgenticOS components rather than introducing a
separate assistant stack:

| Component | Pilot role |
|---|---|
| AgenticOS console | Assistant configuration, publishing, chat, and run review |
| Agent runtime | Executes the selected published assistant with its enabled tools |
| Knowledge collections | Store and retrieve approved documents for policy and business questions |
| Sandbox and chart capability | Support file-based calculations and visual output when configured |
| PostgreSQL with pgvector | Store platform records and knowledge vectors |
| Configured model and embedding providers | Generate responses and, where selected, document embeddings |
| Governance controls | Apply organization access, budgets, approvals, and audit records |

For a document question, the platform retrieves relevant passages from the
agent's bound collection and includes them in the model request. For a
spreadsheet task, a user attaches an approved file; the configured workspace
lets the agent inspect it and run calculations. Each flow can involve external
providers depending on deployment choices.

Self-hosting does not automatically mean that no data leaves the deployment.
Prompts and tool results go to the configured model provider unless a local
model is used. Document text may go to an external embedding provider during
ingestion. The pilot's security review must map these flows and approve the
chosen configuration before company data is used.

## Scope and guardrails

### Included

- One pilot organization and a defined pilot user group.
- Three assistants: policy and knowledge, data analysis, and business analysis.
- A small, approved document collection and representative test files.
- Web-console access for pilot users.
- Agent configuration, versioned publishing, and run review.
- Initial access, budget, approval, and data-flow checks.
- Evaluation against agreed representative tasks and a documented baseline.

### Excluded from the initial pilot

- Unrestricted access to production databases or enterprise applications.
- Autonomous decisions or actions with financial, legal, employment, or
  customer impact.
- Using assistants to make hiring, promotion, disciplinary, or other
  consequential HR decisions.
- Automatic publication of external communications.
- Broad rollout across departments or a commitment to integrate every company
  system.
- Claims of regulatory certification or guaranteed accuracy based solely on
  deploying the platform.

Any later integration or expansion requires a separate data-owner and security
review.

## Security, privacy, and human oversight

The pilot should follow least privilege and use only the information needed for
its selected tasks:

- Create a dedicated pilot organization or equivalent isolated scope.
- Grant access only to named pilot users and approved assistants and
  collections.
- Start with public, synthetic, redacted, or otherwise explicitly approved
  content. Do not upload sensitive personal or confidential material until the
  relevant owners approve the data flow and storage configuration.
- Select the model and embedding providers only after reviewing where prompts,
  files, and embeddings are processed.
- Set agent and organization spending limits before user testing.
- Require approval for enabled tools that can cause side effects; do not enable
  external write actions for this pilot.
- Keep human review for calculations, business recommendations, policy
  interpretation, and any output that could affect a person or company
  commitment.
- Retain failed as well as successful test runs so evaluation reflects actual
  behavior.

The pilot validates the configured deployment. It does not by itself establish
compliance with a particular legal or regulatory framework.

## Delivery approach

The duration and staffing should be agreed after a short discovery session.
Proceed through decision gates rather than committing to a broad rollout up
front.

### Phase 1 — Select workflows and establish the baseline

- Name the sponsor, process owners, security contact, and pilot users.
- Select representative questions and files for each workflow.
- Document the current task steps, time, review effort, and known error risks.
- Agree the allowed data classification and model/provider constraints.
- Define measurable pass criteria before configuration begins.

**Gate:** The data owners and security contact approve the use cases, data, and
proposed processing path.

### Phase 2 — Configure the pilot

- Prepare the pilot organization, roles, grants, model profile, and budgets.
- Ingest the approved documents and check retrieval.
- Configure and publish the three assistants with narrow instructions and only
  the required capabilities.
- Configure a sandbox runtime for the data-analysis assistant if that workflow
  is selected for the first demonstration.
- Test refusal behavior for unsupported questions and inaccessible data.

**Gate:** Owners accept the test setup and the pilot passes access and data-flow
checks.

### Phase 3 — Run and evaluate

- Give the pilot group a short orientation and the approved usage guidance.
- Run the agreed tasks using recorded versions and representative inputs.
- Check answers against source documents and calculations against known
  results.
- Collect task time, user feedback, review effort, failures, latency, and
  recorded usage.
- Review access attempts, approvals, and run records.

**Gate:** Compare results with the agreed acceptance criteria and baseline.

### Phase 4 — Decide

Management reviews the evidence and chooses to stop, refine, or expand the
pilot. Any expansion should name its additional data sources, owners, controls,
costs, and acceptance criteria.

## Success measures

Set numeric thresholds with the process owners during Phase 1. The pilot should
not pass based on a polished demonstration alone.

| Measure | How it will be checked |
|---|---|
| Source-grounded answers | Check that policy answers use the correct passages, cite the source, and say when evidence is missing |
| Calculation correctness | Reconcile selected totals, row counts, and chart values against independently checked results |
| Draft usefulness | Have business owners score completeness, factual fidelity, and correction effort against a rubric |
| Task efficiency | Compare elapsed time and review effort with the recorded baseline for the same tasks |
| Access boundaries | Verify that users cannot access unapproved agents or collections and that denied access is recorded appropriately |
| Safe operation | Confirm budgets and approval settings behave as intended and no unapproved external write action occurs |
| User experience | Collect structured feedback from the pilot group, including confusing or unusable results |
| Operating cost | Record model and infrastructure usage for the tested tasks and estimate the cost of the defined pilot workload |

Acceptance thresholds, test inputs, and who signs off each measure must be
agreed before the pilot begins.

## Expected value and limitations

If the pilot meets its criteria, the company will have evidence about whether
these workflows can be completed faster or more consistently with AI support.
It will also have a reusable, governed platform configuration and a clearer
view of data-flow, operating, and integration requirements.

Potential benefits to test include quicker document discovery, reduced effort
for repeatable analysis, faster first drafts, and less duplication between
department-specific AI experiments. Actual benefits depend on source quality,
workflow suitability, configuration, human review, and adoption. No productivity
or cost saving is assumed before measurement.

The main limitations to manage are incorrect or incomplete model output,
retrieval gaps, spreadsheet edge cases, provider and infrastructure costs, and
the work needed to maintain current source material and agent instructions.
Human review remains part of the workflow.

## Resources and operating ownership

Before approval, identify owners for:

- **Executive sponsorship:** Resolve cross-functional priorities and review the
  pilot decision.
- **Business workflows:** Provide representative tasks, validate outputs, and
  approve acceptance criteria.
- **Data and security:** Classify pilot inputs, approve providers and storage,
  and review access boundaries.
- **Platform operations:** Configure and maintain AgenticOS, models, knowledge
  collections, sandbox services, backups, and monitoring.
- **Pilot users:** Test the assistants, follow usage guidance, and report
  failures as well as useful results.

Costs may include hosting, model and embedding usage, storage, implementation,
security review, and ongoing operations. These should be estimated from the
chosen deployment and the measured pilot workload; this proposal does not
assume a fixed price or a particular service-level commitment.

## Approval requested

Approve the discovery and bounded pilot described here, subject to the Phase 1
data and security gate. Specifically:

1. Appoint an executive sponsor and the named business, data/security, and
   platform owners.
2. Select the pilot workflows and user group.
3. Authorize use of the agreed test materials and approve the model and
   embedding provider review.
4. Agree the baseline, acceptance thresholds, and pilot operating budget before
   user testing.
5. Require a management review of results before any expansion or production
   integration.

## Recommendation

Approve a small, evidence-led pilot using AgenticOS's existing agent,
knowledge, analysis, and governance capabilities. Begin with approved data and
human-reviewed tasks. Expand only where measured results, data-owner approval,
and security review support the next step.

The objective is not to automate business judgment. It is to test whether a
governed AI assistant can help employees find information, analyze approved
data, and prepare useful drafts while people remain accountable for decisions.
