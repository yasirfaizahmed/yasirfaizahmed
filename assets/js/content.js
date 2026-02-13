const projects = [
  {
    id: "llm-inference-platform-kubernetes",
    title: "LLM Inference Platform on Kubernetes",
    summary:
      "Built a production inference stack with autoscaling, canary rollout, and latency SLO monitoring for transformer-based services.",
    details:
      "This platform standardized the path from trained LLM checkpoints to production endpoints.\n\nIt included autoscaling policies based on token throughput, rollout gates using latency/error budgets, and dashboard-first observability for SRE and ML teams.\n\nResult: faster releases, safer deployment confidence, and lower incident response time.",
    tags: ["Kubernetes", "LLM", "Inference", "Prometheus", "Grafana"],
    link: "#"
  },
  {
    id: "mlops-pipeline-multilingual-nlp",
    title: "MLOps Pipeline for Multilingual NLP",
    summary:
      "Designed CI/CD + training pipelines with experiment tracking, model registry, and reproducible deployment for multilingual transformer models.",
    details:
      "Created a complete experiment-to-production workflow for multilingual NLP models.\n\nThe solution combined dataset versioning, automated validation, benchmark reports, and promotion stages from dev to production.\n\nThis reduced training-serving mismatch and improved model reproducibility across teams.",
    tags: ["MLflow", "Airflow", "Transformers", "CI/CD", "NLP"],
    link: "#"
  },
  {
    id: "drift-aware-monitoring-system",
    title: "Drift-Aware Monitoring System",
    summary:
      "Implemented feature and concept drift detection with alerting policy and retraining triggers for reliable production ML behavior.",
    details:
      "Implemented drift monitoring with both statistical and performance-based drift detectors.\n\nAlerts were tied to on-call escalation and retraining playbooks, making the system operationally actionable instead of just informational.\n\nTeams gained early warning and better model lifecycle control.",
    tags: ["Monitoring", "Drift", "Data Quality", "MLOps"],
    link: "#"
  },
  {
    id: "rag-knowledge-assistant",
    title: "RAG Knowledge Assistant for Internal Docs",
    summary:
      "Developed a retrieval-augmented assistant with evaluation harness, prompt governance, and observability for enterprise knowledge search.",
    details:
      "Built a RAG assistant for internal documentation and standards lookup.\n\nIncluded retrieval diagnostics, response quality scoring, and prompt/version governance to maintain factuality and consistency.\n\nDelivered faster internal search outcomes with measurable quality controls.",
    tags: ["RAG", "Embeddings", "Evaluation", "LLM Ops"],
    link: "#"
  },
  {
    id: "vision-model-deployment-blueprint",
    title: "Vision Model Deployment Blueprint",
    summary:
      "End-to-end deployment workflow for a computer vision model: training lineage, staged releases, and cost-performance optimization.",
    details:
      "Designed production deployment architecture for a vision model with strict latency constraints.\n\nThe blueprint covered dataset lineage, staging validation, rollout checks, and resource tuning for GPU efficiency.\n\nIt became a reusable baseline for subsequent CV deployments.",
    tags: ["Deep Learning", "Computer Vision", "Deployment"],
    link: "#"
  },
  {
    id: "feature-store-adoption-playbook",
    title: "Feature Store Adoption Playbook",
    summary:
      "Introduced feature store standards for offline/online parity, reducing training-serving skew across teams.",
    details:
      "Defined feature contracts and ownership standards to align data engineering and ML development.\n\nThe playbook covered feature validation, freshness SLAs, backfill workflows, and discoverability conventions.\n\nOutcome: reduced leakage/skew risks and improved cross-team feature reuse.",
    tags: ["Feature Store", "Platform", "Data Engineering"],
    link: "#"
  }
];

const articles = [
  {
    id: "notebook-to-reliable-ml-system",
    title: "From Notebook to Reliable ML System: A Pragmatic MLOps Checklist",
    summary: "A practical framework for reproducibility, deployment safety, and model governance.",
    content:
      "This article walks through a practical, production-first MLOps checklist.\n\nIt covers reproducible experiments, model registry usage, CI/CD release gates, and post-deployment observability metrics.\n\nThe key message: reliability comes from disciplined process design, not tooling alone.",
    tags: ["MLOps", "Production", "Governance"],
    category: "Technical",
    link: "#"
  },
  {
    id: "transformer-architectures-practice",
    title: "Transformer Architectures: What Actually Matters in Practice",
    summary: "A field guide to architectural choices, trade-offs, and deployment implications.",
    content:
      "A practical look at transformer design choices across encoder/decoder setups, context windows, and fine-tuning modes.\n\nThe article maps architecture decisions to real deployment costs and quality trade-offs.\n\nIdeal for teams moving from experimentation to productionized LLM systems.",
    tags: ["Transformers", "Deep Learning", "LLMs"],
    category: "Technical",
    link: "#"
  },
  {
    id: "evaluating-llm-systems",
    title: "Evaluating LLM Systems Beyond Benchmark Scores",
    summary: "Designing robust evaluation pipelines with domain metrics and failure taxonomy.",
    content:
      "Benchmarks rarely reflect production complexity.\n\nThis piece introduces a layered evaluation strategy: task metrics, robustness checks, hallucination analysis, and human review loops.\n\nIt emphasizes ongoing evaluation as a product capability, not a one-time report.",
    tags: ["LLM Evaluation", "Reliability", "AI Safety"],
    category: "Technical",
    link: "#"
  },
  {
    id: "knowledge-intention-responsibility",
    title: "Knowledge, Intention, and Responsibility in Engineering",
    summary: "A reflection on niyyah, accountability, and ihsān in modern technical work.",
    content:
      "Engineering is not value-neutral in practice.\n\nThis reflection explores how intention (niyyah), trust, and professional accountability shape ethical design choices.\n\nIt proposes an ihsān-oriented mindset for sustained, principled technical excellence.",
    tags: ["Ethics", "Islamic Thought", "Professional Conduct"],
    category: "Islamic Thought",
    link: "#"
  },
  {
    id: "reason-and-revelation-notes",
    title: "Reason and Revelation: Notes on Islamic Philosophy",
    summary: "An introductory set of notes on major themes in Islamic theology and philosophy.",
    content:
      "A beginner-friendly pathway through foundational questions in Islamic theology and philosophy.\n\nTopics include knowledge, causality, moral responsibility, and reason-revelation harmony.\n\nIt is written for readers seeking clarity with balanced references.",
    tags: ["Aqidah", "Philosophy", "Theology"],
    category: "Islamic Thought",
    link: "#"
  },
  {
    id: "tadabbur-for-professionals",
    title: "Tadabbur for the Working Professional",
    summary: "Building a weekly rhythm for Qur'anic reflection while sustaining deep technical work.",
    content:
      "This article presents a realistic framework for weekly tadabbur amid demanding professional schedules.\n\nIt combines small daily reflection units with weekly synthesis and actionable intentions.\n\nThe aim is continuity: consistent heart-work alongside knowledge-work.",
    tags: ["Tadabbur", "Spirituality", "Habits"],
    category: "Islamic Thought",
    link: "#"
  }
];

const tafseerCollections = [
  {
    title: "Surah Al-Fatihah: Orientation of the Believer",
    summary:
      "Themes of servitude, guidance, and worldview formation with compact tafsīr references.",
    tags: ["Al-Fatihah", "Tafseer", "Foundations"],
    link: "#"
  },
  {
    title: "Ayat Al-Kursi (2:255): Divine Sovereignty and Trust",
    summary:
      "A curated reading thread linking theological implications with spiritual reliance (tawakkul).",
    tags: ["Al-Baqarah", "Ayat Al-Kursi", "Aqidah"],
    link: "#"
  },
  {
    title: "Surah Al-‘Asr: Time, Truth, and Discipline",
    summary:
      "On meaningful productivity, righteous action, and sustaining sabr in long-term pursuits.",
    tags: ["Al-Asr", "Character", "Productivity"],
    link: "#"
  },
  {
    title: "Surah Al-Mulk: Awareness and Responsibility",
    summary:
      "Reflections on accountability, humility, and living with an akhirah-centered perspective.",
    tags: ["Al-Mulk", "Accountability", "Reflection"],
    link: "#"
  },
  {
    title: "Selected Verses on Knowledge and Wisdom",
    summary: "A thematic collection of verses on learning, understanding, and beneficial knowledge.",
    tags: ["Ilm", "Hikmah", "Qur'an Themes"],
    link: "#"
  }
];
