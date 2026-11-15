---
layout: post
title: "Building a Searchable SEC Filing Library"
description: "A small Apple filing experiment, and the choices that change when document search becomes historical trading research."
permalink: /quants/sec-filings-search-and-point-in-time-research.html
toc: true
date: 2026-11-15
categories: ["Research methods"]
article_label: Research methods · Financial text
---

I wanted to start with something small: download Apple's annual reports, store
them locally, and search for passages about its business. That led to three
decisions that matter for a larger research system. What information should a
search be allowed to use? What makes a passage relevant? And what needs to be
stored so the result can be reproduced?

I downloaded 31 annual reports covering fiscal years 1996–2026, plus two
amendments. The retained primary-report documents and SEC metadata occupy about
48 MB. A local language model was enough to produce embeddings, but a small
retrieval experiment gave a useful warning: cleaner-looking passages and hybrid
search did not automatically improve the result.

## The task determines the information boundary

For a discretionary investor reading a company today, a current embedding model
can help find relevant historical disclosures. The source filing, its date and
the surrounding context still matter. A passage discussing a supplier ten years
ago is evidence about that period, not necessarily about the current business.

Historical prediction adds a stricter condition: every input must have been
available at the simulated decision time. That condition applies to the
language model as well as to the document. A model trained on later articles
can carry later knowledge into an old filing's representation.

The distinction follows the task rather than the investor's job title.

| Use | Appropriate starting point | Time requirement |
|:--|:--|:--|
| Read company disclosures today | Current retrieval model, keyword search and source citations | Preserve document dates and versions |
| Reconstruct an earlier discretionary decision | Documents and representations restricted to that information set | Point-in-time evidence is necessary |
| Backtest a systematic text predictor | Dated encoder or historically restricted training, then time-ordered estimation | Documents, model, transformations and research selection all need chronological controls |
| Evaluate a fixed system going forward | Freeze the currently available pipeline and log its future inputs and outputs | New outcomes must follow the frozen decisions |

[ChronoBERT](https://huggingface.co/manelalab/chrono-bert-v1-19991231) offers
checkpoints with historical training-information cutoffs. I used the earliest,
dated 31 December 1999, on a report filed in December 2000. These checkpoints
were created much later: they support a reconstruction of a historical
information set, rather than showing that the same software was available then.
Their suitability also depends on the authors' training-data provenance.
[The paper](https://arxiv.org/abs/2502.21206) describes that construction.

For an actual historical forecast, I would also keep amendments separate,
respect publication lags, and fit corpus statistics only on available documents.
An SEC acceptance timestamp and the first moment a document became publicly
available are different concepts. A daily prototype can use a conservative lag;
an intraday strategy needs evidence about the actual availability clock.
[The SEC explains this distinction](https://www.sec.gov/about/webmaster-frequently-asked-questions).

## Several tools cover different parts of the workflow

The SEC provides free filing-history and financial-data APIs. The filing history
also points to additional files containing older submissions. Structured XBRL
facts are a useful route for standard financial numbers; full documents are
needed for narrative disclosures and many detailed tables.
[SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
describes those interfaces.

For the download and parsing layer, examples include:

- [sec-edgar-downloader](https://github.com/jadchaar/sec-edgar-downloader), focused on downloading filings;
- [Datamule](https://github.com/john-friedman/datamule-python), which combines acquisition and document parsing, with optional paid data services;
- [EdgarTools](https://github.com/dgunning/edgartools), which provides interfaces for analysing filings and financial information.

I used Datamule. The SEC submissions index supplied the list, and Datamule
downloaded the actual filings. This also reached reports before the SEC's
[full-text search cutoff of 2001](https://www.sec.gov/edgar/search/efts-faq.html).
The downloader retained the primary annual report and its header metadata;
unrelated exhibits and graphics were outside this small collection's scope.

Embedding models solve a different problem. They map a passage and a question
into vectors so their similarity can be measured. A model's ability to represent
language and its ability to rank search results are related but distinct.

| Option | Useful role | Main trade-off |
|:--|:--|:--|
| Word counts or BM25 | Exact terms, product names, clauses and numbers | Vocabulary overlap can miss paraphrases |
| [BGE-small English](https://huggingface.co/BAAI/bge-small-en-v1.5) | Compact local retrieval baseline | Its training chronology needs consideration in a historical backtest |
| [Qwen3 Embedding](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | Larger local multilingual retrieval model | More computational work; larger size does not establish better results for a particular collection |
| [A hosted embedding API](https://developers.openai.com/api/docs/models/text-embedding-3-small) | Convenient managed inference | API dependency, recurring inference charges and model-vintage questions |
| ChronoBERT | A candidate representation for historical-information experiments | A masked-language encoder needs evaluation before using its pooled outputs for retrieval |

Among embedding models, only ChronoBERT was run in the comparison below. The other models are available
options, rather than measured winners on these filings.

## Passage boundaries changed the retrieval result

I first tried three questions and three excerpts from Apple's fiscal 2000
report. Mean-pooled ChronoBERT representations retrieved the intended excerpt
for the products and manufacturing questions, but chose the products excerpt
for the competition question. That products passage itself referred to a
competition section elsewhere in the filing.

The local model produced six 768-dimensional vectors in about two seconds on
an Apple M2 Pro CPU with four threads. That establishes a small inference
example, not throughput for a large collection.

I then fixed twelve additional questions and supporting answer phrases before
computing a larger comparison. Twenty-one raw excerpts provided the control.
The first cleaner used section headings, paragraph boundaries, removal of
reference-only sentences and a 300-token limit. Dense search, BM25 and hybrid
search all used the same cleaned candidates. Hybrid search combined the two
rankings with equal-weight reciprocal-rank fusion; its settings were fixed.
There were 21 raw excerpts, 27 passages from the first cleaner and 28 from the
sentence-based follow-up. Comparing raw and clean therefore changes segmentation
as well as representation. Within each clean corpus, all three rankers search
identical candidates.

The first cleaner left very short token fragments. After inspecting that
failure, I made one exploratory follow-up that kept whole sentences together.
The model, questions, keyword settings and fusion rule stayed fixed. The
earlier query and raw-passage vectors were reused.

Counts below measure whether the returned text contains one of the specified
answer phrases, among twelve questions on this one report.

| Passage and ranking method | Phrase found in first result | Phrase found in first three |
|:--|--:|--:|
| Raw excerpts, dense search | 7/12 | 10/12 |
| First cleaner, dense search | 2/12 | 3/12 |
| First cleaner, keyword search | 3/12 | 6/12 |
| First cleaner, hybrid search | 3/12 | 7/12 |
| Sentence-based follow-up, dense search | 2/12 | 3/12 |
| Sentence-based follow-up, keyword search | 3/12 | 7/12 |
| Sentence-based follow-up, hybrid search | 2/12 | 7/12 |

The raw excerpts did better on this measure. Four of their seven first-result
hits, however, obtained the answer from a neighbouring section included in the
excerpt. They found useful text without necessarily identifying the right
section. The phrase measure also missed a plausible answer: a retrieved passage
explicitly named the Macintosh platform, but lacked the particular sentences
chosen as its answer anchors.

This is a small exploratory diagnostic. The sentence-based version was designed
after seeing the first results, and the same questions were then reused. The
counts establish neither general search quality nor a trading advantage. They
show why I would inspect returned passages and preserve a simple baseline
before adding more components. The ChronoBERT weights stayed fixed, no later
filing text entered the comparison, and no teacher model or fine-tuning was
introduced; that does not independently certify the checkpoint's full training
provenance.

## Store originals, tables and indexes for different purposes

I would retain original documents once, with company identifiers, accession
numbers, filing dates and source links. Extracted text, tables and passages
should point back to those originals and carry their extraction versions.
Embeddings need the model revision, pooling rule and chunk version alongside
their vectors. Changing the model creates a different coordinate system; vectors
from different checkpoints should not be casually compared as if they shared one.

The local example uses DuckLake for tabular data, including passages and vectors,
with Parquet files underneath. The source report bundles stay as files. The
candidate search is an exact vector comparison plus a small keyword scorer.
DuckLake supplies table storage and catalogue management; a low-latency vector
service is a separate choice.

```text
SEC documents -> retained originals -> extracted text and tables
                                     -> passages -> embeddings
Dates, identifiers and versions ------> DuckLake catalogue
Question ----------------------------> retrieval -> passages and source links
```

For a single local client, DuckDB can hold DuckLake's catalogue. Its documented
cross-process attachment rules make a shared team workflow a different design
decision. DuckLake recommends PostgreSQL for a multi-user lakehouse with remote
clients. Its table snapshots record storage history; financial point-in-time
validity still depends on the publication and availability fields.
[DuckLake's catalogue guide](https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database)
sets out those choices.

## Storage is only one part of the bill

The retained Apple report bundles occupy 47.8 MB. The pinned model and tokenizer
occupy about 602 MB. Neither requires a cloud service to run locally, although
hardware, electricity and backups still have costs.

For context, these are illustrative monthly storage charges before free
allowances and other services, using decimal units and a constant stored volume.
Prices were checked on 15 November 2026.

| Object storage | 100 GB | 1,000 GB | Important charging detail |
|:--|--:|--:|:--|
| [Cloudflare R2 Standard](https://developers.cloudflare.com/r2/pricing/) | $1.50 | $15.00 | Request charges; standard free allowances; direct egress is free |
| [Backblaze B2](https://www.backblaze.com/cloud-storage/pricing) | About $0.70 | $6.95 | Free transactions and egress up to three times average stored volume |
| [Amazon S3 Standard, US East N. Virginia](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json) | $2.30 | $23.00 | First storage tier; requests and data transfer can add charges |

These are storage arithmetic, not quotes for a complete search system. They
exclude tax, extra copies, managed databases, serving compute and embedding or
answer-generation inference. Provider units, allowances and workload details
need checking against an actual bill.

Vector payloads can also be estimated directly. One million 768-dimensional
float32 embeddings occupy 3.072 GB before metadata, index structures, replicas
and file-format overhead. An approximate search index can require additional
memory even when the stored vectors themselves are inexpensive.

Embedding charges and answer generation belong in separate budgets. For
example, OpenAI currently lists text-embedding-3-small at $0.02 per million
input tokens: 100 million billed input tokens would cost $2 for embeddings
alone. A generative model producing answers introduces another workload and
another bill. [Model pricing](https://developers.openai.com/api/docs/models/text-embedding-3-small)
provides the current input rate.

## Scale the part that becomes a bottleneck

For a personal collection, local files, a catalogue and exact search are easy
to inspect. I would measure loading time, query latency and relevance before
adding a separate vector database.

A wider filing universe needs incremental acquisition, persistent identifiers,
deduplication and versioned extraction. Batch embeddings can be cached by
passage content and model revision. A changed passage needs a new embedding;
a changed encoder can require re-embedding the collection. Tables and narrative
text also need different handling: a semantically related paragraph is not a
substitute for extracting the correct financial number, unit and reporting period.

For shared, concurrent search, examples include
[PostgreSQL with pgvector](https://github.com/pgvector/pgvector) and
[Qdrant](https://qdrant.tech/documentation/search/hybrid-queries/).
pgvector supports exact search and approximate indexes; Qdrant supports
multi-stage and hybrid queries. Approximate search trades some nearest-neighbour
recall for efficiency. Exact nearest neighbours themselves are only as useful
as the representation and relevance definition behind them. Neither service
was benchmarked in the Apple example.

## The useful system depends on the decision

For reading disclosures today, I would start with a small retrieval-trained
model, keyword search and inspectable citations. For historical prediction,
I would first establish the information boundary and test a dated representation
against a simple historical baseline. The same file collection can support both
tasks, with different controls.

The Apple experiment supports keeping the raw-excerpt baseline for now. The
tested cleaners and hybrid rule did not earn a replacement. A useful research
library should make that comparison cheap to reproduce, preserve the source
behind every result, and add infrastructure when a measured bottleneck justifies it.
