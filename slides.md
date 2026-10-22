---
theme: default
title: Account intelligence for sellers
info: Use case and system design
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: fade
mdc: true
---

<div class="h-full flex flex-col items-center justify-center text-center">
  <div class="text-sm tracking-widest uppercase opacity-60 mb-4">Use case and system design</div>
  <h1 class="text-5xl !mb-4">Account intelligence for sellers</h1>
  <p class="text-xl opacity-80">A knowledge graph for one selling company</p>
  <p class="mt-10 opacity-60">Acme · Anna · Bob · Rival</p>
</div>

---
layout: center
class: text-center
---

# Use case

---

# The use case

<div class="grid grid-cols-3 gap-5 mt-8">
  <div class="rounded-xl border border-gray-200 p-6 h-64 flex flex-col justify-center">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">Problem</div>
    <div class="text-2xl font-semibold mb-3">The deal went quiet</div>
    <p>Late stage, one known contact, no recent activity.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-64 flex flex-col justify-center">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">What we connect</div>
    <div class="text-2xl font-semibold mb-3">CRM and calls</div>
    <p>This sale, what was said, and similar deals at the same company.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-64 flex flex-col justify-center">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">What the seller gets</div>
    <div class="text-2xl font-semibold mb-3">A next action</div>
    <p>Who is missing, what was said, and what worked before.</p>
  </div>
</div>

---

# The situation

<div class="grid grid-cols-2 gap-5 mt-6">
  <div class="rounded-xl border border-gray-200 p-6">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">CRM</div>
    <div class="text-xl font-semibold mb-3">Looks paused</div>
    <p>Late stage. A known contact. An amount. No recent activity.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">Last call</div>
    <div class="text-xl font-semibold mb-3">Says why</div>
    <ul>
      <li>An approver who is not a contact</li>
      <li>A competitor</li>
      <li>A concrete reason they will not move</li>
    </ul>
  </div>
</div>

<div class="rounded-xl border border-gray-200 p-5 mt-5 text-center">
  The same pattern is already on other deals here. Some closed. Some did not.
</div>

---

# Who this is for

<div class="mt-8">

| | |
| --- | --- |
| **B2B** | A company sells to another company. Several people must agree. |
| **Seller** | Owns many deals. Will not re-read old calls before each meeting. |
| **Selling company** | One company's deals stay inside that company. |
| **Buyer** | The account they are trying to sell to. |

</div>

---

# What the CRM already holds

<div class="mt-6">

| Field | Meaning |
| --- | --- |
| Account, industry | The buyer, and what that company does |
| Contact | A person at the buyer |
| Opportunity | The deal |
| Stage, amount | How far it has gone, and the price |
| Last activity | When something last happened |
| Competitor | Who else the buyer is considering |

</div>

<p class="mt-6 text-center opacity-70">Fields are often empty. The useful facts were said on a call.</p>

---

# What the last call adds

<div class="grid grid-cols-3 gap-5 mt-10">
  <div class="rounded-xl border border-gray-200 p-6 h-56 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-3">Missing approver</div>
    <p>Named on the call. Absent from the contacts.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-56 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-3">Competitor</div>
    <p>Named on the call. The CRM field is empty.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-56 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-3">Objection</div>
    <p>The reason this purchase is stuck.</p>
  </div>
</div>

---

# Three kinds of facts

<div class="grid grid-cols-3 gap-5 mt-10">
  <div class="rounded-xl border border-gray-200 p-6 h-56 flex flex-col justify-center text-center">
    <div class="text-3xl mb-3">1</div>
    <div class="text-xl font-semibold mb-2">CRM</div>
    <p>Account, contacts, stage, amount</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-56 flex flex-col justify-center text-center">
    <div class="text-3xl mb-3">2</div>
    <div class="text-xl font-semibold mb-2">This call</div>
    <p>People, competitors, objections</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-56 flex flex-col justify-center text-center">
    <div class="text-3xl mb-3">3</div>
    <div class="text-xl font-semibold mb-2">Other calls</div>
    <p>Similar deals, outcomes, first action</p>
  </div>
</div>

---

# The brief

<div class="grid grid-cols-3 gap-5 mt-8">
  <div class="rounded-xl border border-gray-200 p-6 h-48 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">Who is missing</div>
    <p>Named on the call, absent from the CRM.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-48 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">What was said</div>
    <p>A competitor or objection never typed in.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-48 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">What worked</div>
    <p>The action that came before similar wins.</p>
  </div>
</div>

<div class="grid grid-cols-3 gap-5 mt-5 text-center text-sm">
  <div class="soft rounded-lg p-3">Own call: a quote</div>
  <div class="soft rounded-lg p-3">Other deals: a count</div>
  <div class="soft rounded-lg p-3">Unmatched name: unconfirmed</div>
</div>

---

# Why the day changes

<div class="grid grid-cols-2 gap-6 mt-10">
  <div class="rounded-xl border border-gray-200 p-8 h-64 flex flex-col justify-center">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">Before</div>
    <div class="text-2xl font-semibold mb-3">Follow up</div>
    <p>The CRM shows silence. A summary repeats the last call.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-8 h-64 flex flex-col justify-center">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">After</div>
    <div class="text-2xl font-semibold mb-3">A specific move</div>
    <p>Meet the approver. Answer the objection. Repeat what preceded wins.</p>
  </div>
</div>

---

# Why a graph

<div class="flex items-center justify-between mt-16 text-center">
  <div class="rounded-xl border border-gray-200 px-4 py-6 w-36"><b>This deal</b></div>
  <div class="opacity-40">→</div>
  <div class="rounded-xl border border-gray-200 px-4 py-6 w-36"><b>What was said</b></div>
  <div class="opacity-40">→</div>
  <div class="rounded-xl border border-gray-200 px-4 py-6 w-36"><b>Similar deals</b></div>
  <div class="opacity-40">→</div>
  <div class="rounded-xl border border-gray-200 px-4 py-6 w-36"><b>Outcomes</b></div>
</div>

<p class="text-center mt-12 text-lg">The answer is that path, with the evidence still attached.</p>

---
layout: center
class: text-center
---

# System design

---

# One example throughout

<div class="grid grid-cols-4 gap-4 mt-8">
  <div class="rounded-xl border border-gray-200 p-4 h-36 flex flex-col justify-center">
    <div class="font-semibold">Acme</div>
    <div class="text-sm opacity-70">Buyer, retail</div>
  </div>
  <div class="rounded-xl border border-gray-200 p-4 h-36 flex flex-col justify-center">
    <div class="font-semibold">Anna</div>
    <div class="text-sm opacity-70">Already in the CRM</div>
  </div>
  <div class="rounded-xl border border-gray-200 p-4 h-36 flex flex-col justify-center">
    <div class="font-semibold">Bob</div>
    <div class="text-sm opacity-70">Said on the call</div>
  </div>
  <div class="rounded-xl border border-gray-200 p-4 h-36 flex flex-col justify-center">
    <div class="font-semibold">Rival</div>
    <div class="text-sm opacity-70">Known vendor</div>
  </div>
</div>

<div class="grid grid-cols-3 gap-4 mt-4 text-sm">
  <div class="soft rounded-lg p-4">"Bob on the security team hasn't signed off."</div>
  <div class="soft rounded-lg p-4">"We're also still comparing you with Rival."</div>
  <div class="soft rounded-lg p-4">"A big change this quarter would stop the project."</div>
</div>

<p class="text-center mt-4 text-sm opacity-70">$120k · Negotiation · open · quiet 16 days · vendor field empty</p>

---

# Three CRM records

<div class="grid grid-cols-3 gap-4 mt-6 text-sm">
  <div class="rounded-xl border border-gray-200 p-5">
    <div class="text-lg font-semibold mb-2">Account</div>
    <p class="opacity-70 mb-3">One buyer. Acme.</p>
    <p>Name · industry · CRM id</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-5">
    <div class="text-lg font-semibold mb-2">Contact</div>
    <p class="opacity-70 mb-3">One person. Anna.</p>
    <p>Name · title · CRM id · company</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-5">
    <div class="text-lg font-semibold mb-2">Opportunity</div>
    <p class="opacity-70 mb-3">One possible sale.</p>
    <p>Stage · amount · outcome · owner · vendor field</p>
  </div>
</div>

<p class="text-center mt-6">Outcome is copied from the CRM. The call is never asked who won.</p>

---

# Shared lists

<div class="grid grid-cols-3 gap-5 mt-10">
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">Competitor</div>
    <p>A known vendor. Rival.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">Concept</div>
    <p>A stable worry label. <code>timing</code>, <code>price</code>.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">Action</div>
    <p>What happened next. <code>small_start</code>.</p>
  </div>
</div>

<p class="text-center mt-8 opacity-70">Many sales point at the same label, so they can be counted together.</p>

---

# What a call adds

<div class="mt-6">

| Record | Keeps | Acme |
| --- | --- | --- |
| Meeting | One call, tied by the calendar | This sale |
| Span | One exact sentence | Three sentences |
| Person mention | Spoken name, plus a job hint | Bob, security |
| Competitor mention | Spoken vendor | Rival |
| Concept mention | Worry, plus the shared label | timing |

</div>

<p class="text-center mt-6">The full text stays outside the graph. Bob has a mention. Anna has a contact.</p>

---

# The links

<div class="grid grid-cols-2 gap-x-10 mt-4 text-sm">
<div>

| Link | Meaning |
| --- | --- |
| Belongs to | Anna works at Acme |
| Is with | The sale is to Acme |
| Involved in | Anna's role sits on this link |
| Is about | Calendar ties the call to the sale |
| Has span | The call contains the sentence |
| Supported by | The claim hangs off that sentence |

</div>
<div>

| Link | Acme |
| --- | --- |
| Matches contact | Bob has none |
| Matches competitor | Rival, resolved |
| Classified as | The third sentence is timing |
| Raised | The sale raised timing |
| Faced | The sale faced Rival |

</div>
</div>

---

# The buying group is a query

<div class="grid grid-cols-2 gap-6 mt-12">
  <div class="rounded-xl border border-gray-200 p-8 h-48 flex flex-col justify-center text-center">
    <div class="text-2xl font-semibold mb-2">Anna</div>
    <p>Contact, from the CRM</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-8 h-48 flex flex-col justify-center text-center">
    <div class="text-2xl font-semibold mb-2">Bob</div>
    <p>Mention, with no contact</p>
  </div>
</div>

<p class="text-center mt-8">Read the links. A stored group would be a second copy.</p>

---

# Two ways in

<div class="grid grid-cols-2 gap-6 mt-10">
  <div class="rounded-xl border border-gray-200 p-8 h-56 flex flex-col justify-center">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">CRM</div>
    <div class="text-2xl font-semibold mb-3">Already in fields</div>
    <p>Acme, Anna, price, stage, empty vendor field.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-8 h-56 flex flex-col justify-center">
    <div class="text-xs uppercase tracking-wide opacity-50 mb-3">Calls</div>
    <div class="text-2xl font-semibold mb-3">Three sentences</div>
    <p>Bob, Rival, and a change this quarter.</p>
  </div>
</div>

<p class="text-center mt-8">The screen asks a reader. It never opens the graph itself.</p>

---

# CRM sync

<div class="grid grid-cols-3 gap-5 mt-12">
  <div class="rounded-xl border border-gray-200 p-6 h-44 flex flex-col justify-center text-center">
    <div class="text-lg font-semibold mb-2">Copy fields</div>
    <p>Company, person, sale</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-44 flex flex-col justify-center text-center">
    <div class="text-lg font-semibold mb-2">No model</div>
    <p>The values are already structured</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-44 flex flex-col justify-center text-center">
    <div class="text-lg font-semibold mb-2">Update in place</div>
    <p>A second copy refreshes Acme</p>
  </div>
</div>

---

# Call to graph

<div class="mt-4">

| Step | Role |
| --- | --- |
| Store | Save the exact text, outside the graph |
| Queue | One job per call. It can wait and be retried |
| Extract | The model fills a form. Each item includes its sentence |
| Validate | Keep the item only when that sentence is in the file |
| Resolve | Match names only among people at Acme |
| Writer | The only update. A rerun replaces that call's claims |

</div>

---

# Confirm and reject

<div class="grid grid-cols-3 gap-5 mt-10">
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">Seller</div>
    <p>Confirms Bob, or rejects a bad match.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">Memory</div>
    <p>The next run of the call reuses that choice.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-xl font-semibold mb-2">CRM</div>
    <p>Bob becomes a contact only after someone adds him there.</p>
  </div>
</div>

---

# The brief, then a question

<div class="mt-4">

| Question | Acme answer | Evidence |
| --- | --- | --- |
| Who is unconfirmed? | Bob | His sentence |
| What was said, not typed? | Rival, timing | Those sentences |
| What happened on similar sales? | 7 small starts, 2 full switches | A count |

</div>

<div class="grid grid-cols-3 gap-4 mt-5 text-center text-sm">
  <div class="soft rounded-lg p-4">Same facts as the brief</div>
  <div class="soft rounded-lg p-4">The model only phrases them</div>
  <div class="soft rounded-lg p-4">A sentence with no retrieved source is dropped</div>
</div>

---
class: diagram components
---

# Components

<p class="opacity-60 -mt-2">Two ways in. One writer. One reader.</p>

<script setup>
import componentsDiagram from './showpad.svg?url'
</script>

<img :src="componentsDiagram" alt="Components" class="components-figure" />

---
class: diagram
---

# Example graph

<p class="opacity-60 -mt-2">Acme. Anna is a contact. Bob is a mention.</p>

```mermaid
%%{init: {'flowchart': {'htmlLabels': true, 'curve': 'basis', 'nodeSpacing': 10, 'rankSpacing': 16, 'padding': 2}, 'themeVariables': {'fontSize': '13px'}}}%%
flowchart LR
  Acme["Account Acme\nretail"] --> Anna["Contact Anna"]
  Anna -->|"champion\nfrom the CRM"| Opp["Opportunity\nNegotiation, open"]
  Acme --> Meet["Meeting"]
  Meet --> S1["Span 1"] --> Bob["Bob\nunresolved"]
  Meet --> S2["Span 2"] --> RivalMention["Rival mention\nresolved"] --> Rival["Competitor Rival"]
  Meet --> S3["Span 3"] --> Timing["Timing\nobjection"]
  Opp -->|faced| Rival
  Opp -->|raised| Timing
```

---
layout: center
class: text-center
---

# Five challenges

---

# 1. Records and links

<div class="grid grid-cols-3 gap-5 mt-10">
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-lg font-semibold mb-2">From the CRM</div>
    <p>Acme, Anna, the sale. Plus Rival, timing, small_start.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-lg font-semibold mb-2">From the call</div>
    <p>One meeting, three sentences, three claims.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-lg font-semibold mb-2">The group</div>
    <p>Anna from the CRM. Bob from the call.</p>
  </div>
</div>

---

# 2. Volume

<div class="grid grid-cols-2 gap-5 mt-8">
  <div class="rounded-xl border border-gray-200 p-6 h-44 flex flex-col justify-center">
    <div class="font-semibold mb-2">CRM sync</div>
    <p>Batches of fields. A second copy updates the same record.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-44 flex flex-col justify-center">
    <div class="font-semibold mb-2">Call jobs</div>
    <p>Saved first, then queued. Workers pull when free.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-44 flex flex-col justify-center">
    <div class="font-semibold mb-2">One writer</div>
    <p>Both paths meet at the graph writer.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-44 flex flex-col justify-center">
    <div class="font-semibold mb-2">Wait for the account</div>
    <p>If Anna has not arrived, the job retries.</p>
  </div>
</div>

---

# 3. Accuracy

<div class="mt-6">

| Gate | Acme |
| --- | --- |
| Extract fills a form | Bob, Rival, timing, and an invented discount |
| Validate checks the file | The discount sentence is dropped |
| Resolve stays inside Acme | Bob stays open. Rival links. Two Sams would stay open |
| Memory keeps the decision | Confirming Bob does not create a CRM contact |
| Counts use labels | Both wordings can point at timing |

</div>

---

# 4. Reading

<div class="grid grid-cols-3 gap-5 mt-10">
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-lg font-semibold mb-2">Fixed brief</div>
    <p>Three questions. Same sale, same brief.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-lg font-semibold mb-2">Typed question</div>
    <p>The model may only phrase those facts.</p>
  </div>
  <div class="rounded-xl border border-gray-200 p-6 h-52 flex flex-col justify-center">
    <div class="text-lg font-semibold mb-2">Check</div>
    <p>A citation outside the brief is removed.</p>
  </div>
</div>

---

# 5. Tools

<div class="mt-6">

| Box | Tool |
| --- | --- |
| Graph | Neo4j |
| Extract | A model API that must return the form |
| Queue | A durable job queue, workers, and a CRM schedule |
| Transcript store | File storage |
| Memory, jobs, labels, counts | PostgreSQL |

</div>

<p class="text-center mt-6">The model runs once, between the queue and Validate.</p>

<style>
.soft {
  background: rgba(0, 0, 0, 0.06);
  color: inherit;
}
html.dark .soft {
  background: rgba(255, 255, 255, 0.12);
  color: inherit;
}
.slidev-layout.diagram {
  padding-bottom: 0.75rem;
  overflow: hidden;
}
.slidev-layout.diagram h1 {
  margin-bottom: 0.15rem;
}
.slidev-layout.diagram .mermaid {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 400px;
  overflow: hidden;
}
.slidev-layout.diagram .mermaid svg {
  max-width: 100%;
  max-height: 100%;
}
.slidev-layout.components {
  display: flex !important;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.slidev-layout.components .components-figure {
  display: block;
  width: 100%;
  height: auto;
  max-height: 100%;
  min-height: 0;
  margin: auto 0;
  object-fit: contain;
  flex: 1 1 auto;
}
</style>
